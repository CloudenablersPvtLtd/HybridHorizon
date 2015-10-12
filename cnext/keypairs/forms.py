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

import re
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions, forms, messages
from horizon.utils import fields
from cnext_api import api
from cnext.resource import provider_keypairs_choices,region_keypairs_choices
from mongoengine.django.mongo_auth.models import get_user_document

NEW_LINES = re.compile(r"\r|\n")

class Regionlist():
    def __init__(self, provider, region):
        self.name = region
        self.provider = provider
        self.region = region


class CreateKeypair(forms.SelfHandlingForm):

    name = forms.CharField(max_length="20",
                           label=_("Keypair Name"),
                           validators=[validators.validate_slug],
                           error_messages={'invalid': _('Keypair names may '
                                'only contain letters, numbers, underscores '
                                'and hyphens.')})
    key_provider_list = forms.ChoiceField(
        label=_("Providers List"),
        required=True,
        )
    key_region_list = forms.ChoiceField(
        label=_("Regions List"),
        required=True,
        widget=fields.SelectWidget(data_attrs=('provider', 'region', ),
                                   transform=lambda x: ("%s " % (x.name)))
        )

    def handle(self, request, data):
        return True  # We just redirect to the download view.
    def __init__(self, request, *args, **kwargs):
        forms.SelfHandlingForm.__init__(self, request, *args, **kwargs)
        provider_list = api.providers(self.request)
        region_list = api.region(self.request)
        p = [("", _("Select Provider"))]
        for provider in provider_list:
            if provider.provider in provider_keypairs_choices:
                p.append((provider.provider.lower(),provider.provider))
        t = tuple(p)
        tuple_providers = t
        self.fields['key_provider_list'].choices = tuple_providers
        r = [("", _("Select Region"))]
        for region in region_list:
            if region.name in region_keypairs_choices:
                r.append((region.name,Regionlist(region.provider,region.name)))
        r = tuple(r)
        tuple_regions = r
        self.fields['key_region_list'].choices = tuple_regions


class ImportKeypair(forms.SelfHandlingForm):
    name = forms.CharField(max_length="20", label=_("Keypair Name"),
                 validators=[validators.RegexValidator('\w+')])
    public_key = forms.CharField(label=_("Public Key"), widget=forms.Textarea)

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            data['public_key'] = NEW_LINES.sub("", data['public_key'])
            keypair = api.keypairs(request)
            messages.success(request, _('Successfully imported public key: %s')
                                       % data['name'])
            return keypair
        except Exception:
            exceptions.handle(request, ignore=True)
            self.api_error(_('Unable to import keypair.'))
            return False

class AccountChangeForm(forms.SelfHandlingForm):
    accounts_list=[]
    def __init__(self, *args, **kwargs):
        accounts_list = kwargs["initial"]["account_choices"]
        super(AccountChangeForm, self).__init__(*args,**kwargs) 
        self.fields['account_name'] = forms.ChoiceField(label="Account Name", choices=accounts_list)
    
    account_name = forms.ChoiceField(label=_("Account Name"),
                                    required=True,
                                    choices = accounts_list,
                                    help_text=_("Select your account"))
    
    def handle(self, request, data):
        user = get_user_document().objects(username=request.user.username).first()
        cnext_clouds = sum([[y.cloudid for y in i.policy if 
                            y.cloudid.platform == "Cnext"] for i in request.user.roles], [])
        for cloud in cnext_clouds:
            if str(cloud.id) == str(data['account_name']):
                user.cnextpublickey = cloud["cloud_meta"]["publickey"]
                user.cnextprivatekey = cloud["cloud_meta"]["privatekey"]
                user.cnextendpoint = cloud["cloud_meta"]["endpoint"]
                user.cnextname = cloud["name"]
                user.save()
                return True
        return False
