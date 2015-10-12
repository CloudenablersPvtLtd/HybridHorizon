from django.utils.translation import ugettext_lazy as _

import horizon

from cnext import dashboard


class Keys(horizon.Panel):
    name = _("Keys")
    slug = "keys"


dashboard.Cnext.register(Keys)
