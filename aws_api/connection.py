import logging
from boto import ec2
from cloud_mongo.trail import encode_decode

LOG = logging.getLogger(__name__)

class AWS():
    def __init__(self, request):
        self.request = request
        self.client = connection(request)
        self.awscloud = request.user.awsname
    
    def get_zone(self):
        if self.client:
            zone = self.client.get_all_zones()
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return zone

    def get_regions(self):
        if self.client:
            regions = self.client.get_all_regions()
        else:
            raise Exception("Unable to connect " + self.awscloud)
        return regions

def get_regions_wo_connection():
    regions_list = []
    regions = ec2.regions()
    for region in regions:
        regions_list.append(tuple((region.name,region.name)))
    return regions_list

def test(region,access_key,secret_key):
    try:
        client = ec2.connect_to_region(region_name = region,
                                     aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key)
        zones = client.get_all_zones()
        return True
    except:
        return False
    
def connection(request):
    try:
        client = ec2.connect_to_region(region_name = request.user.awsendpoint\
                                     ,aws_access_key_id=request.user.awspublickey\
                                     ,aws_secret_access_key=\
                                     encode_decode(request.user.awsprivatekey,"decode"))
        return client
    except:
        return None

    