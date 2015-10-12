from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Securitygroups(horizon.Panel):
    name = _("Security Groups")
    slug = "securitygroups"


dashboard.Amazon.register(Securitygroups)
