from keystoneclient import exceptions as keystone_exceptions
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import logging

LOG = logging.getLogger(__name__)

from cloud_mongo.utils import get_keystone_client, check_token_expiration, get_keystone_version
from cloud_mongo.user import Token, create_user_from_token
from cloud_mongo.exceptions import KeystoneAuthException

KEYSTONE_CLIENT_ATTR = "_keystoneclient"

user_domain_name = None
username = "admin"
password = "admin"
auth_url = "http://192.168.3.165:5000/v2.0"


def check_auth_expiry(auth_ref):
        if not check_token_expiration(auth_ref):
            msg = _("The authentication token issued by the Identity service "
                    "has expired.")
            LOG.warning("The authentication token issued by the Identity "
                        "service appears to have expired before it was "
                        "issued. This may indicate a problem with either your "
                        "server or client configuration.")
            raise KeystoneAuthException(msg)
        return True


def authenticate(request=None, username=None, password=None,
                     user_domain_name=None, auth_url=None):
        """Authenticates a user via the Keystone Identity API. """
        LOG.debug('Beginning user authentication for user "%s".' % username)

        insecure = getattr("settings", 'OPENSTACK_SSL_NO_VERIFY', False)
        endpoint_type = getattr(
            "settings", 'OPENSTACK_ENDPOINT_TYPE', 'publicURL')

        keystone_client = get_keystone_client()
        try:
            client = keystone_client.Client(
                user_domain_name=user_domain_name,
                username=username,
                password=password,
                auth_url=auth_url,
                insecure=insecure,
                debug=settings.DEBUG)

            unscoped_auth_ref = client.auth_ref
            unscoped_token = Token(auth_ref=unscoped_auth_ref)
        except (keystone_exceptions.Unauthorized,
                keystone_exceptions.Forbidden,
                keystone_exceptions.NotFound) as exc:
            msg = _('Invalid user name or password.')
            LOG.debug(exc.message)
            raise KeystoneAuthException(msg)
        except (keystone_exceptions.ClientException,
                keystone_exceptions.AuthorizationFailure) as exc:
            msg = _("An error occurred authenticating. "
                    "Please try again later.")
            LOG.debug(exc.message)
            raise KeystoneAuthException(msg)

        # Check expiry for our unscoped auth ref.
        check_auth_expiry(unscoped_auth_ref)

        # Check if token is automatically scoped to default_project
        if unscoped_auth_ref.project_scoped:
            auth_ref = unscoped_auth_ref
        else:
            # For now we list all the user's projects and iterate through.
            try:
                if get_keystone_version() < 3:
                    projects = client.tenants.list()
                else:
                    client.management_url = auth_url
                    projects = client.projects.list(
                        user=unscoped_auth_ref.user_id)
            except (keystone_exceptions.ClientException,
                    keystone_exceptions.AuthorizationFailure) as exc:
                msg = _('Unable to retrieve authorized projects.')
                raise KeystoneAuthException(msg)

            # Abort if there are no projects for this user
            if not projects:
                msg = _('You are not authorized for any projects.')
                raise KeystoneAuthException(msg)

            while projects:
                project = projects.pop()
                try:
                    client = keystone_client.Client(
                        tenant_id=project.id,
                        token=unscoped_auth_ref.auth_token,
                        auth_url=auth_url,
                        insecure=insecure,
                        debug=settings.DEBUG)
                    auth_ref = client.auth_ref
                    break
                except (keystone_exceptions.ClientException,
                        keystone_exceptions.AuthorizationFailure):
                    auth_ref = None

            if auth_ref is None:
                msg = _("Unable to authenticate to any available projects.")
                raise KeystoneAuthException(msg)

        # Check expiry for our new scoped token.
        check_auth_expiry(auth_ref)

        # If we made it here we succeeded. Create our User!
        user = create_user_from_token(
            request,
            Token(auth_ref),
            client.service_catalog.url_for(endpoint_type=endpoint_type))

        if request is not None:
            request.session['unscoped_token'] = unscoped_token.id
            request.user.token = user.token
            request.user.authorized_tenants = user.authorized_tenants
            request.user.service_catalog = user.service_catalog
            request.user.services_region = user.services_region


            # Support client caching to save on auth calls.
            setattr(request, KEYSTONE_CLIENT_ATTR, client)

        LOG.debug('Authentication completed for user "%s".' % username)
        return user
