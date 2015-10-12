from django.conf.urls import patterns, url

from .views import IndexView, LaunchInstanceView, DetailView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^launch$', LaunchInstanceView.as_view(), name='launch'),
    url(r'^(?P<instance_id>[^/]+)/$', DetailView.as_view(), name='detail'),
)
