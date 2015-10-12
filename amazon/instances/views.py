from .tables import InstancesTable
from django.utils.translation import ugettext_lazy as _
from horizon import tables, exceptions, workflows, tabs
from amazon.instances import workflows as project_workflows
from django.core.urlresolvers import reverse
from amazon.instances import tabs as project_tabs
from amazon.instances import forms as project_forms
from aws_api.instance import get_accounts
from horizon import forms,messages
from django.core.urlresolvers import reverse_lazy
from aws_api.instance import Instances
from aws_api.connection import get_regions_wo_connection
import logging

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = InstancesTable
    template_name = 'amazon/instances/index.html'
    
    def get_data(self):
        instances = []
        try:
            instances = Instances(self.request).get_instances() 
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return instances


class LaunchInstanceView(workflows.WorkflowView):
    workflow_class = project_workflows.LaunchInstance
    
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabs
    template_name = 'amazon/instances/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["instance"] = self.get_data()
        return context

    def get_data(self):
        try:
            return Instances(self.request).instance_detail(self.kwargs['instance_id'])
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            redirect = reverse('horizon:amazon:instances:index')
            exceptions.handle_redirect(self.request, redirect)

    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)

class RegionSwitch(forms.ModalFormView):
    form_class = project_forms.SwitchRegionForm
    template_name = 'amazon/region.html'
    success_url = reverse_lazy('horizon:amazon:instances:index')
    
    def get_initial(self):
        region_choices = get_regions_wo_connection()
        return {
                'region_choices':region_choices
                }

class AccountChange(forms.ModalFormView):
    form_class = project_forms.AccountChangeForm
    template_name = 'amazon/account.html'
    success_url = reverse_lazy('horizon:amazon:instances:index')
     
    def get_initial(self):
        aws_accounts = get_accounts(self.request)
        return {
                'account_choices':aws_accounts
                }
