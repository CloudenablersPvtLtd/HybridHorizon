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

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from hpcloud import api

class DeleteKeyPairs(tables.DeleteAction):
    data_type_singular = _("Keypair")
    data_type_plural = _("Keypairs")

    def allowed(self, request, kp=None):
        if "Delete KP" in request.session['user_policies'].get(request.user.hpname):
            return True
        else:
            return False

    def delete(self, request, obj_id):
        api.nova.keypair_delete(request, obj_id)


class ImportKeyPair(tables.LinkAction):
    name = "import"
    verbose_name = _("Import Keypair")
    url = "horizon:hpcloud:access_and_security:keypairs:import"
    classes = ("ajax-modal", "btn-upload")


class CreateKeyPair(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Keypair")
    url = "horizon:hpcloud:access_and_security:keypairs:create"
    classes = ("ajax-modal", "btn-create")
    
    def allowed(self, request, volume=None):
        if "Create KP" in request.session['user_policies'].get(request.user.hpname):
            return True
        else:
            return False


class KeypairsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Keypair Name"))
    fingerprint = tables.Column("fingerprint", verbose_name=_("Fingerprint"))

    def get_object_id(self, keypair):
        return keypair.name

    class Meta:
        name = "keypairs"
        verbose_name = _("Keypairs")
        table_actions = (CreateKeyPair, ImportKeyPair, DeleteKeyPairs,)
        row_actions = (DeleteKeyPairs,)
