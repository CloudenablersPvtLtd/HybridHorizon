import logging
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables
from horizon import exceptions,messages
from horizon import forms
from horizon.utils import fields
from horizon import workflows
from aws_api.images import Images
from aws_api.keypairs import KeyPairs
from aws_api.security_groups import SecurityGroups
from aws_api.instance import Instances
from amazon.instances.instance_types import instance_type_choices

LOG = logging.getLogger(__name__)


class SetInstanceDetailsAction(workflows.Action):
    
    SOURCE_TYPE_CHOICES = (
        ('', _("--- Select source ---")),
        ("owned_images_id", _("My Image.")),
        ("amazon_images_id", _("Amazon Image.")),
    )
    name = forms.CharField(max_length=80, label=_("Instance Name"))
  
    count = forms.IntegerField(label=_("Instance Count"),
                                min_value=1,
                                initial=1,
                                help_text=_("Number of instances to launch."))
    availability_zone = forms.ChoiceField(label=_("Availability Zone"),
                                    required=True,
                                    help_text=_("Choose Your Zone "))
    source_types = forms.ChoiceField(label=_("Instance Boot Source"),
                                    required=True,
                                    choices = SOURCE_TYPE_CHOICES,
                                    help_text=_("Choose Your Boot Source "
                                                "Type."))
    owned_images_id = forms.ChoiceField(
        label=_("Owned Images"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('id','name','root_device_name','architecture','region','state','kernel_id','virtualization_type','root_device_type',),
            transform=lambda x: ("%s" % (x.name))))
    amazon_images_id = forms.ChoiceField(
                                        label=_("Amazon Images"),
                                        widget=fields.SelectWidget(
                                            data_attrs=('id','name','root_device_name','architecture','region','state','kernel_id','virtualization_type','root_device_type',),
                                            transform=lambda x: ("%s" % (str(x.id) + " - (" + str(x.name) + ")",))),
                                        required=False)
    imagetype = forms.CharField(label=_("Image Type"),
                                widget=forms.HiddenInput(),
                                required=False
                                )
    instance_type = forms.ChoiceField(label = _("Instance Type"),
                                      required = True,
                                      help_text=_("Choose Your Instance Type."),
                                      choices = instance_type_choices,
                                      widget=fields.SelectWidget(data_attrs=('imagetype', 'instancetype', ),
                                                                 transform=lambda x: ("%s " % (x.name)))
                                      )
    
    class Meta:
        name = _("Details")
        help_text_template = ("amazon/instances/"
                              "_launch_details_help.html")
    def __init__(self, request, context, *args, **kwargs):
        super(SetInstanceDetailsAction, self).__init__(
            request, context, *args, **kwargs)
    def clean(self):
        cleaned_data = super(SetInstanceDetailsAction, self).clean()
        # Validate our instance source.
        source_type = self.data.get('source_type', None)

        if source_type == "owned_images_id":
            if not cleaned_data.get('owned_images_id'):
                msg = _("You must select an image.")
                self._errors['owned_images_id'] = self.error_class([msg])

        elif source_type == 'amazon_images_id':
            if not cleaned_data['amazon_images_id']:
                msg = _("You must select a image.")
                self._errors['amazon_images_id'] = self.error_class([msg])
        return cleaned_data

    def populate_owned_images_id_choices(self, request, context):
        aws_tuples  = []
        aws_images = Images(request).get_images('self')
        if "owned_images_id" in context:
            cimage_id = context["owned_images_id"]
            aws_images = list( filter((lambda x: x.__dict__["id"].lower() \
                                            == cimage_id ), aws_images ))
        for cimage in aws_images:
            cnid = cimage.__dict__['id']
            aws_tuples.append((cnid, cimage))
        aws_tuples.insert(0, ("", _("Select Image")))

        return aws_tuples
    def populate_amazon_images_id_choices(self, request, context):
        aws_tuples  = []
        aws_images = Images(request).get_images('amazon')
        if "amazon_images_id" in context:
            cimage_id = context["amazon_images_id"]
            aws_images = list( filter((lambda x: x.__dict__["id"].lower() \
                                            == cimage_id ), aws_images ))
        for cimage in aws_images:
            cnid = cimage.__dict__['id']
            aws_tuples.append((cnid, cimage))
        aws_tuples.insert(0, ("", _("Select Image")))

        return aws_tuples
    def populate_availability_zone_choices(self, request, context):
        aws_tuples  = []        
        aws_zone = Instances(request).get_zone()
        for zone in aws_zone:
            aws_tuples.append((str(zone.name), str(zone.name)))
        aws_tuples.insert(0, ("", _("Select Zone")))

        return aws_tuples
