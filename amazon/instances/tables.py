"""Created on 19/3/2014
Author:Annamalai"""


from django.utils.translation import ugettext_lazy as _
from horizon import tables,messages
from aws_api.instance import Instances
import logging

LOG = logging.getLogger(__name__)

REFRESH_STATES = ("pending", "stopping",)


class LaunchLink(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Instance")
    url = "horizon:amazon:instances:launch"
    classes = ("btn-launch", "ajax-modal")
    success_url = 'horizon:amazon:instances:index'

    def allowed(self, request, datum):
        if "Create Instance" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False

class StartInstance(tables.BatchAction):
    name = "start"
    action_present = _("START")
    action_past = _("STARTING")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:amazon:instances:index'

    def allowed(self, request, instance):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) in ("stopped",):
                    return True
                else:
                    return False
         
        if "Start Instance" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) in ("stopped",):
                    return True
        return False

    def action(self, request, obj_id):
        try:
            Instances(request).start_instances(obj_id)
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)


class StopInstance(tables.BatchAction):
    name = "stop"
    action_present = _("STOP")
    action_past = _("STOPPING")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:amazon:instances:index'

    def allowed(self, request, instance=None):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) in ("running",):
                    return True
                else:
                    return False
         
        if "Stop Instance" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) in ("running",):
                    return True
        return False

    def action(self, request, obj_id):
        try:
            Instances(request).stop_instances(obj_id)
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)


class TerminateInstance(tables.BatchAction):
    name = "terminate"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:amazon:instances:index'

    def allowed(self, request, instance=None):
        if "Tenant Admin" in request.session['user_roles']:
            if instance:
                if str(instance.status) not in ("deleting", "deleted","terminated","shutting-down",):
                    return True
                else:
                    return False
         
        if "Delete Instance" in request.session['user_policies'].get(request.user.awsname):
            if instance:
                if str(instance.status) not in ("deleting", "deleted","terminated","shutting-down",):
                    return True

    def action(self, request, obj_id):
        try:
            Instances(request).terminate_instances(obj_id)
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)


class RefreshInst(tables.BatchAction):
    name = "refresh"
    action_present = _("REFRESH")
    action_past = _("Refreshed Instance")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    success_url = 'horizon:amazon:instances:index'

    def allowed(self, request, instance=None):
        self.inst_obj = instance.__dict__
        return instance.status in REFRESH_STATES

    def action(self, request, obj_id):
        try:
            Instances(request).refresh_instances(obj_id)
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)


class InstancesTable(tables.DataTable):
    name = tables.Column("name", link=("horizon:amazon:instances:detail"), verbose_name=_("Name"))
    ids = tables.Column("id", verbose_name=_("InstanceId"))
    region = tables.Column("region", verbose_name=_("Region"))
    zone = tables.Column("zone", verbose_name=_("Zone"))
    imageid = tables.Column("imageid", verbose_name=_("ImageId"))
    status = tables.Column("status", verbose_name=_("Status"))


    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        table_actions = (LaunchLink,)
        row_actions = (StartInstance, TerminateInstance, StopInstance, RefreshInst,)
 