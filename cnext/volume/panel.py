from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Volume(horizon.Panel):
    name = _("Volume")
    slug = "volume"


dashboard.Cnext.register(Volume)
