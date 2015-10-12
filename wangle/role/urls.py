from django.conf.urls import patterns,url
from .views import IndexView,CreateRoleView,\
                    AddPolicyView,RemovePolicyView, EditAccessView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateRoleView.as_view(), name='create'),
    url(r'^(?P<role_id>[^/]+)/add_policy/$',  AddPolicyView.as_view(),
        name='add_policy'),
    url(r'^(?P<policy_id>[^/]+)/remove_policy/$', RemovePolicyView.as_view(),
        name='remove_policy'),
    url(r'^(?P<access_id>[^/]+)/edit_access/$', EditAccessView.as_view(),
        name='edit_access'),
)
