'''
Created on 01-Apr-2014

@author: annamalai
'''

from horizon import tabs
from django.utils.translation import ugettext_lazy as _

class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/images/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"image": self.tab_group.kwargs['image']}


class OwnedDetailTabs(tabs.TabGroup):
    slug = "image_details"
    tabs = (OverviewTab,)