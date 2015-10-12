import httplib2
import json
import requests
import logging
import time
import cloud_mongo.trail

LOG = logging.getLogger(__name__)

class Provider():
    def __init__(self,provider):
        self.provider = provider
        
class Pro_Reg():
    def __init__(self,provider,region,action):
        self.provider = provider
        self.region =region
        self.action = action


def providers(request):
    pro_obj_list = []
    provider_obj_list = []
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    for role in request.user.roles:
        if role.roletype == "Tenant Admin":
            url = endpoint + "/api/resourceQuery/region/distinct/provider"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            msg = "Provider Listing status %s" %resp.status_code
            LOG.debug(msg)
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    provider_obj_list.append(Provider(elem))
            return provider_obj_list
        else:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    pro_obj_list.append(policy.provider.title())
                else:
                    pass
    pro_obj_list = list(set(pro_obj_list))
    for x in pro_obj_list:
        provider_obj_list.append(Provider(x))
    return provider_obj_list    
    
def provider_image(request,uri):
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        url = endpoint + '/api/resourceQuery/capabilities' + uri
        httpInst.add_credentials(name=credential_username,password=credential_password)
        time.sleep(1)
        resp, b = httpInst.request(url)
        b=json.loads(b)
        if resp.get('status') == '200' and b:
            if b['createImageSupported'] == "true":
                return True
            else:
                return False
             
             
def provider_region(request,provider_list):
        pro_reg_list = []
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        for provider in provider_list:
            url = endpoint + ':8888/region/provider/' + provider
            httpInst.add_credentials(name=credential_username,password=credential_password)
            resp, b = httpInst.request(url)
            b=json.loads(b)
            if resp.get('status') == '200' and b:
                for elem in b:
                    pro_reg_list.append(Pro_Reg(str(provider.lower()),str(elem['Name'].lower()), elem['supportedActions']))

        return pro_reg_list
