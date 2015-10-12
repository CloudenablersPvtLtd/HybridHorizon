from horizon import tables,workflows
from .tables import TenantTable
from wangle.users import forms as project_forms
from django.core.urlresolvers import reverse_lazy
from cloud_mongo.trail import User
from wangle.role.forms import roledetail
from cloud_mongo.trail import refresh_session_policies

class UserObj():
    def __init__(self,id,name,role):
        self.id = id
        self.name=name
        self.role = role
   


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = TenantTable
    template_name = 'wangle/users/index.html'
   
    
    def get_data(self):
        # Add data to the context here...
        if "Tenant Admin" not in self.request.session['user_roles']: 
                refresh_session_policies(self.request, self.request.user)
        obj = User.objects(tenantid=self.request.user.tenantid.id)
        users = []
        for user in obj:
            role_name = ""
            for a in  user.roles:
                role = roledetail.objects(id=a.id).first()
                role_name = role_name + role.name+","
            tet_obj = UserObj(user.id,user.username,role_name[:-1])
            users.append(tet_obj)
        return users
    
class CreateUserView(workflows.WorkflowView):
    workflow_class = project_forms.CreateUserForm
    
class AddRoleView(workflows.WorkflowView):
    
    workflow_class = project_forms.AddRole
    template_name = 'wangle/users/add_role.html'
    success_url = reverse_lazy("horizon:wangle:users:index")
    def get_context_data(self, **kwargs):
        context = super(AddRoleView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs["user_id"]
        return context

    def get_initial(self):
        id = self.kwargs["user_id"]
        return {'id':id}
    
class RemoveRoleView(workflows.WorkflowView):
    
    workflow_class = project_forms.RemoveRole
    template_name = 'wangle/users/remove_role.html'
    success_url = reverse_lazy("horizon:wangle:users:index")
    def get_context_data(self, **kwargs):
        context = super(RemoveRoleView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs["user_id"]
        return context

    def get_initial(self):
        id = self.kwargs["user_id"]
        return {'id':id}


class ChangePasswordView(workflows.WorkflowView):    
    workflow_class = project_forms.ChangePassword
    template_name = 'wangle/users/change_password.html'
    success_url = reverse_lazy("horizon:wangle:users:index")
    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs["user_id"]
        return context

    def get_initial(self):
        id = self.kwargs["user_id"]
        user = User.objects(id = id).first()
        username = user.username
        email = user.email
        old_password = user.password
        return {'id':id,'username':username,'email':email,'oldpassword':old_password}

class ResetPasswordView(workflows.WorkflowView):
    
    workflow_class = project_forms.ResetPassword
    template_name = 'wangle/users/reset_password.html'
    success_url = reverse_lazy("horizon:wangle:users:index")
    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs["user_id"]
        return context

    def get_initial(self):
        id = self.kwargs["user_id"]
        user = User.objects(id = id).first()
        username = user.username
        return {'id':id,'username':username}
