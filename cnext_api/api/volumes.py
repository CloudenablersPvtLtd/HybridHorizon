import httplib2
import json
import time
import requests
from cnext_api.api import code
import logging
import cloud_mongo.trail
LOG = logging.getLogger(__name__)


class Volume:
    def __init__(self,emp_id=None,volume_name=None,size=None,instanceid=None,provider=None,region=None,status=None):
        self.id = emp_id
        self.volume_name=volume_name
        self.size=size
        self.name = instanceid
        self.provider= provider
        self.region= region
        self.status = status 

def volume_create(request,no,name,description,provider,region):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")  
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
    h = {"content-type": "application/json"}
    b={"sizeInGBytes": int(no), "metadata" : {"name":name,"description" : description}}
    b=json.dumps(b)
    url=endpoint + "/api/resource/vs/"+str(provider).lower()+"/"+str(region).lower()+"/standard.50"
    resp, body = httpInst.request(url, method = "POST", body = b, headers = h)
    LOG.debug("Inside Volume Create Status %s" % resp.status)
    time.sleep(3)
    if resp.status == 200:
        dd=json.loads(body)
        a = dd["requestId"]
        def check_call(reqid, url):
                url = endpoint + "/api/request/" + a
                resp, body = httpInst.request(url)
                body = json.loads(body)[0]
                return body            
        body = check_call(a, url)
        acount = 0
        while (body["requestStatus"] != "completed"):
            if body["requestStatus"] == "failed":
                return False
            else:
                time.sleep(1)
                body = check_call(a, url)
                acount += 0
        return True
    else:
        return False

def volumelist(request):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, \
                                     password = credential_password)
        pro_reg_list =[]
        pro_reg_list = [[(policy.provider,policy.region) for policy in role.policy] for role in request.user.roles] 
        pro_reg_list[0] = set(pro_reg_list[0])
        pro_reg_list[0] = list(pro_reg_list[0])
        volumes = []
        if ("ALL","ALL") in pro_reg_list[0]:
            url=endpoint + "/api/instance?resourceType=vs"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            LOG.debug("Inside Volume list Status %s" % resp.status_code)
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    if (elem["attributes"]["instanceStatus"] != "deleted"):
                        volumes.append(Volume(elem['instanceId'],elem['metadata']['name'],elem['parameters']['sizeInGBytes'],\
                                              elem['instanceId'],elem['provider'],elem['region'],elem['attributes']['instanceStatus']))
                    else:
                        pass                              
            else:
                volumes = []
            return volumes
        else:
            print pro_reg_list
            for param in pro_reg_list[0]:
                url = endpoint + "/api/instance?resourceType=vs&&provider="+str(param[0]).lower()+"&&region="+str(param[1]).lower()
                resp = requests.get(url=url, auth=(credential_username, credential_password))
                body = resp.json()
                if resp.status_code == 200 and body:
                    for elem in body:
                        if (elem['attributes']['instanceStatus']!='deleted'):
                            volumes.append(Volume(elem['instanceId'],elem['metadata']['name'],elem['parameters']['sizeInGBytes'],\
                                                  elem['instanceId'],elem['provider'],elem['region'],"active"))
                        else:
                            pass                       
                else:   
                    volumes = []
            return volumes
    except Exception, e:
        print "volume listing exveption", e
        volumes = []
    return volumes   


def delete_volume(request,instanceid):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode") 
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                                     password = credential_password)
    url=endpoint + "/api/instance/"+instanceid
    resp, body = httpInst.request(url, method = "DELETE")
    LOG.debug("Inside  Delete Volume  Status %s" % resp.status)
    if resp.status == 200:
        time.sleep(2)
        body = json.loads(body)
        a = body['requestId']
        acount = 0
        def check_call(endpoint,reqid):
            url =endpoint +'/api/request/' + reqid
            resp, body = httpInst.request(url)
            body = json.loads(body)
            return body
        body =  check_call(endpoint,a)
        while (body[0]["requestStatus"] != "completed" ):
            if (body[0]["requestStatus"] == "failed"):
                    return False
            else:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        time.sleep(1)
        code.refresh(request,instanceid)
        return True
    else:
        return False
    
    
