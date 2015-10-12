from horizon import tables
from .tables import WorkloadsTable

class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = WorkloadsTable
    template_name = 'cnext/workloads/index.html'

    def get_data(self):
        # Add data to the context here...
	workloads = []
        return workloads

