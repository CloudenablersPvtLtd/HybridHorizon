from django.utils.translation import ugettext_lazy as _
from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/keypairs/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"keypairs": self.tab_group.kwargs['keypairs']}
    
    

class KeypairsDetailTabs(tabs.TabGroup):
    slug = "instance_details"
    tabs = (OverviewTab,)