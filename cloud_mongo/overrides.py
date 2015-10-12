'''
Created on 19-Dec-2013

@author: ganesh
'''

import horizon

# Rename "User Settings" to "User Options"
project = horizon.get_dashboard("project")
admin = horizon.get_dashboard("admin")
cnext = horizon.get_dashboard("cnext")
wangle = horizon.get_dashboard("wangle")
amazon = horizon.get_dashboard("amazon")
hpcloud = horizon.get_dashboard("hpcloud") 


permissions = list(getattr(project, 'permissions', []))
permissions.append('openstack')
project.permissions = tuple(permissions)

volume_panel = project.get_panel("volumes")
volume_panel.permissions = tuple()

network_panel = project.get_panel("networks")
network_panel.permissions = tuple()

permission = list(getattr(admin, 'permissions', []))
permission.append('openstack')
admin.permissions = tuple(permission)


permission = list(getattr(cnext, 'permissions', []))
permission.append('cnext')
cnext.permissions = tuple(permission)

permission = list(getattr(amazon, 'permissions', []))
permission.append('amazon')
amazon.permissions = tuple(permission)

permission = list(getattr(hpcloud, 'permissions', []))
permission.append('hpcloud')
hpcloud.permissions = tuple(permission)
