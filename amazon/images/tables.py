from django.utils.translation import ugettext_lazy as _
from horizon import tables


class InstancesFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [instance for instance in instances
                if q in instance.name.lower()]
        

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
                         link=("horizon:amazon:images:detail"),
                         verbose_name=_("Name"))
    region = tables.Column("region", verbose_name=_("Region"))
    platform = tables.Column("platform", verbose_name=_("Platform"))
    ownerid = tables.Column("ownerid", verbose_name=_("OwnerId"))
    is_public = tables.Column("is_public", verbose_name=_("Is_Public"))
    state = tables.Column("state", verbose_name=_("State"))

    class Meta:
        name = "images"
        verbose_name = _("Images")
        table_actions = (InstancesFilterAction,)