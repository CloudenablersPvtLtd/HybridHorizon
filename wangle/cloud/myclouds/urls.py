from django.conf.urls import patterns,url
from .views import EditCloudView

VIEWS_MOD = ('wangle.cloud.myclouds.views')

urlpatterns = patterns(VIEWS_MOD,
     url(r'^(?P<cloud_id>[^/]+)/edit_cloud/$', EditCloudView.as_view(),
        name='edit_cloud'),
)




