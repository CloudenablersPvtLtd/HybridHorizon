from horizon import forms,workflows,messages
from mongoengine import *
from django.utils.translation import ugettext_lazy as _  
from cloud_mongo.trail import User,make_password,\
    check_password
from horizon.utils import validators
from wangle.role.forms import roledetail
from datetime import datetime
from hashlib import sha1
from django.template import Context, loader
from django.conf import settings
from tenantsignreg.views import Mail
import logging
from django.core.validators import RegexValidator

LOG = logging.getLogger(__name__)

   
class CreateUserAction(workflows.Action):
    username = forms.CharField(max_length=80, label=_("User Name"),
                               validators=[RegexValidator(r'^[\w]*$',
                                                          message='Username must be alphanumeric without spaces',
                                                          code='Invalid Username')]
                               )
    
    roles = forms.MultipleChoiceField(label=_("Roles"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Create user with these "
                                                   "roles."))
    password = forms.RegexField(
        label=_("Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False))
    email = forms.EmailField(label=_("Email ID"),
             required=True)


    def populate_roles_choices(self, request, context):
        roles = []
        success = []
        try:
            if request.user.roles:
                for role in  request.user.roles:
                    if (role.name == "Tenant Admin") & (role.roletype == "Tenant Admin"):
                        success.append("Tenant Admin")
                    else:
                        success.append("Member")
                if "Tenant Admin" in success:
                    rolelist = roledetail.objects(tenantid=request.user.tenantid.id)
                    roles = [(role.id, role.name) for role in rolelist]
                else:   
                    rolelist = roledetail.objects(tenantid=request.user.tenantid.id)
                    for role in rolelist:
                        if (role.name == "Tenant Admin") & (role.roletype == "Tenant Admin"):
                            pass
                        else:
                            roles.append((role.id, role.name))
            else:
                roles = []
                                  
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            roles = []
        return roles

    class Meta:
        name = _("Create User")

class CreateUser(workflows.Step):
    action_class = CreateUserAction 
    
    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['email'] = data.get("email", None)
            context['password'] = data.get("password", None)
            context['username'] = data.get("username", None)
            context['role'] = data.get("roles", "")
        return context 

class CreateUserForm(workflows.Workflow):
    slug = "create_user"
    name = _("Create User")
    finalize_button_name = _("Create")
    success_url = "horizon:wangle:users:index"
    default_steps = (CreateUser, )
    
        
    def handle(self, request, context):
        username = context.get('username', None) 
        roles = context.get('role', None)
        email = context.get('email', None)
        password = context.get('password', None)
        try:
            time = datetime.now().isoformat()
            plain = username + '\0' + time
            activation_key = sha1(plain).hexdigest()
            tenant_db = User.create_user(username=username.lower(), password= password, roles = roles,email = email, tenantid=request.user.tenantid,key=activation_key)
            tenant_db.save()
            t = loader.get_template("activation_email.txt")
            c = Context({'name': username,
                         'activation_key' : activation_key,
                         'email' : email,
                        'product_url' : "http://" + request.HTTP_HOST + + "/signup/activate",
            })
            m = Mail(email)
            m.send_mail(t.render(c))
            return True
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
        return False


class EditUserAccessControlsAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    
    roles = forms.MultipleChoiceField(label=_("Roles"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Create user with these "
                                                   "roles."))

    def populate_roles_choices(self, request, context):
        try:
            id = context['id']
            rolelist = []
            success = []
            user_rolelist = User.objects(id=id).first()
            if request.user.roles:
                for role in  request.user.roles:
                    if (role.name == "Tenant Admin") & (role.roletype == "Tenant Admin"):
                        success.append("Tenant Admin")
                    else:
                        success.append("Member")
                aval_rolelist = roledetail.objects(tenantid=request.user.tenantid.id)
                if "Tenant Admin" in success:
                    for i in aval_rolelist:
                        if i in user_rolelist.roles:
                            pass
                        else:
                            rolelist.append(i) 
                else:
                    for i in aval_rolelist:
                        if i in user_rolelist.roles:
                            pass
                        else:
                            if i.roletype == "Tenant Admin":
                                pass
                            else:
                                rolelist.append(i) 
                roles = [(role.id, role.name) for role in rolelist]
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            roles = []
        return roles
    
    class Meta:
        name = _("Add Role")

class EditUserAccessControls(workflows.Step):
    action_class = EditUserAccessControlsAction 
    contributes = ("id",)

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['id'] = data.get("id","")
            context['role'] = data.get("roles", "")
        return context 

  
    
class AddRole(workflows.Workflow):
    slug = "add_role"
    name = _("ADD ROLE")
    finalize_button_name = _("ADD")
    success_url = "horizon:wangle:users:index"
    default_steps = (EditUserAccessControls, )
      
    def handle(self, request, context):
        id = context.get('id', None) 
        roles = context.get('role', None)
        try:
            for i in roles:
                User.objects(id=id).update(push__roles=i)
            return True
  
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False

class RemoveRoleAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    
    roles = forms.MultipleChoiceField(label=_("Roles"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Create user with these "
                                                   "roles."))

    def populate_roles_choices(self, request, context):
        try:
            id = context['id']
            rolelist = []
            success = []
            user_rolelist = User.objects(id=id).first()
            if request.user.roles:
                for role in  request.user.roles:
                    if (role.name == "Tenant Admin") & (role.roletype == "Tenant Admin"):
                        success.append("Tenant Admin")
                    else:
                        success.append("Member")
                aval_rolelist = roledetail.objects(tenantid=request.user.tenantid.id)
                if "Tenant Admin" in success:
                    for i in aval_rolelist:
                        if i in user_rolelist.roles:
                            rolelist.append(i)
                        else:
                            pass 
                else:
                    for i in aval_rolelist:
                        if i in user_rolelist.roles:
                            if i.roletype == "Tenant Admin":
                                pass
                            else:
                                rolelist.append(i)
                        else:
                            pass
                roles = [(role.id, role.name) for role in rolelist]
           
        except Exception, e:
            messages.error(request,_(e.message))
            LOG.error(e.message)
            roles = []
        return roles
    
    class Meta:
        name = _("Remove Role")   

class RemoveRoleControls(workflows.Step):
    action_class = RemoveRoleAction 
    contributes = ("id",)

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['id'] = data.get("id","")
            context['role'] = data.get("roles", "")
        return context 


    
class RemoveRole(workflows.Workflow):
    
    slug = "remove_role"
    name = _("REMOVE ROLE")
    finalize_button_name = _("REMOVE")
    success_url = "horizon:wangle:users:index"
    default_steps = (RemoveRoleControls, )
      
    def handle(self, request, context):
        id = context.get('id', None) 
        roles = context.get('role', None)
        try:
            for i in roles:
                User.objects(id=id).update(pull__roles=i)
            return True
  
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False

class PasswordEditAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    oldpassword= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    email = forms.EmailField(required=True,max_length=100, label=_("Email"))
    new_password = forms.RegexField(
        label=_("New Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    old_password = forms.CharField(
        label=_("Old Password"),
        required=False,
        widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        name = _("Change Password")

    
    
class PasswordEdit(workflows.Step):
    action_class = PasswordEditAction
    contributes = ("id",'email','new_password','old_password','oldpassword')

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['email'] = data.get("email", None)
            context['new_password'] = data.get("new_password", None)
            context['old_password'] = data.get("old_password", None)
            context['oldpassword'] = data.get("oldpassword", None)
        return context

class ChangePassword(workflows.Workflow):
    
    slug = "change_password"
    name = _("Change Email/Password")
    finalize_button_name = _("SAVE")
    success_url = "horizon:wangle:users:index"
    default_steps = (PasswordEdit, )
    
    def handle(self, request, context):
        id = context.get('id', None) 
        email = context.get('email',None)
        password = context.get('new_password',None)
        old_password = context.get('old_password',None)
        oldpassword = context.get('oldpassword',None)
        try:
            if password != '':
                encrypted_pwd = make_password(password)
                if check_password(old_password,oldpassword):
                    user_pwd = User.objects(id = id).update(set__password = encrypted_pwd)
                else:
                    return False
            if email is not None:
                try:
                    email_name, domain_part = email.strip().split('@', 1)
                except ValueError:
                    pass
            else:
                email = '@'.join([email_name, domain_part.lower()])
            user_email = User.objects(id = id).update(set__email = email)
            return True
  
        except Exception,e:            
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False


class PasswordResetAction(workflows.Action):

    id= forms.CharField(widget=forms.HiddenInput(),
                                required=False)
    username = forms.CharField(required=False, label=_("User Name"),
                               widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    new_password = forms.RegexField(
        label=_("New Password"),
        required=True,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    
    class Meta:
        name = _("Reset Password")

    
    
class PasswordReset(workflows.Step):
    action_class =PasswordResetAction
    contributes = ("id",'username','new_password')

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['new_password'] = data.get("new_password", None)
            context['username'] = data.get("username", None)
        return context

class ResetPassword(workflows.Workflow):
    
    slug = "reset_password"
    name = _("Reset Password")
    finalize_button_name = _("SAVE")
    success_url = "horizon:wangle:users:index"
    default_steps = (PasswordReset, )
    
    def handle(self, request, context):
        id = context.get('id', None) 
        password = context.get('new_password',None)
        try:
            if password is not None:
                encrypted_pwd = make_password(password)
                user_pwd = User.objects(id = id).update(set__password = encrypted_pwd)
            return True
  
        except Exception,e:
            messages.error(request,_(e.message))
            LOG.error(e.message)

        return False