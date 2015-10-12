from horizon import tables,workflows,messages
from .tables import RoleTable
from wangle.role import forms as project_forms
from django.core.urlresolvers import reverse_lazy
from wangle.role.forms import roledetail,tenantclouds
from cloud_mongo.trail import refresh_session_policies
import logging

LOG = logging.getLogger(__name__)

class RoleObj():
    def __init__(self,id,name,roletype,policy="",access=None):
        self.id = id
        self.name=name
        self.roletype = roletype
        self.policy = policy
        self.access = access

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = RoleTable
    template_name = 'wangle/role/index.html'
      
    def get_data(self):
        try:
        # Add data to the context here...
            if "Tenant Admin" not in self.request.session['user_roles']: 
                refresh_session_policies(self.request, self.request.user)
            obj = roledetail.objects(tenantid=self.request.user.tenantid.id)
            roles = []
            for role in obj:
                action = []
                access = ""
                if role.policy == [] and role.access == []:
                    role_obj = RoleObj(id = role.id,name = role.name,roletype = role.roletype)
                elif role.policy == [] and role.access:
                    for k in role.access:
                        access = access+""+k+","+"\n"
                        role_obj = RoleObj(id = role.id,name = role.name,roletype = role.roletype,access = access[:-2].title())
                else:   
                    for i in role.policy:
                        cloud = tenantclouds.objects(id = i.cloudid.id).first()
                        action.append(cloud.name)
                        action = set(action)
                        action = list(action)
                    for k in role.access:
                        access = access+""+k+","+"\n"
                        role_obj = RoleObj(role.id,role.name,role.roletype,\
                                            ",\n".join(action).title(),access[:-2].title())   
                roles.append(role_obj)
        except Exception,e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            roles =[]
        return roles


class CreateRoleView(workflows.WorkflowView):
    workflow_class = project_forms.CreateRoleForm
     
class AddPolicyView(workflows.WorkflowView):
    workflow_class = project_forms.AddPolicy
    template_name = 'wangle/role/add_policy.html'
    success_url = reverse_lazy("horizon:wangle:role:index")
    def get_context_data(self, **kwargs):
        context = super(AddPolicyView, self).get_context_data(**kwargs)
        context['role_id'] = self.kwargs["role_id"]
        return context

    def get_initial(self):
        id = self.kwargs["role_id"]
        return {'id':id}
    

class RemovePolicyView(workflows.WorkflowView):
    
    workflow_class = project_forms.RemovePolicy
    template_name = 'wangle/role/remove_policy.html'
    success_url = reverse_lazy("horizon:wangle:role:index")
    def get_context_data(self, **kwargs):
        context = super(RemovePolicyView, self).get_context_data(**kwargs)
        context['policy_id'] = self.kwargs["policy_id"]
        return context

    def get_initial(self):
        id = self.kwargs["policy_id"]
        return {'id':id}
    
    

class EditAccessView(workflows.WorkflowView):
    
    workflow_class = project_forms.EditAccess
    template_name = 'wangle/role/edit_access.html'
    success_url = reverse_lazy("horizon:wangle:role:index")
    def get_context_data(self, **kwargs):
        context = super(EditAccessView, self).get_context_data(**kwargs)
        context['access_id'] = self.kwargs["access_id"]
        return context

    def get_initial(self):
        id = self.kwargs["access_id"]
        return {'roleid':id}
