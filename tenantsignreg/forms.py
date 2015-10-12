
from mongoengine import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from cloud_mongo.trail import User,Tenant
from django.core.validators import RegexValidator


class RegistrationForm(forms.Form):
   
    username = forms.CharField(required=True, max_length=30, label=_("Tenant Name"),
                               validators=[RegexValidator(r'^[\w]*$',
                                                          message='Name must be alphanumeric without spaces',
                                                          code='Invalid Tenant Name')])
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=50)), label=_("Tenant Email Address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Confirm Password"))
   

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2  

 
    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('Tenant with email "%s" already exists' % email)
        return email
    
    def clean_username(self, *args, **kwargs):
        username = self.cleaned_data['username']
        if Tenant.objects.filter(name=username).count() > 0:
            raise forms.ValidationError('Tenant with name "%s" already exists' % username)
        return username



