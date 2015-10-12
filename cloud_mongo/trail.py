from mongoengine import *

from django.utils.encoding import smart_str
from django.contrib.auth.models import _user_has_perm, _user_get_all_permissions, _user_has_module_perms
from django.db import models
from django.contrib.contenttypes.models import ContentTypeManager
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from .date_time import datetime_now
import base64
from Crypto.Cipher import AES

REDIRECT_FIELD_NAME = 'next'

try:
    from django.contrib.auth.hashers import check_password, make_password
except ImportError:
    """Handle older versions of Django"""
    from django.utils.hashcompat import md5_constructor, sha_constructor

    def get_hexdigest(algorithm, salt, raw_password):
        raw_password, salt = smart_str(raw_password), smart_str(salt)
        if algorithm == 'md5':
            return md5_constructor(salt + raw_password).hexdigest()
        elif algorithm == 'sha1':
            return sha_constructor(salt + raw_password).hexdigest()
        raise ValueError('Got unknown password algorithm type in password')

    def check_password(raw_password, password):
        algo, salt, hash = password.split('$')
        return hash == get_hexdigest(algo, salt, raw_password)

    def make_password(raw_password):
        from random import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random()), str(random()))[:5]
        hash = get_hexdigest(algo, salt, raw_password)
        return '%s$%s$%s' % (algo, salt, hash)


def set_session_from_user(request, user):
    user_roles = []
    user_roleaccess = []
    user_ploicies ={}
    for role in user.roles:
        user_roles.append(role.roletype)
        for role_access in role.access:
            if role_access not in user_roleaccess:
                user_roleaccess.append(role_access)
    for role in user.roles:
        for policy in role.policy:
            cloud = tenantclouds.objects(id = policy.cloudid.id).first()
            if cloud.platform == "Cnext":
                if cloud.name in user_ploicies:
                    user_ploicies[str(cloud.name)].append(((policy.provider).lower(),(policy.region).lower(),policy.allowed))
                else:
                    user_ploicies[str(cloud.name)] = [((policy.provider).lower(),(policy.region).lower(),policy.allowed)]
            else:
                user_ploicies[str(cloud.name)] = policy.allowed
    if user.hp_attr:
        request.session['token'] = user.hp_attr.token
        request.session['user_id'] = user.id
        request.session['region_endpoint'] = user.hp_attr.endpoint
    else:
        request.session['token'] = user.token
        request.session['user_id'] = user.id
        request.session['region_endpoint'] = user.endpoint
    request.session['user_roles'] = user_roles
    request.session['user_roleaccess'] = user_roleaccess
    request.session['user_policies'] = user_ploicies

def refresh_session_policies(request, user):
    user_roles = []
    user_roleaccess = []
    user_ploicies ={}
    for role in user.roles:
        user_roles.append(role.roletype)
        for role_access in role.access:
            if role_access not in user_roleaccess:
                user_roleaccess.append(role_access)
    for role in user.roles:
        for policy in role.policy:
            cloud = tenantclouds.objects(id = policy.cloudid.id).first()
            if cloud.platform == "Cnext":
                if cloud.name in user_ploicies:
                    user_ploicies[str(cloud.name)].append(((policy.provider).lower(),(policy.region).lower(),policy.allowed))
                else:
                    user_ploicies[str(cloud.name)] = [((policy.provider).lower(),(policy.region).lower(),policy.allowed)]
            else:
                user_ploicies[str(cloud.name)] = policy.allowed
    request.session['user_roles'] = user_roles
    request.session['user_roleaccess'] = user_roleaccess
    request.session['user_policies'] = user_ploicies

def create_user_from_token(request, token, endpoint, services_region=None):
    return User(id=token.user['id'],
                token=token,
                user=token.user['name'],
                user_domain_id=token.user_domain_id,
                project_id=token.project['id'],
                project_name=token.project['name'],
                domain_id=token.domain['id'],
                domain_name=token.domain['name'],
                enabled=True,
                service_catalog=token.serviceCatalog,
                roles=token.roles,
                endpoint=endpoint,
                services_region=services_region)


class DocToken(EmbeddedDocument):

    user = DictField()
    user_domain_id = StringField()
    id = StringField(verbose_name=_('token_id'))
    project = DictField()
    tenant = DictField()
    domain = DictField()
    serviceCatalog = ListField()
    roles = ListField()
    
    
