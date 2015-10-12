from django.utils.translation import ugettext_lazy as _

import horizon

from wangle import dashboard


class Role(horizon.Panel):
    name = _("Role")
    slug = "role"


dashboard.Wangle.register(Role)
