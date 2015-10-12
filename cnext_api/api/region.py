import requests
import logging
import cloud_mongo.trail

LOG = logging.getLogger(__name__)

class Region():
    def __init__(self, name, provider):
        self.name = name
        self.provider = provider

def region(request):
    credential_username = request.user.cnextpublickey
    credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
    endpoint = request.user.cnextendpoint    
    region_obj_list = []
    reg_obj_list = []  
    for role in request.user.roles:
        if role.roletype == "Tenant Admin":
            url = endpoint + '/api/resourceQuery/region'
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            body = resp.json()
            msg = "Region Listing status %s" %resp.status_code
            LOG.debug(msg)
            if resp.status_code == 200 and body:
                for elem in body:
                    """
                    Modified (lower() commented) for Get Providers and Regions by API instead of hard Code.
                    """
                    region_obj_list.append(Region(str(elem['name']),str(elem['provider']).lower()))
                import operator
                region_obj_list.sort(key = operator.attrgetter('name'))
            return region_obj_list
        else:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    reg_obj_list.append((policy.region,policy.provider.lower())) 
    reg_obj_list = list(set(reg_obj_list))
    for x in reg_obj_list:
        region_obj_list.append(Region(x[0],x[1]))        
    return region_obj_list  
