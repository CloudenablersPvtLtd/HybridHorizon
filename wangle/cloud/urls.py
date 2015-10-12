from django.conf.urls import include,patterns,url
from wangle.cloud.addcloud \
    import urls as addcloud_urls
from wangle.cloud.myclouds \
    import urls as myclouds_urls
from wangle.cloud import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'', include(addcloud_urls, namespace='addcloud')),
    url(r'', include(myclouds_urls, namespace='myclouds')),

)
