from django.conf.urls import patterns, url

from .views import IndexView, CreateView, GenerateView, DownloadView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$',  CreateView.as_view(), name='create'),
    url(r'^(?P<keypair_name>[^/]+)/download/$',
        DownloadView.as_view(), name='download'),
    url(r'^(?P<keypair_name>[^/]+)/generate/$',
        GenerateView.as_view(), name='generate'),
)
