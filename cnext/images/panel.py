from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Images(horizon.Panel):
    name = _("Images")
    slug = "images"


dashboard.Cnext.register(Images)
