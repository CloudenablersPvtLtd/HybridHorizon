# Create your views here
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.conf import settings
from datetime import datetime
from hashlib import sha1
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from mongoengine import *
from django.utils.translation import ugettext_lazy as _
from wangle.role.forms import roledetail 
from cloud_mongo.trail import User,Tenant,clouds,actions,roleaccess
from tenantsignreg.forms import RegistrationForm
from config import mail_id, pwd


def register(request):
    if request.method == 'POST':
        
        form = RegistrationForm(request.POST)
        
        
        if form.is_valid():
            # To Create master collections when first tenant sign up
            tenant = Tenant.objects.all()
            if tenant.count() == 0:
                create_master_db_schema()
            username=form.data['username']
            password=form.data['password1']
            email=form.data['email']
            time = datetime.now().isoformat()
            plain = username + '\0' + time
            token = sha1(plain).hexdigest()
            tenant = Tenant(name=username)
            tenant.save()
            role_access = roleaccess.objects.all()
            access = role_access[0].access
            access.append("Edit User")
            envi1 = roledetail(roletype = "Tenant Admin",name="Tenant Admin", policy=[], access=access, tenantid=tenant.id)
            envi1.save()
            envi = User.create_user(username=email.lower(),email=email, password=password, roles=[envi1.id], key=token, tenantid=tenant.id,hp_attr = None)
            envi.save()   
            t = loader.get_template("activation_email.txt")
            c = Context({'name': username,
                         'activation_key' : token,
                         'email' : email,
                        'product_url' : "http://" + request.META["HTTP_HOST"] + "/signup/activate",
            })
            m = Mail(email)
            m.send_mail(t.render(c))            
            return HttpResponseRedirect('/signup/success')
          
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })
 
    return render_to_response(
    'register.html',
    variables,
    )

def register_success(request):
    return render_to_response(
    'registration_complete.html',)
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
"""
def myview(request):      
    if request.method == 'POST':  
        form = RegistrationForm(request.POST)
        # talk to the reCAPTCHA service  
        response = captcha.submit(  
            request.POST.get('recaptcha_challenge_field'),  
            request.POST.get('recaptcha_response_field'),  
            '[[ 6LfqW-wSAAAAADd7Kq9rpwHWUrTQuGjI34uTQSQY ]]',  
            request.META['REMOTE_ADDR'],)  
          
        # see if the user correctly entered CAPTCHA information  
        # and handle it accordingly.  
        if response.is_valid:  
            captcha_response = "YOU ARE HUMAN: %(data)s" % {'data' :  
        RegistrstionForm.data['username']}  
        else:  
            captcha_response = 'YOU MUST BE A ROBOT'  
          
        return render_to_response('register.html', {  
                'RegistrstionForm': RegistrationForm,  
                'captcha_response': captcha_response})  
    else:  
        RegistrationForm = RegistrationForm()  
    return render_to_response('register.html', {'RegistrationForm': RegistrationForm})

      

"""
def activate(request, activation_key, name):
    name1 = str(name)
    data = User.objects.all()
    data1 = roledetail.objects.all()
    g = data(key=activation_key).update_one(set__status="true")
    h = data1(name=name1).update_one(set__status="true")   
    return render_to_response(
    'activate_complete.html',)

 


class Mail:
    def __init__(self,email):
        self.email = email
    def send_mail(self, message):
        gmailUser = mail_id
        gmailPassword = pwd
        recipient = self.email

        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = "Activate your account "
        msg.attach(MIMEText(message))

        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()


def create_master_db_schema():
    """ Creates master collections. (clouds,actions,roleaccess) """
    allowed = [ 
        "Create Instance", 
        "Delete Instance", 
        "Create KP", 
        "Create SG", 
        "Delete KP",  
        "Delete SG", 
        "Start Instance", 
        "Stop Instance", 
        "Create Volume", 
        "Delete Volume", 
        "Attach Volume", 
        "Dettach Volume", 
        "Create Snapshot",
        "Delete Snapshot",
        "Allocate IP",
        "Release IP",
        "Associate IP",
        "Disassociate IP"
    ]
    access = [ 
        "Create Role", 
        "Delete Role", 
        "Create User", 
        "Delete User", 
        "Create Cloud", 
        "Delete Cloud", 
        "Add and Edit Policy", 
        "Add Role", 
        "Remove Policy", 
        "Remove Role", 
        "Edit Cloud", 
        "Edit Access"
    ]
    
    role_access = roleaccess(access=access)
    role_access.save()
    
    action = actions(allowed=allowed)
    action.save()
    
    cloud = clouds(name='Amazon',type=["Public"],credential_fields=["Public Key","Secret Key","Default Region"])
    cloud.save()
    cloud = clouds(name='Cnext',type=["Public"],credential_fields=["Public Key","Secret Key","Endpoint"])
    cloud.save()
    cloud = clouds(name='Hpcloud',type=["Public"],credential_fields=["Username","Password","Endpoint"])
    cloud.save()
    cloud = clouds(name='Openstack',type=["Private","Public"],credential_fields=["Username","Password","Endpoint"])
    cloud.save()
