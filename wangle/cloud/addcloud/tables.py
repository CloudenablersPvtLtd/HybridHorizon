import logging
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables

LOG = logging.getLogger(__name__)


class AddCloud(tables.LinkAction):
    name = "Add_cloud"
    verbose_name = _("Add cloud")
    data_type_singular = _("Add Cloud ")
    data_type_plural = _(" Add Cloud")
    url = "horizon:wangle:cloud:addcloud:create"
    classes = ("ajax-modal", "btn-add")
   
    def get_link_url(self, datum):
        return reverse("horizon:wangle:"
                       "cloud:addcloud:create", args=[datum.id])
    def allowed(self, request, instance=None):
        if "Create Cloud" in request.session['user_roleaccess']:
            return True
        return False

class AddCloudTable(tables.DataTable):
    name = tables.Column("name",verbose_name=_("Platforms"))
    id = tables.Column('id', verbose_name=_("Cloud Id"),hidden = True)
   
    class Meta:
        
        name = "addcloud"
        verbose_name = _("Add Cloud")
        row_actions = (AddCloud,)
