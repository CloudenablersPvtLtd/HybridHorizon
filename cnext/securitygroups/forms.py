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
from django.core.urlresolvers import reverse
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions,forms, messages
from horizon.utils import fields
from cnext_api import api
from cnext.resource import provider_sg_choices,region_sg_choices 


LOG = logging.getLogger(__name__)

class Regionlist():
    def __init__(self, provider, region):
        self.name = region
        self.provider = provider
        self.region = region

class portlist():
    def __init__(self, protocoldetail,fromport):
        self.protocoldetail = protocoldetail
        self.fromport = fromport
        self.toport = fromport
        self.protocol = protocoldetail



class CreateGroup(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])
    description = forms.CharField(label=_("Description"))   
    key_provider_list = forms.ChoiceField(
        label=_("Providers List"),
        required=True,
        )
    key_region_list = forms.ChoiceField(
        label=_("Regions List"),
        required=True,
        widget=fields.SelectWidget(data_attrs=('provider','region',),transform=lambda x: ("%s " % (x.name)))
        )


    def handle(self, request, data):
        try:
            sg = api.create_securitygroups(request,
                                                   data['name'],
                                                   data['description'],
                                                   data['key_provider_list'],
                                                   data['key_region_list'])
            if sg == True:
                messages.success(request,
                             _('Successfully created security group: %s')
                               % data['name'])
            return sg
 
            
        except Exception,e:
            print e
            redirect = reverse("horizon:cnext:securitygroups:index")
            exceptions.handle(request,
                              _('Unable to create security group.'),
                              redirect=redirect)
    def __init__(self, request, *args, **kwargs):
        forms.SelfHandlingForm.__init__(self, request, *args, **kwargs)
        provider_list = api.providers(self.request)
        region_list = api.region(self.request)
        p = [("", _("Select Provider"))]
        for provider in provider_list:
            if provider.provider in provider_sg_choices:
                p.append((provider.provider.lower(), provider.provider))
        t = tuple(p)
        tuple_providers = t
        self.fields['key_provider_list'].choices = tuple_providers
        r = [("", _("Select Region"))]
        for region in region_list:
            if region.name in region_sg_choices:
                r.append((region.name,Regionlist(region.provider.lower(), region.name)))
        r = tuple(r)
        tuple_regions = r
        self.fields['key_region_list'].choices = tuple_regions


class AddRule(forms.SelfHandlingForm):
      
    instanceid= forms.CharField(label=_("instanceiD"),
                                widget=forms.HiddenInput(),
                                required=False)
   
    
    from_port = forms.IntegerField(label=_("From Port"),
                                   required=False,
                                   help_text=_("Enter an integer value "
                                               "between 1 and 65535."))
                                   
    to_port = forms.IntegerField(label=_("To Port"),
                                 required=False,
                                 help_text=_("Enter an integer value "
                                             "between 1 and 65535."))
    cidr_ip = forms.CharField(label=_("CIDR"))
    print type(cidr_ip)                     
                         
    protocol_choices = (
    ('tcp','tcp'),
    ('udp','udp'),
    ('icmp','icmp'),)
    
    protocol_list = forms.ChoiceField(
        label=_("Protocols"),
        required=True,
        choices=protocol_choices
        )
       

    def handle(self, request, data):
        try:
            cidr = []
            cidr.append(data['cidr_ip'])
            rule = api.add_securitygroups(request,data['instanceid'],data['from_port'],data['to_port'],data['protocol_list'],cidr)
            messages.success(request, _('Successfully added rule: %s') 
                                        % data['instanceid'])
            return rule
        except Exception,e:
            redirect = reverse("horizon:cnext:"
                               "securitygroups:index")
            exceptions.handle(request,
                              _('Unable to add rule to security group.'),
                              redirect=redirect)

