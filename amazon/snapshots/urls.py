from django.conf.urls import patterns, url
from .views import IndexView, DetailView, CreateSnapshotView, CreateVolumeView, CopySnapshotView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$',  CreateSnapshotView.as_view(), name='create'),     
    url(r'^(?P<snapshot_id>[^/]+)/(?P<zone>[^/]+)/create_volume/$',
        CreateVolumeView.as_view(),
        name='create_volume'),
    url(r'^(?P<snapshot_id>[^/]+)/(?P<zone>[^/]+)/copy_snapshot/$',
        CopySnapshotView.as_view(),
        name='copy_snapshot'),
    url(r'^(?P<snapshot_id>[^/]+)/$',
        DetailView.as_view(),
        name='detail'),
)
