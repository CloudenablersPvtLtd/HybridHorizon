 
from wangle.cloud.addcloud import forms as project_forms
from django.core.urlresolvers import reverse_lazy
from horizon import workflows



class CreateCloudView(workflows.WorkflowView):
    workflow_class = project_forms.CreateCloudForm
     
    def get_initial(self):
        return {'cloud_id':self.kwargs["cloud_id"]}
         