def attach_to_vm(request,instanceid,vmid,name):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
           
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, \
                                     password = credential_password)
        h = {"content-type": "application/json"}
        body={"virtualMachineId":vmid,"deviceName":name}
        b=json.dumps(body)
        url=endpoint + "/api/instance/"+instanceid+"?action=attach"
        resp, body = httpInst.request(url, method = "PUT", body = b, headers = h)
        LOG.debug("Inside Volume attach Status %s" % resp.status)
        if resp.status == 200:
            dd = json.loads(body)
            acount = 0
            a = dd["requestId"]
            def check_call(endpoint,reqid):
                url =endpoint +'/api/request/' + reqid
                resp, body = httpInst.request(url)
                body = json.loads(body)
                return body
            time.sleep(1)
            body =  check_call(endpoint,a)
            while (body[0]["requestStatus"] != "completed"):
                if (body[0]["requestStatus"] == "failed"):
                    return False
                else:
                    time.sleep(1.5)
                    body = check_call(endpoint,body[0]['requestId'])
                    acount += 1
            return True
        else:
            pass
    except Exception ,e:
        print e
        return False
    
def dettach(request,instanceid,vmid,device):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode") 
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, \
                                     password = credential_password)  
        h = {"content-type": "application/json"}
        body={"virtualMachineId":vmid,"deviceName":device}
        b=json.dumps(body)
        url=endpoint + "/api/instance/"+instanceid+"?action=detach"
        time.sleep(1)
        resp, body = httpInst.request(url, method = "PUT", body = b, headers = h)
        LOG.debug("Inside Volume Detach Status %s" % resp.status)
        dd = json.loads(body)
        acount = 0
        a = dd["requestId"]
        def check_call(endpoint,reqid):
            url =endpoint +'/api/request/' + reqid
            resp, body = httpInst.request(url)
            body = json.loads(body)
            return body
        time.sleep(1)
        body =  check_call(endpoint,a)
        while (body[0]["requestStatus"] != "completed" ):
            if (body[0]["requestStatus"] == "failed"):
                return False
            else:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        time.sleep(1)
        code.refresh(request,instanceid)
        return True
    except:
        print "inside exception of attach to vm api call"
        return False


def choices(request,provider,region):
    httpInst = httplib2.Http()
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    
    httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
    
    endpoint = request.user.cnextendpoint
    url=endpoint + "/api/instance?resourceType=vm"
    h = {"content-type": "application/json"}
    resp, body = httpInst.request(url, method = "GET", headers = h)
    LOG.debug("Inside Instance list for volume attachment Status %s" % resp.status)
    dd=json.loads(body)
    choices=[]
    volume_choices=[]
    for i in dd:
        if i['provider']==provider:
            if i['region']==region:
                if i["attributes"]["instanceStatus"] !="deleted":
                    volume_choices=[i['instanceId'],i['instanceId']]
                    choices.append(volume_choices)
                else:
                    print "Deleted Instances"
            else:
                print "Different Regions"
        else:
            print "Different parameters"

    return choices

def volume_dettach(request,instanceid):
    h = {"content-type": "application/json"}
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
    url=endpoint + "/api/instance/"+instanceid
    resp, body = httpInst.request(url, method = "GET", headers = h)
    LOG.debug("Inside detach VM id getting Status %s" % resp.status)
    dd=json.loads(body)
    return dd['attributes']['virtualMachineId']


def instance(request,instanceid):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
    h = {"content-type": "application/json"}
    url=endpoint +"/api/instance/"+instanceid
    resp, body = httpInst.request(url, method = "GET", headers = h)
    time.sleep(1)
    LOG.debug("Inside Volume detail Status %s" % resp.status)
    dd=json.loads(body)
    return dd
