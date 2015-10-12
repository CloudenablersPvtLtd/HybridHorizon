# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables
from horizon import exceptions
from horizon import forms
from horizon.utils import fields, validators
from horizon import workflows
from cnext_api import api as capi
LOG = logging.getLogger(__name__)


class SetInstanceDetailsAction(workflows.Action):
    PROVIDER_TYPE_CHOICES = (
        ('provider_list', _("--- PROVIDER LISTS---")),)
    
    CPU_TYPE_CHOICES = (
        ('cpu_list', _("--- CPU LISTS---")),)
    
    name = forms.CharField(max_length=80, label=_("Instance Name"))
  
    count = forms.IntegerField(label=_("Instance Count"),
                                min_value=1,
                                initial=1,
                                help_text=_("Number of instances to launch."))
    provider = forms.ChoiceField(label=_("Provider"),
                                 required=True,
                                 help_text=_("Choose Your Provider" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider',),
                                                            transform=lambda x: ("%s" % (x.provider.title()))))
    region = forms.ChoiceField(label=_("Region"),
                                 required=True,
                                 help_text=_("Choose Your Region" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider','name',),
                                                            transform=lambda x: ("%s" % (x.name.title()))))

   
 
    cnext_images_id = forms.ChoiceField(
        label=_("Image Name"),
        required=True,
        choices=PROVIDER_TYPE_CHOICES,
        help_text=_("Choose Your Image Name" "."),
        widget=fields.SelectWidget(
            data_attrs=('provider','region', 'cost'),
            transform=lambda x: ("%s (%s)" % (x.name,x.provider))))
       
    provider_list = forms.ChoiceField(
        label=_("Instance Type"),
        required=True,
        choices=CPU_TYPE_CHOICES,
        widget=fields.SelectWidget(
            data_attrs=('provider','region','cpuCount', 'ram', 'localStorage', 'cost'),
            transform=lambda x: ("%s (%s)(cpucount=%s,RAM=%sGB,localstorage=%sGB)" % (x.name,x.provider,x.cpuCount,x.ram,x.localStorage))))
    

    cpu_list = forms.ChoiceField(
        label=_("CPU Count"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('provider','region',),
            transform=lambda x: ("%s " % (x.attr))))

    ram_list = forms.ChoiceField(
        label=_("RAM (in GB)"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('provider','region',),
            transform=lambda x: ("%s " % (x.attr))))

    localstorage_list = forms.ChoiceField(
        label=_("Local storage (in GB)"),
        required=False,
        widget=fields.SelectWidget(
            data_attrs=('provider','region',),
            transform=lambda x: ("%s " % (x.attr))))


    class Meta:
        name = _("Details")
        help_text_template = ("cnext/instances/"
                              "_launch_details_help.html")

    def __init__(self, request, context, *args, **kwargs):
        #self._init_images_cache()
        super(SetInstanceDetailsAction, self).__init__(
            request, context, *args, **kwargs)
        self.provider_list_choices = []
        self.check_list = []

    def populate_provider_choices(self, request, context):
        cnext_tuples  = []
        self.check_list= []
        for role in request.user.roles:
            for policy in role.policy:
                if ((policy.provider).lower(),(policy.region).lower(),policy.allowed) in self.check_list:
                    pass
                else:
                    self.check_list.append(((policy.provider).lower(),(policy.region).lower(),policy.allowed))
        policy_allow = [[i.roletype if i.roletype == "Tenant Admin" else "Member"] for i in request.user.roles]            
        if "Tenant Admin" in policy_allow[0]:
            cnext_provider = capi.providers(request)
            if "provider" in context:
                cprovider = context["provider"].lower()
                cnext_provider = list( filter((lambda x: x.__dict__["provider"].lower() \
                                                == cprovider ), cnext_provider ))
            for cprovider in cnext_provider:
                cnid = cprovider.__dict__['provider']
                cnext_tuples.append((cnid, cprovider))
            if "provider" not in context:
                if cnext_tuples:
                    cnext_tuples.insert(0, ("", _("Select Provider")))
                else:
                    cnext_tuples.insert(0, ("", _("No provider available")))
            return cnext_tuples
        else:
            pro_check_list =[]
            pro_list = []
            if "provider" in context:
                cprovider = context["provider"].lower()
                for pro in self.check_list:
                    print pro[0] in self.check_list
                    if ( pro[0] == cprovider) &( pro[0]  not in pro_check_list) :
                        pro_check_list.append(pro)
                    else:
                        pass
            if pro_check_list:
                self.check_list = pro_check_list
            for provider in self.check_list:
                if "Create Instance" in provider[2]:
                    pro_list.append(provider[0])
                else:
                    pass
            pro_list = list(set(pro_list))
            print pro_list
            for pro in pro_list:
                cnext_tuples.append((pro,capi.Provider(pro)))

            if "provider" not in context:
                if cnext_tuples:
                    cnext_tuples.insert(0, ("", _("Select Provider")))
                else:
                    cnext_tuples.insert(0, ("", _("No provider available")))
            return cnext_tuples

    def populate_region_choices(self, request, context):
        cnext_tuples  = []
        policy_allow = [[i.roletype if i.roletype == "Tenant Admin" else "Member"] for i in request.user.roles]            
        if "Tenant Admin" in policy_allow[0]:
            cnext_region = capi.region(request)
            if "region" in context:
                cregion = context["region"].lower()
                cnext_region = list( filter((lambda x: x.__dict__["name"].lower() \
                                                == cregion ), cnext_region ))
            for cregion in cnext_region:
                cnid = cregion.__dict__['name']
                cnext_tuples.append((cnid, cregion))
            
            if "region" not in context:
                if cnext_tuples:
                    cnext_tuples.insert(0, ("", _("Select Region")))
                else:
                    cnext_tuples.insert(0, ("", _("No Region available")))
            return cnext_tuples
        
        else:
            if "region" in context:
                cregion = context["region"].lower()
                self.check_list = list( filter((lambda x: x[1].lower() \
                                                == cregion ), self.check_list ))
            
            for region in self.check_list:
                if "Create Instance" in region[2]:
                    cnext_tuples.append((region[1],capi.Region(region[1],region[0])))
                else:
                    pass
            if "region" not in context:
                if cnext_tuples:
                    cnext_tuples.insert(0, ("", _("Select Region")))
                else:
                    cnext_tuples.insert(0, ("", _("No Region available")))
            return cnext_tuples
