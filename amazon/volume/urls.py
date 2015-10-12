from django.conf.urls import patterns, url
from .views import IndexView,CreateVolumeView,Attachments,DetailView,CreateSnapshotView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$',  CreateVolumeView.as_view(), name='create'),     
    url(r'^(?P<volume_id>[^/]+)/(?P<zone>[^/]+)/attach/$',
        Attachments.as_view(),
        name='attach'),
    url(r'^(?P<volume_id>[^/]+)/(?P<zone>[^/]+)/create_snapshot/$',
        CreateSnapshotView.as_view(),
        name='create_snapshot'),
    url(r'^(?P<volume_id>[^/]+)/$',
        DetailView.as_view(),
        name='detail'),
)
