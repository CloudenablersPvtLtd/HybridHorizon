# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from django import shortcuts
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import (login as django_login,
                                       logout_then_login as django_logout)
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.functional import curry
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

try:
    from django.utils.http import is_safe_url
except ImportError:
    from .utils import is_safe_url

from keystoneclient.v2_0 import client as keystone_client_v2
from keystoneclient import exceptions as keystone_exceptions

from .forms import Login
from .trail import set_session_from_user
from .user import create_user_from_token
from .user import Token
from .utils import get_keystone_client
from .utils import get_keystone_version
from cloud_mongo import trail
from mongoengine.django.mongo_auth.models import get_user_document
from cloud_mongo.trail import Hpclouddata,tenantclouds

LOG = logging.getLogger(__name__)

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    """ Logs a user in using the :class:`~openstack_auth.forms.Login` form. """
    # Get our initial region for the form.
    initial = {}
    current_region = request.session.get('region_endpoint', None)
    requested_region = request.GET.get('region', None)
    regions = dict(getattr(settings, "AVAILABLE_REGIONS", []))
    if requested_region in regions and requested_region != current_region:
        initial.update({'region': requested_region})

    if request.method == "POST":
        form = curry(Login, request)
    else:
        form = curry(Login, initial=initial)

    extra_context = {'redirect_field_name': REDIRECT_FIELD_NAME}

    if request.is_ajax():
        template_name = 'auth/_login.html'
        extra_context['hide'] = True
    else:
        template_name = 'auth/login.html'
    res = django_login(request,
                       template_name=template_name,
                       authentication_form=form,
                       extra_context=extra_context)
    # Set the session data here because django's session key rotation
    # will erase it if we set it earlier.
    if request.user.is_authenticated():
        set_session_from_user(request, request.user)
        regions = dict(Login.get_region_choices())
        region = request.user.endpoint
        region_name = regions.get(region)
        request.session['region_endpoint'] = region
        request.session['region_name'] = region_name
    
    return res


def logout(request):
    msg = 'Logging out user "%(username)s".' % \
        {'username': request.user.username}
    LOG.info(msg)
    try:    
        user = get_user_document().objects(username=request.user.username).first()
        if request.user.hp_attr:
            hp_clouds = Hpclouddata.objects.all()
            for hp_cloud in hp_clouds:
                delete_token(endpoint=hp_cloud.endpoint,token_id=hp_cloud.token.id)
                hp = Hpclouddata.objects(id = hp_cloud.id).first()
                hp.delete()
            user.hp_attr = None
            user.hpname = None
        if request.user.token and request.user.endpoint:
            delete_token(endpoint=request.user.endpoint, token_id=request.user.token.id)
            user.token = None
            user.authorized_tenants = None
            user.service_catalog = None
            user.services_region = None
            user.project_name = None
            user.tenant_name = None
            user.tenant_id = None
            user.project_id = None
            user.endpoint = None
            user.openstackname = None
        else:
            LOG.debug("User token not deleted")
        user.is_superuser = False
        user.save()
    except:
        LOG.debug("User token not deleted")
    return django_logout(request)
        


def delete_token(endpoint, token_id):
    """Delete a token."""
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    try:
        if get_keystone_version() < 3:
            client = keystone_client_v2.Client(
                endpoint=endpoint,
                token=token_id,
                insecure=insecure,
                debug=settings.DEBUG
            )
            client.tokens.delete(token=token_id)
            LOG.debug('Deleted token %s' % token_id)
        else:
            # FIXME: KS-client does not have delete token available
            # Need to add this later when it is exposed.
            pass
    except keystone_exceptions.ClientException as e:
        print e
        LOG.info('Could not delete token')


@login_required
def switch(request, tenant_id, redirect_field_name=REDIRECT_FIELD_NAME):
    """ Switches an authenticated user from one project to another. """
    LOG.debug('Switching to tenant %s for user "%s".'
              % (tenant_id, request.user.username))
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    endpoint = request.user.endpoint
    try:
        if get_keystone_version() >= 3:
            endpoint = endpoint.replace('v2.0', 'v3')
        client = get_keystone_client().Client(tenant_id=tenant_id,
                                              token=request.user.token.id,
                                              auth_url=endpoint,
                                              insecure=insecure,
                                              debug=settings.DEBUG)
        auth_ref = client.auth_ref
        msg = 'Project switch successful for user "%(username)s".' % \
            {'username': request.user.username}
        LOG.info(msg)
    except keystone_exceptions.ClientException:
        msg = 'Project switch failed for user "%(username)s".' % \
            {'username': request.user.username}
        LOG.warning(msg)
        auth_ref = None
        LOG.exception('An error occurred while switching sessions.')

    # Ensure the user-originating redirection url is safe.
    # Taken from django.contrib.auth.views.login()
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL

    if auth_ref:
        old_endpoint = request.session['region_endpoint']
        old_token = request.user.token
        if old_token and old_endpoint and old_token.id != auth_ref.auth_token:
            delete_token(endpoint=old_endpoint, token_id=old_token.id)
        openstack_user = create_user_from_token(request, Token(auth_ref), endpoint)
        
        user = get_user_document().objects(username=request.user.username).first()
        
        utoken = openstack_user.token
        otoken = trail.DocToken(user=utoken.user, 
                                    user_domain_id=utoken.user_domain_id,
                                    id=utoken.id,
                                    project=utoken.project,
                                    tenant=utoken.project,
                                    domain=utoken.domain,
                                    roles=utoken.roles,
                                    serviceCatalog=utoken.serviceCatalog
                                    )
        user.token = otoken
        user.authorized_tenants = [remove_tenants(d.__dict__) for d in openstack_user.authorized_tenants]
        user.service_catalog = openstack_user.service_catalog
        user.services_region = openstack_user.services_region
        user.project_name = openstack_user.project_name
        user.tenant_name = openstack_user.tenant_name
        user.tenant_id = openstack_user.tenant_id
        user.project_id = openstack_user.project_id
        role_perms = set(["openstack.roles.%s" % role['name'].lower()
                                  for role in otoken.roles])
        if "openstack.roles.admin" in role_perms:
            user.is_superuser = True
        else:
            user.is_superuser = False       
        
        user.save()
        set_session_from_user(request, user)
    return shortcuts.redirect(redirect_to)


def switch_region(request, region_name,
                  redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Switches the non-identity services region that is being managed
    for the scoped project.
    """
    if region_name in request.user.available_services_regions:
        request.session['services_region'] = region_name
        LOG.debug('Switching services region to %s for user "%s".'
                  % (region_name, request.user.username))

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL

    return shortcuts.redirect(redirect_to)

def remove_tenants(tenant):
    del tenant["manager"]
    return tenant


@login_required
def switch_cnext_tenants(request, tenant_id, redirect_field_name=REDIRECT_FIELD_NAME):
    """ Switches an authenticated user from one project to another. """
    LOG.debug('Switching to tenant %s for user "%s".'
              % (tenant_id, request.user.username))
    
    user = get_user_document().objects(username=request.user.username).first()
    
    cnext_tenant = tenantclouds.objects(id=tenant_id).first()
    user.cnextpublickey = cnext_tenant["cloud_meta"]["publickey"]
    user.cnextprivatekey = cnext_tenant["cloud_meta"]["privatekey"]
    user.cnextendpoint = cnext_tenant["cloud_meta"]["endpoint"]
    user.cnextname = cnext_tenant["name"]
    
    user.save()  
    
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL
    
    return shortcuts.redirect(redirect_to)
