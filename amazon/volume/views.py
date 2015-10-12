from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from amazon.volume import forms as project_forms
from amazon.volume import tabs as project_tabs
from horizon import forms, workflows, tabs, tables, messages, exceptions
from .tables import VolumedisplayTable
from aws_api.volumes import Volumes
from amazon.volume.forms import CreateVolume
import logging

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = VolumedisplayTable
    template_name = 'amazon/volume/index.html'
 
    def get_data(self):
        volume = []
        try:
            volume = Volumes(self.request).get_volumes()
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return volume


class CreateVolumeView(workflows.WorkflowView):
    workflow_class =  CreateVolume

 
class Attachments(forms.ModalFormView):
    form_class = project_forms.AttachForm
    template_name = 'amazon/volume/create.html'
    success_url = reverse_lazy("horizon:amazon:volume:index")
     
    def get_context_data(self, **kwargs):
        context = super(Attachments, self).get_context_data(**kwargs)
        context['volume_id'] = self.kwargs["volume_id"]
        context['zone'] = self.kwargs["zone"]
        return context
     
    def get_initial(self):
        vol_id = self.kwargs["volume_id"]
        zone = self.kwargs["zone"]
        inst_id=Volumes(self.request).get_instance_for_volume(zone)
        return {
                'volume_id':vol_id,
                'instance_choices':inst_id
                }

class CreateSnapshotView(forms.ModalFormView):
    form_class = project_forms.CreateSnapshotForm
    template_name = 'amazon/volume/create_snapshot.html'
    success_url = reverse_lazy("horizon:amazon:volume:index")
     
    def get_context_data(self, **kwargs):
        context = super(CreateSnapshotView, self).get_context_data(**kwargs)
        context['volume_id'] = self.kwargs["volume_id"]
        context['zone'] = self.kwargs["zone"]
        return context
     
    def get_initial(self):
        volume_id = self.kwargs["volume_id"]
        zone = self.kwargs["zone"]
        return {
                'volume_id':volume_id,
                'zone':zone
                }

 
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.VolumeDetailTabs
    template_name = 'amazon/volume/detail.html'
            
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["volume"] = self.get_data()
        return context
     
    def get_data(self):
        try:
            vol=Volumes(self.request).get_volume_detail(self.kwargs['volume_id'])
            return vol[0]
        except Exception, e:
                redirect = reverse('horizon:amazon:volumes:index')
                messages.error(self.request,_(e.message))
                LOG.error(e.message)
                exceptions.handle_redirect(self.request,redirect)
 
 
    def get_tabs(self, request, *args, **kwargs):
        volume = self.get_data()
        return self.tab_group_class(request, volume=volume, **kwargs)
