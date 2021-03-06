# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing volumes.
"""

from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions,forms,tables,tabs
from hpcloud import api
from hpcloud.api import cinder
from hpcloud.usage import quotas
from hpcloud.volumes \
    import forms as project_forms
from hpcloud.volumes \
    import tables as project_tables
from hpcloud.volumes \
    import tabs as project_tabs


class VolumeTableMixIn(object):
    def _get_volumes(self, search_opts=None):
        try:
            return cinder.volume_list(self.request, search_opts=search_opts)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve volume list.'))
            return []

    def _get_instances(self, search_opts=None):
        try:
            instances, has_more = api.nova.server_list(self.request,
                                                       search_opts=search_opts)
            return instances
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve volume/instance "
                                "attachment information"))
            return []

    def _set_id_if_nameless(self, volumes, instances):
        for volume in volumes:
            # It is possible to create a volume with no name through the
            # EC2 API, use the ID in those cases.
            if not volume.display_name:
                volume.display_name = volume.id

    def _set_attachments_string(self, volumes, instances):
        instances = SortedDict([(inst.id, inst) for inst in instances])
        for volume in volumes:
            for att in volume.attachments:
                server_id = att.get('server_id', None)
                att['instance'] = instances.get(server_id, None)


class IndexView(tables.DataTableView, VolumeTableMixIn):
    table_class = project_tables.VolumesTable
    template_name = 'hpcloud/volumes/index.html'

    def get_data(self):
        volumes = self._get_volumes()
        instances = self._get_instances()
        self._set_id_if_nameless(volumes, instances)
        self._set_attachments_string(volumes, instances)
        return volumes


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.VolumeDetailTabs
    template_name = 'hpcloud/volumes/detail.html'


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateForm
    template_name = 'hpcloud/volumes/create.html'
    success_url = reverse_lazy("horizon:hpcloud:volumes:index")

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request)
        return context


class CreateSnapshotView(forms.ModalFormView):
    form_class = project_forms.CreateSnapshotForm
    template_name = 'hpcloud/volumes/create_snapshot.html'
    success_url = reverse_lazy("horizon:hpcloud:images_and_snapshots:index")

    def get_context_data(self, **kwargs):
        context = super(CreateSnapshotView, self).get_context_data(**kwargs)
        context['volume_id'] = self.kwargs['volume_id']
        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request)
        return context

    def get_initial(self):
        return {'volume_id': self.kwargs["volume_id"]}


class EditAttachmentsView(tables.DataTableView, forms.ModalFormView):
    table_class = project_tables.AttachmentsTable
    form_class = project_forms.AttachForm
    template_name = 'hpcloud/volumes/attach.html'
    success_url = reverse_lazy("horizon:hpcloud:volumes:index")

    def get_object(self):
        if not hasattr(self, "_object"):
            volume_id = self.kwargs['volume_id']
            try:
                self._object = cinder.volume_get(self.request, volume_id)
            except Exception:
                self._object = None
                exceptions.handle(self.request,
                                  _('Unable to retrieve volume information.'))
        return self._object

    def get_data(self):
        try:
            volumes = self.get_object()
            attachments = [att for att in volumes.attachments if att]
        except Exception:
            attachments = []
            exceptions.handle(self.request,
                              _('Unable to retrieve volume information.'))
        return attachments

    def get_initial(self):
        try:
            instances, has_more = api.nova.server_list(self.request)
        except Exception:
            instances = []
            exceptions.handle(self.request,
                              _("Unable to retrieve attachment information."))
        return {'volume': self.get_object(),
                'instances': instances}

    def get_form(self):
        if not hasattr(self, "_form"):
            form_class = self.get_form_class()
            self._form = super(EditAttachmentsView, self).get_form(form_class)
        return self._form

    def get_context_data(self, **kwargs):
        context = super(EditAttachmentsView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        volume = self.get_object()
        if volume and volume.status == 'available':
            context['show_attach'] = True
        else:
            context['show_attach'] = False
        context['volume'] = volume
        if self.request.is_ajax():
            context['hide'] = True
        return context

    def get(self, request, *args, **kwargs):
        # Table action handling
        handled = self.construct_tables()
        if handled:
            return handled
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.get(request, *args, **kwargs)
