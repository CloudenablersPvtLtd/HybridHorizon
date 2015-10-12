from horizon import tables, messages, exceptions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from aws_api.volumes import Volumes
import logging

LOG = logging.getLogger(__name__)


class CreateVolume(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Volume")
    url = "horizon:amazon:volume:create"
    classes = ("ajax-modal", "btn-create")
    
    def allowed(self, request, datum):
        if "Create Volume" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False


class DeleteVolume(tables.BatchAction):
    name = "terminate"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:amazon:volume:index'
 
    def action(self, request, obj_id):
        try:
            Volumes(request).delete_volumes(obj_id)
        except Exception ,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request, self.success_url)
            

    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) in ("available",):
                    return True
                else:
                    return False
         
        if "Delete Volume" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) in ("available",):
                    return True
        return False


class VolumeAttachments(tables.LinkAction):
    name = "attachment"
    verbose_name = _("ATTACH")
    url = "horizon:amazon:volume:attach"
    classes = ("ajax-modal", "btn-edit")
     
    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) in ("available",):
                    return True
                else:
                    return False
         
        if "Attach Volume" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) in ("available",):
                    return True
        return False

    def get_link_url(self, datum):    
        return reverse("horizon:amazon:"
                       "volume:attach", args=[datum.id,datum.zone])
        

class VolumeDetachment(tables.BatchAction):
    name = "detachment"
    action_present = _("DETACH")
    action_past = _("DETACHING")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:amazon:volume:index'
 
    def action(self, request, obj_id):
        try:
            Volumes(request).detach_volumes(obj_id)
        except Exception ,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request, self.success_url)

    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) in ("in-use",):
                    return True
                else:
                    return False
         
        if "Dettach Volume" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) in ("in-use",):
                    return True
        return False


class CreateSnapshot(tables.LinkAction):
    name = "create_snapshot"
    verbose_name = _("CREATE_SNAPSHOT")
    url = "horizon:amazon:volume:create_snapshot"
    classes = ("ajax-modal", "btn-edit")
     
    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            return True
        if "Create Snapshot" in request.session['user_policies'].get(request.user.awsname):
            return True
        return False

    def get_link_url(self, datum):    
        return reverse("horizon:amazon:"
                       "volume:create_snapshot", args=[datum.id,datum.region])


class VolumedisplayTable(tables.DataTable):
    instanceid =tables.Column("id",verbose_name=_("VolumeId"),link=("horizon:amazon:volume:detail"))
    name =tables.Column("name",verbose_name=_("Volume Name"))
    region = tables.Column("region",verbose_name=_("Region"))
    zone= tables.Column("zone", verbose_name=_("Zone"))
    create_time= tables.Column("create_time", verbose_name=_("Create Time"))
    type= tables.Column("type", verbose_name=_("Type"))
    size= tables.Column("size", verbose_name=_("Size"))
    status = tables.Column("status",
                         verbose_name=_("Status"))
    
    def get_object_display(self, vol_type):
        return vol_type.id

    def get_object_id(self, vol_type):
        return str(vol_type.id)
        
 
    class Meta:
        name = "Volumes"
        verbose_name = _("Volumes")
        table_actions = (CreateVolume,)
        row_actions = (DeleteVolume,VolumeAttachments,VolumeDetachment,CreateSnapshot,)

