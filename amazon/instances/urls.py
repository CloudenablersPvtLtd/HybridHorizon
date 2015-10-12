from django.conf.urls import patterns, url

from .views import IndexView,LaunchInstanceView,DetailView,RegionSwitch,AccountChange


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^launch$', LaunchInstanceView.as_view(), name='launch'),
    url(r'^(?P<instance_id>[^/]+)/$', DetailView.as_view(), name='detail'),
    url(r'region/region_change',RegionSwitch.as_view(),name = 'region'),
    url(r'account/account_change',AccountChange.as_view(),name = 'account'),
)