class DeleteRule(forms.SelfHandlingForm):
    
    def __init__(self, *args, **kwargs):
        rule_choice = kwargs["initial"]["rule_list"] 
        super(DeleteRule, self).__init__(*args,**kwargs)
        self.fields['rule_list'] = forms.ChoiceField(label=_("Rules"),
                                       required=True,choices = rule_choice,
                                       help_text=_("Select the rule to be deleted"))
      
    instanceid= forms.CharField(label=_("instanceId"),
                                widget=forms.HiddenInput(),
                                required=False)
    rule_list = forms.ChoiceField(label=_("Rules"),
                                       required=True,
                                       help_text=_("Select the rule to be deleted"))
    def handle(self, request, data):
        print data
        try:
            rules = api.deleteport_securitygroups(request,data['instanceid'],data['rule_list'])
            if rules is not None:    
                messages.success(request, _('Successfully deleted rule: %s') 
                                        % data['instanceid'])
                return rules
            else:
                raise Exception
        except Exception,e:
            redirect = reverse("horizon:cnext:"
                               "securitygroups:index")
            exceptions.handle(request,
                              _('Unable to delete rule to security group.'),
                              redirect=redirect)

class AddPort(forms.SelfHandlingForm):
      
    instanceid= forms.CharField(label=_("instanceId"),
                                widget=forms.HiddenInput(),
                                required=False)
    protocoldetail_choices = (
    ("", _("Select Protocoldetails")),
    ('ssh','ssh'),
    ('http','http'),
    ('rdp','rdp'),
    ('https','https'),
    ('mysql','mysql'),
    ('ldap','ldap'),
    ('microsoftsql','microsoftsql'),
    ('pop3','pop3'),
    ('pop3s','pop3s'),
    ('imap','imap'),
    ('imaps','imaps'),
    ('smtp','smtp'),
    ('smtps','smtps'),
    ('other','other'),)
   
    protocoldetail_details = forms.ChoiceField(
        label=_("ProtocolDetails"),
        required=True,
        choices=protocoldetail_choices
        )

    fromport_choices = (
    ('22',portlist('ssh','22')),
    ('80',portlist('http','80')),
    ('3389',portlist('rdp','3389')),
    ('443',portlist('https','443')),
    ('3306',portlist('mysql','3306')),
    ('389',portlist('ldap','389')),
    ('1433',portlist('microsoftsql','1433')),
    ('110',portlist('pop3','110')),
    ('995',portlist('pop3s','995')),
    ('220',portlist('imap','220')),
    ('993',portlist('imaps','993')),
    ('25',portlist('smtp','25')),
    ('465',portlist('smtps','465')),)
   
    fromport_details = forms.ChoiceField(
        label=_("From_Port"),
        required=True,
        choices=fromport_choices,
        widget=fields.SelectWidget(data_attrs=('protocoldetail','fromport',),transform=lambda x: ("%s " % (x.fromport)))
        )
    
    toport_choices = (
    ('22',portlist('ssh','22')),
    ('80',portlist('http','80')),
    ('3389',portlist('rdp','3389')),
    ('443',portlist('https','443')),
    ('3306',portlist('mysql','3306')),
    ('389',portlist('ldap','389')),
    ('1433',portlist('microsoftsql','1433')),
    ('110',portlist('pop3','110')),
    ('995',portlist('pop3s','995')),
    ('220',portlist('imap','220')),
    ('993',portlist('imaps','993')),
    ('25',portlist('smtp','25')),
    ('465',portlist('smtps','465')),)
    
   
    toport_details = forms.ChoiceField(
        label=_("To_Port"),
        required=True,
        choices=fromport_choices,
        widget=fields.SelectWidget(data_attrs=('protocoldetail','toport',),transform=lambda x: ("%s " % (x.toport)))
        )   
    protocol_choices = (
    ('tcp','tcp'),
    ('udp','udp'),
    ('icmp','icmp'),)
    
    protocol_list = forms.ChoiceField(
        label=_("Protocols"),
        required=True,
        choices=protocol_choices
        )
    cidr_ip = forms.CharField(label=_("CIDR"))
                         

    def handle(self, request, data):
        try:
            cidr = []
            cidr.append(data['cidr_ip'])
            ports = api.add_securitygroups(request,data['instanceid'],data['fromport_details'],data['toport_details'],data['protocol_list'],cidr)
            messages.success(request, _('Successfully added port: %s') 
                                        % data['instanceid'])
            return ports
        except Exception,e:
            redirect = reverse("horizon:cnext:"
                               "securitygroups:index", args=[data['id']])
            exceptions.handle(request,
                              _('Unable to add rule to security group.'),
                              redirect=redirect)

