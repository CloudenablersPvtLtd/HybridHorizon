from django.utils.translation import ugettext_lazy as _
from horizon import tables

from django.core.urlresolvers import reverse
from django.utils.http import urlencode

class LaunchImage(tables.LinkAction):
    name = "launch_image"
    verbose_name = _("Launch")
    url = "horizon:amazon:instances:launch"
    classes = ("btn-launch", "ajax-modal")
 
    def get_link_url(self, datum):
        base_url = reverse(self.url)
        source_type = "owned_images_id"
        params = urlencode({
                            "source_types":source_type,
                            "owned_images_id": self.table.get_object_id(datum)
                            })
        return "?".join([base_url, params])
  
    def allowed(self, request, datum):
        if "Tenant Admin" in request.session['user_roles']:
            return True 
        if "Create Instance" in request.session['user_policies'].get(request.user.awsname):
            return True
        return False


class InstancesFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        instance_list = []
        for instance in instances:
            if instance.name != None and instance.platform != None:
                if q in [instance.name.lower(),instance.ownerid.lower()]:
                    instance_list.append(instance)
        return instance_list


class OwnedImagesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("saving", None),
        ("queued", None),
        ("pending_delete", None),
        ("killed", False),
        ("deleted", False),
    )
    ids = tables.Column("id",link=("horizon:amazon:images:ownedimage:detail"),verbose_name=_("Id"))
    name = tables.Column("name",verbose_name=_("Name"))
    region = tables.Column("region", verbose_name=_("Region"))
    platform = tables.Column("platform", verbose_name=_("Platform"))
    ownerid = tables.Column("ownerid", verbose_name=_("OwnerId"))
    is_public = tables.Column("is_public", verbose_name=_("Is_Public"))
    state = tables.Column("state", verbose_name=_("State"))

    class Meta:
        name = "ownedimage"
        verbose_name = _("Owned Images")
        table_actions = (InstancesFilterAction,)
        row_actions = (LaunchImage,)
