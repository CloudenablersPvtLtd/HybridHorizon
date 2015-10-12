from django.utils.translation import ugettext_lazy as _

from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/volume/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"volume":self.tab_group.kwargs['volume'] }


class VolumeDetailTabs(tabs.TabGroup):
    slug = "volume_details"
    tabs = (OverviewTab,)
