from django.utils.translation import ugettext_lazy as _

import horizon

from wangle import dashboard


class Users(horizon.Panel):
    name = _("Users")
    slug = "users"


dashboard.Wangle.register(Users)
