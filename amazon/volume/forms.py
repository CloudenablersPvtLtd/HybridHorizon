from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from horizon import exceptions,forms,messages,workflows
from aws_api.volumes import Volumes
import logging

LOG = logging.getLogger(__name__)


class Regionlist():
    def __init__(self, provider, region):
        self.name = region
        self.provider = provider
        self.region = region

class SetVolumeDetailsAction(workflows.Action):
    
    VOLUME_TYPE_CHOICES = (("", _("Select Volume Type")),\
                            ('standard', 'Standard'),\
                            ('io1', 'Provisioned IOPS'),)
    volume_name=forms.CharField(max_length="60",
                           label=_("Volume Name"), required=False)
    volume_type = forms.ChoiceField(
        label=_("Volume Type"),
        required=True,
        choices=VOLUME_TYPE_CHOICES
        )
    size = forms.CharField(label=_("Volume Size (in GiB)"),required = True,
                           widget=forms.TextInput(attrs={'type':'number','min':'1','max':'1024'}))
    availability_zone = forms.ChoiceField(
        label=_("Zone List"),
        required=True
        )
    iops = forms.IntegerField(min_value = 100,max_value=4000,
                              label=_("IOPS"),
                              required=False)
    class Meta:
        name = _("Details")
        help_text_template = ("amazon/volume/"
                               "_create_details_help.html")
    def __init__(self, request, context, *args, **kwargs):
        super(SetVolumeDetailsAction, self).__init__(
            request, context, *args, **kwargs)
    def populate_availability_zone_choices(self, request, context):
        aws_tuples  = []
        aws_zone = Volumes(request).get_zone()
        for zone in aws_zone:
            aws_tuples.append((str(zone.name), str(zone.name)))
        aws_tuples.insert(0, ("", _("Select Zone")))

        return aws_tuples

class SetVolumeDetails(workflows.Step):
    action_class = SetVolumeDetailsAction
    contributes = ("volume_name","volume_type","size","availability_zone","iops",)
    
class CreateVolume(workflows.Workflow):
    slug = "create_volume"
    name = _("Create Volume")
    finalize_button_name = _("Create")
    success_message = _('Created %(count)s named "%(name)s".')
    failure_message = _('Unable to create %(count)s named "%(name)s".')
    success_url = "horizon:amazon:volume:index"
    default_steps = (SetVolumeDetails,
                    )
    
    def format_status_message(self, message):
        name = self.context.get('volume_name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s volume") % count,
                              "name": name}
        else:
            return message % {"count": _("volume"), "name": name}
    def handle(self, request, context):
        try:
            Volumes(request).create_volume(size=context['size'], zone=context['availability_zone'],
                                                       volume_type=context['volume_type'],
                                                       iops=context['iops'], name=str(context['volume_name']))
            return True
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            return False

 
class AttachForm(forms.SelfHandlingForm):
    instance_choice=[]
    def __init__(self, *args, **kwargs):
        instance_choice = kwargs["initial"]["instance_choices"] 
        super(AttachForm, self).__init__(*args,**kwargs)
        self.fields['instance_id'] = forms.ChoiceField(label="Attach to Instance", choices=instance_choice)
     
    volume_id= forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
     
    instance_id = forms.ChoiceField(label=_("Attach to Instance"),
                                 help_text=_("Select an instance to "
                                             "attach to."),choices=instance_choice)
    device = forms.CharField(label=_("Device Name"))
 
  
    def handle(self,request,data):
        try:
            volume = Volumes(request).attach_volume(data['instance_id'],data['volume_id'],
                                                                data['device'])
            if str(volume) == "attaching":
                messages.success(request, _('Schedule to attach a volume: %s')
                                        % data['volume_id'])
            else:
                messages.error(request,_('Unable  to attach a volume: %s') %data['volume_id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:volume:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)


class CreateSnapshotForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(CreateSnapshotForm, self).__init__(request,*args,**kwargs)
    
    volume_id= forms.CharField(label=_("Volume ID"),
                                  widget=forms.HiddenInput(),
                                  required=True)
    snapshot_name=forms.CharField(max_length="255",
                           label=_("Snapshot Name"), required=False)
    description=forms.CharField(max_length="255",
                           label=_("Description"), required=False) 
 
  
    def handle(self,request,data):
        try:
            Volumes(request).create_snapshot(data['volume_id'],data['description'],
                                                         data['snapshot_name'])
            messages.success(request, _('Snapshot Created for Volume %s: ')
                                        % data['volume_id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:volume:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
