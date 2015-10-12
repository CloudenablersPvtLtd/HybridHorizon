from horizon import workflows, forms
from django.utils.translation import ugettext_lazy as _
from horizon.utils import fields


class SetInstanceDetailsAction(workflows.Action):
    SOURCE_TYPE_CHOICES = (
        ('', _("--- Select source ---")),
        ("image_id", _("Boot from image.")),
        ("instance_snapshot_id", _("Boot from snapshot.")),
        ("volume_id", _("Boot from volume.")),
        ("volume_image_id", _("Boot from image "
                                  "(creates a new volume).")),
        ("volume_snapshot_id", _("Boot from volume snapshot "
                                 "(creates a new volume).")),
    )

    availability_zone = forms.ChoiceField(label=_("Availability Zone"),
                                          required=False)

    name = forms.CharField(max_length=80, label=_("Instance Name"))

    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of image to launch."))

    count = forms.IntegerField(label=_("Instance Count"),
                               min_value=1,
                               initial=1,
                               help_text=_("Number of instances to launch."))

    source_type = forms.ChoiceField(label=_("Instance Boot Source"),
                                    required=True,
                                    choices=SOURCE_TYPE_CHOICES,
                                    help_text=_("Choose Your Boot Source "
                                                "Type."))

    instance_snapshot_id = forms.ChoiceField(label=_("Instance Snapshot"),
                                             required=False)

    volume_id = forms.ChoiceField(label=_("Volume"), required=False)

    volume_snapshot_id = forms.ChoiceField(label=_("Volume Snapshot"),
                                               required=False)

    image_id = forms.ChoiceField(
        label=_("Image Name"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('volume_size',),
            transform=lambda x: ("%s (%s)" % (x.name,
                                              filesizeformat(x.bytes)))))

    volume_size = forms.CharField(label=_("Device size (GB)"),
                                  required=False,
                                  help_text=_("Volume size in gigabytes "
                                              "(integer value)."))

    device_name = forms.CharField(label=_("Device Name"),
                                  required=False,
                                  initial="vda",
                                  help_text=_("Volume mount point (e.g. 'vda' "
                                              "mounts at '/dev/vda')."))

    delete_on_terminate = forms.BooleanField(label=_("Delete on Terminate"),
                                             initial=False,
                                             required=False,
                                             help_text=_("Delete volume on "
                                                         "instance terminate"))

    class Meta:
        name = _("Details")
        help_text_template = ("project/instances/"
                              "_launch_details_help.html")

    def __init__(self, request, context, *args, **kwargs):
        self._init_images_cache()
        super(SetInstanceDetailsAction, self).__init__(
            request, context, *args, **kwargs)

    def clean(self):
        cleaned_data = super(SetInstanceDetailsAction, self).clean()

        count = cleaned_data.get('count', 1)
        # Prevent launching more instances than the quota allows
        usages = quotas.tenant_quota_usages(self.request)
        available_count = usages['instances']['available']
        if available_count < count:
            error_message = ungettext_lazy('The requested instance '
                                           'cannot be launched as you only '
                                           'have %(avail)i of your quota '
                                           'available. ',
                                           'The requested %(req)i instances '
                                           'cannot be launched as you only '
                                           'have %(avail)i of your quota '
                                           'available.',
                                           count)
            params = {'req': count,
                      'avail': available_count}
            raise forms.ValidationError(error_message % params)

        # Validate our instance source.
        source_type = self.data.get('source_type', None)

        if source_type == 'image_id':
            if not cleaned_data.get('image_id'):
                msg = _("You must select an image.")
                self._errors['image_id'] = self.error_class([msg])

        elif source_type == 'instance_snapshot_id':
            if not cleaned_data['instance_snapshot_id']:
                msg = _("You must select a snapshot.")
                self._errors['instance_snapshot_id'] = self.error_class([msg])

        elif source_type == 'volume_id':
            if not cleaned_data.get('volume_id'):
                msg = _("You must select a volume.")
                self._errors['volume_id'] = self.error_class([msg])
            # Prevent launching multiple instances with the same volume.
            # TODO(gabriel): is it safe to launch multiple instances with
            # a snapshot since it should be cloned to new volumes?
            if count > 1:
                msg = _('Launching multiple instances is only supported for '
                        'images and instance snapshots.')
                raise forms.ValidationError(msg)

        elif source_type == 'volume_image_id':
            if not cleaned_data['image_id']:
                msg = _("You must select an image.")
                self._errors['image_id'] = self.error_class([msg])
            if not self.data.get('volume_size', None):
                msg = _("You must set volume size")
                self._errors['volume_size'] = self.error_class([msg])
            if not cleaned_data.get('device_name'):
                msg = _("You must set device name")
                self._errors['device_name'] = self.error_class([msg])

        elif source_type == 'volume_snapshot_id':
            if not cleaned_data.get('volume_snapshot_id'):
                msg = _("You must select a snapshot.")
                self._errors['volume_snapshot_id'] = self.error_class([msg])
            if not cleaned_data.get('device_name'):
                msg = _("You must set device name")
                self._errors['device_name'] = self.error_class([msg])

        return cleaned_data

    def _init_images_cache(self):
        if not hasattr(self, '_images_cache'):
            self._images_cache = {}

    def _get_volume_display_name(self, volume):
        if hasattr(volume, "volume_id"):
            vol_type = "snap"
            visible_label = _("Snapshot")
        else:
            vol_type = "vol"
            visible_label = _("Volume")
        return (("%s:%s" % (volume.id, vol_type)),
                (_("%(name)s - %(size)s GB (%(label)s)") %
                 {'name': volume.display_name or volume.id,
                  'size': volume.size,
                  'label': visible_label}))

    def populate_image_id_choices(self, request, context):
        choices = []
        images = api.images(request)
        for image in images:
            image.bytes = image.size
            image.volume_size = functions.bytes_to_gigabytes(image.bytes)
            choices.append((image.id, image))
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available")))
        return choices

    def populate_instance_snapshot_id_choices(self, request, context):
        images = api.images(request)
        choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("image_type", '') == "snapshot"]
        if choices:
            choices.insert(0, ("", _("Select Instance Snapshot")))
        else:
            choices.insert(0, ("", _("No snapshots available.")))
        return choices