class ContentType(Document):
    name = StringField(max_length=100)
    app_label = StringField(max_length=100)
    model = StringField(max_length=100, verbose_name=_('python model class name'),
                        unique_with='app_label')
    objects = ContentTypeManager()

    class Meta:
        verbose_name = _('content type')
        verbose_name_plural = _('content types')

    def __unicode__(self):
        return self.name

    def model_class(self):
        "Returns the Python model class for this type of content."
        return models.get_model(self.app_label, self.model)

    def get_object_for_this_type(self, **kwargs):
        """
        Returns an object of this type for the keyword arguments given.
        Basically, this is a proxy around this object_type's get_object() model
        method. The ObjectNotExist exception, if thrown, will not be caught,
        so code that calls this method should catch it.
        """
        return self.model_class()._default_manager.using(self._state.db).get(**kwargs)

    def natural_key(self):
        return (self.app_label, self.model)


class SiteProfileNotAvailable(Exception):
    pass


class PermissionManager(models.Manager):
    def get_by_natural_key(self, codename, app_label, model):
        return self.get(
            codename=codename,
            content_type=ContentType.objects.get_by_natural_key(app_label, model)
        )


class Permission(Document):
    """The permissions system provides a way to assign permissions to specific
    users and groups of users.

    The permission system is used by the Django admin site, but may also be
    useful in your own code. The Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add"
          form and add an object.
        - The "change" permission limits a user's ability to view the change
          list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.

    Permissions are set globally per type of object, not per specific object
    instance. It is possible to say "Mary may change news stories," but it's
    not currently possible to say "Mary may change news stories, but only the
    ones she created herself" or "Mary may only change news stories that have
    a certain status or publication date."

    Three basic permissions -- add, change and delete -- are automatically
    created for each Django model.
    """
    name = StringField(max_length=50, verbose_name=_('username'))
    content_type = ReferenceField(ContentType)
    codename = StringField(max_length=100, verbose_name=_('codename'))
        # FIXME: don't access field of the other class
        # unique_with=['content_type__app_label', 'content_type__model'])

    objects = PermissionManager()

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __unicode__(self):
        return u"%s | %s | %s" % (
            unicode(self.content_type.app_label),
            unicode(self.content_type),
            unicode(self.name))

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()
    natural_key.dependencies = ['contenttypes.contenttype']


class Group(Document):
    """Groups are a generic way of categorizing users to apply permissions,
    or some other label, to those users. A user can belong to any number of
    groups.

    A user in a group automatically has all the permissions granted to that
    group. For example, if the group Site editors has the permission
    can_edit_home_page, any user in that group will have that permission.

    Beyond permissions, groups are a convenient way to categorize users to
    apply some label, or extended functionality, to them. For example, you
    could create a group 'Special users', and you could write code that would
    do special things to those users -- such as giving them access to a
    members-only portion of your site, or sending them members-only
    e-mail messages.
    """
    name = StringField(max_length=80, unique=True, verbose_name=_('name'))
    permissions = ListField(ReferenceField(Permission, verbose_name=_('permissions'), required=False))

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __unicode__(self):
        return self.name

class Tenant(Document):
    
    name = StringField(max_length=50, unique=True,  verbose_name=_('Tenantname'))

class clouds(Document):
    name = StringField(max_length=50, unique=True,  verbose_name=_('AvailableCloudName'))
    type = ListField(verbose_name=_('Type'))
    credential_fields = ListField()

class roleaccess(Document):
    access = ListField(verbose_name=_('RoleAccess'))

class actions(Document):
    allowed = ListField(verbose_name=_('Allowed Action'))

class tenantclouds(Document):
    
    name = StringField(max_length=50, unique=False,  verbose_name=_('cloudname'))
    platform = StringField(max_length=20,verbose_name=_('platform'))
    cloud_type = StringField(max_length=50, verbose_name=_('cloudtype'))
    cloud_meta = DictField(verbose_name=_('CloudMetadata'))
    tenantid = ReferenceField(Tenant)
    cloudid = ReferenceField(clouds)
    
    class Meta:
        verbose_name = _('cloud')
        verbose_name_plural = _('clouds')
        
    def __unicode__(self):
        return self.name
   
class Roles(Document):
    
    id = StringField(max_length=30,
                             verbose_name=_('roleid'))
    name = StringField(max_length=50, unique=True,  verbose_name=_('rolename'))
    
    tenant_id = ReferenceField(Tenant)
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __unicode__(self):
        return self.name

