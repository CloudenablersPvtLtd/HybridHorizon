from horizon import tables, exceptions
from .tables import ImagesTable
from django.utils.translation import ugettext_lazy as _
from cnext_api import api

from cnext.images import tabs as project_tabs
from cnext.images import forms as project_forms
from horizon import forms
from horizon import tabs

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy


class IndexView(tables.DataTableView):
    table_class = ImagesTable
    template_name = 'cnext/images/index.html'

    def get_data(self):
        try:
            images = []
            images = api.images(self.request)
        except:
            images = []
            exceptions.handle(self.request, _('Unable to retrieve images'))
        return images

    
    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data()
        context["provider"] = api.providers(self.request)
        context["region"] = api.region(self.request)
        return context


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateImageForm
    template_name = 'cnext/images/create.html'
    context_object_name = 'image'
    success_url = reverse_lazy("horizon:cnext:images:index")


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateImageForm
    template_name = 'cnext/images/update.html'
    success_url = reverse_lazy("horizon:cnext:images:index")

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                self._object = api.glance.image_get(self.request,
                                                    self.kwargs['image_id'])
            except Exception:
                msg = _('Unable to retrieve image.')
                url = reverse('horizon:cnext:images:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['image'] = self.get_object()
        return context

    def get_initial(self):
        image = self.get_object()
        return {'image_id': self.kwargs['image_id'],
                'name': image.name,
                'description': image.properties.get('description', ''),
                'kernel': image.properties.get('kernel_id', ''),
                'ramdisk': image.properties.get('ramdisk_id', ''),
                'architecture': image.properties.get('architecture', ''),
                'disk_format': image.disk_format,
                'public': image.is_public,
                'protected': image.protected}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ImageDetailTabs
    template_name = 'cnext/images/detail.html'
