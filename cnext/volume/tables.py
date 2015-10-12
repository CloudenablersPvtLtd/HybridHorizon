from horizon import tables
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cnext_api import api


class CreateVolume(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Volume")
    url = "horizon:cnext:volume:create"
    classes = ("ajax-modal", "btn-create")
    def allowed(self, request, datum):
        for policy in request.session['user_policies'].get(request.user.cnextname):
            if "Create Volume" in policy[2]:
                return True
        return False
    

class DeleteVolume(tables.DeleteAction):
    data_type_singular = _("Volume")
    data_type_plural = _("Volumes")
    action_past = _(" Deletion of")

    def action(self, request, obj_id):
        api.delete_volume(request, obj_id)
    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status in ("detached",):
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Delete Volume" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status in ("detached",):
                        return True
        return False
        

class EditAttachments(tables.LinkAction):
    name = "attachment"
    verbose_name = _("VM Attachment")
    url = "horizon:cnext:volume:attach"
    classes = ("ajax-modal", "btn-edit")
    
    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status in ("stopped","attached","stopping",):
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Attach Volume" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status in ("stopped","attached","stopping",):
                        return True
        return False
  
    def get_link_url(self, datum):
        return reverse("horizon:cnext:"
                       "volume:attach", args=[datum.name, datum.region,datum.provider])

class DeleteVm(tables.LinkAction):
    name = "Detachment"
    verbose_name = _("VM Detachment")
    url = "horizon:cnext:volume:dettach"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status in ("attached","attaching"):
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Attach Volume" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status in ("attached","attaching"):
                        return True
        return False

    def get_link_url(self, datum):
        return reverse("horizon:cnext:"
                       "volume:dettach", args=[datum.name])
 

class VolumesFilterAction(tables.FilterAction):

    def filter(self, table, volumes, filter_string):
        q = filter_string.lower()
        return [volume for volume in volumes
                if q in volume.display_name.lower()]
        
class RefreshInst(tables.BatchAction):
    name = "refresh"
    action_present = _("Refresh")
    action_past = _("Refreshed Instance")
    data_type_singular = _(" ")
    data_type_plural = _("es")
    success_url = 'horizon:cnext:volume:index'

    def allowed(self, request, instance=None):
        return instance.status in ("creating",)

    def action(self, request, obj_id):
        api.refresh(request, obj_id)


class TabledisplayTable(tables.DataTable):
    volume_name =tables.Column("volume_name",verbose_name=_("Volume Name"),
                                             link=("horizon:cnext:volume:detail"))
    instanceid =tables.Column("size",verbose_name=_("Size"))
    name = tables.Column("name",verbose_name=_("Instance Id"))
    provider= tables.Column("provider", verbose_name=_("Provider"))
    region= tables.Column("region", verbose_name=_("Region"))
    status = tables.Column("status",
                         verbose_name=_("Status"))    
 
    class Meta:
        name = "Volumes"
        verbose_name = _("Volumes")
        #status_columns = ["status"]
        table_actions = (VolumesFilterAction,CreateVolume,DeleteVolume,)
        row_actions = (EditAttachments,DeleteVolume,DeleteVm,)
