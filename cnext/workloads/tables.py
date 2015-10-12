from django.utils.translation import ugettext_lazy as _
from horizon import tables

class WorkloadsTable(tables.DataTable):
    wname = tables.Column('Name', verbose_name=_("Name"))
    wstatus = tables.Column('Status', verbose_name=_("Status"))
    wid = tables.Column('ID', verbose_name=_("ID"))
    wcreated = tables.Column('CreateDate', verbose_name=_("CreatedDate"))

    class Meta:
        name = "workloads"
    verbose_name = _("Workloads")
