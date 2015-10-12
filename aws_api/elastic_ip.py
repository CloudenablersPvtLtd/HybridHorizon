'''
Created on 15-Apr-2014

@author: narenthirasamy
'''
from connection import AWS

class StructElasticIP():
    def __init__(self, id, instance_id, private_ip_address, domain, region):
        self.id = id
        self.instance_id = instance_id
        self.private_ip_address = private_ip_address
        self.domain = domain
        self.region = region

class ElasticIPs(AWS):
    
    def get_addresses(self):
        address_list = []
        if self.client:
            addresses = self.client.get_all_addresses()
            for address in addresses:
                address_list.append(StructElasticIP(address.public_ip,address.instance_id,address.private_ip_address,address.domain,address.region.name))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return address_list
    
    def create_address(self,eip):
        if self.client:
            if eip == "ec2":            
                address = self.client.allocate_address(domain=None)
            else:
                address = self.client.allocate_address(domain=eip)
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
        return address
    
    def release_ip(self,id):
        if self.client:
            address = self.client.get_all_addresses(addresses=id)
            if str(address[0].domain) == 'standard':
                var = self.client.release_address(public_ip=id)
                return var 
            else:
                var = self.client.release_address(public_ip=None, allocation_id=str(address[0].allocation_id))
                return var
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
    
    def associate_addr(self, id, inst_id):
        if self.client:
            na = self.client.associate_address(public_ip=id,
                               instance_id=inst_id)
            return na
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
    
    def get_instance_ids(self,domain):
        ids_list = []
        if self.client:
            ids = self.client.get_only_instances()
            for id_list in ids:
                if domain == "standard" and id_list.vpc_id == None and (id_list.state == "running" or id_list.state == "stopped"):
                    ids_list.append((id_list.id,id_list))
                elif domain == "vpc" and id_list.vpc_id != None and (id_list.state == "running" or id_list.state == "stopped"):
                    ids_list.append((id_list.id,id_list))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return ids_list
    
    def disassociate_ip(self,id):
        if self.client:
            address = self.client.get_all_addresses(addresses=id)
            if str(address[0].domain) == 'standard':
                dis_add = self.client.disassociate_address(public_ip=id)
                return dis_add
            else:
                dis_add = self.client.disassociate_address(public_ip=None, allocation_id=str(address[0].allocation_id))
                return dis_add
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None

    def elastic_ip_details(self, id):
        if self.client:
            elastic_ip_list = self.client.get_all_addresses(addresses=id)
            return elastic_ip_list[0]
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
