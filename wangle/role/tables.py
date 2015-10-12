
from horizon import tables,messages,exceptions
from django.core.urlresolvers import reverse 
from django.utils.translation import ugettext_lazy as _ 
from wangle.role.forms import roledetail
from cloud_mongo.trail import User

class CreateRoleLink(tables.LinkAction):
    name = "roles"
    verbose_name = _("Create Roles")
    url = "horizon:wangle:role:create"
    classes = ("btn-launch", "ajax-modal")
    
    def allowed(self, request, instance=None):
        if "Create Role" in request.session['user_roleaccess']:
            return True
        return False


class DeleteRole(tables.BatchAction):
    name = "Delete"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:wangle:role:index'
    def allowed(self, request, instance=None):
        if instance:
            if instance.roletype == "Tenant Admin":
                return False
            else:
                if "Delete Role" in request.session['user_roleaccess']:
                    return True
                return False
        return False

    def action(self, request, obj_id):
        try:
            role = roledetail.objects(id = obj_id).first()
            users = User.objects.all()
            for user in users:
                if (len(user.roles) == 1):
                    for roles in user.roles:
                        if roles.id == role.id:
                            raise Exception("Role can't be delete. Some users have this role only. Remove them first...")
            for user in users:
                role_list = []
                for roles in user.roles:
                    if roles.id == role.id:
                        pass
                    else:
                        role_list.append(roles)
                User.objects(id = user.id).update(set__roles = role_list)
            role.delete()
        except Exception, e:
            messages.info(request,_(e.message))
            exceptions.handle_redirect(request,self.success_url)
        
    
    
class AddPolicy(tables.LinkAction):
    name = "add_policy"
    verbose_name = _("Add/Edit Policy")
    data_type_singular = _(" ")
    data_type_plural = _(" s")
    url = "horizon:wangle:role:add_policy"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "role:add_policy", args=[datum.id])
    def allowed(self, request, instance=None):
        if instance:
            if instance.roletype == "Tenant Admin":
                return False
            else:
                if "Add and Edit Policy" in request.session['user_roleaccess']:
                    return True
                return False
        return False


class RemovePolicy(tables.LinkAction):
    name = "remove_policy"
    verbose_name = _("Remove Policy")
    data_type_singular = _("Remove Policy ")
    data_type_plural = _(" Remove policies")
    url = "horizon:wangle:role:remove_policy"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "role:remove_policy", args=[datum.id])
    def allowed(self, request, instance=None):
        if instance:
            if instance.policy:
                if instance.roletype == "Tenant Admin":
                    return False
                else:
                    if "Remove Policy" in request.session['user_roleaccess']:
                        return True
                    return False
        return False


class EditAccess(tables.LinkAction):
    name = "edit_access"
    verbose_name = _("Edit Access")
    data_type_singular = _("Edit Access ")
    data_type_plural = _(" Edit Accesses")
    url = "horizon:wangle:role:edit_access"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "role:edit_access", args=[datum.id])
    def allowed(self, request, instance=None):
        if instance:
            if instance.roletype == "Tenant Admin":
                return False
            else:
                if "Edit Access" in request.session['user_roleaccess']:
                    return True
                return False
        return False


class RoleTable(tables.DataTable):
    name = tables.Column("name",verbose_name=_("Role Name"))
    roletype = tables.Column('roletype', verbose_name=_("Role Type"))
    cloudtype = tables.Column("access",verbose_name=_("Role Access"))
    policy = tables.Column('policy',verbose_name=_("Clouds"))     
   
    class Meta:
        
        name = "roles"
        verbose_name = _("Roles")
        table_actions = (CreateRoleLink,DeleteRole,)
        row_actions = (DeleteRole,AddPolicy,RemovePolicy,EditAccess,)
