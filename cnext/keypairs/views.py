from django.core.urlresolvers import reverse
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django import http
from horizon import tables, exceptions
from .tables import KeypairsTable
from horizon import forms
from horizon import tabs
from cnext_api import api
from cnext.keypairs import forms as project_forms
from cnext.keypairs import tabs as project_tabs

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = KeypairsTable
    template_name = 'cnext/keypairs/index.html'

    def get_data(self):
        keypairs = []
        try:
            keypairs = api.keypairs(self.request)
        except:
            exceptions.handle(self.request,
                              _('Unable to retrieve keypairs'))
        return keypairs

       
    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data()
        context["provider"] = api.providers(self.request)
        context["region"] = api.region(self.request)
        return context


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateKeypair
    template_name = 'cnext/keypairs/create.html'
    success_url = 'horizon:cnext:keypairs:download'

    def get_success_url(self):
        return reverse(self.success_url,
                       kwargs={"keypair_name": self.request.POST['name'],
                               "provider": self.request.POST['key_provider_list'],
                               "region": self.request.POST['key_region_list']
                               })


class ImportView(forms.ModalFormView):
    form_class = project_forms.ImportKeypair
    template_name = 'cnext/keypairs/import.html'
    success_url = reverse_lazy('horizon:cnext:keypairs')

    def get_object_id(self, keypair):
        return keypair.name


class DownloadView(TemplateView):
    template_name = 'cnext/keypairs/download.html'

    def get_context_data(self, keypair_name=None, provider=None,
                         region=None):
        return {'keypair_name': keypair_name,
                'provider': provider,
                'region': region}

class GenerateView(View):
    def get(self, request, keypair_name=None, provider=None, region=None):
        try:
            keypair = api.create_keypairs(request, keypair_name, provider,
                                          region)
        except Exception:
            redirect = reverse('horizon:cnext:keypairs:index')
            exceptions.handle(self.request,
                              _('Unable to create keypair: %(exc)s'),
                              redirect=redirect)
 
        response = http.HttpResponse(mimetype='application/binary')
        response['Content-Disposition'] = \
                'attachment; filename=%s.pem' % slugify(keypair[0].name)
        response.write(keypair[0].privatekey)
        response['Content-Length'] = str(len(response.content))
        return response
    
    
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.KeypairsDetailTabs
    template_name = 'cnext/keypairs/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["keypairs"] = self.get_data()
        return context
    
    def get_data(self):
            try:
                key_pair = api.inst_detail(self.request,self.kwargs['keypairs_id'])
            except Exception:
                redirect = reverse('horizon:cnext:instances:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve keypair details.'),
                                  redirect=redirect)
            return key_pair

    def get_tabs(self, request, *args, **kwargs):
        keypairs = self.get_data()
        return self.tab_group_class(request, keypairs=keypairs, **kwargs)

class AccountChange(forms.ModalFormView):
    form_class = project_forms.AccountChangeForm
    template_name = 'cnext/account.html'
    success_url = reverse_lazy('horizon:cnext:keypairs:index')
     
    def get_initial(self):
        cnext_accounts = api.get_accounts(self.request)
        return {
                'account_choices':cnext_accounts
                }
