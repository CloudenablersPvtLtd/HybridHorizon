from django.utils.translation import ugettext_lazy as _

import horizon

from amazon import dashboard


class Elastic_IP(horizon.Panel):
    name = _("Elastic IPs")
    slug = "elastic_ip"


dashboard.Amazon.register(Elastic_IP)