class SetInstanceDetails(workflows.Step):
    action_class = SetInstanceDetailsAction
    depends_on = ("project_id", "user_id")
    contributes = ("source_type", "source_id",
                   "availability_zone", "name", "count", "flavor",
                   "device_name",  # Can be None for an image.
                   "delete_on_terminate")

    def prepare_action_context(self, request, context):
        if 'source_type' in context and 'source_id' in context:
            context[context['source_type']] = context['source_id']
        return context

    def contribute(self, data, context):
        context = super(SetInstanceDetails, self).contribute(data, context)
        # Allow setting the source dynamically.
        if ("source_type" in context and "source_id" in context
                and context["source_type"] not in context):
            context[context["source_type"]] = context["source_id"]

        # Translate form input to context for source values.
        if "source_type" in data:
            if data["source_type"] in ["image_id", "volume_image_id"]:
                context["source_id"] = data.get("image_id", None)
            else:
                context["source_id"] = data.get(data["source_type"], None)

        if "volume_size" in data:
            context["volume_size"] = data["volume_size"]

        return context



class LaunchInstance(workflows.Workflow):
    slug = "launch_instance"
    name = _("Launch Instance")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s named "%(name)s".')
    failure_message = _('Unable to launch %(count)s named "%(name)s".')
    success_url = "horizon:cnext:instances:index"
    default_steps = (
                     SetInstanceDetails)


    def format_status_message(self, message):
        name = self.context.get('name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s instances") % count,
                              "name": name}
        else:
            return message % {"count": _("instance"), "name": name}
