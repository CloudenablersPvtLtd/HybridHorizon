from django.conf.urls import patterns,url
from .views import CreateCloudView

VIEWS_MOD = ('wangle.cloud.addcloud.views')

urlpatterns = patterns(VIEWS_MOD,
     url(r'^(?P<cloud_id>[^/]+)/create/$', CreateCloudView.as_view(), name='create'),

)