#         
        

    
    def populate_cnext_images_id_choices(self, request, context):
        cnext_tuples  = []
        
        cnext_images = capi.images(request)
        
        if "cnext_images_id" in context:
            cimage_id = context["cnext_images_id"]
            cnext_images = list( filter((lambda x: x.__dict__["id"].lower() \
                                            == cimage_id ), cnext_images ))

        
        for cimage in cnext_images:
            cnid = cimage.__dict__['uri']
            cnext_tuples.append((cnid, cimage))
        
        if "cnext_images_id" not in context:
            if cnext_tuples:
                cnext_tuples.insert(0, ("", _("Select Image")))
            else:
                cnext_tuples.insert(0, ("", _("No images available")))
        return cnext_tuples

    def populate_provider_list_choices(self, request, context):
        cnext_tuples = []
        
        cnext_instances = capi.instances_list(request)
        self.provider_list_choices = cnext_instances ##adding to global variable
        
        if "cnext_images_id" in context:
            pop_provider = context["cnext_images_id"].split("_")[1].lower()
            pop_region = context["cnext_images_id"].split("_")[2].lower()
            
            cnext_instances = list( filter((lambda x: x.__dict__ \
                                            ["provider"].lower() == pop_provider \
                                            and x.__dict__["region"].lower() == \
                                            pop_region), cnext_instances) )    
       
        for cinstances in cnext_instances :
            cnid = cinstances.__dict__['uri']
            cnext_tuples.append((cnid, cinstances))
        if cnext_tuples:
            cnext_tuples.insert(0, ("", _("Select Instance Type")))
        else:
            cnext_tuples.insert(0, ("", _("No images available")))
        return cnext_tuples


    
    def populate_cpu_list_choices(self, request, context):
        print "cpulistcontext:",context
        cnext_tuples  = []
         
        for cinstances in self.provider_list_choices:
            cnid = cinstances.__dict__['uri']
            cnid = str(cnid)
            a=cnid.split("/")
            if a[-1] == "configurable":
                b = cinstances.__dict__['cpuCount']
                b = str(b)
                b = b.split("-")
                class SimpleClass(object):
                    pass
                for count in xrange(int(b[0][0])):
                    x = SimpleClass()
                    simplelist = []
                    x.attr = count+1
                    x.provider = cinstances.__dict__['provider']
                    x.region = cinstances.__dict__['region']
                    simplelist.append(x)
                    cnext_tuples.append((x.attr, simplelist[0]))
        if cnext_tuples:
            cnext_tuples.insert(0, ("", _("Select CPU count")))
        else:
            cnext_tuples.insert(0, ("", _("No images available")))
        return cnext_tuples
    
    def populate_ram_list_choices(self, request, context):
        cnext_tuples  = []      
        for cinstances in self.provider_list_choices :
            cnid = cinstances.__dict__['uri']
            cnid = str(cnid)
            a=cnid.split("/")
            if a[-1] == "configurable":
                b = cinstances.__dict__['ram']
                b = str(b)
                b = b.split("-")
                class SimpleClass(object):
                    pass
                for count in xrange(int(b[0][0])):
                    x = SimpleClass()
                    simplelist = []
                    x.attr = count+1
                    x.provider = cinstances.__dict__['provider']
                    x.region = cinstances.__dict__['region']
                    simplelist.append(x)
                    cnext_tuples.append((x.attr, simplelist[0]))
        if cnext_tuples:
            cnext_tuples.insert(0, ("", _("Select CPU count")))
        else:
            cnext_tuples.insert(0, ("", _("No images available")))
        return cnext_tuples
    
    def populate_localstorage_list_choices(self, request, context):
        cnext_tuples  = []        
        for cinstances in self.provider_list_choices :
            cnid = cinstances.__dict__['uri']
            cnid = str(cnid)
            a=cnid.split("/")
            if a[-1] == "configurable":
                b = cinstances.__dict__['localStorage']
                b = str(b)
                if "," in b:
                    b = b.split(",")
                    class SimpleClass(object):
                        pass
                    for i in b:
                        x = SimpleClass()
                        simplelist = []
                        x.attr = i
                        x.provider = cinstances.__dict__['provider']
                        x.region = cinstances.__dict__['region']
                        simplelist.append(x)
                        cnext_tuples.append((x.attr, simplelist[0]))
                else:
                    b = b.split("-")
                    class SimpleClass(object):
                        pass
                    for count in range(0,int(b[1]),10):
                        x = SimpleClass()
                        simplelist = []
                        x.attr = count
                        x.provider = cinstances.__dict__['provider']
                        x.region = cinstances.__dict__['region']
                        simplelist.append(x)
                        cnext_tuples.append((x.attr, simplelist[0]))
        if cnext_tuples:
            cnext_tuples.insert(0, ("", _("Select CPU count")))
        else:
            cnext_tuples.insert(0, ("", _("No images available")))
        return cnext_tuples
    
 

