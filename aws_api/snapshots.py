from connection import AWS

class StructSnapshots():
    def __init__(self, id, name, description, size, starttime, region, status, progress, volumeid):
        self.region = region
        self.id = id
        self.name = name
        self.status = status
        self.description = description
        self.size = size
        self.starttime = starttime
        self.progress = progress
        self.volumeid = volumeid

class Snapshots(AWS):
    
    def get_snapshots(self):
        snapshots_list = []
        if self.client:
            snapshots = self.client.get_all_snapshots(owner='self')
            for snapshot in snapshots:
                if 'Name' in snapshot.tags:
                    name = snapshot.tags['Name']
                else:
                    name = " "          
                snapshots_list.append(StructSnapshots(snapshot.id, name, snapshot.description, snapshot.volume_size, snapshot.start_time , snapshot.region.name, snapshot.status, snapshot.progress,snapshot.volume_id))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return snapshots_list

    def delete_snapshots(self,ids):
        if self.client:
            self.client.delete_snapshot(snapshot_id = ids)
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def get_snapshot_detail(self,snapshot_id):
        if self.client:
            snapshot = self.client.get_all_snapshots(snapshot_ids = snapshot_id)
            return snapshot
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return None

    def get_volumes(self):
        if self.client:
            volumes = self.client.get_all_volumes()
            return volumes
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def create_volume(self,snapshot_id,zone,volume_name,volume_type,size,iops):
        if self.client:
            status = self.client.create_volume(size= int(size), zone= str(zone), snapshot= str(snapshot_id), volume_type= str(volume_type), iops=iops)
            self.client.create_tags(resource_ids = [str(status.id)], tags = {"Name":str(volume_name)})
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def copy_snapshot(self,snapshot_id,region,description):
        if self.client:
            status = self.client.copy_snapshot(source_region = str(region),
                                             source_snapshot_id=str(snapshot_id),
                                             description=str(description))
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def create_snapshot(self,volume_id,description,name):
        if self.client:
            status = self.client.create_snapshot(volume_id = volume_id,description = description)
            self.client.create_tags(resource_ids = [str(status.id)], tags = {"Name":name})
        else:
            raise Exception("Unable to connect " + self.awscloud)
