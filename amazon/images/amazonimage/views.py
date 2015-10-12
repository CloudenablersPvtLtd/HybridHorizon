from horizon import exceptions,messages
from django.utils.translation import ugettext_lazy as _
from horizon import tabs
from django.core.urlresolvers import reverse
from amazon.images.amazonimage import tabs as project_tabs
from aws_api.images import Images
import logging

LOG = logging.getLogger(__name__)

class DetailView(tabs.TabView):
    tab_group_class = project_tabs.AmazonDetailTabs
    template_name = 'amazon/images/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["image"] = self.get_data()
        return context

    def get_data(self):
        try:
            return Images(self.request).get_images_detail(self.kwargs['image_id'])
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
            redirect = reverse('horizon:amazon:images:index')
            exceptions.handle_redirect(self.request,redirect)

    def get_tabs(self, request, *args, **kwargs):
        image = self.get_data()
        return self.tab_group_class(request, instance=image, **kwargs)




