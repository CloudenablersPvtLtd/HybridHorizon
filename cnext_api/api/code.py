import httplib2
import json
import time

import requests
import cloud_mongo.trail

class InstImage():
    def __init__(self, name, provider, region,  platform, \
                 description, cost, os, uri, ids,min_conf = None):
        self.name = name
        self.provider = provider
        self.region = region
        self.min_conf = min_conf
        self.platform = platform
        self.description = description
        self.uri = uri
        self.id = ids
        self.cost = cost
        self.os = os


class Inst():
    def __init__(self, name, cpuCount, ram, localStorage, provider, region, \
                 location, ids, uri, cost):
        self.name = name
        self.provider = provider
        self.location = location
        self.region = region
        self.id = ids
        self.cpuCount = cpuCount
        self.ram = ram
        self.localStorage = localStorage
        self.uri = uri
        self.cost = cost


class Instances():
    def __init__(self, name, ids, provider, region, status,uri):
        self.id = ids
        #self.instanceId = instanceId
        self.provider = provider
        self.region = region
        self.name = name
        self.status = status
        self.uri = uri


def image_detail(request,image_id):
    httpInst = httplib2.Http()
    cnext_url = request.user.cnextendpoint
    url = cnext_url + ":5902/apiv1.0/resource/"+image_id
    resp, body = httpInst.request(url)
    body = json.loads(body)
    return body

def inst_detail(request,inst_id):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    cnext_url = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, password = credential_password)
    url = cnext_url + "/api/instance/"+inst_id
    resp, body = httpInst.request(url)
    time.sleep(1)
    body = json.loads(body)
    return body


def instances(request):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        pro_reg_list =[]
        pro_reg_list = [[(policy.provider,policy.region) for policy in role.policy] for role in request.user.roles] 
        pro_reg_list[0] = set(pro_reg_list[0])
        pro_reg_list[0] = list(pro_reg_list[0])
        vm = []
        if ("ALL","ALL") in pro_reg_list[0]:        
            url =   endpoint +"/api/instance?resourceType=vm"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    if 'uri'  in elem['parameters']:
                        elem["parameters"]["uri"] = elem["parameters"]["uri"]
                    else:
                        elem["parameters"]["uri"] = elem["parameters"]["imageUri"]
                        
                    if (elem["attributes"]["instanceStatus"] !="deleted"):
                        vm_dict = Instances(elem['metadata']['name'], \
                                        elem['instanceId'], elem['provider'], \
                                        elem['region'], elem["attributes"]["instanceStatus"],elem["parameters"]["uri"])
                        vm.append(vm_dict)
                    else:
                        pass
            else:
                vm = []
            return vm
        else:
            for param in pro_reg_list[0]:
                url = endpoint + "/api/instance?resourceType=vm&&provider="+str(param[0]).lower()+"&&region="+str(param[1]).lower()
                resp = requests.get(url=url, auth=(credential_username, credential_password))
                body = resp.json()
                if resp.status_code == 200 and body:
                    for elem in body:
                        if 'uri'  in elem['parameters']:
                            elem["parameters"]["uri"] = elem["parameters"]["uri"]
                        else:
                            elem["parameters"]["uri"] = elem["parameters"]["imageUri"]
                        if (elem["attributes"]["instanceStatus"] !="deleted"):
                            vm_dict = Instances(elem['metadata']['name'], \
                                        elem['instanceId'], elem['provider'], \
                                        elem['region'], elem["attributes"]["instanceStatus"],elem["parameters"]["uri"])
                            vm.append(vm_dict)
                        else:
                            pass
                else:
                    pass
            return vm 
        
    except Exception, e:
        print "exception", e
        vm = []
    return vm


def instances_list(request):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        httpInst = httplib2.Http()
        cnext_url =request.user.cnextendpoint
        httpInst.add_credentials(name = credential_username, password = credential_password)
        url = cnext_url + "/api/resourceQuery/query/instanceType"
        resp, body = httpInst.request(url)
        body = json.loads(body)
        instances = []
        if resp.get('status') == '200' and body:
            for elem in body:
                if 'options' in elem:
                    elem['cpuCount'] = elem['options']['cpuCount']['label']
                    elem['ram'] = elem['options']['ram']['label']
                    elem['localStorage'] = elem['options']['localStorage']['label']
                else:
                    elem['cpuCount'] = elem['cpuCount']
                    elem['ram'] = elem['ram']
                    elem['localStorage'] = elem['localStorage']
                inst_dict = Inst(elem['name'], elem['cpuCount'], \
                                     elem['ram'], elem['localStorage'], \
                                     str(elem['provider']).lower(), str(elem['region']).lower(), \
                                     elem['location'], elem['id'], elem['uri'], \
                                     elem["costPerUnit"]  + elem["costUnit"])
                instances.append(inst_dict)
        else:
            instances.append({'Name': '', 'CPU Count': '',
                              'RAM': '', 'LocalStorage': '', 'Provider': '',
                              'Location': '', 'Id': ''})
    except:
        instances = []
    return instances


