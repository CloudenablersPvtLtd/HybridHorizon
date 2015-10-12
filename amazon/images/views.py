from horizon import tables, messages
from django.utils.translation import ugettext_lazy as _
from amazon.images.ownedimage import tables as ownedimage_table
from amazon.images.amazonimage import tables as amazonimage_table
from aws_api.images import Images
import logging

LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = (ownedimage_table.OwnedImagesTable,
                     amazonimage_table.AmazonImagesTable)
    template_name = 'amazon/images/index.html'

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)

    def get_ownedimage_data(self):
        images = []
        try:
            images = Images(self.request).get_images('self')
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return images

    def get_amazonimage_data(self):
        images = []
        try:
            images = Images(self.request).get_images('amazon')
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return images