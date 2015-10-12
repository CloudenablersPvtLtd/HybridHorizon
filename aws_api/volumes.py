'''
Created on 20-Mar-2014

@author: annamalai
'''
from connection import AWS

class StructVolumes():
    def __init__(self, id ,name,region,zone,create_time,type,size,status):
        self.region = region
        self.id = id
        self.zone = zone
        self.create_time = create_time
        self.type = type
        self.size = size
        self.name = name
        self.status = status

class Volumes(AWS):
    
    def get_volumes(self):
        volume_list = []
        if self.client:
            volumes= self.client.get_all_volumes()
            for volume in volumes:
                if 'Name' in volume.tags:
                    name = volume.tags['Name']
                else:
                    name = " "          
                volume_list.append(StructVolumes(volume.id,name,volume.region.name,volume.zone,volume.create_time,volume.type,volume.size,volume.status))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return volume_list

    def delete_volumes(self,ids):
        if self.client:
            self.client.delete_volume(volume_id = ids)
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def get_instance_for_volume(self,zone):
        instance_list = []
        if self.client:
            instancess= self.client.get_all_instances()
            for instance in instancess:
                elem = instance.instances[0] 
                if elem.state == "stopped" or elem.state == "running":
                    if str(elem._placement) == str(zone):
                        if "Name" in elem.tags:
                            instance_list.append((elem.id,elem.id + " - " + elem.tags["Name"]))
                        else:
                            instance_list.append((elem.id,elem.id))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return instance_list

    def attach_volume(self,inst_id,vol_id,device):
        if self.client:
            return self.client.attach_volume(volume_id = str(vol_id) ,
                                           instance_id = str(inst_id),device = str(device))
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None

    def detach_volumes(self,vol_id):
        if self.client:
            volume = self.client.get_all_volumes(volume_ids = vol_id)
            self.client.detach_volume(str(vol_id),str(volume[0].attach_data.instance_id))
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def get_volume_detail(self,vol_id):
        if self.client:
            volume = self.client.get_all_volumes(volume_ids = vol_id)
            return volume
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
    
    def create_snapshot(self,volume_id,description,snapshot_name):
        if self.client:
            status = self.client.create_snapshot(volume_id= volume_id, description= description)
            self.client.create_tags(resource_ids = [str(status.id)], tags = {"Name":str(snapshot_name)})
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def create_volume(self,size,zone,volume_type,iops,name):
        if self.client:
            status = self.client.create_volume(size = size,zone = zone,volume_type = volume_type,iops = iops)
            self.client.create_tags(resource_ids = [str(status.id)], tags = {"Name":name})
        else:
            raise Exception("Unable to connect " + self.awscloud)
