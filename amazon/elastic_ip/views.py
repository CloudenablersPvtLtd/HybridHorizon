from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from amazon.elastic_ip import forms as project_forms
from amazon.elastic_ip import tabs as project_tabs
from horizon import forms,tables,tabs,exceptions,messages
from .tables import ElasticIPdisplayTable
import logging
from aws_api.elastic_ip import ElasticIPs
LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = ElasticIPdisplayTable
    template_name = 'amazon/elastic_ip/index.html'
 
    def get_data(self):
        try:
            address = ElasticIPs(self.request).get_addresses()
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return address

    
class AllocateAddressView(forms.ModalFormView):
    form_class = project_forms.AllocateAddress
    template_name = 'amazon/elastic_ip/create.html'
    success_url = reverse_lazy('horizon:amazon:elastic_ip:index')

 
class AssociateAddressView(forms.ModalFormView):
    form_class = project_forms.AssociateAddress
    template_name = 'amazon/elastic_ip/associate.html'
    success_url = reverse_lazy("horizon:amazon:elastic_ip:index")

    def get_context_data(self, **kwargs):
        context = super(AssociateAddressView, self).get_context_data(**kwargs)
        context['id'] = self.kwargs["id"]
        context['domain'] = self.kwargs["domain"]
        return context
   
    def get_initial(self):
        id = self.kwargs["id"]
        domain = self.kwargs["domain"]
        inst_id = ElasticIPs(self.request).get_instance_ids(domain)
        return {
                    'id':id,
                    'instance_choices':inst_id
                    }


class DisassociateAddressView(forms.ModalFormView):
      
    form_class = project_forms.DisassociateAddress
    template_name = 'amazon/elastic_ip/disassociate.html'
    success_url = reverse_lazy("horizon:amazon:elastic_ip:index")
     
    def get_context_data(self, **kwargs):
        context = super(DisassociateAddressView, self).get_context_data(**kwargs)
        context['id'] = self.kwargs["id"]
        return context
      
    def get_initial(self):
        address_info = []
        addr_id = self.kwargs["id"]
        address_info.append((addr_id,addr_id))
        return {
                'addr_id':address_info
                }
 
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ElasticIPDetailTabs
    template_name = 'amazon/elastic_ip/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["elasticips"] = self.get_data()
        return context
     
    def get_data(self):
        try:
            el_ip = ElasticIPs(self.request).elastic_ip_details(self.kwargs['id'])
        except Exception, e:
            redirect = reverse('horizon:amazon:elastic_ip:index')
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(self.request,redirect)
        return el_ip
 
    def get_tabs(self, request, *args, **kwargs):
        elasticips = self.get_data()
        return self.tab_group_class(request, elasticips=elasticips,
                                    **kwargs)
 
