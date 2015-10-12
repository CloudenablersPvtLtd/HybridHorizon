import httplib2
import json
import time
import requests
import cloud_mongo.trail

class Snapshots():
    def __init__(self, name, ids, provider, region, status):
        self.id = ids
        self.provider = provider
        self.region = region
        self.name = name
        self.status = status


def snapshots(request):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name=credential_username, \
                                 password=credential_password)
        pro_reg_list =[]
        pro_reg_list = [[(policy.provider,policy.region) for policy in role.policy] for role in request.user.roles] 
        pro_reg_list[0] = set(pro_reg_list[0])
        pro_reg_list[0] = list(pro_reg_list[0])
        snap_shot = []
        if ("ALL","ALL") in pro_reg_list[0]:        
            url = endpoint + "/api/instance?resourceType=image"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    snap_dict = Snapshots(elem['metadata']['name'], \
                                        elem['instanceId'], str(elem['provider']).lower(), \
                                        str(elem['region']).lower(), elem["attributes"]["instanceStatus"])
                    snap_shot.append(snap_dict)
            else:
                snap_shot = []
            return  snap_shot

        else:
            for param in pro_reg_list[0]:
                url = endpoint + "/api/instance?resourceType=image&&provider="+str(param[0]).lower()+"&&region="+str(param[1]).lower()
                resp = requests.get(url=url, auth=(credential_username, credential_password))
                body = resp.json()
                if resp.status_code == 200 and body:
                    for elem in body:
                        snap_dict = Snapshots(elem['metadata']['name'], \
                                        elem['instanceId'], str(elem['provider']).lower(), \
                                        str(elem['region']).lower(), elem["attributes"]["instanceStatus"])
                        snap_shot.append(snap_dict)
                else:
                    pass
            return snap_shot
    except:
        snap_shot = []
    return snap_shot


def create_snapshots(request, name, instanceId, provider, region ,description):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        endpoint = request.user.cnextendpoint
        httpInst = httplib2.Http()
        httpInst.add_credentials(name=credential_username, \
                                 password=credential_password)
        url = endpoint + "/api/resource/image/" + provider + "/" + region + "/standard"
        h = {"content-type": "application/json"}
        b = {
                "virtualMachineId": instanceId,
                "metadata":
                           {
                                 "name": name,
                                 "description": description
                           }
             }
        b = json.dumps(b)
        resp, body = httpInst.request(url, method="POST", body=b, headers=h)
        body = json.loads(body)
        time.sleep(15)
        url = endpoint + "/api/request/" + body["requestId"]
        resp, body = httpInst.request(url)
        dd = json.loads(body)
        b = dd[0]["requestStatus"]
        if b == "failed":
            return False
        else:
            return True
    except:
        return False
