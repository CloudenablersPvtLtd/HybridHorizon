from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from horizon import exceptions, forms, messages
from horizon.utils import fields
from cnext_api import api
import re
from cnext.resource import provider_volume_choices,region_volume_choices

NEW_LINES = re.compile(r"\r|\n")

class Regionlist():
    def __init__(self, provider, region):
        self.name = region
        self.provider = provider
        self.region = region


class CreateVolume(forms.SelfHandlingForm):
    volume_name=forms.CharField(max_length="60",
                           label=_("Volume Name"), required=False)
    description = forms.CharField(max_length="200",
                           label=_("Volume Description"), required=False)
    name = forms.IntegerField(min_value=1,
                           label=_("Volume Size (in GB)"))
    key_provider_list = forms.ChoiceField(
        label=_("Providers List"),
        required=True,
        )
    key_region_list = forms.ChoiceField(
        label=_("Regions List"),
        required=True,
        widget=fields.SelectWidget(data_attrs=('provider','region',),transform=lambda x: ("%s " % (x.name)))
        )
    
    def handle(self,request, data):
        try:
            volume = api.volume_create(request,data['name'],data['volume_name'],data['description'], \
                                              data['key_provider_list'],data['key_region_list'])
            if volume == True:
                messages.success(request, _('Schedule to create a volume: %s')
                                       % data['volume_name'])
            else:
                messages.error(request, _('Unable to create a volume: %s')
                                       % data['volume_name'])
            return True
            
        except Exception:
            exceptions.handle(request,
                              _('Unable to create volume.'),)
            redirect = reverse("horizon:cnext:volume:index")

    def __init__(self, request, *args, **kwargs):
        forms.SelfHandlingForm.__init__(self, request, *args, **kwargs)
        provider_list = api.providers(self.request)
        region_list = api.region(self.request)
        p = [("", _("Select Provider"))]
        for provider in provider_list:
            if provider.provider in provider_volume_choices:
                p.append((provider.provider.lower(),provider.provider))
        t = tuple(p)
        tuple_providers = t
        self.fields['key_provider_list'].choices = tuple_providers
        r = [("", _("Select Region"))]
        for region in region_list:
            if region.name in region_volume_choices:
                r.append((region.name,Regionlist(region.provider,region.name)))
        r = tuple(r)
        tuple_regions = r
        self.fields['key_region_list'].choices = tuple_regions


class AttachForm(forms.SelfHandlingForm):
    volume_choices=[]
    def __init__(self, *args, **kwargs):
        volume_choices = kwargs["initial"]["volume_choices"] 
        super(AttachForm, self).__init__(*args,**kwargs)
        self.fields['VMinstance'] = forms.ChoiceField(label="Attach to Instance", choices=volume_choices)
    
    instanceid= forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    
    VMinstance = forms.ChoiceField(label=_("Attach to Instance"),
                                 help_text=_("Select an instance to "
                                             "attach to."),choices=volume_choices)
    device = forms.CharField(label=_("Device Name"))

 
    def handle(self,request,data):
        try:
            volume = api.attach_to_vm(request,data['instanceid'],data['VMinstance'],data['device'])
            if volume == True:
                messages.success(request, _('Schedule to attach a volume: %s')
                                        % data['instanceid'])
            else:
                messages.error(request,_('Unable  to attach a volume: %s') %data['instanceid'])
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to create volume.'),)
            redirect = reverse("horizon:cnext:volume:index")


class DettachForm(forms.SelfHandlingForm):
    volume_choices=[]
    def __init__(self, *args, **kwargs):
        print kwargs
        volume_choices = kwargs["initial"]["volume_choices"] 
        super(DettachForm, self).__init__(*args,**kwargs)
        self.fields['VMinstance'] = forms.ChoiceField(label="Dettach to Instance", choices=volume_choices)
    
   
    
    instanceid= forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    
    VMinstance = forms.ChoiceField(label=_("Attach to Instance"),
                                 help_text=_("Select an instance to "
                                             "dettach to."),choices=volume_choices)
    device = forms.CharField(label=_("Device Name"))

 
    def handle(self,request,data):
        try:
            volume = api.dettach(request,data['instanceid'],data['VMinstance'],data['device'])
            messages.success(request, _('Schedule to dettach a volume:: %s')
                                        % data['instanceid'])
            return volume
        except Exception:
            exceptions.handle(request,
                              _('Unable to create volume.'),)
            redirect = reverse("horizon:cnext:volume:index")
