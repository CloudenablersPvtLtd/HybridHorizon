from django.conf.urls import patterns, url

from cnext.images import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<image_id>[^/]+)/update/$',
        views.UpdateView.as_view(), name='update'),
    url(r'^(?P<image_id>[^/]+)/$', views.DetailView.as_view(), name='detail'),
)
