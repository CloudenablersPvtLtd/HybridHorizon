import logging
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import messages
from horizon import tables
from aws_api.security_groups import SecurityGroups 

LOG = logging.getLogger(__name__)

class DeleteGroup(tables.DeleteAction):
    data_type_singular = _(" ")
    data_type_plural = _(" ")
     
    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            return True 
        if "Delete SG" in request.session['user_policies'].get(request.user.awsname):
            return True
        return False
            
 
    def delete(self, request, id):
        try:
            SecurityGroups(request).delete_sg(id = id)  
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
             
   
class CreateGroup(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Security Group")
    url = "horizon:amazon:securitygroups:create"
    classes = ("ajax-modal", "btn-create")
     
    def allowed(self, request, datum):
        if "Create SG" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False


class AddRule(tables.LinkAction):
    name = "add_rule"
    verbose_name = _("Add Rule")
    url = "horizon:amazon:securitygroups:add_rule"
    classes = ("ajax-modal", "btn-add")
    
    def get_link_url(self, datum):
        return reverse("horizon:amazon:"
                       "securitygroups:add_rule", args=[datum.id])


class DeleteRule(tables.LinkAction):
    name = "delete_rule"
    verbose_name = _("Delete Rule")
    url = "horizon:cnext:securitygroups:delete_rule"
    classes = ("ajax-modal", "btn-deleterule")
     
    def get_link_url(self, datum):
        return reverse("horizon:amazon:"
                        "securitygroups:delete_rule", args=[datum.id])    
     
    def allowed(self, request, instance=None):
        return True

class SecurityGroupsTable(tables.DataTable):
    name = tables.Column('name', link=("horizon:amazon:securitygroups:detail"),verbose_name=_("Name"))
    id = tables.Column('id', verbose_name=_("Group ID"))
    vpc_id = tables.Column('vpc_id', verbose_name=_("Vpc ID"))
    description = tables.Column("description", verbose_name=_("Description"))
    rules = tables.Column('rules', verbose_name=_("IP Permissions"))
    def get_object_id(self, sg):
        return sg.id

    class Meta:
        name = "securitygroups"
        verbose_name = _("Security Groups")
        table_actions = (CreateGroup,)
        row_actions = (DeleteGroup,AddRule,DeleteRule)