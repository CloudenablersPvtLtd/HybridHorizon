from django.utils.translation import ugettext_lazy as _
from horizon import tabs

class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/elastic_ip/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"elasticips":self.tab_group.kwargs['elasticips'] }


class ElasticIPDetailTabs(tabs.TabGroup):
    slug = "elastic_ip_details"
    tabs = (OverviewTab,)

