from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables, messages
import logging
from aws_api.elastic_ip import ElasticIPs

LOG = logging.getLogger(__name__)

class AllocateAddress(tables.LinkAction):
    name = "allocate"
    verbose_name = _("Allocate Address")
    url = "horizon:amazon:elastic_ip:allocate"
    classes = ("ajax-modal", "btn-create")
    def allowed(self, request, datum):
        if "Allocate IP" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False
    
class ReleaseAddress(tables.DeleteAction):
    data_type_singular = _(" ")
    data_type_plural = _(" ")
    
    def allowed(self, request, instance):
        if instance.instance_id == None or instance.instance_id == "":
            if "Release IP" in request.session['user_policies'].get(request.user.awsname):
                return True
            else:
                return False
        else:
            return False
 
    def delete(self, request, id):
        try:
            valu = ElasticIPs(request).release_ip(id=id)
            if valu == True:
                pass
            elif valu == False:
                messages.error(request, _('An error occurred while attempting to release the IP address '
                    'The address "%s" does not belong to you.')
                                       % id)
        except Exception, e:  
            messages.error(request,_(e.message))
            LOG.error(e.message)
           

class AssociateAddress(tables.LinkAction):
    name = "associate"
    verbose_name = _("Associate Address")
    url = "horizon:amazon:elastic_ip:associate"
    classes = ("ajax-modal", "btn-associate")
     
    def get_link_url(self, datum):
        return reverse("horizon:amazon:"
                       "elastic_ip:associate", args=[datum.id,datum.domain])
    def allowed(self, request, elastic_ip):
        if "Associate IP" in request.session['user_policies'].get(request.user.awsname):
            return True
        else:
            return False

class DisassociateAddress(tables.LinkAction):
    name = "disassociate"
    verbose_name = _("Disassociate Address")
    url = "horizon:cnext:elastic_ip:disassociate"
    classes = ("ajax-modal", "btn-disassociate")
      
  
    def get_link_url(self, datum):
        return reverse("horizon:amazon:"
                        "elastic_ip:disassociate", args=[datum.id])    
      
    def allowed(self, request, elastic_ip):
        if elastic_ip.instance_id == None or elastic_ip.instance_id == "":
            return False
        else:
            if "Disassociate IP" in request.session['user_policies'].get(request.user.awsname):
                return True 

class ElasticIPdisplayTable(tables.DataTable):

    address = tables.Column("id",verbose_name=_("Address"),link=("horizon:amazon:elastic_ip:detail"))
    instance =tables.Column("instance_id",verbose_name=_("Instance"))
    private_ip = tables.Column("private_ip_address",verbose_name=_("Private IP Address"))
    scope = tables.Column("domain", verbose_name=_("Scope"))
    region = tables.Column("region", verbose_name=_("Region"))
    
        
    def get_object_display(self, elast_ip):
        return elast_ip.id

    def get_object_id(self, elast_ip):
        return str(elast_ip.id)
    
    class Meta:
        name = "Elastic IPs"
        verbose_name = _("Elastic IPs")
        table_actions = (AllocateAddress,)
        row_actions = (ReleaseAddress, AssociateAddress, DisassociateAddress)