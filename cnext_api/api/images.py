'''
Created on 06-Feb-2014

@author: user
'''

import requests
import cloud_mongo.trail

class InstImage():
    def __init__(self, name, provider, region,  platform, \
                 description, cost, os, uri, ids):
        self.name = name
        self.provider = provider
        self.region = region
        self.platform = platform
        self.description = description
        self.uri = uri
        self.id = ids
        self.cost = cost
        self.os = os

def images(request):
    try:
        credential_username = request.user.cnextpublickey
        credential_password = cloud_mongo.trail.encode_decode(request.user.cnextprivatekey,"decode")
        
        cnext_url = request.user.cnextendpoint
        pro_reg_list =[]
        pro_reg_list = [[(policy.provider,policy.region) for policy in role.policy] for role in request.user.roles] 
        pro_reg_list[0] = set(pro_reg_list[0])
        pro_reg_list[0] = list(pro_reg_list[0])
        images = []
        if ("ALL","ALL") in pro_reg_list[0]:
            url = cnext_url + "/api/resourceQuery/query/image"
            resp = requests.get(url=url, auth=(credential_username, credential_password))
            body = resp.json()
            if resp.status_code == 200 and body:
                for elem in body:
                    image_dict = InstImage(elem['name'], str(elem['provider']).lower(), \
                                           str(elem['region']).lower(),\
                                           elem["platform"], elem["description"],\
                                           " ".join([elem["costPerUnit"], elem["costUnit"]]),
                                           " ".join([elem["operatingSystem"], elem["operatingSystemVersion"]]),\
                                            elem['uri'], elem['id'])

                    images.append(image_dict)
            else:
                images = []
            return images

        else:
            for param in pro_reg_list[0]:
                url = cnext_url + "/api/resourceQuery/query/image?provider=" + str(param[0]) + "&&region=" + str(param[1])
                resp = requests.get(url=url, auth=(credential_username, credential_password))
                body = resp.json()
                if resp.status_code == 200 and body:
                    for elem in body:
                        image_dict = InstImage(elem['name'], str(elem['provider']).lower(), \
                                               str(elem['region']).lower(),\
                                               elem["platform"], elem["description"],\
                                               " ".join([elem["costPerUnit"], elem["costUnit"]]),
                                               " ".join([elem["operatingSystem"], elem["operatingSystemVersion"]]),\
                                                elem['uri'], elem['id'])
    
                        images.append(image_dict)
            return images
    except Exception, e:
        print "Images listing Exception", e
        images = []
    return images

