from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from horizon import exceptions, forms, messages
from horizon.utils import fields
from aws_api.elastic_ip import ElasticIPs
import logging

LOG = logging.getLogger(__name__)


class AllocateAddress(forms.SelfHandlingForm):
    
    def __init__(self, *args, **kwargs):
        super(AllocateAddress, self).__init__(*args,**kwargs)
        EIP_TYPE_CHOICES = (( 'ec2' , 'EC2'),('vpc', 'VPC'),)
        self.fields['eip'] = forms.ChoiceField(
                label=_("EIP used in"),
                required=True,
                choices=EIP_TYPE_CHOICES
                )
   
    def handle(self, request, data):
        try:
            address = ElasticIPs(request).create_address(data['eip'])
            if address.region.name != None:
                messages.success(request, _('New address request succeeded, Elastic IP: %s.')
                                       % address.public_ip)
            return True            
        except Exception, e:
            redirect = reverse("horizon:amazon:elastic_ip:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
            return False


class AssociateAddress(forms.SelfHandlingForm):
    instance_choice=[]
    def __init__(self, *args, **kwargs):
        instance_choice = kwargs["initial"]["instance_choices"]
        super(AssociateAddress, self).__init__(*args,**kwargs)
        self.fields['instance_id'] = forms.ChoiceField(label=_("Instance"),
                                      widget=fields.SelectWidget(
                                             data_attrs=(),
                                             transform=lambda x: ("%s (%s) (%s)" % (x.id,x.state,x.tags['Name']))),
                                                        choices=instance_choice)
        
    id = forms.CharField(label=_("id"),
                                widget=forms.HiddenInput(),
                                required=False)
   
    instance_id = forms.ChoiceField(label=_("Instance"),
                                      widget=fields.SelectWidget(
                                             data_attrs=(),
                                             transform=lambda x: ("%s (%s)" % (x.id,x.state))),
                                   help_text=_("Search Instance" 
                                               "ID"),choices=instance_choice)

    def handle(self, request, data):
        try:
            associate = ElasticIPs(request).associate_addr(data['id'],data['instance_id'])
            if associate == True:
                messages.success(request, _('Successfully Associated: %s') 
                                        % data['id'])
            else:
                messages.error(request, _('Unable to associate address: %s') % data['id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:elastic_ip:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
        
        
class DisassociateAddress(forms.SelfHandlingForm):
    id_choice = []
    instance_choice = []
    def __init__(self, *args, **kwargs):
        super(DisassociateAddress, self).__init__(*args,**kwargs)
        id_choice = kwargs['initial']['addr_id']
        self.fields['id'] = forms.ChoiceField(label="Address", choices=id_choice)
        id = forms.ChoiceField(label=_("Address"),
                                    required=False,choices = id_choice)
   
    def handle(self, request, data):
        try:
            disassociate = ElasticIPs(request).disassociate_ip(data['id'])
            if disassociate == True:
                messages.success(request, _('Successfully Disassociated: %s') 
                                        % data['id'])
            else:
                messages.error(request, _('Unable to Disassociate address: %s') % data['id'])
            return disassociate
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
