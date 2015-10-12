from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from amazon.snapshots import forms as project_forms
from amazon.snapshots import tabs as project_tabs
from horizon import forms, workflows, tabs, tables, messages, exceptions
from .tables import SnapshotsdisplayTable
from aws_api.snapshots import Snapshots
from amazon.snapshots.forms import CreateSnapshot
import logging

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = SnapshotsdisplayTable
    template_name = 'amazon/snapshots/index.html'
 
    def get_data(self):
        snapshot = []
        try:
            snapshot = Snapshots(self.request).get_snapshots()
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return snapshot


class CreateVolumeView(forms.ModalFormView):
    form_class = project_forms.CreateVolumeForm
    template_name = 'amazon/snapshots/create_volume.html'
    success_url = reverse_lazy("horizon:amazon:snapshots:index")
     
    def get_context_data(self, **kwargs):
        context = super(CreateVolumeView, self).get_context_data(**kwargs)
        context['snapshot_id'] = self.kwargs["snapshot_id"]
        context['zone'] = self.kwargs["zone"]
        return context
     
    def get_initial(self):
        aws_tuples = []
        snapshot_id = self.kwargs["snapshot_id"]
        zone = self.kwargs["zone"]
        zone_id = Snapshots(self.request).get_zone()
        for zone in zone_id:
            aws_tuples.append((str(zone.name), str(zone.name)))
        snapshots = Snapshots(self.request).get_snapshot_detail(self.kwargs['snapshot_id'])
        volume_size = snapshots[0].volume_size
        aws_tuples.insert(0, ("", _("Select Zone")))
        return {
                'snapshot_id':snapshot_id,
                'zone_choices':aws_tuples,
                'volume_size':volume_size
                }

class CopySnapshotView(forms.ModalFormView):
    form_class = project_forms.CopySnapshotForm
    template_name = 'amazon/snapshots/copy_snapshot.html'
    success_url = reverse_lazy("horizon:amazon:snapshots:index")
     
    def get_context_data(self, **kwargs):
        context = super(CopySnapshotView, self).get_context_data(**kwargs)
        context['snapshot_id'] = self.kwargs["snapshot_id"]
        context['zone'] = self.kwargs["zone"]
        return context
     
    def get_initial(self):
        aws_tuples = []
        snapshot_id = self.kwargs["snapshot_id"]
        regions = Snapshots(self.request).get_regions()
        for region in regions:
            aws_tuples.append((str(region.name), str(region.name)))
        aws_tuples.insert(0, ("", _("Select Region")))
        return {
                'snapshot_id':snapshot_id,
                'region_choices':aws_tuples
                }


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.SnapshotDetailTabs
    template_name = 'amazon/snapshots/detail.html'
            
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["snapshot"] = self.get_data()
        return context
     
    def get_data(self):
        try:
            vol=Snapshots(self.request).get_snapshot_detail(self.kwargs['snapshot_id'])
            return vol[0]
        except Exception, e:
            redirect = reverse('horizon:amazon:snapshots:index')
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(self.request,redirect)
 
    def get_tabs(self, request, *args, **kwargs):
        snapshot = self.get_data()
        return self.tab_group_class(request, snapshot=snapshot, **kwargs)


class CreateSnapshotView(workflows.WorkflowView):
    workflow_class =  CreateSnapshot