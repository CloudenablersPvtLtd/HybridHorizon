from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Workload(horizon.Panel):
    name = _("Workload")
    slug = "workload"


dashboard.Cnext.register(Workload)