class SetInstanceDetails(workflows.Step):
    action_class = SetInstanceDetailsAction
    contributes = ("source_type", "cnext_images_id","source_id",
                   "availability_zone", "name", "count", "flavor","ins_uri",
                   "device_name",  # Can be None for an image.
                   "delete_on_terminate", "provider", "region")

    def prepare_action_context(self, request, context):
        if 'source_type' in context and 'source_id' in context:
            context[context['source_type']] = context['source_id']
        return context

    def contribute(self, data, context):
        context = super(SetInstanceDetails, self).contribute(data, context)
        if "cnext_images_id" in data:
            context["cnext_images_id"] = data.get("cnext_images_id", None)
        if "provider_list" in data:
            context["provider_list"] = data.get("provider_list", None)
        if "cpu_list" in data:
            context["cpu_list"] = data.get("cpu_list",None)
        if "ram_list" in data:
            context["ram_list"] = data.get("ram_list", None)
        if "localstorage_list" in data:
            context["localstorage_list"] = data.get("localstorage_list", None)    
        return context


KEYPAIR_IMPORT_URL = "horizon:cnext:keypairs:import"
 
 
class SetAccessControlsAction(workflows.Action):
    keypair = forms.DynamicChoiceField(label=_("Keypair"),
                                       required=False,
                                       help_text=_("Which keypair to use for "
                                                   "authentication."),
                                       widget=fields.SelectWidget(
                                            data_attrs=('provider','region','instanceId'),
                                            transform=lambda x: ("%s (%s)(%s)" % (x.name,x.provider,x.region))),
                                       add_item_link=KEYPAIR_IMPORT_URL)
    admin_pass = forms.RegexField(
        label=_("Admin Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_admin_pass = forms.CharField(
        label=_("Confirm Admin Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False))
    groups = forms.MultipleChoiceField(label=_("Security Groups"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Launch instance in these "
                                                   "security groups."))
 
    class Meta:
        name = _("Access & Security")
        help_text = _("Control access to your instance via keypairs, "
                      "security groups, and other mechanisms.")
 
    def populate_keypair_choices(self, request, context):
        try:
            keypairs = capi.keypairs(request)
            keypair_list = [(kp.id, kp) for kp in keypairs]
        except Exception:
            keypair_list = []
            exceptions.handle(request,
                              _('Unable to retrieve keypairs.'))
        if keypair_list:
            keypair_list.insert(0, ("", _("Select a keypair")))
        else:
            keypair_list = (("", _("No keypairs available.")),)
        return keypair_list
 
    def populate_groups_choices(self, request, context):
        try:
            groups = capi.securitygroups(request)
            if groups:
                security_group_list = [(sg.id, sg.name) for sg in groups]
            else:
                security_group_list = [] 
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve list of security groups'))
            security_group_list = []
        return security_group_list
 

class SetAccessControls(workflows.Step):
    action_class = SetAccessControlsAction
    depends_on = ("project_id", "user_id")
    contributes = ("keypair_id", "security_group_ids",
            "admin_pass", "confirm_admin_pass")
 
    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['security_group_ids'] = post.getlist("groups")
            context['keypair_id'] = data.get("keypair", None)
            context['admin_pass'] = data.get("admin_pass", "")
            context['confirm_admin_pass'] = data.get("confirm_admin_pass", "")
        return context
 

class LaunchInstance(workflows.Workflow):
    slug = "launch_instance"
    name = _("Launch Instance")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s named "%(name)s".')
    failure_message = _('Unable to launch %(count)s named "%(name)s".')
    success_url = "horizon:cnext:instances:index"
    default_steps = (SetInstanceDetails,
                     SetAccessControls,
                    )
    def format_status_message(self, message):
        name = self.context.get('name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s instances") % count,
                               "name": name}
        else:
            return message % {"count": _("instance"), "name": name}
         

    @sensitive_variables('context')
    def handle(self, request, context):
        source_type = context.get('source_type', None)
        cnext_images_id = context.get('cnext_images_id', None) 
        
        try:
            uri = context.get('provider_list',None)
            image_uri = context.get('cnext_images_id',None)
            cpucount = context.get('cpu_list', None)
            localstorage = context.get("localstorage_list", None)
            keypair = context.get("keypair_id", None)
            securitygroup = context.get("security_group_ids", None)
            context.get("admin_pass", None) 
            password = context.get("confirm_admin_pass", None)
            RAM = context.get("ram_list", None)
            if cpucount == ""  and RAM == "" and localstorage =="":
                body = {
                             "instanceTypeUri" : uri,
                             "imageUri" : image_uri
                        }
            else:
                body = {
                             "instanceTypeUri" : uri,
                             "imageUri" : image_uri,
                             "ram" : RAM,
                             "cpuCount" : cpucount,
                             "localStorage" : localstorage
                        }
            y = capi.validate(request,body)
            if y == "200":
                status = capi.launch_instance(request, uri, image_uri,context['name'], keypair, securitygroup)
                return status
            else :
                return False
        except Exception:
            return False
