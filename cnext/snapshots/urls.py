from django.conf.urls import patterns, url

from .views import IndexView,CreateView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<instance_name>[^/]+)/(?P<instance_id>[^/]+)/(?P<provider>[^/]+)/(?P<region>[^/]+)/create/$', 
        CreateView.as_view(),name='create'),
)