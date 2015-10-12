from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tabs, tables, exceptions, workflows
from .tables import InstancesTable
from cnext_api import api
from cnext.instances import workflows as project_workflows
from cnext.instances import tabs as project_tabs


class IndexView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'cnext/instances/index.html'

    def get_data(self):
        instances = []
        try:
            instances = api.instances(self.request)
        except:
            exceptions.handle(self.request, _('Unable to retrieve instances'))
        return instances

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        context["provider"] = api.providers(self.request)
        context["region"] = api.region(self.request)
        return context


class LaunchInstanceView(workflows.WorkflowView):
    workflow_class = project_workflows.LaunchInstance

    def get_initial(self):
        initial = super(LaunchInstanceView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabs
    template_name = 'cnext/instances/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["instance"] = self.get_data()
        return context

    def get_data(self):
        try:
            inst = api.inst_detail(self.request, self.kwargs['instance_id'])
        except Exception:
            redirect = reverse('horizon:cnext:instances:index')
            exceptions.handle(self.request,
                                  _('Unable to retrieve instance details.'),
                                  redirect=redirect)
        return inst

    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)
