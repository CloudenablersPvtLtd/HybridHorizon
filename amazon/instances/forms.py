'''
Created on 08-Apr-2014

@author: annamalai
'''
from horizon import forms
from mongoengine.django.mongo_auth.models import get_user_document
from django.utils.translation import ugettext_lazy as _


class SwitchRegionForm(forms.SelfHandlingForm):
    region_list=[]
    def __init__(self, *args, **kwargs):
        region_list = kwargs["initial"]["region_choices"]
        super(SwitchRegionForm, self).__init__(*args,**kwargs)
        self.fields['region_name'] = forms.ChoiceField(label="Region List", choices=region_list)

    region_name = forms.ChoiceField(label=_("Region List"),
                                    required=True,
                                    choices = region_list,
                                    help_text=_("Select your region"))
    
    def handle(self, request, data):
        user = get_user_document().objects(username=request.user.username).first()
        user.awsendpoint = str(data['region_name'])
        user.save()        
        return True

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
        aws_clouds = sum([[y.cloudid for y in i.policy if 
                            y.cloudid.platform == "Amazon"] for i in request.user.roles], [])
        for cloud in aws_clouds:
            if str(cloud.id) == str(data['account_name']):
                user.awspublickey = cloud["cloud_meta"]["publickey"]
                user.awsprivatekey = cloud["cloud_meta"]["privatekey"]
                user.awsendpoint = cloud["cloud_meta"]["endpoint"]
                user.awsname = cloud["name"]
                user.save()
                return True
        return False


