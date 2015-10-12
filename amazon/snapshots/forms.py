from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions, forms, messages, workflows
from aws_api.snapshots import Snapshots 
import logging

LOG = logging.getLogger(__name__)

class Regionlist():
    def __init__(self, provider, region):
        self.name = region
        self.provider = provider
        self.region = region

class CreateVolumeForm(forms.SelfHandlingForm):
    zone_choice=[]
    def __init__(self, request, *args, **kwargs):
        zone_choice = kwargs["initial"]["zone_choices"]
        super(CreateVolumeForm, self).__init__(request,*args,**kwargs)
        self.fields['availability_zone'] = forms.ChoiceField(label="Zone List",required=True, choices=zone_choice)
        self.fields['size'] = forms.IntegerField(min_value=kwargs['initial']['volume_size'],
                                                 required = True, label=_("Volume Size (in GB)"))
    
    snapshot_id= forms.CharField(label=_("Snapshot ID"),
                                  widget=forms.HiddenInput(),
                                  required=True)
     
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
    size = forms.IntegerField(required = True,
                           label=_("Volume Size (in GB)"))

    iops = forms.IntegerField(min_value = 100,
                              label=_("IOPS"),
                              required=False)
 
  
    def handle(self,request,data):
        try:
            Snapshots(request).create_volume(data['snapshot_id'],
                                                           data['availability_zone'],
                                                           data['volume_name'],data['volume_type'],
                                                           data['size'], data['iops'])
            messages.success(request, _('Volume created for Snapshot : %s')
                                        % data['snapshot_id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:snapshots:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)


class CopySnapshotForm(forms.SelfHandlingForm):
    region_choice=[]
    def __init__(self, request, *args, **kwargs):
        region_choice = kwargs["initial"]["region_choices"]
        super(CopySnapshotForm, self).__init__(request,*args,**kwargs)
        self.fields['destination_region'] = forms.ChoiceField(label="Destination Region",required=True, choices=region_choice)
    
    snapshot_id= forms.CharField(label=_("Snapshot ID"),
                                  widget=forms.HiddenInput(),
                                  required=True)
    description=forms.CharField(max_length="255",
                           label=_("Description"), required=False) 
 
  
    def handle(self,request,data):
        try:
            Snapshots(request).copy_snapshot(data['snapshot_id'],
                                                           data['destination_region'],
                                                           data['description'])
            messages.success(request, _('Snapshot %s Copied to the Selected Region : ')
                                        % data['snapshot_id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:snapshots:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)


class SetSnapshotDetailsAction(workflows.Action):
    
    availability_volume = forms.ChoiceField(
        label=_("Volume List"),
        required=True
        )
    snapshot_name=forms.CharField(max_length="255",
                           label=_("Snapshot Name"), required=False)
    description=forms.CharField(max_length="255",
                           label=_("Description"), required=False)
    
    
    class Meta:
        name = _("Details")
        help_text_template = ("amazon/snapshots/"
                               "_create_details_help.html")
    def __init__(self, request, context, *args, **kwargs):
        super(SetSnapshotDetailsAction, self).__init__(
            request, context, *args, **kwargs)
    def populate_availability_volume_choices(self, request, context):
        aws_tuples  = []        
        aws_volumes = Snapshots(request).get_volumes()
        for volume in aws_volumes:
            if "Name" in volume.tags:
                aws_tuples.append((str(volume.id), str(volume.id) + " - " + str(volume.tags["Name"])))
            else:
                aws_tuples.append((str(volume.id), str(volume.id)))
        aws_tuples.insert(0, ("", _("Select Volume")))

        return aws_tuples

class SetSnapshotDetails(workflows.Step):
    action_class = SetSnapshotDetailsAction
    contributes = ("availability_volume","snapshot_name","description",)

class CreateSnapshot(workflows.Workflow):
    slug = "create_snapshot"
    name = _("Create Snapshot")
    finalize_button_name = _("Create")
    success_message = _('Created %(count)s named "%(name)s".')
    failure_message = _('Unable to create %(count)s named "%(name)s".')
    success_url = "horizon:amazon:snapshots:index"
    default_steps = (SetSnapshotDetails,
                    )
    
    def format_status_message(self, message):
        name = self.context.get('snapshot_name', 'availability_volume')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s snapshot") % count,
                              "name": name}
        else:
            return message % {"count": _("snapshot"), "name": name}
    def handle(self, request, context):
        try:
            Snapshots(request).create_snapshot(volume_id=context['availability_volume'],
                                                             description=context['description'],
                                                             name=str(context['snapshot_name']))
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:snapshots:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
            return False
