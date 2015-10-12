from django.utils.translation import ugettext_lazy as _
from horizon import tables


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, snap_id):
        snapshot = api.inst_detail(request, snap_id)
        return security_group
 
    def load_cells(self, snapshots=None):
        super(UpdateRow, self).load_cells(snapshots)
        # Tag the row with the image category for client-side filtering.
        snap_shots = self.datum
        self.attrs['data-provider'] = snap_shots.provider
        self.attrs['data-region'] = snap_shots.region     


class SnapshotTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    provider = tables.Column("provider", verbose_name=_("Provider"))
    region = tables.Column("region", verbose_name=_("Region"))
    ids = tables.Column("id",verbose_name=_("InstanceId"))
    status = tables.Column("status", verbose_name=_("Status"))
 
    
    class Meta:
        name = "snapshots"
        row_class = UpdateRow
        verbose_name = _("Snapshots")
