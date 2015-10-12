from django.utils.translation import ugettext_lazy as _

from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/snapshots/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"snapshot":self.tab_group.kwargs['snapshot'] }


class SnapshotDetailTabs(tabs.TabGroup):
    slug = "snapshot_details"
    tabs = (OverviewTab,)
