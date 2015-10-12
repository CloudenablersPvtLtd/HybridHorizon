from django.utils.translation import ugettext_lazy as _
from horizon import tables

from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from cnext_api import api

class LaunchImage(tables.LinkAction):
    name = "launch_image"
    verbose_name = _("Launch")
    url = "horizon:cnext:instances:launch"
    classes = ("btn-launch", "ajax-modal")
    


    def get_link_url(self, datum):
        base_url = reverse(self.url)
        provider = datum.provider
        region = datum.region
        params = urlencode({"provider": provider,
                            "region": region,
                            "cnext_images_id": self.table.get_object_id(datum)
                            })
        return "?".join([base_url, params])

    def allowed(self, request, datum):
        if "Tenant Admin" in request.session['user_roles']:
            return True 
        for policy in request.session['user_policies'].get(request.user.cnextname):
            if ("Create Instance" in policy[2] and (datum.provider,datum.region) == (policy[0],policy[1])):
                return True
        return False


class DeleteImage(tables.DeleteAction):
    data_type_singular = _("Image")
    data_type_plural = _("Images")

    def delete(self, request, obj_id):
        api.glance.image_delete(request, obj_id)


class CreateImage(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Image")
    url = "horizon:cnext:images:create"
    classes = ("ajax-modal", "btn-create")


class EditImage(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:cnext:images:update"
    classes = ("ajax-modal", "btn-edit")


class CreateVolumeFromImage(tables.LinkAction):
    name = "create_volume_from_image"
    verbose_name = _("Create Volume")
    url = "horizon:project:volumes:create"
    classes = ("ajax-modal", "btn-camera")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"image_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])


class InstancesFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [instance for instance in instances
                if q in instance.name.lower()]
        

class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.image_detail(request, image_id)
        return image
 
    def load_cells(self, image=None):
        super(UpdateRow, self).load_cells(image)
        # Tag the row with the image category for client-side filtering.
        image = self.datum
        self.attrs['data-provider'] = image.provider
        self.attrs['data-region'] = image.region



class ImagesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("saving", None),
        ("queued", None),
        ("pending_delete", None),
        ("killed", False),
        ("deleted", False),
    )
    name = tables.Column("name",
                         link=("horizon:cnext:images:detail"),
                         verbose_name=_("Name"))
    provider = tables.Column("provider", verbose_name=_("Provider"))
    region = tables.Column("region", verbose_name=_("Region"))
    platform = tables.Column("platform", verbose_name=_("Platform"))
    os = tables.Column("os", verbose_name=_("Os"))
    cost = tables.Column("cost", verbose_name=_("Cost"))
    description = tables.Column("description", verbose_name=_("Description"))

    class Meta:
        name = "images"
        row_class = UpdateRow
        verbose_name = _("Images")
        table_actions = (InstancesFilterAction,)
        row_actions = (LaunchImage,)


def get_image_type(image):
    return getattr(image, "properties", {}).get("image_type", "image")


def get_format(image):
    formats = getattr(image, "disk_format", "")
    # The "container_format" attribute can actually be set to None,
    # which will raise an error if you call upper() on it.
    if formats is not None:
        return formats.upper()
