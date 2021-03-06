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

from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils import safestring
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from hpcloud import api
from hpcloud.api import cinder
from hpcloud.volumes \
    import tables as volume_tables


class DeleteVolumeSnapshot(tables.DeleteAction):
    data_type_singular = _("Volume Snapshot")
    data_type_plural = _("Volume Snapshots")
    action_past = _("Scheduled deletion of")

    def delete(self, request, obj_id):
        api.cinder.volume_snapshot_delete(request, obj_id)


class CreateVolumeFromSnapshot(tables.LinkAction):
    name = "create_from_snapshot"
    verbose_name = _("Create Volume")
    url = "horizon:hpcloud:volumes:create"
    classes = ("ajax-modal", "btn-camera")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"snapshot_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

    def allowed(self, request, volume=None):
        return volume.status == "available" if volume else False


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, snapshot_id):
        snapshot = cinder.volume_snapshot_get(request, snapshot_id)
        snapshot._volume = cinder.volume_get(request, snapshot.volume_id)
        return snapshot


class SnapshotVolumeNameColumn(tables.Column):
    def get_raw_data(self, snapshot):
        volume = snapshot._volume
        if volume:
            volume_name = volume.display_name or volume.id
        else:
            volume_name = _("Unknown")
        return safestring.mark_safe(volume_name)

    def get_link_url(self, snapshot):
        volume = snapshot._volume
        if volume:
            volume_id = volume.id
            return reverse(self.link, args=(volume_id,))


class VolumeSnapshotsTable(volume_tables.VolumesTableBase):
    name = tables.Column("display_name",
                         verbose_name=_("Name"),
                         link="horizon:hpcloud:images_and_snapshots:detail")
    volume_name = SnapshotVolumeNameColumn("display_name",
                              verbose_name=_("Volume Name"),
                              link="horizon:hpcloud:volumes:detail")

    class Meta:
        name = "volume_snapshots"
        verbose_name = _("Volume Snapshots")
        table_actions = (DeleteVolumeSnapshot,)
        row_actions = (CreateVolumeFromSnapshot, DeleteVolumeSnapshot)
        row_class = UpdateRow
        status_columns = ("status",)
