'''
Created on 17-Dec-2013

@author: ganesh
'''
from mongoengine.django.mongo_auth.models import get_user_document

from django.contrib import auth
from .exceptions import KeystoneAuthException
from django.utils.translation import ugettext_lazy as _
from cloud_mongo import trail
import horizon
import logging
from openstack_authenticate import authenticate

LOG = logging.getLogger(__name__)

class CloudMongoBackend(object):
    'To check permission seperate backend'
    """Authenticate using MongoEngine and mongoengine.django.auth.User.
    """

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False
    DEFAULT_IDENTITY_PORT = "" #":5000/v2.0"

    def authenticate(self, request=None,username=None, password=None):
        try:
            get_user_document().objects(username=username.lower()).first()
        except Exception, e:
            print e
        user = get_user_document().objects(username=username.lower()).first()
        if user:
            if password and user.check_password(password):
                if not user.status:
                    msg = _("Your Account is Not Activated. \n"
                          "Please Activate Account, and Login")
                    LOG.debug(msg)
                    raise KeystoneAuthException(msg)
                if user.roles == []:
                    msg = _("You do not have any permission to perform")
                    LOG.debug(msg)
                    raise KeystoneAuthException(msg)
                backend = auth.get_backends()[0]
                user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            else:
                msg = _("Please Login with "
                          "Correct Password.")
                LOG.debug(msg)
                raise KeystoneAuthException(msg)
            
            cloud = []
            cloud1 = []
            cloud2 = []
            cloud1 = sum([[y.cloudid for y in i.policy 
                          if y.cloudid.platform == "Cnext"] 
                         for i in user.roles], [])
            cloud2 = sum([[y.cloudid for y in i.policy 
                          if y.cloudid.platform == "Amazon"] 
                         for i in user.roles], [])
            cloud3 = sum([[y.cloudid for y in i.policy 
                          if y.cloudid.platform == "Hpcloud"] 
                         for i in user.roles], [])
            
            cloud = sum([[y.cloudid for y in i.policy 
                          if y.cloudid.platform == "Openstack"] 
                         for i in user.roles], [])
            if cloud:
                try:
                    cloud_endpoint  = cloud[0]["cloud_meta"]["endpoint"]
                    cloud_accesskey = cloud[0]["cloud_meta"]["publickey"]
                    cloud_privatekey = trail.encode_decode(cloud[0]["cloud_meta"]["privatekey"],"decode")
                    ##Getting openstack user object by calling keystone client ##
                    openstack_user = authenticate(user_domain_name=None,username=cloud_accesskey,
                                 password=cloud_privatekey,
                                 auth_url=cloud_endpoint + self.DEFAULT_IDENTITY_PORT)
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
                    user.endpoint = cloud_endpoint + self.DEFAULT_IDENTITY_PORT
                    user.openstackname = cloud[0]["name"]
                    msg = _("Successfully user token created in "
                          "Mongodb.")
                    LOG.debug(msg)
                except:
                    pass
                
            if cloud1:
                user.cnextpublickey = cloud1[0]["cloud_meta"]["publickey"]
                user.cnextprivatekey = cloud1[0]["cloud_meta"]["privatekey"]
                user.cnextendpoint = cloud1[0]["cloud_meta"]["endpoint"]
                user.cnextname = cloud1[0]["name"]
            if cloud2:
                user.awspublickey = cloud2[0]["cloud_meta"]["publickey"]
                user.awsprivatekey = cloud2[0]["cloud_meta"]["privatekey"]
                user.awsendpoint = cloud2[0]["cloud_meta"]["endpoint"]
                user.awsname = cloud2[0]["name"]
            if cloud3:
                try:
                    for x in range(len(cloud3)):
                        cloud_endpoint  = cloud3[x]["cloud_meta"]["endpoint"]
                        cloud_accesskey = cloud3[x]["cloud_meta"]["publickey"]
                        cloud_privatekey = trail.encode_decode(cloud3[x]["cloud_meta"]["privatekey"],"decode")
                        ##Getting openstack user object by calling keystone client ##
                        openstack_user = authenticate(user_domain_name=None,username=cloud_accesskey,
                                                      password=cloud_privatekey,
                                                      auth_url=cloud_endpoint + self.DEFAULT_IDENTITY_PORT)
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
                        hp = trail.Hpclouddata(token = otoken,\
                                               authorized_tenants = [remove_tenants(d.__dict__) for d in openstack_user.authorized_tenants],\
                                               service_catalog = openstack_user.service_catalog,\
                                               services_region = openstack_user.services_region,\
                                               project_name = openstack_user.project_name,\
                                               tenant_name = openstack_user.tenant_name,\
                                               tenant_id = openstack_user.tenant_id,\
                                               project_id = openstack_user.project_id,\
                                               endpoint = cloud_endpoint + "",\
                                               hpcloudid = cloud3[x]["id"]
                                               )
                        hp.save()
                        if x == 0:
                            user.hp_attr = hp
                            user.hpname = cloud3[x]["name"]
                    msg = _("Successfully user token created in "
                          "Mongodb.")
                    LOG.debug(msg)    
                except:
                    pass
                
            user.save() 
            return user

        else:
            msg = _("Invalid Credentials.")
            LOG.debug(msg)
            raise KeystoneAuthException(msg)
        return None

    def get_user(self, user_id):
        return get_user_document().objects.with_id(user_id)
    
    def get_all_permissions(self, user, obj=None):
        """Returns a set of permission strings that this user has through
           his/her Keystone "roles".

          The permissions are returned as ``"openstack.{{ role.name }}"``.
        """
        if user.is_anonymous() or obj is not None:
            return set()
        # TODO(gabrielhurley): Integrate policy-driven RBAC
        #                      when supported by Keystone.
        
        role_perms = set()
        service_perms = set()
        
        cloud = sum([[y.cloudid.platform for y in i.policy ] for i in user.roles], [])
        clouds = set(["%s" % a.lower()
                          for a in cloud])
        
        if user.token:
            role_perms = set(["openstack.roles.%s" % role['name'].lower()
                          		for role in user.token.roles])
            service_perms = set(["openstack.services.%s" % service['type'].lower()
                          for service in user.service_catalog])
            if "openstack.roles.admin" in role_perms:
                user.is_superuser = True
                user.save()
        else:
            if "openstack" in clouds:
                clouds.remove("openstack")
            
            if "openstack" in role_perms:
                role_perms.remove("openstack")
        
        if "openstack" in clouds:
            project_name = horizon.get_dashboard("project")
            project_name.name = user.openstackname

        if not user.cnextpublickey:
            if "cnext" in clouds:
                clouds.remove("cnext")
            if "cnext" in role_perms:
                role_perms.remove("cnext")
        if not user.awspublickey:
            if "amazon" in clouds:
                clouds.remove("amazon")
            if "amazon" in role_perms:
                role_perms.remove("amazon")    
        
        if "cnext" in clouds:
                cproject_name = horizon.get_dashboard("cnext")
                cproject_name.name = user.cnextname   
        if "hpcloud" in clouds:
                hproject_name = horizon.get_dashboard("hpcloud")
                hproject_name.name = user.hpname
        if "amazon" in clouds:
                cproject_name = horizon.get_dashboard("amazon")
                cproject_name.name = user.awsname
        
        LOG.debug("End of get all permission check %s obj %s perm"%(obj,clouds.union(role_perms)))
        role_perm = role_perms | service_perms
        return clouds.union(role_perm)



    def has_perm(self, user, perm, obj=None):
        """Returns True if the given user has the specified permission. """
        if not user.is_active:
            return False
        LOG.debug(perm)
        return perm in self.get_all_permissions(user, obj)

    def has_module_perms(self, user, app_label):
        """Returns True if user has any permissions in the given app_label.

           Currently this matches for the app_label ``"openstack"``.
        """
        if not user.is_active:
            return False
        for perm in self.get_all_permissions(user):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

def get_user(userid):
    """Returns a User object from an id (User.id). Django's equivalent takes
    request, but taking an id instead leaves it up to the developer to store
    the id in any way they want (session, signed cookie, etc.)
    """
    if not userid:
        #return AnonymousUser()
        return None
    #return MongoEngineBackend().get_user(userid) or AnonymousUser()
    return MongoEngineBackend().get_user(userid) or None

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)
        
def default_services_region(service_catalog):
        """
        Returns the first endpoint region for first non-identity service
        in the service catalog
        """
        if service_catalog:
            for service in service_catalog:
                if service['type'] == 'identity':
                    continue
                for endpoint in service['endpoints']:
                    return endpoint['region']
        return None
    
def remove_tenants(tenant):
    del tenant["manager"]
    return tenant
