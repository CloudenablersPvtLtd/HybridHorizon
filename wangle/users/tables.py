from django.utils.translation import ugettext_lazy as _
from horizon import tables
from cloud_mongo.trail import User
from django.core.urlresolvers import reverse


class CreateUserLink(tables.LinkAction):
    name = "launch"
    verbose_name = _("Create User")
    url = "horizon:wangle:users:create"
    classes = ("btn-launch", "ajax-modal")
    
    def allowed(self, request, instance=None):
        if "Create User" in request.session['user_roleaccess']:
            return True
        return False
    
class DeleteUser(tables.BatchAction):
    name = "Delete"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:wangle:users:index'
    def allowed(self, request, instance=None):
        if instance:
            if instance.role == "Tenant Admin":
                    return False
            else:
                if instance.id != request.user.id:
                    if "Delete User" in request.session['user_roleaccess']:
                        return True
                return False
        return False
    def action(self, request, obj_id):
        user = User.objects(id = obj_id)
        user.delete()
        
class AddRole(tables.LinkAction):
    name = "add_role"
    verbose_name = _("Add Role")
    data_type_singular = _(" ")
    data_type_plural = _(" s")
    url = "horizon:wangle:users:add_role"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "users:add_role", args=[datum.id])
    def allowed(self, request, instance=None):
        if instance:
            if instance.role == "Tenant Admin":
                    return False
            else:
                if "Add Role" in request.session['user_roleaccess']:
                    return True
                return False
        return False

class RemoveRole(tables.LinkAction):
    name = "remove_role"
    verbose_name = _("Remove Role")
    data_type_singular = _("Remove Role ")
    data_type_plural = _(" Remove Roles")
    url = "horizon:wangle:users:remove_role"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "users:remove_role", args=[datum.id])
    def allowed(self, request, instance=None):
        if instance:
            if instance.role == "Tenant Admin":
                    return False
            else:
                if "Remove Role" in request.session['user_roleaccess']:
                    return True
                return False
        return False


class ChangePassword(tables.LinkAction):
    name = "change_password"
    verbose_name = _("Change Email/Password")
    data_type_singular = _("Change Password")
    data_type_plural = _(" Change Passwords")
    url = "horizon:wangle:users:change_password"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "users:change_password", args=[datum.id])
    def allowed(self, request, datum, instance=None):
        if request.user.id == datum.id:
            return True
        else:
            return False   


class ResetPassword(tables.LinkAction):
    name = "reset_password"
    verbose_name = _("Reset Password")
    data_type_singular = _("Reset Password")
    data_type_plural = _(" Reset Passwords")
    url = "horizon:wangle:users:reset_password"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "users:reset_password", args=[datum.id])
    def allowed(self, request, datum, instance=None):
        if request.user.id != datum.id and "Tenant Admin" in request.session['user_roles']:
            return True
        else:
            return False

class TenantTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_("Name"))
    roles = tables.Column('role', verbose_name=_("Roles"))
    id = tables.Column('id', verbose_name=_("ID"),hidden=True )

    class Meta:
        name = "users"
        verbose_name = _("Users")
        table_actions = (CreateUserLink,DeleteUser,)
        row_actions = (DeleteUser,AddRole,RemoveRole,
                       ChangePassword,ResetPassword,)