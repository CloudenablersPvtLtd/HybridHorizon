from horizon import tables, messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from aws_api.snapshots import Snapshots 
import logging

LOG = logging.getLogger(__name__)

class CreateSnapshot(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Snapshot")
    url = "horizon:amazon:snapshots:create"
    classes = ("ajax-modal", "btn-create")
    
    def allowed(self, request, datum):
        if "Create Snapshot" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False


class CreateVolume(tables.LinkAction):
    name = "create_volume"
    verbose_name = _("CREATE_VOLUME")
    url = "horizon:amazon:snapshots:create_volume"
    classes = ("ajax-modal", "btn-edit")
     
    def allowed(self, request, datum):
        if "Create Volume" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False

    def get_link_url(self, datum):    
        return reverse("horizon:amazon:"
                       "snapshots:create_volume", args=[datum.id,datum.region])
        
class CopySnapshot(tables.LinkAction):
    name = "copy_snapshot"
    verbose_name = _("COPY_SNAPSHOT")
    url = "horizon:amazon:snapshots:copy_snapshot"
    classes = ("ajax-modal", "btn-edit")
     
    def allowed(self, request, instance):
        if "Create Snapshot" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False

    def get_link_url(self, datum):    
        return reverse("horizon:amazon:"
                       "snapshots:copy_snapshot", args=[datum.id,datum.region])
    

class DeleteSnapshot(tables.BatchAction):
    name = "terminate"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:amazon:snapshots:index'
 
    def action(self, request, obj_id):
        try:
            Snapshots(request).delete_snapshots(obj_id)
        except Exception ,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

    def allowed(self, request, instance):
        if "Delete Snapshot" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False



class SnapshotsdisplayTable(tables.DataTable):
    snapshotid =tables.Column("id",verbose_name=_("SnapshotId"),link=("horizon:amazon:snapshots:detail"))
    name =tables.Column("name",verbose_name=_("Snapshot Name"))
    volumeid =tables.Column("volumeid",verbose_name=_("Volume ID"))
    description =tables.Column("description",verbose_name=_("Description"))
    size =tables.Column("size",verbose_name=_("Capacity (GB)"))
    starttime =tables.Column("starttime",verbose_name=_("Start Time"))
    region = tables.Column("region",verbose_name=_("Region"))
    status = tables.Column("status", verbose_name=_("Status"))
    progress = tables.Column("progress", verbose_name=_("Progress"))
     
    def get_object_display(self, snapshot_type):
        return snapshot_type.id
 
    def get_object_id(self, snapshot_type):
        return str(snapshot_type.id)
        

    class Meta:
        name = "snapshots"
        verbose_name = _("snapshots")
        table_actions = (CreateSnapshot,)
        row_actions = (DeleteSnapshot,CreateVolume,CopySnapshot,)

