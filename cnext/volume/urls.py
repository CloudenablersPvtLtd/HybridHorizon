from django.conf.urls import patterns, url
from .views import IndexView,CreateView,Attachments,DetailView,Dettachments

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$',  CreateView.as_view(), name='create'),
    url(r'^(?P<volume_id>[^/]+)/(?P<volume_name>[^/]+)/(?P<volume_provider>[^/]+)/attach/$',
        Attachments.as_view(),
        name='attach'),
    url(r'^(?P<volume_id>[^/]+)/dettach/$',
        Dettachments.as_view(),
        name='dettach'),
    url(r'^(?P<volume_id>[^/]+)/$',
        DetailView.as_view(),
        name='detail'),
)
