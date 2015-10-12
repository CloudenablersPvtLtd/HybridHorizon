'''
Created on 10-Feb-2014

@author: Ganesh
'''

import logging

LOG = logging.getLogger(__name__)


def cnext_switch(request):

    context = {}

    # Auth/Keystone context
    context.setdefault('cnext_tenants', [])
    current_dash = request.horizon['dashboard']
    needs_tenants = getattr(current_dash, 'supports_tenants', False)
    dashboard_name = getattr(current_dash, 'slug', False)
    if dashboard_name == "cnext":
        if request.user.is_authenticated() and needs_tenants:
            context["cnext_tenants"] = sum([[y.cloudid for y in i.policy 
                                             if y.cloudid.platform == "Cnext"] for i in 
                                            request.user.roles], [])
    return context