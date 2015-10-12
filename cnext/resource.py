
"""
Get Lists of providers and regions from resource_file.yaml for Services: keyPairs, SecurityGroups, Volume, Instance(Start,Stop) 
"""

import yaml, os
from os.path import join
f = open(join(os.path.dirname(os.path.abspath(__file__)), 'resource_file.yaml'))
resource_data = yaml.safe_load(f)

provider_keypairs_choices = resource_data['provider_keypairs_choices'] 
region_keypairs_choices = resource_data['region_keypairs_choices']

provider_sg_choices = resource_data['provider_sg_choices']
region_sg_choices = resource_data['region_sg_choices']

provider_volume_choices = resource_data['provider_volume_choices']
region_volume_choices = resource_data['region_volume_choices']

START_STOP_PROVIDER = list(tuple(a) for a in resource_data['START_STOP_PROVIDERS'])