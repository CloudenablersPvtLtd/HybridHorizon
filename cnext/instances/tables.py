from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from horizon import tables
from cnext_api import api
import logging

SNAPSHOT_READY_STATES = ("stopped", "running", "created",)
REFRESH_STATES = ("creating", "starting",)
from cnext.resource import START_STOP_PROVIDER
LOG = logging.getLogger(__name__)


class LaunchLink(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Instance")
    url = "horizon:cnext:instances:launch"
    classes = ("btn-launch", "ajax-modal")
    success_url = 'horizon:cnext:instances:index'

    def allowed(self, request, datum):
        for policy in request.session['user_policies'].get(request.user.cnextname):
            if "Create Instance" in policy[2]:
                return True
        return False


class InstancesFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [instance for instance in instances
                if q in instance.name.lower()]


class StartInstance(tables.BatchAction):
    name = "start"
    action_present = _("START")
    action_past = _("STARTING")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:cnext:instances:index'

    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status in ("shutoff", "stopped", "created", "creating", "stopping",) and (instance.provider.lower(),instance.region.lower()) in START_STOP_PROVIDER:
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Start Instance" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status in ("shutoff", "stopped", "created", "creating", "stopping",) and (instance.provider.lower(),instance.region.lower()) in START_STOP_PROVIDER:
                        return True
        return False

    def action(self, request, obj_id):
        api.start(request, obj_id)


class StopInstance(tables.BatchAction):
    name = "stop"
    action_present = _("STOP")
    action_past = _("STOPPING")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:cnext:instances:index'

    def allowed(self, request, instance=None):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status  in ("running", "starting") and ((instance.provider.lower(),instance.region.lower()) in START_STOP_PROVIDER):
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Stop Instance" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status  in ("running", "starting") and ((instance.provider.lower(),instance.region.lower()) in START_STOP_PROVIDER):
                        return True
        return False

    def action(self, request, obj_id):
        api.stop(request,obj_id)

class TerminateInstance(tables.BatchAction):
    name = "terminate"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:cnext:instances:index'

    def allowed(self, request, instance=None):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if instance.status not in ("deleting", "deleted",):
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Delete Instance" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if instance.status not in ("deleting", "deleted",):
                        return True
        return False

    def action(self, request, obj_id):
        api.delete(request, obj_id)


class CreateSnapshot(tables.LinkAction):
    name = "snapshot"
    verbose_name = _("Create Snapshot")
    url = "horizon:cnext:snapshots:create"
    classes = ("ajax-modal", "btn-camera",)
    success_url = 'horizon:cnext:snapshots:index'

    def get_link_url(self, datum):
        return reverse(self.url, args=[datum.name, datum.id,
                                       datum.provider, datum.region])

    def allowed(self, request, instance=None):
        IMAGE_CREATION_PROVIDER = api.provider_image(request,instance.uri)
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if IMAGE_CREATION_PROVIDER and instance.status in SNAPSHOT_READY_STATES:
                    return True
                else:
                    return False
         
        if instance:
            for policy in request.session['user_policies'].get(request.user.cnextname):
                if ("Create Snapshot" in policy[2] and (instance.provider.lower(),instance.region.lower()) == (policy[0],policy[1])):
                    if IMAGE_CREATION_PROVIDER and instance.status in SNAPSHOT_READY_STATES:
                        return True
        return False
                

class RefreshInst(tables.BatchAction):
    name = "refresh"
    action_present = _("To Run")
    action_past = _("In Running Status")
    data_type_singular = _(" ")
    data_type_plural = _("es")
    success_url = 'horizon:cnext:instances:index'

    def allowed(self, request, instance=None):
        self.inst_obj = instance.__dict__
        return instance.status in REFRESH_STATES

    def action(self, request, obj_id):
        LOG.debug("refresh  action")
        api.refresh(request, obj_id)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        instance = api.inst_detail(request, image_id)
        return instance

    def load_cells(self, instance=None):
        super(UpdateRow, self).load_cells(instance)
        # Tag the row with the image category for client-side filtering.
        inst = self.datum
        self.attrs['data-provider'] = inst.provider
        self.attrs['data-region'] = inst.region


class InstancesTable(tables.DataTable):
    name = tables.Column("name", link=("horizon:cnext:instances:detail"), verbose_name=_("Name"))
    provider = tables.Column("provider", verbose_name=_("Provider"))
    region = tables.Column("region", verbose_name=_("Region"))
    ids = tables.Column("id", verbose_name=_("InstanceId"))
    status = tables.Column("status", verbose_name=_("Status"))
    uri = tables.Column("uri", verbose_name=_("URI"), hidden = True)

    class Meta:
        name = "instances"
        row_class = UpdateRow
        verbose_name = _("Instances")
        table_actions = (LaunchLink, InstancesFilterAction,)
        row_actions = (StartInstance, TerminateInstance, StopInstance, RefreshInst, CreateSnapshot)
