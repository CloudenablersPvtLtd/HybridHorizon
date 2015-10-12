from horizon import tables
from .tables import WorkloadTable, WorkloadDetailsTable

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = WorkloadTable
    template_name = 'cnext/workload/index.html'

    def get_data(self):
        # Add data to the context here...
	workload = []
        return workload

class DetailView(tables.DataTableView):
    table_class = WorkloadDetailsTable
    template_name = 'cnext/workload/detail.html'

    def get_data(self):
        workloadDetails = []           
	return workloadDetails

