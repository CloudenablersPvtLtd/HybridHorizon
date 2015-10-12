from django.utils.translation import ugettext_lazy as _

import horizon

class Amazon(horizon.Dashboard):
    name = _("Amazon")
    slug = "amazon"
    panels = ('instances','images','keypairs','securitygroups','volume','snapshots','elastic_ip')  # Add your panels here.
    default_panel = 'instances'  # Specify the slug of the dashboard's default panel.

horizon.register(Amazon)
