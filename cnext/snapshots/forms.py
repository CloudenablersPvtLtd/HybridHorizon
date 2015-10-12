# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from cnext_api import api


class CreateSnapshot(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    provider = forms.CharField(label=_("Provider"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    region = forms.CharField(label=_("Region"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    instance_name = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    name = forms.CharField(max_length="255", label=_("Snapshot Name"))
    description = forms.CharField(max_length="255", label=_("Description"))

    def handle(self, request, data):
        try:
            snapshot = api.create_snapshots(request, data['name'], data['instance_id'], data['provider'], data['region'],data['description'])
            vals = {"name": data['name'], "inst": data['instance_name']}
            messages.success(request, _('Snapshot "%(name)s" created for '
                                        'instance "%(inst)s"') % vals)
            return snapshot
        except Exception:
            redirect = reverse("horizon:cnext:instances:index")
            exceptions.handle(request,
                              _('Unable to create snapshot.'),
                              redirect=redirect)
