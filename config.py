import yaml, os
from os.path import join
f = open(join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml'))
resource_data = yaml.safe_load(f)

mail_id = resource_data['mail_id']
pwd = resource_data['password']