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
from aws_api.security_groups import SecurityGroups

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
    vpc_choices=[]
    def __init__(self, *args, **kwargs):
        vpc_choices = kwargs["initial"]["vpc_choices"] 
        super(CreateGroup, self).__init__(*args,**kwargs)
        self.fields['vpc_id'] = forms.ChoiceField(label="VPC ID", required=False, choices=vpc_choices)
    name = forms.CharField(label=_("Name"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])
    description = forms.CharField(label=_("Description"))
    vpc_id = forms.ChoiceField(label=_("VPC ID"),
                                    required=False,
                                    help_text=_("Choose your VPC ID"))
    def handle(self, request, data):
        try:
            sg = SecurityGroups(request).\
            create_security_groups(data['name'],data['description'],data['vpc_id'])
            if sg.status == True:
                messages.success(request, _('Created Security Group named: %s')
                                       % data['name'])
                return True
            else:
                messages.error(request, _('Unable to create security group named: %s')
                                       % data['name'])
                return False
        except Exception, e:
            redirect = reverse("horizon:amazon:securitygroups:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
            return False


class AddRule(forms.SelfHandlingForm):
      
    group_name = forms.CharField(label=_("group_name"),
                                widget=forms.HiddenInput(),
                                required=True)
   
    
    from_port = forms.IntegerField(label=_("From Port"),
                                   required=True,
                                   help_text=_("Enter an integer value "
                                               "between 1 and 65535."))
                                   
    to_port = forms.IntegerField(label=_("To Port"),
                                 required=True,
                                 help_text=_("Enter an integer value "
                                             "between 1 and 65535."))
    cidr_ip = forms.CharField(label=_("CIDR"))                  
                         
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
            rule = SecurityGroups(request).\
            add_rules_security_groups(data['group_name'],data['from_port'],
                                      data['to_port'],data['protocol_list'],cidr)
            messages.success(request, _('Successfully added rule: %s') 
                                        % data['group_name'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:securitygroups:index")
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)

            
class DeleteRule(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        rule_choice = kwargs["initial"]["rule_list"] 
        super(DeleteRule, self).__init__(*args,**kwargs)
        self.fields['rule_list'] = forms.MultipleChoiceField(label=_("Rules"),
                                       required=False,choices = rule_choice,
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Select the rules to be deleted"))
    
    sg_id= forms.CharField(label=_("Security Group ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
       
    rule_list = forms.MultipleChoiceField(label=_("Rules"),
                                       required=False,
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Select the rules to be deleted"))
  
    def handle(self, request, data):
        try:
            for rule in data['rule_list']:
                port = str(rule).split(",")
                SecurityGroups(request).\
                delete_rule(sg_id = data['sg_id'], from_port = port[0],
                            to_port = port[1], protocol = port[2],cidr = port[3])  
            messages.success(request, _('Successfully deleted rule: %s') 
                                        % data['sg_id'])
            return True
        except Exception, e:
            redirect = reverse("horizon:amazon:securitygroups:index", args=[data['id']])
            messages.error(request,_(e.message))
            LOG.error(e.message)
            exceptions.handle_redirect(request,redirect)
 


