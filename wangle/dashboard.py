from django.utils.translation import ugettext_lazy as _

import horizon


class Wangle(horizon.Dashboard):
    name = _("Manage")
    slug = "wangle"
    panels = ('cloud', 'users', 'role',)  # Add your panels here.
    default_panel = 'cloud'  # Specify the slug of the dashboard's default panel.


horizon.register(Wangle)
