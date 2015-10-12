from mongoengine import *
from django.utils.translation import ugettext_lazy as _
from horizon import forms,workflows,messages,exceptions
from horizon.utils import validators,fields
from mongoengine.django.mongo_auth.models import get_user_document
from cloud_mongo.trail import refresh_session_policies,Hpclouddata,tenantclouds,clouds
from aws_api.connection import get_regions_wo_connection,test
from cloud_mongo import openstack_authenticate
from cloud_mongo import trail
from cloud_mongo.cloudmongobackend import remove_tenants
from cloud_mongo.views import delete_token
import httplib2
import logging

LOG = logging.getLogger(__name__)


class CloudEditAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    
    cloudtype_choices = (
    ("", _("Select CloudType")),
    ('private','Private'),
    ('public','Public'),)
     
    cloudtype = forms.ChoiceField(
        label=_("Cloud Type"),
        required=False,
        widget=forms.HiddenInput(),
        choices=cloudtype_choices
        )
    
    
    cloudslist = forms.ChoiceField(
        label=_("Platform"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('platform',),
            transform=lambda x: ("%s " % (x.platform)))
         )

    cloudname1 = forms.CharField(label=_("Cloud Name"),max_length=80)
    username1 = forms.CharField(max_length=80, label=_("User Name"))
    password1 = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=True),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    endpoint1 =  forms.CharField(max_length=80, label=_("Endpoint(IP with HTTP)"))


    def populate_cloudslist_choices(self, request, context):
        try:
            roles = []
            id = context.get('id', None) 
            cloud = tenantclouds.objects(id = id).first()
            roles.append((cloud.id,cloud))
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve list of Cloud Details'))
            roles = []
        return roles

    class Meta:
        name = _("Edit Cloud")

    def __init__(self, *args, **kwargs):
        super(CloudEditAction, self).__init__(*args, **kwargs)
        try:
            region_list = get_regions_wo_connection()
            tenantcloud_id = args[-1]["id"]
            cloud = tenantclouds.objects(id = tenantcloud_id).first()
            cloud_obj = clouds.objects(id=cloud.cloudid.id).first()
            self.fields['username1'].label = _(cloud_obj.credential_fields[0])
            self.fields["password1"].label = _(cloud_obj.credential_fields[1])
            if cloud_obj.name == "Amazon":
                self.fields["endpoint1"] = forms.ChoiceField(label=_("Default Region"),
                                                           choices = region_list,
                                                           help_text=_("Select default region"))
                self.fields["endpoint1"].label = _(cloud_obj.credential_fields[2])
            else:
                self.fields["endpoint1"].label = _(cloud_obj.credential_fields[2])
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)

class CloudEdit(workflows.Step):
    action_class = CloudEditAction
    contributes = ("id","username1","password1","endpoint1","cloudname1","publickey1","privatekey1")

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['endpoint'] = data.get("endpoint1", None)
            context['password'] = data.get("password1", None)
            context['cloudname'] = data.get("cloudname1", None)
            context['username'] = data.get("username1", None)
            context['publickey'] = data.get("publickey1", None)
            context['secretkey'] = data.get("secretkey1", None)
        return context
    
class EditCloud(workflows.Workflow):
    
    slug = "edit_cloud"
    name = _("Edit Cloud")
    finalize_button_name = _("Save")
    success_url = "horizon:wangle:cloud:index"
    default_steps = (CloudEdit, )
    
    success_message = _("Cloud Edited successfully.")
    failure_message = _("Cloud Not Edited. Either Credential or Endpoint Given is Invalid")
    
    def handle(self, request, context):
        id = context.get('id', None) 
        username = context.get('username', None)
        cloudname = context.get('cloudname', None)
        password = context.get('password', None)
        endpoint = context.get('endpoint', None)
        if (username == '') & (password == ''):
            username = context.get('publickey', None)
            password = context.get('secretkey', None)
        try:
            user = get_user_document().objects(username=request.user.username).first()
            cloud = tenantclouds.objects(id = id).first()
            if cloud.platform =="Amazon":
                status = test(endpoint,username,password)
                if status == True:
                    if user.awsname == cloud.name:
                        user.awspublickey = username
                        user.awsprivatekey = trail.encode_decode(password,"encode")
                        user.awsendpoint = endpoint
                        user.awsname = cloudname
                else:
                    return False
            if cloud.platform =="Cnext":
                httpInst = httplib2.Http()
                httpInst.add_credentials(name = username, \
                                     password = password)
                url = endpoint + ":8130/apiv2/instance"   
                resp, body = httpInst.request(url)
                if resp.status == 200 :
                    if user.cnextname == cloud.name:
                        user.cnextpublickey = username
                        user.cnextprivatekey = trail.encode_decode(password,"encode")
                        user.cnextendpoint = endpoint
                        user.cnextname = cloudname
                else:
                    return False
            if cloud.platform =="Hpcloud":
                openstack_user = openstack_authenticate.authenticate(user_domain_name=None,username=username,
                                 password=password,
                                 auth_url= endpoint)
                utoken = openstack_user.token
                if utoken:
                    hp = Hpclouddata.objects(id = request.user.hp_attr.id).first()
                    hpcloud = tenantclouds.objects(id = hp.hpcloudid.id).first()
                    if hpcloud.name == cloud.name:
                        otoken = trail.DocToken(user=utoken.user, 
                                                    user_domain_id=utoken.user_domain_id,
                                                    id=utoken.id,
                                                    project=utoken.project,
                                                    tenant=utoken.project,
                                                    domain=utoken.domain,
                                                    roles=utoken.roles,
                                                    serviceCatalog=utoken.serviceCatalog
                                                    )
                        hp.token = otoken
                        hp.authorized_tenants = [remove_tenants(d.__dict__) for d in openstack_user.authorized_tenants]
                        hp.service_catalog = openstack_user.service_catalog
                        hp.services_region = openstack_user.services_region
                        hp.project_name = openstack_user.project_name
                        hp.tenant_name = openstack_user.tenant_name
                        hp.tenant_id = openstack_user.tenant_id
                        hp.project_id = openstack_user.project_id
                        hp.endpoint = endpoint
                        hp.save()
                        user.hpname = cloudname
                else:
                    return False
            if cloud.platform =="Openstack":
                openstack_user = openstack_authenticate.authenticate(user_domain_name=None,username=username,
                                 password=password,
                                 auth_url= endpoint)
                utoken = openstack_user.token
                if utoken:
                    if user.openstackname == cloud.name:
                        delete_token(user.endpoint,user.token.id)
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
                    else:
                        delete_token(endpoint,utoken.id)
                else:
                    return False
            clouds = tenantclouds.objects(id = id).update(set__name = cloudname,set__cloud_meta ={"publickey":username,"privatekey":trail.encode_decode(password,"encode"),"endpoint":endpoint})
            user.save()
            refresh_session_policies(request, request.user)
            return True
  
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return False
