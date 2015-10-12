from horizon import forms
from mongoengine.django.mongo_auth.models import get_user_document
from django.utils.translation import ugettext_lazy as _
from cloud_mongo import openstack_authenticate
from cloud_mongo import trail
from cloud_mongo.trail import tenantclouds,encode_decode
from cloud_mongo.views import delete_token
from cloud_mongo.cloudmongobackend import remove_tenants

class AccountChangeForm(forms.SelfHandlingForm):
    accounts_list=[]
    def __init__(self, *args, **kwargs):
        accounts_list = kwargs["initial"]["account_choices"]
        super(AccountChangeForm, self).__init__(*args,**kwargs) 
        self.fields['account_name'] = forms.ChoiceField(label="Account Name", choices=accounts_list)
    
    account_name = forms.ChoiceField(label=_("Account Name"),
                                    required=True,
                                    choices = accounts_list,
                                    help_text=_("Select your account"))
    
    def handle(self, request, data):
        user = get_user_document().objects(username=request.user.username).first()
        openstack_clouds = sum([[y.cloudid for y in i.policy if 
                            y.cloudid.platform == "Openstack"] for i in request.user.roles], [])
        for cloud in openstack_clouds:
            if str(cloud.id) == str(data['account_name']):
                os_cloud = tenantclouds.objects(id = cloud.id).first()
                openstack_user = openstack_authenticate.authenticate(user_domain_name=None,
                                                                     username=os_cloud.cloud_meta['publickey'],
                                                                     password=encode_decode(os_cloud.cloud_meta['privatekey'],'decode'),
                                                                     auth_url= os_cloud.cloud_meta['endpoint'])
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
                    user.endpoint = os_cloud.cloud_meta['endpoint'] + ""
                    user.openstackname = os_cloud.name
                    user.save()
                    return True
        return False

