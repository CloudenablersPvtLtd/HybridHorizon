from django.utils.translation import ugettext_lazy as _
from horizon import tables

def get_wid(workload):
    if workload.has_key("WorkloadId"):
        wid = workload["WorkloadId"]
        return wid
    return _("Not available")

class WorkloadTable(tables.DataTable):
    wname = tables.Column('WorkloadName',
			  link=("http://192.168.3.228:8080/CNext/workload/detail"),
                          verbose_name=_("WorkloadName"))
    wrsrcs = tables.Column('NumberOfResourcesInWorkload', verbose_name=_("NumberOfResourcesInWorkload"))
    
    class Meta:
        name = "workload"
        verbose_name = _("Workload")

class WorkloadDetailsTable(tables.DataTable):
    wename = tables.Column('WorkloadElementName', verbose_name=_("WorkloadElementName"))
    weprice = tables.Column('Price', verbose_name=_("Price"))
    weunit = tables.Column('Unit', verbose_name=_("Unit"))
    
    class Meta:
        name = "workloadDetails"
        verbose_name = _("Workload Details")
