'''
Created on 12-Nov-2013

@author: ganesh
'''
import httplib2
import json
import time
import logging
import cloud_mongo.trail

LOG = logging.getLogger(__name__)

class Security():
    def __init__(self, instanceId,name,description,status,provider,region,rules):
        self.id = instanceId
        self.status = status
        self.provider = provider
        self.region = region
        self.name = name
        self.description = description
        self.rules = rules


class Securitys():
    def __init__(self,instanceid,from_port,to_port, cidr_ip, protocol):
        self.id = instanceid
        self.from_port = from_port
        self.to_port  = to_port 
        self.cidr_ip = cidr_ip
        self.protocol = protocol

def securitygroups(request):
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
        security_group = []
        if ("ALL","ALL") in pro_reg_list[0]:
            time.sleep(2)
            url=endpoint + "/api/instance?resourceType=sg"   
            resp, body = httpInst.request(url) 
            LOG.debug("Security Group Listing status %s" % resp.get('status'))
            body = json.loads(body)
            security_group = []
            if resp.get('status') == '200' and body:
                for elem in body:
                    if "rules" in elem["attributes"]:
                        elem['attributes']['rules'] = elem['attributes']['rules']
                    else:
                        elem['attributes']['rules'] = []
                    if "description" in elem["metadata"]:
                        elem['metadata']['description'] = elem['metadata']['description']
                    else:
                        elem['metadata']['description'] = ""
                    if (elem["attributes"]["instanceStatus"] != "deleted"):                            
                        sg_dict = Security(elem['instanceId'], \
                                           elem['metadata']['name'],\
                                           elem['metadata']['description'],\
                                           elem['attributes']["instanceStatus"],\
                                           str(elem['provider']).lower(),str(elem['region']).lower(),\
                                           elem['attributes']['rules'])
                        security_group.append(sg_dict)
                    else:
                        pass
            else:
                security_group = []
            return security_group
        else:
            for param in pro_reg_list[0]:
                url = endpoint + "/api/instance?resourceType=sg&&provider="+str(param[0]).lower()+"&&region="+str(param[1]).lower()
                time.sleep(1)
                resp, body = httpInst.request(url)         
                body = json.loads(body)
                security_group = []
                if resp.get('status') == '200' and body:
                    for elem in body:
                        if "rules" in elem["attributes"]:
                            elem['attributes']['rules'] = elem['attributes']['rules']
                        else:
                            elem['attributes']['rules'] = []  
                        if "description" in elem["metadata"]:
                            elem['metadata']['description'] = elem['metadata']['description']
                        else:
                            elem['metadata']['description'] = ""  
                        if (elem["attributes"]["instanceStatus"] !="deleted"):                               
                            sg_dict = Security(elem['instanceId'], \
                                               elem['metadata']['name'],\
                                               elem['metadata']['description'],
                                               elem['attributes']["instanceStatus"],\
                                               str(elem['provider']).lower(),str(elem['region']).lower(),\
                                               elem['attributes']['rules'])
                            security_group.append(sg_dict) 
                        else:
                            pass
                else:
                    pass
            return security_group                        
    except Exception,e:
        security_group = []
        print e

def create_securitygroups(request,name,description,provider,region):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
        url = endpoint + "/api/resource/sg/"+ provider + "/" + region + "/standard"
        b = {"metadata": {
                  "name": name,
                  "description": description
                     }     
            }
        h= {"content-type":"application/json"}
        b = json.dumps(b)
        resp, body = httpInst.request(url,method="POST",body=b,headers=h)
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
        while (body[0]["requestStatus"] == "failed" ) and acount == 5:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        return True
    except Exception,e:
        print e



def delete_securitygroup(request,instanceid):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint
    httpInst = httplib2.Http()
    httpInst.add_credentials(name = credential_username, \
	                                 password = credential_password)
    url=endpoint + "/api/instance/"+instanceid
    h = {"content-type": "application/json"}
    resp, body = httpInst.request(url, method = "DELETE", headers = h)
    time.sleep(1)
    dd=json.loads(body)
    print dd



def detail_securitygroups(request,sg_id):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")  
        endpoint = request.user.cnextendpoint 
        httpInst = httplib2.Http()
        
        httpInst.add_credentials(name = credential_username, \
                                  password = credential_password)
        url=endpoint + "/api/instance" + "/" + sg_id
        resp, body = httpInst.request(url,method="GET")
        body = json.loads(body)
        security_groups = []
        if resp.get('status') == '200' and body:
            if body['resourceType'] == "sg" and 'rules' in body['attributes'] != None:   
                sg_dict = Securitys(sg_id,body['attributes']['rules'][0]['from-port'],\
                                    body['attributes']['rules'][0]['to-port'],\
                                    body['attributes']['rules'][0]['cidr-ip'],\
                                    body['attributes']['rules'][0]['protocol'])
                security_groups.append(sg_dict)
        else:
            security_groups = []
    except:
        security_groups = []
    return security_groups


def add_securitygroups(request,instanceid,from_port,to_port,protocol,cidr):

    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        
        httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
        url = endpoint + "/api/instance/"+ instanceid +"?action=add-access"
        
        body  =  {	"rules": [
			  {
		"protocol": protocol,
	        "from-port": from_port,
		"to-port": to_port,
		"cidr-ip": cidr
		  },
  {
           "protocol": "tcp",
		"from-port": "22",
		"to-port": "22",
		"cidr-ip": ["0.0.0.0/0"]
	  }
	]
}
        h = {"content-type":"application/json"}
        b = json.dumps(body)
        resp, body = httpInst.request(url,method="PUT",body=b,headers=h)
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
        while (body[0]["requestStatus"] == "failed" ) and acount == 5:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        return True
    except Exception,e:
        print e


def deleteport_securitygroups(request,instanceid,index):

    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        
        httpInst.add_credentials(name = credential_username, \
                                 password = credential_password)
        url = endpoint + "/api/instance/"+ instanceid +"?action=remove-access"
        
        body  =  { "ruleIndexes": [index] }
        h = {"content-type":"application/json"}
        b = json.dumps(body)
        time.sleep(1)
        resp, body = httpInst.request(url,method="PUT",body=b,headers=h)
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
        while (body[0]["requestStatus"] == "failed" ) and acount == 5:
                time.sleep(1.5)
                body = check_call(endpoint,body[0]['requestId'])
                acount += 1
        return True
    except Exception,e:
        print e

def get_rules(request,sg_id):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")  
        endpoint = request.user.cnextendpoint 
        httpInst = httplib2.Http()
        
        httpInst.add_credentials(name = credential_username, \
                                  password = credential_password)
        url=endpoint + "/api/instance" + "/" + sg_id
        resp, body = httpInst.request(url,method="GET")
        body = json.loads(body)
        sg_rules = []
        if resp.get('status') == '200' and body:
            if body['resourceType'] == "sg" and 'rules' in body['attributes'] != None:
                for i in range(0,len(body['attributes']['rules'])):
                    sg_dict = Securitys(sg_id,body['attributes']['rules'][i]['from-port'],\
                                    body['attributes']['rules'][i]['to-port'],\
                                    body['attributes']['rules'][i]['cidr-ip'],\
                                    body['attributes']['rules'][i]['protocol'])
                    sg_rules.append(sg_dict)
            else:
                sg_rules = []
                
    except:
        sg_rules = []
    return sg_rules
