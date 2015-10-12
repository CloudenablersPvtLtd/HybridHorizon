from django.conf.urls import patterns,url
from .views import IndexView,CreateUserView,AddRoleView,RemoveRoleView,ChangePasswordView,ResetPasswordView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateUserView.as_view(), name='create'),
    url(r'^(?P<user_id>[^/]+)/add_role/$',  AddRoleView.as_view(),
        name='add_role'),
    url(r'^(?P<user_id>[^/]+)/remove_role/$', RemoveRoleView.as_view(),
        name='remove_role'),
    url(r'^(?P<user_id>[^/]+)/change_password/$', ChangePasswordView.as_view(),
        name='change_password'),
    url(r'^(?P<user_id>[^/]+)/reset_password/$', ResetPasswordView.as_view(),
        name='reset_password'),
)
