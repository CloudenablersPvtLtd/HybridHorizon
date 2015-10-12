from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from cnext.volume import forms as project_forms
from cnext.volume import tabs as project_tabs
from cnext_api import api
from horizon import forms, tabs, tables, exceptions
from .tables import TabledisplayTable

class IndexView(tables.DataTableView):
    table_class = TabledisplayTable
    template_name = 'cnext/volume/index.html'
 
    def get_data(self):
        volume = []
        try:
            volume = api.volumelist(self.request)
        except:
            exceptions.handle(self.request,
                              _('Unable to retrieve keypairs'))
        return volume
    
    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data()
        context["provider"] = api.providers(self.request)
        context["region"] = api.region(self.request)
        return context

class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateVolume
    template_name = 'cnext/volume/create.html'
    success_url = reverse_lazy('horizon:cnext:volume:index')


class Attachments(forms.ModalFormView):
    form_class = project_forms.AttachForm
    template_name = 'cnext/volume/vcreate.html'
    success_url = reverse_lazy("horizon:cnext:volume:index")
    
    def get_context_data(self, **kwargs):
        context = super(Attachments, self).get_context_data(**kwargs)
        context['volume_id'] = self.kwargs["volume_id"]
        context['volume_name'] = self.kwargs["volume_name"]
        context['volume_provider'] = self.kwargs["volume_provider"]
        return context
    
    def get_initial(self):
        ins_id = self.kwargs["volume_id"]
        provider = self.kwargs["volume_provider"]
        region = self.kwargs["volume_name"]
        vmid=api.choices(self.request,provider,region)
        return {
                'instanceid':ins_id,
                'volume_choices':vmid
                }


class Dettachments(forms.ModalFormView):
    form_class = project_forms.DettachForm
    template_name = 'cnext/volume/screate.html'
    success_url = reverse_lazy("horizon:cnext:volume:index")
    
    def get_context_data(self, **kwargs):
        context = super(Dettachments, self).get_context_data(**kwargs)
        context['volume_id'] = self.kwargs["volume_id"]
        return context
    
    def get_initial(self):
        ins_id = self.kwargs["volume_id"]
        vm=api.volume_dettach(self.request,ins_id)
        vmid=[[vm,vm]]
        return {
                'instanceid':ins_id,
                'volume_choices':vmid
                }


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.VolumeDetailTabs
    template_name = 'cnext/volume/detail.html'
           
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["volume"] = self.get_data()
        return context
    
    def get_data(self):
            try:
                inst=api.instance(self.request,self.kwargs['volume_id'])
                return inst

            except Exception:
                redirect = reverse('horizon:project:volumes:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve volume details.'),
                                  redirect=redirect)


    def get_tabs(self, request, *args, **kwargs):
        volume = self.get_data()
        return self.tab_group_class(request, volume=volume, **kwargs)
