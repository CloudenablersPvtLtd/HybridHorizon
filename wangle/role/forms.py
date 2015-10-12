from django.utils.translation import ugettext_lazy as _
from horizon import forms,workflows,messages
from horizon.utils import fields
from mongoengine import *
from cnext_api import api as capi
from cloud_mongo.trail import roleaccess,actions,tenantclouds,PolicyDoc,roledetail
import logging

LOG = logging.getLogger(__name__)


class CreateRoleAction(workflows.Action):

    rolename = forms.CharField(label=_("Role Name"),max_length=80)   
     
    roletype_choices = (
    ("", _("Select Role Type")),
    ('Tenant Member','Tenant Member'),)
     
    roletype = forms.ChoiceField(
        label=_("Roletype"),
        required=True,
        choices=roletype_choices
        )
    
    access = forms.MultipleChoiceField(label=_("Access"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Create Access for the Role."))

    def populate_access_choices(self, request, context):
        access = []
        try:
            rolelist = roleaccess.objects.all()
            for role in rolelist:
                access = [(a, a) for a in role.access] 
                access.insert(0, ("All", _("All")))
                    
           
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return access
    
    class Meta:
        name = _("Role")
    
    
class CreateRole(workflows.Step):
    action_class = CreateRoleAction 
    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['rolename'] = data.get("rolename", None)
            context['roletype'] = data.get("roletype", None)
            context['access'] = data.get("access", None)

           
        return context 

class CnextTabAction(workflows.Action):
    
    cloudid = forms.ChoiceField(
        label=_("Cloud Name"),
        required=False,
        widget=fields.SelectWidget(
                                   data_attrs=('platform',),
                                   transform=lambda x: ("%s" % (x.name)))
    )

    provider = forms.ChoiceField(label=_("Provider"),
                                 required=False,
                                 help_text=_("Choose Your Provider" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider',),
                                                            transform=lambda x: ("%s" % (x.provider))))
    region = forms.ChoiceField(label=_("Region"),
                                 required=False,
                                 help_text=_("Choose Your Region" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider','name',),
                                                            transform=lambda x: ("%s(%s)" % ((x.name).title(),(x.provider).title()))))
    allowed = forms.MultipleChoiceField(label=_("Allowed Actions"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Allowed Action for the Role."))

    def populate_cloudid_choices(self, request, context):
        try:
            cloudid = []
            cloudlist = tenantclouds.objects(tenantid=self.request.user.tenantid.id)
            cloudid = [(cloud.id,cloud) for cloud in cloudlist]
            cloudid.insert(0, ("", _("Select Cloud")))
                
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            cloudid = []
        return cloudid
    
    
    def populate_provider_choices(self, request, context):
        cnext_tuples  = []
        status = []
        for role in request.user.roles:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    status.append("True")
                else:
                    pass
        if "True" in status:
            cnext_provider = capi.providers(request)        
            for cprovider in cnext_provider:
                cnid = cprovider.__dict__['provider']
                cnext_tuples.append((cnid, cprovider))
            cnext_tuples.insert(0, ("", _("Select Provider")))
            return cnext_tuples
        else:
            return cnext_tuples
    
    
    
    def populate_region_choices(self, request, context):
        cnext_tuples  = []
        status = []
        for role in request.user.roles:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    status.append("True")
                else:
                    pass
        if "True" in status:      
            cnext_region = capi.region(request)
            for cregion in cnext_region:
                cnid = cregion.__dict__['name']
                cnext_tuples.append((cnid, cregion))
            cnext_tuples.insert(0, ("", _("Select Region")))
    
            return cnext_tuples
        else:
            return cnext_tuples
    
    
    
    def populate_allowed_choices(self,request,context):
        try:
            action = actions.objects.all()
            for a in action:
                actionss = [(a, a) for a in a.allowed] 
            actionss.insert(0, ("All", _("All")))
   
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            actionss = []
        return actionss

    
    class Meta:
        name = _("Policies")
    
    

class CloudPolicy(workflows.Step):
    action_class = CnextTabAction
    
    def contribute(self, data, context):
        if data:
            context['cloudid'] = data.get("cloudid", None)
            context['provider'] = data.get("provider", None)
            context['region'] = data.get("region", None)
            context['allowed'] = data.get("allowed", None)
        return context 

        
class CreateRoleForm(workflows.Workflow):
    slug = "create_role"
    name = _("Create Role")
    finalize_button_name = _("Create")
    success_url = "horizon:wangle:role:index"
    default_steps = (CreateRole,
                     CloudPolicy,
                    )
    
        
    def handle(self, request, context):
        rolename = context.get('rolename', None)
        roletype = context.get('roletype', None)
        access = context.get('access', None)
        cloudid = context.get('cloudid', None)
        provider = context.get('provider', None)  
        region = context.get('region', None)  
        allowed = context.get('allowed', None)  
    

        try:
            if ("All" in access):
                access.remove("All")
            if ("All" in allowed):
                allowed.remove("All")               
            if (cloudid == '') & (allowed == []) & (provider == '') & (region == ''):
                role = roledetail(name = rolename,roletype = roletype,access = access,policy = [], tenantid = request.user.tenantid.id)
                role.save()
            else:
                cloud = PolicyDoc(cloudid = cloudid,provider = provider, region = region, allowed = allowed)
                role = roledetail(name = rolename,roletype = roletype,access = access,policy = [cloud], tenantid = request.user.tenantid.id)
                role.save()
            return True
   
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return False
    
class PolicyAddAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    
        
    cloudids = forms.ChoiceField(
        label=_("Cloud Name"),
        required=True,
        widget=fields.SelectWidget(
                                   data_attrs=('platform','allowed'),
                                   transform=lambda x: ("%s" % (x.name)))
    )

    providers = forms.ChoiceField(label=_("Provider"),
                                 required=False,
                                 help_text=_("Choose Your Provider" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider',),
                                                            transform=lambda x: ("%s" % (x.provider))))
    regions = forms.ChoiceField(label=_("Region"),
                                 required=False,
                                 help_text=_("Choose Your Region" "."),
                                 widget=fields.SelectWidget(data_attrs=('provider','name','allowed',),
                                                            transform=lambda x: ("%s(%s)" % ((x.name).title(),(x.provider).title()))))
    
    allowed = forms.MultipleChoiceField(label=_("Allowed Actions"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Allowed Action for the Role."))
    
    
    def populate_cloudids_choices(self, request, context):
        try:
            cloudid = []
            cloudlist = tenantclouds.objects(tenantid=self.request.user.tenantid.id)
            roles = roledetail.objects(id = context['id']).first()
            for cloud in cloudlist:
                if roles.policy:
                    for a in roles.policy:
                        if cloud.name == a.cloudid.name:
                            if a.cloudid.platform != "Cnext":
                                cloud.__dict__['allowed'] = a.allowed
                            else:
                                pass
                            cloudid.append((cloud.id,cloud))
                        else:
                            cloudid.append((cloud.id,cloud))
                else:
                    cloudid.append((cloud.id,cloud))
            cloudid = set(cloudid)
            cloudid = list(cloudid)
            cloudid.insert(0, ("", _("Select Cloud")))
               
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            cloudid = []
        return cloudid

    def populate_providers_choices(self, request, context):
        cnext_tuples  = []
        status = []
        for role in request.user.roles:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    status.append("True")
                else:
                    pass
        if "True" in status:
            cnext_provider = capi.providers(request)        
            for cprovider in cnext_provider:
                cnid = cprovider.__dict__['provider']
                cnext_tuples.append((cnid, cprovider))
            cnext_tuples.insert(0, ("", _("Select Provider")))
            return cnext_tuples
        else:
            return cnext_tuples
    
    


    def populate_regions_choices(self, request, context):
        cnext_tuples  = []
        status = []
        for role in request.user.roles:
            for policy in role.policy:
                if policy.cloudid.platform == "Cnext":
                    status.append("True")
                else:
                    pass
        if "True" in status:
            cnext_region = capi.region(request)
            list_reg = []  
            roles = roledetail.objects(id = context['id']).first()
            for a in roles.policy:
                if (a.region.lower(),a.provider.lower(),a.allowed) in list_reg:
                    pass
                else:
                    list_reg.append((a.region.lower(),a.provider.lower(),a.allowed))
            if list_reg:
                for reg in  list_reg:
                    for cregion in cnext_region:
                        cnid_reg = cregion.__dict__['name']
                        cnid_pro = cregion.__dict__['provider']
                        if (str(cnid_reg).lower() == reg[0]) & (str(cnid_pro).lower() == reg[1]) :
                            cregion.__dict__['allowed'] = reg[2]
            for cregion in cnext_region:
                cnid_reg = cregion.__dict__['name']
                cnext_tuples.append((cnid_reg, cregion))              
            cnext_tuples.insert(0, ("", _("Select Region")))
            return cnext_tuples
        else:
            return cnext_tuples
    

    
    
    
    def populate_allowed_choices(self,request,context):
        actionss = []
        try:
            action = actions.objects.all()
            for a in action:
                actionss = [(a, a) for a in a.allowed] 
                actionss.insert(0, ("All", _("All")))
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return actionss
    
    
    class Meta:
        name = _("Policies")
    

class PolicyAdd(workflows.Step):
    action_class = PolicyAddAction
    contributes = ("id",)

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['id'] = data.get("id","")
            context['cloudid'] = data.get("cloudids", "")
            context['provider'] = data.get("providers", None)
            context['region'] = data.get("regions", None)
            context['allowed'] = data.get("allowed", "")
        return context 

class AddPolicy(workflows.Workflow):
    
    slug = "add_policy"
    name = _("ADD/EDIT Policy")
    finalize_button_name = _("SAVE")
    success_url = "horizon:wangle:role:index"
    default_steps = (PolicyAdd, )
      
    def handle(self, request, context):
        id = context.get('id', None) 
        cloudid = context.get('cloudid', None)
        provider = context.get('provider', None)  
        region = context.get('region', None)
        allowed = context.get('allowed', None)
        try:
            if "All" in allowed:
                allowed.remove("All")
            i = {"cloudid":cloudid,"allowed":allowed,"provider":provider,"region":region}
            roles = roledetail.objects(id=id).first()
            policies = []
            flag = False
            if roles.policy:
                for r in roles.policy:
                    if str(r.provider).lower() == str(provider).lower() and str(r.region).lower() == str(region).lower() and str(r.cloudid.id) == str(cloudid):
                        roledetail.objects(id=id).update(pull__policy=r)
                        policies.append(i)
                        flag = True
                    else:
                        policies.append(r)
                if flag == False:
                    policies.append(i)
                roledetail.objects(id=id).update(set__policy=policies)

            else:
                roledetail.objects(id=id).update(push__policy=i)            
            return True
  
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False


class PolicyRemoveAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    
    cloudid = forms.MultipleChoiceField(label=_("Cloud Name"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Allowed Action for the Role."))

    
    
    def populate_cloudid_choices(self, request, context):
        try:
            clouds =[]
            id = context['id']
            roles = roledetail.objects(id =id).first()
            for policy in roles.policy:
                cloudlist = tenantclouds.objects(id = policy.cloudid.id).first()
                if (cloudlist.id,cloudlist.name) in clouds:
                    pass
                else:
                    clouds.append((cloudlist.id,cloudlist.name))              
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            clouds = []
        return clouds
    
    
    class Meta:
        name = _("Policies")
    

class PolicyRemove(workflows.Step):
    action_class = PolicyRemoveAction
    contributes = ("id",)

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['id'] = data.get("id","")
            context['cloudid'] = data.get("cloudid", "")
        return context 

class RemovePolicy(workflows.Workflow):
    
    slug = "remove_policy"
    name = _("Remove Policy")
    finalize_button_name = _("Remove")
    success_url = "horizon:wangle:role:index"
    default_steps = (PolicyRemove, )
      
    def handle(self, request, context):
        id = context.get('id', None) 
        cloudid = context.get('cloudid', None)
        try:
            roles = roledetail.objects(id=id).first()
            list1 = []
            for a in roles.policy:
                if (str(a.cloudid.id) in cloudid):
                    pass
                else:
                    list1.append(a)
            roledetail.objects(id=id).update(set__policy=list1)
            return True
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False
    
    
class AccessEditAction(workflows.Action):   
    roleid = forms.ChoiceField(
        label=_("Role Name"),
        required=True,
        widget=fields.SelectWidget(data_attrs=('access',),
                                   transform=lambda x: ("%s" % (x.name)))
    )
    
    
    access = forms.MultipleChoiceField(label=_("Access"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Create Access for the Role."))
    
    def populate_roleid_choices(self, request, context):
        try:
            role = []
            roles = roledetail.objects(id = context['roleid']).first()
            role.append((roles.id,roles))
            role.insert(0, ("", _("Select Role")))
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            role =[]
        return role
    
    
    def populate_access_choices(self, request, context):
        access = []
        try:
            rolelist = roleaccess.objects.all()
            for role in rolelist:
                access = [(a, a) for a in role.access]     
                access.insert(0, ("All", _("All")))  
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return access
    
    class Meta:
        name = _("Role Access")


class AccessEdit(workflows.Step):
    action_class = AccessEditAction
    contributes = ("roleid",)

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['roleid'] = data.get("roleid","")
            context['access'] = data.get("access", "")
        return context 
    
class EditAccess(workflows.Workflow):
    
    slug = "edit_access"
    name = _("Edit Access")
    finalize_button_name = _("Save")
    success_url = "horizon:wangle:role:index"
    default_steps = (AccessEdit, )
      
    def handle(self, request, context):
        id = context.get('roleid', None) 
        access = context.get('access', None)
        try:
            if "All" in access:
                access.remove("All")
            roledetail.objects(id=id).update(set__access = access)
            return True
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False
