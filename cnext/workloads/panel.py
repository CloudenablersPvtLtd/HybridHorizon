from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Workloads(horizon.Panel):
    name = _("Workloads")
    slug = "workloads"


dashboard.Cnext.register(Workloads)
