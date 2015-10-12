from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Snapshots(horizon.Panel):
    name = _("Snapshots")
    slug = "snapshots"


dashboard.Amazon.register(Snapshots)
