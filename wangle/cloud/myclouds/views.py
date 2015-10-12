from wangle.cloud.myclouds import forms as project_forms
from django.core.urlresolvers import reverse_lazy
from wangle.cloud.myclouds.forms import tenantclouds
from horizon import workflows
from cloud_mongo.trail import encode_decode

class CloudObj():
    def __init__(self,id,name,platform,tenantid,endpoint,cloudtype,username):
        self.id = id
        self.name=name
        self.platform = platform
        self.tenantid = tenantid
        self.endpoint = endpoint
        self.cloudtype = cloudtype
        self.username = username



class EditCloudView(workflows.WorkflowView):
    
    workflow_class = project_forms.EditCloud
    template_name = 'wangle/cloud/myclouds/edit_cloud.html'
    success_url = reverse_lazy("horizon:wangle:cloud:index")
    def get_context_data(self, **kwargs):
        context = super(EditCloudView, self).get_context_data(**kwargs)
        context['cloud_id'] = self.kwargs["cloud_id"]
        return context

    def get_initial(self):
        id = self.kwargs["cloud_id"]
        cloud = tenantclouds.objects(id = id).first()
        username = cloud.cloud_meta['publickey']
        cloudname = cloud.name
        platform = cloud.platform
        password = encode_decode(cloud.cloud_meta['privatekey'],"decode")
        endpoint = cloud.cloud_meta['endpoint']
        cloud_type = cloud.cloud_type
        return {'id':id,'username1':username,'cloudname1':cloudname,'password1':password,'endpoint1':endpoint}