class PolicyDoc(EmbeddedDocument):
    
    cloudid = ReferenceField(tenantclouds)
    provider = StringField(verbose_name=_('Provider'))
    region =  StringField(verbose_name=_('Region'))
    allowed = ListField(verbose_name=_('Allowed Action'))


class roledetail(Document):
    
    name = StringField(max_length=50,verbose_name=_('Rolename'))
    roletype = StringField(max_length=20,verbose_name=_('Roletype'))
    policy = ListField(EmbeddedDocumentField(PolicyDoc))
    access = ListField(verbose_name=_('RoleAccess'))
    status = BooleanField(default=False)
    tenantid = ReferenceField(Tenant)

  
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        
    def __unicode__(self):
        return self.name


class Cloud_Per(Document):
    
    id = StringField(max_length=30,
                             verbose_name=_('cloudid'))
    name = StringField(max_length=50, unique=True,  verbose_name=_('Cloudname'))
    
    endpoint = StringField(max_length=50, required=False,  verbose_name=_('endpoint'))
    
    accesskey = StringField(max_length=50, verbose_name=_('accesskey'))
    privatekey = StringField(max_length=50, required=False,  verbose_name=_('privatekey'))
    
    class Meta:
        verbose_name = _('cloud_per')
        verbose_name_plural = _('cloud_pers')

    def __unicode__(self):
        return self.name



