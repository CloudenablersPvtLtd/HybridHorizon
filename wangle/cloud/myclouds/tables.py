import logging
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from wangle.cloud.addcloud.forms import tenantclouds
from wangle.role.forms import roledetail
from mongoengine.django.mongo_auth.models import get_user_document
from cloud_mongo.trail import Hpclouddata,encode_decode
from cloud_mongo import trail
from cloud_mongo.cloudmongobackend import remove_tenants
from cloud_mongo.views import delete_token
from cloud_mongo import openstack_authenticate

LOG = logging.getLogger(__name__)


class DeleteCloud(tables.BatchAction):
    name = "Delete"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:wangle:cloud:index'
    def allowed(self, request, instance=None):
        if "Delete Cloud" in request.session['user_roleaccess']:
            return True
        return False
    
    def action(self, request, obj_id):
        cloud = tenantclouds.objects(id = obj_id).first()
        roles = roledetail.objects(tenantid=request.user.tenantid)
        for role in roles:
            list1 = []
            for a in role.policy:
                if (str(a.cloudid.id) == str(obj_id)):
                    pass
                else:
                    list1.append(a)
            roledetail.objects(id=role.id).update(set__policy=list1)
        user = get_user_document().objects(username=request.user.username).first()
        
        if cloud.platform == "Openstack":
            if user.openstackname == cloud.name:
                clouds = sum([[y.cloudid for y in i.policy 
                               if y.cloudid.platform == "Openstack"] 
                              for i in user.roles], [])
                if clouds:
                    openstack_user = openstack_authenticate.authenticate(user_domain_name=None,username=clouds[0]["cloud_meta"]["publickey"],
                                 password=encode_decode(clouds[0]["cloud_meta"]["privatekey"],"decode"),
                                 auth_url= clouds[0]["cloud_meta"]["endpoint"])
                    utoken = openstack_user.token
                    if utoken:
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
                        user.endpoint = clouds[0]["cloud_meta"]["endpoint"] + ""
                        user.openstackname = clouds[0]["name"]
                else:
                    delete_token(user.endpoint,user.token.id)
                    user.authorized_tenants = []
                    user.service_catalog = []
                    user.services_region = None
                    user.project_name = None
                    user.tenant_name = None
                    user.tenant_id = None
                    user.project_id = None
                    user.endpoint = None
                    user.token = None
                    user.openstackname = None
        
        if cloud.platform =="Cnext":
            if user.cnextname == cloud.name:
                clouds = sum([[y.cloudid for y in i.policy 
                               if y.cloudid.platform == "Cnext"] 
                              for i in user.roles], [])
                if clouds:
                    user.cnextpublickey = clouds[0]["cloud_meta"]["publickey"]
                    user.cnextprivatekey = encode_decode(clouds[0]["cloud_meta"]["privatekey"],"encode")
                    user.cnextendpoint = clouds[0]["cloud_meta"]["endpoint"]
                    user.cnextname = clouds[0]["name"]
                else:
                    user.cnextpublickey = ""
                    user.cnextprivatekey = ""
                    user.cnextendpoint = ""
                    user.cnextname = ""
        
        if cloud.platform == "Hpcloud":
            hp_clouds = Hpclouddata.objects.all()
            for hp_cloud in hp_clouds:
                if hp_cloud.hpcloudid.id == cloud.id:
                    if hp_cloud.id == request.user.hp_attr.id:
                        clouds = sum([[y.cloudid for y in i.policy 
                                        if y.cloudid.platform == "Hpcloud"] 
                                        for i in user.roles], [])
                        if clouds:
                            hpclouds = Hpclouddata.objects.all()
                            for hpcloud in hpclouds:
                                if hpcloud.hpcloudid.id != cloud.id:
                                    user.hp_attr = hpcloud
                                    hpcloudobj = tenantclouds.objects(id = hpcloud.hpcloudid.id).first()
                                    user.hpname = hpcloudobj.name
                        else:
                            user.hp_attr = None
                            user.hpname = None
                        hp = Hpclouddata.objects(id = hp_cloud.id).first()
                        hp.delete()
                    else:
                        hp = Hpclouddata.objects(id = hp_cloud.id).first()
                        hp.delete()
        
        if cloud.platform =="Amazon":
            if user.awsname == cloud.name:
                clouds = sum([[y.cloudid for y in i.policy 
                               if y.cloudid.platform == "Amazon"] 
                              for i in user.roles], [])
                if clouds:
                    user.awspublickey = clouds[0]["cloud_meta"]["publickey"]
                    user.awsprivatekey = encode_decode(clouds[0]["cloud_meta"]["privatekey"],"encode")
                    user.awsendpoint = clouds[0]["cloud_meta"]["endpoint"]
                    user.awsname = clouds[0]["name"]
                else:
                    user.awspublickey = ""
                    user.awsprivatekey = ""
                    user.awsendpoint = ""
                    user.awsname = ""
        user.save()
        cloud.delete()
               
class EditCloud(tables.LinkAction):
    name = "edit_cloud"
    verbose_name = _("Edit cloud")
    data_type_singular = _("Edit Cloud ")
    data_type_plural = _(" Edit Cloud")
    url = "horizon:wangle:cloud:myclouds:edit_cloud"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "cloud:myclouds:edit_cloud", args=[datum.id])
    def allowed(self, request, instance=None):
        if "Edit Cloud" in request.session['user_roleaccess']:
            return True
        return False
        
class MyCloudsTable(tables.DataTable):
    name = tables.Column("name",verbose_name=_("Cloud Name"))
    id = tables.Column('id', verbose_name=_("Cloud Id"),hidden = True)
    type = tables.Column('platform', verbose_name=_("Platform"))
    cloudtype = tables.Column("cloudtype",verbose_name=_("CloudType"))
    endpoint = tables.Column("endpoint",verbose_name=_("Endpoint/Default Region"))
    username = tables.Column("username",verbose_name=_("Username"))
     
   
    class Meta:
        name = "myclouds"
        verbose_name = _("My Clouds")
        table_actions = (DeleteCloud,)
        row_actions = (DeleteCloud,EditCloud)
       
   
        
