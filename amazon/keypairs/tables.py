from django.utils.translation import ugettext_lazy as _
from horizon import tables,messages
from aws_api.keypairs import KeyPairs 
import logging

LOG = logging.getLogger(__name__)

class DeleteKeyPairs(tables.BatchAction):
    name = "delete"
    action_present = _("DELETE")
    action_past = _("DELETED")
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    classes = ('btn-danger', 'btn-terminate',)
    success_url = 'horizon:amazon:keypairs:index'
     
     
    def allowed(self, request, datum):
        if "Tenant Admin" in request.session['user_roles']:
            return True 
        if "Delete KP" in request.session['user_policies'].get(request.user.awsname):
            return True
        return False
 
    def action(self, request, datum):
        try:
            KeyPairs(request).delete_keypair(datum)
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)


class CreateKeyPair(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Keypair")
    url = "horizon:amazon:keypairs:create"
    classes = ("ajax-modal", "btn-create")
 
    def allowed(self, request, datum):
        if "Create KP" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False


class KeypairsTable(tables.DataTable):
    name = tables.Column("id", verbose_name=_("Keypair Name"))
    region = tables.Column('region', verbose_name=_("Region"))
    fingerprint = tables.Column("fingerprint", verbose_name=_("Fingerprint"))

    def get_object_display(self,key_pair):
        return key_pair.id

    class Meta:
        name = "keypairs"
        verbose_name = _("Keypairs")
        table_actions = (CreateKeyPair,)
        row_actions = (DeleteKeyPairs,)
