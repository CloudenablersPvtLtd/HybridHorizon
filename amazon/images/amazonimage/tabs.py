'''
Created on 01-Apr-2014

@author: annamalai
'''
from django.utils.translation import ugettext_lazy as _ 
from horizon import tabs

class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("amazon/images/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"image": self.tab_group.kwargs['image']}


class AmazonDetailTabs(tabs.TabGroup):
    slug = "image_details"
    tabs = (OverviewTab,)