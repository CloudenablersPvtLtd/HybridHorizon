from django.core.urlresolvers import reverse
from django.views.generic import View

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django import http

from horizon import tables, exceptions, messages, forms
from .tables import KeypairsTable
from aws_api.keypairs import KeyPairs

from amazon.keypairs import forms as project_forms
import logging

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    table_class = KeypairsTable
    template_name = 'amazon/keypairs/index.html'

    def get_data(self):
        keypair = []
        try:
            keypair = KeyPairs(self.request).get_key_pairs()
        except Exception, e:
            messages.error(self.request,_(e.message))
            LOG.error(e.message)
        return keypair


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateKeypair
    template_name = 'amazon/keypairs/create.html'
    success_url = 'horizon:amazon:keypairs:download'
 
    def get_success_url(self):
        return reverse(self.success_url,
                       kwargs={"keypair_name": self.request.POST['name']
                               })


class DownloadView(TemplateView):
    template_name = 'amazon/keypairs/download.html'
 
    def get_context_data(self, keypair_name=None):
        return {'keypair_name': keypair_name}
 
 
class GenerateView(View):
    def get(self, request, keypair_name=None):
        try:
            keypair = KeyPairs(request).create_keypairs(keypair_name)
        except Exception, e:
            redirect = reverse('horizon:amazon:keypairs:index')
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
 
        response = http.HttpResponse(mimetype='application/binary')
        response['Content-Disposition'] = \
                'attachment; filename=%s.pem' % slugify(keypair.name)
        response.write(keypair.material)
        response['Content-Length'] = str(len(response.content))
        return response

