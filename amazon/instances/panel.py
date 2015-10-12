from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Instances(horizon.Panel):
    name = _("Instances")
    slug = "instances"


dashboard.Amazon.register(Instances)
