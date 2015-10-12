from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Instances(horizon.Panel):
    name = _("Instances")
    slug = "instances"


dashboard.Cnext.register(Instances)
