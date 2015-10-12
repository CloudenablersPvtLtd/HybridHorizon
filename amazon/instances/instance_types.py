

import yaml, os
from os.path import join
f = open(join(os.path.dirname(os.path.abspath(__file__)), 'instance_types.yaml'))
resource_data = yaml.safe_load(f)


class InstanceType():
    def __init__(self, imagetype, instancetype):
        self.name = instancetype
        self.imagetype = imagetype
        self.instancetype = instancetype

l = []
for a in resource_data['i386_paravirtual_ebs']:
    l.append((a,InstanceType('i386_paravirtual_ebs',a)))

for a in resource_data['i386_paravirtual_instance-store']:
    l.append((a,InstanceType('i386_paravirtual_instance-store',a)))

for a in resource_data['x86_64_paravirtual_ebs']:
    l.append((a,InstanceType('x86_64_paravirtual_ebs',a)))

for a in resource_data['x86_64_paravirtual_instance-store']:
    l.append((a,InstanceType('x86_64_paravirtual_instance-store',a)))

for a in resource_data['x86_64_hvm_ebs']:
    l.append((a,InstanceType('x86_64_hvm_ebs',a)))

for a in resource_data['x86_64_hvm_instance-store']:
    l.append((a,InstanceType('x86_64_hvm_instance-store',a)))

t = tuple(l)
instance_type_choices = t
