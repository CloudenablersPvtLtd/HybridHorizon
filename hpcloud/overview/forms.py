
from horizon import forms
from mongoengine.django.mongo_auth.models import get_user_document
from django.utils.translation import ugettext_lazy as _
from cloud_mongo.trail import Hpclouddata

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
        hp_clouds = sum([[y.cloudid for y in i.policy if 
                            y.cloudid.platform == "Hpcloud"] for i in request.user.roles], [])
        for cloud in hp_clouds:
            if str(cloud.id) == str(data['account_name']):
                hpclouds = Hpclouddata.objects.all()
                for hpcloud in hpclouds:
                    if hpcloud.hpcloudid.id == cloud.id:
                        user.hp_attr = hpcloud
                user.hpname = cloud["name"]
                user.save()
                return True
        return False