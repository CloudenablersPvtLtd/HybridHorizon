'''
Created on 19-Mar-2014

@author: annamalai
'''
from connection import AWS

class StructInstances():
    def __init__(self, name, ids, imageid, region,zone, status):
        self.id = ids
        self.imageid = imageid
        self.region = region
        self.name = name
        self.status = status
        self.zone = zone

class Instances(AWS):
    
    def get_instances(self):
        instance_list = []
        if self.client:
            instances= self.client.get_all_instances()
            for instance in instances:
                elem = instance.instances[0]
                if 'Name' in elem.tags:
                    name = elem.tags['Name']
                else:
                    name = " "              
                instance_list.append(StructInstances(name,elem.id,elem.image_id,elem.region.name,elem._placement, elem.state))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return instance_list
    
    def start_instances(self,inst_id):
        if self.client:
            self.client.start_instances(instance_ids = inst_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def stop_instances(self,inst_id):
        if self.client:
            self.client.stop_instances(instance_ids = inst_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def terminate_instances(self,inst_id):
        if self.client:
            self.client.terminate_instances(instance_ids = inst_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def refresh_instances(self,inst_id):
        if self.client:
            self.client.get_all_instances(instance_ids = inst_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def instance_detail(self,inst_id):
        if self.client:
            status = self.client.get_all_instances(instance_ids = inst_id)
            return status[0].instances[0]
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def launch_instances(self,image_id,max_count,placement,key_name,security_groups,name,instance_type):
        if self.client:
            status = self.client.run_instances(image_id = image_id,\
                                             max_count = max_count,placement = placement,\
                                             key_name = key_name,security_groups = security_groups,\
                                             instance_type = instance_type)
            self.client.create_tags(resource_ids = [status.instances[0].id], tags = {"Name":name})
        else:
            raise Exception("Unable to connect " + self.awscloud)

def get_accounts(request):
    accounts_list = []
    aws_clouds = sum([[y.cloudid for y in i.policy if 
                       y.cloudid.platform == 'Amazon'] for i in request.user.roles], [])
    for cloud in aws_clouds:
        if cloud.name != request.user.awsname:
            accounts_list.append((cloud.id,cloud.name))
    return accounts_list
