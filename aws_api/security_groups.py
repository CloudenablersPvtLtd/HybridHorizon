"""
Created on 20-Mar-2014

@author: narenthirasamy
"""
from django.utils.translation import ugettext_lazy as _
import boto.vpc
from cloud_mongo.trail import encode_decode
from connection import AWS

class StructSecurityGroups():
    def __init__(self, id, name, vpc_id, description, rules):
        self.name = name
        self.id = id
        self.vpc_id = vpc_id
        self.rules = rules
        self.description = description
        
class SecurityGroups(AWS):
    
    def get_security_groups(self):
        security_list = []
        if self.client:
            securities = self.client.get_all_security_groups()
            for security in securities:
                rule_count = 0
                for rule in security.rules:
                    rule_count = rule_count + 1
                security_list.append(StructSecurityGroups(security.id,
                                                security.name,
                                                security.vpc_id,
                                                security.description,
                                                str(rule_count) +
                                                "  Permissions"))
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return security_list
    
    def create_security_groups(self, name, desp, vpc_id):
        if self.client:
            sg = self.client.create_security_group(name=name, description=desp,
                                         vpc_id=vpc_id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return sg
    
    def delete_sg(self, id):
        if self.client:
            self.client.delete_security_group(group_id=id)
        else:
            raise Exception("Unable to connect " + self.awscloud)
    
    def add_rules_security_groups(self, id, from_port, to_port,
                                  cidr, protocol_list):
        if self.client:
            self.client.authorize_security_group(group_id=id,
                                               from_port=from_port,to_port=to_port,
                                               ip_protocol=cidr,cidr_ip=protocol_list)
        else:
            raise Exception("Unable to connect " + self.awscloud)

    def security_group_details(self, id):
        if self.client:
            sec_group_list = self.client.get_all_security_groups(group_ids=id)
            return sec_group_list[0]
        else:
            raise Exception("Unable to connect " + self.awscloud)
            return None
    
    def get_rules(self,id):
        if self.client:
            sg = self.client.get_all_security_groups(group_ids = id)
            return sg
        else:
            raise Exception("Unable to connect " + self.awscloud)
 
    def delete_rule(self,sg_id,from_port,to_port,protocol,cidr):
        if self.client:
            sg = self.client.revoke_security_group(group_id = sg_id,ip_protocol=protocol, from_port=from_port, to_port=to_port,cidr_ip = cidr )
        else:
            raise Exception("Unable to connect " + self.awscloud)

def get_vpc_id(request):
    vpc_list = []
    try:
        client = boto.vpc.VPCConnection(
            aws_access_key_id=request.user.awspublickey,
            aws_secret_access_key=encode_decode(request.user.awsprivatekey,"decode"))
        vpc = client.get_all_internet_gateways()
        client.close()
        if len(vpc) > 1:
            vpc_list.append((str(vpc[0].attachments[0].vpc_id),
                             str(vpc[0].attachments[0].vpc_id)))
            vpc_list.insert(0, ("", _("Select VPC ID")))
        else:
            vpc_list.insert(0, ("", _("No VPC Available")))
    except Exception, e:
        raise Exception(e.message)
    return vpc_list