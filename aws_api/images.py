'''
Created on 25-Mar-2014

@author: annamalai
'''

from connection import AWS

class StructImages():
    def __init__(self,ids,platform,state,region,name,ownerid,is_public,kernel_id,root_device_name,architecture,virtualization_type,root_device_type):
        self.id = ids
        self.platform = platform
        self.region = region
        self.name = name
        self.state = state
        self.ownerid = ownerid
        self.is_public = is_public
        self.kernel_id = kernel_id
        self.root_device_name = root_device_name
        self.architecture = architecture
        self.virtualization_type = virtualization_type
        self.root_device_type = root_device_type

class Images(AWS):
    
    def get_images(self,flag):
        images_list = []
        if self.client:
            images= self.client.get_all_images(owners = [flag])
            for image in images:
                if image.type == 'machine':
                    images_list.append(StructImages(image.id,image.platform,image.state,image.region.name, image.name,image.ownerId,image.is_public,image.kernel_id,image.root_device_name,image.architecture,image.virtualization_type,image.root_device_type))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return images_list
    
    def get_images_detail(self,image_id):
        if self.client:
            return self.client.get_all_images(image_ids = image_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
