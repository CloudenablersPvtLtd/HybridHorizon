from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Keypairs(horizon.Panel):
    name = _("Key Pairs")
    slug = "keypairs"


dashboard.Amazon.register(Keypairs)