def launch_instance(request, uri, image_uri, name, keypair, securitygroup):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, password = credential_password)
        url = endpoint + "/api/resource/" + uri
        h = {"content-type": "application/json"}
        if not keypair and not securitygroup :
            b = {"uri": uri, "imageUri": image_uri,
                "metadata": {"name": name,
                         "description": "my first virtual machine"
                         }
                }
            
        else:
            b = {"uri": uri, "imageUri": image_uri,
              "keyPairId" : keypair,
              "securityGroupIds" : securitygroup,
              "metadata": {"name": name,
                         "description": "my first virtual machine"
                         }
             }
        b = json.dumps(b)
        time.sleep(1)
        resp, body = httpInst.request(url, method = "POST", body = b, headers = h)
        time.sleep(1)
        dd = json.loads(body)
        a = dd["requestId"]
        acount = 0
        def check_call(endpoint,reqid):
            url =endpoint +'/api/request/' + reqid
            resp, body = httpInst.request(url)
            body = json.loads(body)
            return body
        body =  check_call(endpoint,a)
        while (body[0]["requestStatus"] != "completed" ):
            print body[0]
            if (body[0]["requestStatus"] == "failed"):
                return False
            else:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        time.sleep(1)
        refresh(request,body[0]["instanceId"])
        return True
    except Exception , e:
        print "exception",e
        return False


def validate(request, body):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                             password = credential_password)
    url = endpoint + "/api/resourceQuery/validate"
    h = {"content-type": "application/json"}
    body = json.dumps(body)
    resp, body1 = httpInst.request(url, method = "POST",body = body,headers = h)
    return resp.get('status')


def start(request,instance):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                             password = credential_password)
    h = {"content-type": "application/json"}
    url = endpoint + "/api/instance/" + instance
    resp, body = httpInst.request(url)
    body = json.loads(body)
    a = body["metadata"]
    b = {
           "uri" : body["parameters"]["uri"],
           "imageUri" : body["parameters"]["imageUri"],
           "metadata" : a
           }

    b = json.dumps(b)
    time.sleep(1)
    url = endpoint + "/api/instance/" + instance + "?action=start"
    resp, body = httpInst.request(url, method = "PUT", body = b ,headers = h)
    body = json.loads(body)
    a = body['requestId']
    acount = 0
    def check_call(endpoint,reqid):
        url =endpoint +'/api/request/' + reqid
        resp, body = httpInst.request(url)
        body = json.loads(body)
        return body
    time.sleep(1)
    body =  check_call(endpoint,a)
    while (body[0]["requestStatus"] != "completed" ):
            time.sleep(1.5)
            body = check_call(endpoint,body[0]['requestId'])
            acount += 1
    time.sleep(1)
    refresh(request,instance)
    
def stop(request,instance):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                             password = credential_password)
    h = {"content-type": "application/json"}
    url = endpoint + "/api/instance/" + instance
    resp, body = httpInst.request(url)
    body = json.loads(body)
    a = body["metadata"]
    b = {
           "uri" : body["parameters"]["uri"],
           "imageUri" : body["parameters"]["imageUri"],
           "metadata" : a
           }

    b = json.dumps(b)
    time.sleep(1)
    url = endpoint + "/api/instance/" + instance + "?action=stop"
    resp, body = httpInst.request(url, method = "PUT", body = b ,headers = h)
    body = json.loads(body)
    a = body['requestId']
    acount = 0
    def check_call(endpoint,reqid):
        url =endpoint +'/api/request/' + reqid
        resp, body = httpInst.request(url)
        body = json.loads(body)
        return body
    time.sleep(1)
    body =  check_call(endpoint,a)
    while (body[0]["requestStatus"] != "completed" ):
            time.sleep(1.5)
            body = check_call(endpoint,body[0]['requestId'])
            acount += 1
    time.sleep(1)
    refresh(request,instance)


def delete(request,instance):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                             password = credential_password)
    url=endpoint + '/api/instance/' + str(instance)
    resp, body = httpInst.request(url,method = "DELETE")
    body = json.loads(body)
    a = body['requestId']
    acount = 0
    def check_call(endpoint,reqid):
        url =endpoint +'/api/request/' + reqid
        resp, body = httpInst.request(url)
        body = json.loads(body)
        return body
    time.sleep(1)
    body =  check_call(endpoint,a)
    while (body[0]["requestStatus"] != "completed" ):
            time.sleep(1.5)
            body = check_call(endpoint,body[0]['requestId'])
            acount += 1
    time.sleep(1)
    refresh(request,instance)
  

def refresh(request,instance):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
                             password = credential_password)
    url=endpoint + "/api/instance/" + instance + "?refresh=true"
    resp, body = httpInst.request(url)
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
            time.sleep(1.5)
            body = check_call(endpoint,body[0]['requestId'])
            acount += 1
