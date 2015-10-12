from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Volume(horizon.Panel):
    name = _("Volumes")
    slug = "volume"


dashboard.Amazon.register(Volume)
