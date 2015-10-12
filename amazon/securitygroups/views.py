
import logging
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions, messages, forms, tabs, tables
from amazon.securitygroups import forms as project_forms,tabs as project_tabs
from .tables import SecurityGroupsTable
from aws_api.security_groups import SecurityGroups, get_vpc_id
LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = SecurityGroupsTable
    template_name = 'amazon/securitygroups/index.html'

    def get_data(self):
        securitygroup = []
        try:
            securitygroup = SecurityGroups(self.request).get_security_groups()
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return securitygroup


class AddRuleView(forms.ModalFormView):
    form_class = project_forms.AddRule
    template_name = 'amazon/securitygroups/add_rule.html'
    success_url = reverse_lazy("horizon:amazon:securitygroups:index")

    def get_context_data(self, **kwargs):
        context = super(AddRuleView, self).get_context_data(**kwargs)
        context['group_name'] = self.kwargs["group_name"]
        return context
  
    def get_initial(self):
        group_name = self.kwargs["group_name"]
        return {'group_name': group_name}


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateGroup
    template_name = 'amazon/securitygroups/create.html'
    success_url = reverse_lazy('horizon:amazon:securitygroups:index')

    def get_initial(self):
        vpc_id = get_vpc_id(self.request)
        return {'vpc_choices': vpc_id, }


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.SecuritygroupsDetailTabs
    template_name = 'amazon/securitygroups/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["securitygroups"] = self.get_data()
        return context
     
    def get_data(self):
        try:
            key_p = SecurityGroups(self.request).security_group_details(self.kwargs['securitygroups_id'])
        except Exception, e:
            redirect = reverse('horizon:amazon:instances:index')
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(self.request,redirect)
        return key_p
 
    def get_tabs(self, request, *args, **kwargs):
        securitygroups = self.get_data()
        return self.tab_group_class(request, securitygroups=securitygroups,
                                    **kwargs)
class DeleteRuleView(forms.ModalFormView):
     
    form_class = project_forms.DeleteRule
    template_name = 'amazon/securitygroups/delete_rule.html'
    success_url = reverse_lazy("horizon:amazon:securitygroups:index")
    
    def get_context_data(self, **kwargs):
        context = super(DeleteRuleView, self).get_context_data(**kwargs)
        context['security_group_id'] = self.kwargs["security_group_id"]
        return context
 
    def get_initial(self):
        sg_id = self.kwargs["security_group_id"]
        sgs = SecurityGroups(self.request).get_rules(sg_id)
        rulelist = []
        for sg in sgs:
            for rule in sg.rules:
                rulelist.append((("%s,%s,%s,%s" % (rule.from_port,rule.to_port,rule.ip_protocol,rule.grants[0])),rule))
        return {
                'sg_id':sg_id,
                'rule_list':rulelist
                }
