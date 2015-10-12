from django.utils.translation import ugettext_lazy as _

import horizon

class Accounts(horizon.PanelGroup):
    slug = "accounts"
    name = _("Accounts")
    panels = ('keys',)


class Workspace(horizon.PanelGroup):
    slug = "workspace"
    name = _("Workspace")
    panels = ('workload',)

class Cnext(horizon.Dashboard):
    name = _("Cnext")
    slug = "cnext"
    panels = ('images', 'keypairs', 'securitygroups','instances','volume','snapshots',)  # Add your panels here.
    default_panel = 'keypairs'  # Specify the slug of the dashboard's default panel.

horizon.register(Cnext)
