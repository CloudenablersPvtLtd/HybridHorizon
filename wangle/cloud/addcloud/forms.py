from mongoengine import *
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions,forms,workflows,messages
from horizon.utils import validators,fields
from cloud_mongo import trail
from mongoengine.django.mongo_auth.models import get_user_document
from cloud_mongo.cloudmongobackend import remove_tenants
import logging
from cloud_mongo.trail import encode_decode,refresh_session_policies,roledetail,actions,clouds,tenantclouds
from cloud_mongo.views import delete_token
from cloud_mongo import openstack_authenticate
from aws_api.connection import test,get_regions_wo_connection
import httplib2

LOG = logging.getLogger(__name__)


class CreateCloudAction(workflows.Action):
     
    cloudtype = forms.ChoiceField(
        label=_("Platform"),
        required=True,
        widget=fields.SelectWidget(
            data_attrs=('name','type',),
            transform=lambda x: ("%s " % (x.name)))
        )
    
    cloudlist = forms.ChoiceField(
        label=_("Cloud Type"),
        required=True,
        widget=fields.SelectWidget(
            data_attrs=('name','type',),
            transform=lambda x: ("%s " % (x.type)))
         )
    cloudname = forms.CharField(label=_("Cloud Name"),max_length=80)
    
    cloud_id = forms.CharField(required=False, widget=forms.HiddenInput())
    publickey = forms.CharField(
                                label=_("Public Key"), max_length=None)
    secretkey = forms.RegexField(
                                label=_("Secret Key"),
                                widget=forms.PasswordInput(render_value=False),
                                regex=validators.password_validator(),
                                error_messages={'invalid': validators.password_validator_msg()})
    endpoint =  forms.CharField(max_length=80, label=_("Endpoint(IP with HTTP)"))



    class Meta:
        name = _("ADD Cloud")
        
    def __init__(self, *args, **kwargs):
        super(CreateCloudAction, self).__init__(*args, **kwargs)
        try:
            region_list = get_regions_wo_connection()
            cloud_id = args[-1]["cloud_id"]
            cloud_obj = clouds.objects(id=cloud_id).first()
            self.fields['publickey'].label = _(cloud_obj.credential_fields[0])
            self.fields["secretkey"].label = _(cloud_obj.credential_fields[1])
            if cloud_obj.name == "Amazon":
                self.fields["endpoint"] = forms.ChoiceField(label=_("Default Region"),
                                                           choices = region_list,
                                                           help_text=_("Select default region"))
                self.fields["endpoint"].label = _(cloud_obj.credential_fields[2])
            else:
                self.fields["endpoint"].label = _(cloud_obj.credential_fields[2])
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)


    def populate_cloudtype_choices(self, request, context):
        try:
            cloudlist = clouds.objects(id=context["cloud_id"]).first()
            clouds_obj = [(cloudlist.name, cloudlist)]
           
        except Exception:
            print "exception"
            exceptions.handle(request,
                              _('Unable to retrieve list of Cloud Details'))
            clouds_obj = []
        return clouds_obj
   


    def populate_cloudlist_choices(self, request, context):
        clouds_obj = []
        try:
            cloudlist = clouds.objects(id=context["cloud_id"]).first()
            for types in cloudlist.type:
                clouds_obj.append((types,types))
           
        except Exception:
            print "exception"
            exceptions.handle(request,
                              _('Unable to retrieve list of Cloud Details'))
            clouds_obj = []
        return clouds_obj



class CreateCloud(workflows.Step):
    action_class = CreateCloudAction
    contributes = ("cloud_id",)
    
    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['endpoint'] = data.get("endpoint", None)
            context['password'] = data.get("password", None)
            context['cloudname'] = data.get("cloudname", None)
            context['username'] = data.get("username", None)
            context['platform'] = data.get("cloudtype", None)
            context['publickey'] = data.get("publickey", None)
            context['secretkey'] = data.get("secretkey", None)
            context['cloud_type'] = data.get("cloudlist", None)
            
           
        return context 


