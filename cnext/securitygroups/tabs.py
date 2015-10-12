from django.utils.translation import ugettext_lazy as _
from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("cnext/securitygroups/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"securitygroups": self.tab_group.kwargs['securitygroups']}
    
    

class SecuritygroupsDetailTabs(tabs.TabGroup):
    slug = "instance_details"
    tabs = (OverviewTab,)
