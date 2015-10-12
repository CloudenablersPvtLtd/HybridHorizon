from django.conf.urls import patterns, url
from tenantsignreg.views import register, register_success, logout_page, activate
 
urlpatterns = patterns('',
    url(r'^logout/$', logout_page),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'), # If user is not login it will redirect to login page
    url(r'^$', register),
    url(r'^success/$', register_success),
    url(r'^activate/(?P<activation_key>[^/]+)/(?P<name>[^/]+)/$', activate),
)

 