class UserManager(models.Manager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, e-mail and password.
        """
        now = datetime_now()
        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])

        user = self.model(username=username, email=email, is_staff=False,
                          is_active=True, is_superuser=False, last_login=now,
                          date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        u = self.create_user(username, email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

class Hpclouddata(Document):
    
    token = EmbeddedDocumentField(DocToken)
    authorized_tenants = ListField(
                             verbose_name=_('authorised tenants'))    
    service_catalog = ListField(verbose_name=_('service catalog')) 
    services_region = StringField(max_length=30,
                             verbose_name=_('service region'))    
    tenant_id =  StringField(max_length=100,
                             verbose_name=_('tenant_id'))
    tenant_name = StringField(max_length=30,
                             verbose_name=_('tenant_name'))
    project_id =  StringField(max_length=100,
                             verbose_name=_('project_id'))
    project_name = StringField(max_length=30,
                             verbose_name=_('project_name'))
    endpoint = StringField(max_length=100,
                             verbose_name=_('endpoint')) 
    hpcloudid = ReferenceField(tenantclouds)  


class User(Document):
    """A User document that aims to mirror most of the API specified by Django
    at http://docs.djangoproject.com/en/dev/topics/auth/#users
    """
    username = StringField(max_length=50, required=True,
                           verbose_name=_('username'),
                           help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))

    id = StringField(max_length=30,
                             verbose_name=_('id'))
    
    status = BooleanField(default = False)
    key = StringField(max_length=50, verbose_name=_('tenant_actkey'))

    token = EmbeddedDocumentField(DocToken)
    user_domain_id = StringField(max_length=30,
                             verbose_name=_('user_domain_id'))
    domain_id = StringField(max_length=30,
                             verbose_name=_('domain_id'))
    domain_name = StringField(max_length=30,
                             verbose_name=_('domain_name'))
    project_id =  StringField(max_length=100,
                             verbose_name=_('project_id'))
    project_name = StringField(max_length=30,
                             verbose_name=_('project_name'))
    service_catalog = ListField(verbose_name=_('service catalog'))
    services_region = StringField(max_length=30,
                             verbose_name=_('service region'))
    
    endpoint = StringField(max_length=100,
                             verbose_name=_('endpoint'))
    cnextpublickey = StringField(max_length=100,
                             verbose_name=_('cnextpublickey'))
    cnextprivatekey = StringField(max_length=200,
                             verbose_name=_('cnextprivatekey'))
    cnextendpoint = StringField(max_length=100,
                             verbose_name=_('cnextendpoint'))
    cnextname = StringField(max_length=100,
                             verbose_name=_('cnextname'))
    awspublickey = StringField(max_length=100,
                             verbose_name=_('awspublickey'))
    awsprivatekey = StringField(max_length=200,
                             verbose_name=_('awsprivatekey'))
    awsendpoint = StringField(max_length=100,
                             verbose_name=_('awsendpoint'))
    awsname = StringField(max_length=100,
                             verbose_name=_('awsname'))
    authorized_tenants = ListField(
                             verbose_name=_('authorised tenants'))

    first_name = StringField(max_length=30,
                             verbose_name=_('first name'))

    last_name = StringField(max_length=30,
                            verbose_name=_('last name'))
    email = EmailField(verbose_name=_('e-mail address'))
    password = StringField(max_length=128,
                           verbose_name=_('password'),
                           help_text=_("Use '[algo]$[iterations]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    is_staff = BooleanField(default=False,
                            verbose_name=_('staff status'),
                            help_text=_("Designates whether the user can log into this admin site."))
    is_active = BooleanField(default=True,
                             verbose_name=_('active'),
                             help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    is_superuser = BooleanField(default=False,
                                verbose_name=_('superuser status'),
                                help_text=_("Designates that this user has all permissions without explicitly assigning them."))
    last_login = DateTimeField(default=datetime_now,
                               verbose_name=_('last login'))
    date_joined = DateTimeField(default=datetime_now,
                                verbose_name=_('date joined'))

    user_permissions = ListField(ReferenceField(Permission), verbose_name=_('user permissions'),
                                                help_text=_('Permissions for the user.'))
    
    roles = ListField(ReferenceField(roledetail), verbose_name=_('user roles'),
                                                help_text=_('Roles for the user.'))
    cloud_per = ListField(ReferenceField(Cloud_Per), verbose_name=_('user clouds'),
                                                help_text=_('clouds for the user.'))


    tenant_id =  StringField(max_length=100,
                             verbose_name=_('project_id'))
    tenant_name = StringField(max_length=30,
                             verbose_name=_('project_name'))
    
    tenantid = ReferenceField(Tenant)
    hp_attr = ReferenceField(Hpclouddata)
    hpname = StringField(max_length=100,
                             verbose_name=_('hpname'))
    openstackname = StringField(max_length=100,
                             verbose_name=_('openstackname'))
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    meta = {
        'allow_inheritance': True,
        'indexes': [
            {'fields': ['username'], 'unique': True, 'sparse': True}
        ]
    }



    def __unicode__(self):
        return self.username

    def get_full_name(self):
        """Returns the users first and last names, separated by a space.
        """
       
        full_name = u'%s %s' % (self.first_name or '', self.last_name or '')
        return full_name.strip()

    def is_anonymous(self):
       
        return False

    def is_authenticated(self):
        
        return True

    def set_password(self, raw_password):
        """Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        self.password = make_password(raw_password)
        self.save()
        return self

    def check_password(self, raw_password):
        """Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        return check_password(raw_password, self.password)

    @classmethod
    def create_user(cls, username, password,  roles, tenantid, key=None,email=None,hp_attr = None):
        """Create (and save) a new user with the given username, password and
        email address.
        """
        now = datetime_now()
        # Normalize the address by lowercasing the domain part of the email
        # address.
        if email is not None:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])

        user = cls(username=username, email=email,roles = roles, date_joined=now, tenantid = tenantid, hp_attr = hp_attr)
        if (key == None):
            user.status = True
        user.set_password(password)
        user.key = key
        user.save()
        return user
    
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """
        return _user_has_perm(self, perm, obj)
    
    def has_a_matching_perm(self, perm_list, obj=None):
        """
        Returns True if the user has one of the specified permissions. If
        object is passed, it checks if the user has any of the required perms
        for this object.
        """
        # If there are no permissions to check, just return true
        if not perm_list:
            return True
        # Check that user has at least one of the required permissions.
        for perm in perm_list:
            if self.has_perm(perm, obj):
                return True
        return False

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through his/her
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)
   

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has all of the specified permissions.
        Tuples in the list will possess the required permissions if
        the user has a permissions matching one of the elements of
        that tuple
        """
        # If there are no permissions to check, just return true
       
        if not perm_list:
            return True
   
        for perm in perm_list:
            if isinstance(perm, basestring):
                # check that the permission matches
                if not self.has_perm(perm, obj):
                    return False
            else:
                # check that a permission in the tuple matches
                if not self.has_a_matching_perm(perm, obj):
                    return False
        return True


   

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)

def encode_decode(password,method):
    BLOCK_SIZE = 16
    PADDING = '{'
    cipher = AES.new('Cl0uden@bler$l@b')
    
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    
    if method == "encode":
        return EncodeAES(cipher, password)
    elif method == "decode":
        return DecodeAES(cipher, password)
    else:
        return password
