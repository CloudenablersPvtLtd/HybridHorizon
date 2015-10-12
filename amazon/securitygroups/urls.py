from django.conf.urls import patterns, url

from .views import IndexView, CreateView, AddRuleView, DetailView, DeleteRuleView

urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^create/$', CreateView.as_view(), name='create'),
                       url(r'^(?P<group_name>[^/]+)/add_rule/$',  
                           AddRuleView.as_view(),name='add_rule'),
                       url(r'^(?P<securitygroups_id>[^/]+)$',
                            DetailView.as_view(),name='detail'),
                        url(r'^(?P<security_group_id>[^/]+)/delete_rule/$',  DeleteRuleView.as_view(),
                        name='delete_rule'),
                        )

