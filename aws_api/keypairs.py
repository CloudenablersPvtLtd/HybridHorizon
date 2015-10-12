'''
Created on 19-Mar-2014

@author: annamalai
'''
from connection import AWS

class StructKeypairs():
    def __init__(self, id, region, fingerprint):
        self.region = region
        self.id = id
        self.fingerprint = fingerprint

class KeyPairs(AWS):
    
    def get_key_pairs(self):
        keypair_list = []
        if self.client:
            keypairs= self.client.get_all_key_pairs()
            for keypair in keypairs:
                keypair_list.append(StructKeypairs(keypair.name,keypair.region.name,keypair.fingerprint))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return keypair_list
    
    def create_keypairs(self, name):
        if self.client:
            key_pair = self.client.create_key_pair(name)
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return key_pair
    
    def keypair_download(self,name):
        keypair = []
        if self.client:
            keypair = self.client.get_all_key_pairs(keynames = str(name))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return keypair

    def delete_keypair(self,name):
        if self.client:
            key_pair = self.client.delete_key_pair(key_name = name)
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return key_pair
