'''
Created on 14-Apr-2014

@author: annamalai
'''
from django.utils.translation import ugettext_lazy as _
import horizon


class BasePanels(horizon.PanelGroup):
    slug = "compute"
    name = _("Manage Compute")
    panels = ('overview',
               'instances',
               'volumes',
              'images_and_snapshots',
               'access_and_security',
)


class NetworkPanels(horizon.PanelGroup):
    slug = "network"
    name = _("Manage Network")
    panels = ('network_topology',
              'networks',
              'routers',)


class ObjectStorePanels(horizon.PanelGroup):
    slug = "object_store"
    name = _("Object Store")
    panels = ('containers',)
    
class IdentityPanels(horizon.PanelGroup):
    slug = "identity1"
    name = _("Identity Panel")
    panels = ('domains', 'projects', 'users', 'groups', 'roles')

class Hpcloud(horizon.Dashboard):
    name = _("Hpcloud")
    slug = "hpcloud"
    panels = (
        BasePanels,
        NetworkPanels,
        ObjectStorePanels,
        )
    default_panel = 'overview'

horizon.register(Hpcloud)