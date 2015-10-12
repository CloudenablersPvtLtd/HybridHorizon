'''
Created on 12-Nov-2013

@author: ganesh
'''

import httplib2
import json
import time
import requests
import logging
import cloud_mongo.trail

LOG = logging.getLogger(__name__)

class Keypairs():
    def __init__(self, instanceId, provider, region,\
                 name, fingerprint, privatekey,status):
        self.id = instanceId
        self.provider = provider
        self.region = region
        self.name = name
        self.fingerprint = fingerprint
        self.privatekey = privatekey
        self.status = status


def keypairs(request):
    key_pairs = []
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        pro_reg_list =[]
        pro_reg_list = [[(policy.provider,policy.region) for policy in role.policy] for role in request.user.roles] 
        pro_reg_list[0] = set(pro_reg_list[0])
        pro_reg_list[0] = list(pro_reg_list[0])
        key_pairs = []
        if ("ALL","ALL") in pro_reg_list[0]:        
            url = endpoint + "/api/instance?resourceType=kp"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            LOG.debug("keypair Listing status %s" % resp.status_code )
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    if (elem["attributes"]["instanceStatus"] !="deleted"):
                        key_dict = Keypairs(elem['instanceId'], \
                                            str(elem['provider']).lower(),str(elem['region']).lower(), \
                                            elem['metadata']['name'], \
                                            elem['attributes']['keyFingerprint'], \
                                            elem['attributes']['privateKey'], \
                                            elem["attributes"]["instanceStatus"])
                        key_pairs.append(key_dict)
                    else:
                        pass
            else:
                key_pairs = []

            return key_pairs

        else:
            for param in pro_reg_list[0]:
                url = endpoint + "/api/instance?resourceType=kp&&provider="+str(param[0]).lower()+"&&region="+str(param[1]).lower()
                resp = requests.get(url=url, auth=(credential_username, credential_password))
                body = resp.json()
                if resp.status_code == 200 and body:
                    for elem in body:
                        if (elem["attributes"]["instanceStatus"] !="deleted"):
                            key_dict = Keypairs(elem['instanceId'], \
                                                str(elem['provider']).lower(),str(elem['region']).lower(), \
                                                elem['metadata']['name'], \
                                                elem['attributes']['keyFingerprint'], \
                                                elem['attributes']['privateKey'], \
                                                elem["attributes"]["instanceStatus"])
                            key_pairs.append(key_dict)
                        else:
                            pass
                else:
                    pass
            return key_pairs   
    except Exception, e:
        print "keypair listing exveption", e
        key_pairs = []
    return key_pairs   


def create_keypairs(request, name,  provider, region):
    key_pairs = []
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
        url = endpoint + "/api/resource/kp/" + provider + "/" + region + "/standard"
        b = {"metadata": {
                 "name":name,
                 "description": "Keypair Response time"
                 }
            }
        b = json.dumps(b)
        h = {"content-type": "application/json"}
        resp, body = httpInst.request(url,method="POST",body = b,headers = h)
        time.sleep(3)
        dd = json.loads(body)
        a = dd["requestId"]
        
        def check_call(reqid, url):
            url = endpoint + "/api/request/" + reqid
            resp, body = httpInst.request(url)
            body = json.loads(body)[0]
            return body
            
        body = check_call(a, url)
        acount = 0
        while (body["requestStatus"] != "completed"):
            time.sleep(1)
            body = check_call(a, url)
            acount += 0
        
        LOG.debug(acount)
        if resp.get('status') == '200' and body:
            key_dict = Keypairs(body["parameters"]['instanceId'], \
                                        body['provider'], body['region'], \
                                        body['metadata']['name'], \
                                        body['results']['keyFingerprint'], \
                                        body['results']['privateKey'], \
                                        body['results']['instanceStatus'])           
            key_pairs.append(key_dict)
            return key_pairs
        else:
            raise Exception
    # check if request succeeded by checking response code
    except Exception,e:
        print e
        key_pairs.append({'name':'', 'privatekey':''})
        return key_pairs
                                                       
def delete_keypair(request,instanceid):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    
    url=endpoint + "/api/instance/"+instanceid
    h = {"content-type": "application/json"}

    resp = requests.delete(url, headers = h, auth=(credential_username, credential_password))
    LOG.debug("Delete keypair"),LOG.debug(resp.status_code)

def get_accounts(request):
    accounts_list = []
    try:
        aws_clouds = sum([[y.cloudid for y in i.policy if 
                            y.cloudid.platform == 'Cnext'] for i in request.user.roles], [])
        for cloud in aws_clouds:
            if cloud.name != request.user.cnextname:
                accounts_list.append((cloud.id,cloud.name))
    except Exception ,e:
        print e
        return accounts_list
    return accounts_list
    
