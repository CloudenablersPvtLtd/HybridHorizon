from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Keypairs(horizon.Panel):
    name = _("Keypairs")
    slug = "keypairs"


dashboard.Cnext.register(Keypairs)