class CreateCloudForm(workflows.Workflow):
    slug = "add_cloud"
    name = _("Add Cloud")
    template_name = 'wangle/cloud/addcloud/create.html'
    finalize_button_name = _("ADD")
    success_url = "horizon:wangle:cloud:index"
    default_steps = (CreateCloud, )
    
    success_message = _("Cloud created with given credential successfully.")
    failure_message = _("Cloud not created. Either Credential or Endpoint Given is Invalid")
    
        
    def handle(self, request, context):
        cloud_id = context.get('cloud_id', None)
        username = context.get('publickey', None)
        cloudname = context.get('cloudname', None)
        platform = context.get('platform', None)
        password = context.get('secretkey', None)
        endpoint = context.get('endpoint', None)
        cloud_type = context.get('cloud_type', None)
        if (username == '') & (password == ''):
            username = context.get('publickey', None)
            password = context.get('secretkey', None)
        get_user_document().objects(username=request.user.username).first()
        user = get_user_document().objects(username=request.user.username).first()
        try:
            if platform == "Cnext":
                httpInst = httplib2.Http()
                httpInst.add_credentials(name = username, \
                                     password = password)
                url = endpoint + "/api/instance?resourceType=vm"
                resp, body = httpInst.request(url)
                if resp.status == 200 :
                    cloud = tenantclouds(name = cloudname,cloud_type = cloud_type, 
                                        platform = platform,cloud_meta ={"publickey":username,"privatekey":encode_decode(password,"encode"),"endpoint":endpoint},
                                        tenantid=request.user.tenantid.id,
                                        cloudid=cloud_id)
                    cloud.save()
                    
                    roles = roledetail.objects(tenantid = request.user.tenantid.id)
                    allowed_action = actions.objects.first().allowed
                    for role in roles:
                        if role.roletype == "Tenant Admin" and role.name == "Tenant Admin":
                            i = {"cloudid":cloud.id,"provider":"ALL","region":"ALL","allowed": allowed_action}
                            roledetail.objects(id = role.id).update(push__policy=i)
                        else:
                            pass
                    if user.cnextname == "" or user.cnextname is None:
                        user.cnextpublickey = username
                        user.cnextprivatekey = encode_decode(password,"encode")
                        user.cnextendpoint = endpoint
                        user.cnextname = cloudname
                        user.save()
                    
                    refresh_session_policies(request, request.user)
                    return True
                else:
                    return False
            
            elif platform == "Openstack":
                openstack_user = openstack_authenticate.authenticate(user_domain_name=None,username=username,
                                 password=password,
                                 auth_url= endpoint)
                utoken = openstack_user.token
                if utoken:
                    cloud = tenantclouds(name = cloudname,cloud_type = cloud_type, 
                                        platform = platform,cloud_meta ={"publickey":username,"privatekey":encode_decode(password,"encode"),"endpoint":endpoint},
                                        tenantid=request.user.tenantid.id,
                                        cloudid=cloud_id)
                    cloud.save()
                    allowed_action = actions.objects.first().allowed
                    roles = roledetail.objects(tenantid = request.user.tenantid.id)
                    for role in roles:
                        if role.roletype == "Tenant Admin" and role.name == "Tenant Admin":
                            i = {"cloudid":cloud.id,"provider":"","region":"","allowed":allowed_action}
                            roledetail.objects(id = role.id).update(push__policy=i)
                    
                    if user.openstackname == "" or user.openstackname is None:
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
                        user.endpoint = endpoint + ""
                        user.openstackname = cloudname
                        msg = _("Successfully user token created in "
                          "Mongodb.")
                        user.save() 
                        LOG.debug(msg)
                    else:
                        delete_token(endpoint,utoken.id)
                    refresh_session_policies(request, request.user)        
                    return True
                else:
                    return False
            elif platform == "Hpcloud":
                openstack_user = openstack_authenticate.authenticate(user_domain_name=None,username=username,
                                 password=password,
                                 auth_url= endpoint)
                utoken = openstack_user.token
                if utoken:
                    cloud = tenantclouds(name = cloudname,cloud_type = cloud_type, 
                                        platform = platform,cloud_meta ={"publickey":username,"privatekey":encode_decode(password,"encode"),"endpoint":endpoint},
                                        tenantid=request.user.tenantid.id,
                                        cloudid=cloud_id)
                    cloud.save()
                    allowed_action = actions.objects.first().allowed
                    roles = roledetail.objects(tenantid = request.user.tenantid.id)
                    for role in roles:
                        if role.roletype == "Tenant Admin" and role.name == "Tenant Admin":
                            i = {"cloudid":cloud.id,"provider":"","region":"","allowed":allowed_action}
                            roledetail.objects(id = role.id).update(push__policy=i)
        
        
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
                                      endpoint = endpoint + "",\
                                      hpcloudid = cloud.id
                                      )
                    hp.save()
                    if user.hp_attr == "" or user.hp_attr is None:
                        user.hp_attr = hp
                        user.hpname = cloudname
                        user.save()
                    msg = _("Successfully user token created in "
                          "Mongodb.") 
                    LOG.debug(msg)        
                    refresh_session_policies(request, request.user)
                    return True
                    
                else:
                    return False
                
            elif platform == "Amazon":  
                    status = test(endpoint,username,password)
                    if status == True:                                     
                        cloud = tenantclouds(name = cloudname,cloud_type = cloud_type, 
                                            platform = platform,cloud_meta ={"publickey":username,"privatekey":encode_decode(password,"encode"),"endpoint":endpoint},
                                            tenantid=request.user.tenantid.id,
                                            cloudid=cloud_id)
                        cloud.save()
                        
                        roles = roledetail.objects(tenantid = request.user.tenantid.id)
                        allowed_action = actions.objects.first().allowed
                        for role in roles:
                            if role.roletype == "Tenant Admin" and role.name == "Tenant Admin":
                                i = {"cloudid":cloud.id,"provider":"ALL","region":"ALL","allowed": allowed_action}
                                roledetail.objects(id = role.id).update(push__policy=i)
                            else:
                                pass
                        if user.awsname == "" or user.awsname is None:
                            user.awspublickey = username
                            user.awsprivatekey = encode_decode(password,"encode")
                            user.awsendpoint = endpoint
                            user.awsname = cloudname
                            user.save()
                        refresh_session_policies(request, request.user)             
                        return True
                    else:
                        return False
            else:
                cloud = tenantclouds(name = cloudname,cloud_type = cloud_type, 
                                        platform = platform,cloud_meta ={"publickey":username,"privatekey":encode_decode(password,"encode"),"endpoint":endpoint},
                                        tenantid=request.user.tenantid.id)
                cloud.save()
                
                roles = roledetail.objects(tenantid = request.user.tenantid.id)
                for role in roles:
                    if role.roletype == "Tenant Admin" and role.name == "Tenant Admin":
                        i = {"cloudid":cloud.id,"provider":[],"region":[],"allowed":[ "Create Instance" , "Delete Instance" , "Create KP and SG" , "Delete KP and SG" , "Start Instance" , "Stop Instance" , "Create Volume" , "Delete Volume" , "Attach and  Dettach  Volume"]}
                        roledetail.objects(id = role.id).update(push__policy=i)
                return True
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)  
        return False