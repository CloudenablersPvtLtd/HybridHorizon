from django.utils.translation import ugettext_lazy as _

import horizon

from wangle import dashboard


class Cloud(horizon.Panel):
    name = _("Cloud")
    slug = "cloud"


dashboard.Wangle.register(Cloud)
