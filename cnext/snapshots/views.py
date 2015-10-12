from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions, forms, tables
from .tables import SnapshotTable
from cnext.snapshots \
    import forms as project_forms
from cnext_api import api


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'cnext/snapshots/index.html'
    table_class = SnapshotTable

    def get_data(self):
        try:
            snapshot = []
            snapshot = api.snapshots(self.request)
        except:
            snapshot = []
            exceptions.handle(self.request,_('Unable to retrieve images'))
        return snapshot
    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data()
        context["provider"] = api.providers(self.request)
        context["region"] = api.region(self.request)
        return context
    
    
class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateSnapshot
    template_name = 'cnext/snapshots/create.html'
    success_url = reverse_lazy("horizon:cnext:snapshots:index")



    def get_initial(self):
        return {"instance_name": self.kwargs["instance_name"],"instance_id": self.kwargs["instance_id"],"provider": self.kwargs["provider"],"region": self.kwargs["region"]}
    

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['instance_id'] = self.kwargs["instance_id"]
        context['provider'] = self.kwargs["provider"]
        context['region'] = self.kwargs["region"]
        context['instance_name'] = self.kwargs["instance_name"]
        return context