class SetInstanceDetails(workflows.Step):
    action_class = SetInstanceDetailsAction
    contributes = ("source_types","source_id","owned_images_id",\
                   "amazon_images_id","name","count","availability_zone","instance_type")

    def prepare_action_context(self, request, context):
        if 'source_types' in context and 'source_id' in context:
            context[context['source_types']] = context['source_id']
        return context

    def contribute(self, data, context):
        context = super(SetInstanceDetails, self).contribute(data, context)
        # Allow setting the source dynamically.
        if ("source_types" in context and "source_id" in context
                and context["source_types"] not in context):
            context[context["source_types"]] = context["source_id"]

        # Translate form input to context for source values.
        if "source_types" in data:
            if data["source_types"] in ["owned_images_id"]:
                context["source_id"] = data.get("owned_images_id", None)
            else:
                context["source_id"] = data.get(data["source_types"], None)
        return context
class SetAccessControlsAction(workflows.Action):
    keypair = forms.ChoiceField(label=_("Select your Keypair"),
                                    required=True,
                                    help_text=_("Choose Your Boot Source "
                                                "Type."))
    groups = forms.MultipleChoiceField(label=_("Security Groups"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Launch instance in these "
                                                   "security groups."))
  
    class Meta:
        name = _("Access & Security")
        help_text = _("Control access to your instance via keypairs, "
                      "security groups, and other mechanisms.")
  
    def populate_keypair_choices(self, request, context):
        try:
            keypair_obj = KeyPairs(request).get_key_pairs()
            keypair_list = [(kp.id, kp.id) for kp in keypair_obj]
        except Exception:
            keypair_list = []
            exceptions.handle(request,
                              _('Unable to retrieve keypairs.'))
        if keypair_list:
            keypair_list.insert(0, ("", _("Select a keypair")))
        else:
            keypair_list = (("", _("No keypairs available.")),)
        return keypair_list
  
    def populate_groups_choices(self, request, context):
        try:
            groups = SecurityGroups(request).get_security_groups()
            if groups:
                security_group_list = [(str(sg.name), sg.name) for sg in groups]
            else:
                security_group_list = [] 
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve list of security groups'))
            security_group_list = []
        return security_group_list
  
 
class SetAccessControls(workflows.Step):
    action_class = SetAccessControlsAction
    contributes = ("keypair_id", "security_group_ids",)
  
    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['security_group_ids'] = post.getlist("groups")
            context['keypair_id'] = data.get("keypair", None)
        return context
class LaunchInstance(workflows.Workflow):
    slug = "launch_instance"
    name = _("Launch Instance")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s named "%(name)s".')
    failure_message = _('Unable to launch %(count)s named "%(name)s".')
    success_url = "horizon:amazon:instances:index"
    default_steps = (SetInstanceDetails,
                     SetAccessControls,
                    )
    def format_status_message(self, message):
        name = self.context.get('name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s instances") % count,
                              "name": name}
        else:
            return message % {"count": _("instance"), "name": name}
    
    @sensitive_variables('context')
    def handle(self, request, context):
        image_id = ''
        source_types = context.get('source_types', None)
        if source_types in ['owned_images_id', 'amazon_images_id']:
            image_id = context['source_id']
        

        try:
            Instances(request).launch_instances(image_id = str(image_id),\
                                                   max_count = context['count'],\
                                                   placement = context['availability_zone'],\
                                                   key_name = context['keypair_id'],\
                                                   security_groups = context['security_group_ids'],\
                                                   name = str(context['name']),\
                                                   instance_type = context['instance_type'])
            return True
        except Exception,e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            return False