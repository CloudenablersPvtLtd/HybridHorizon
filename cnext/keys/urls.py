from django.conf.urls import patterns, url
from .views import manage_keys

urlpatterns = patterns('',
    url(r'^$', manage_keys, name='index')
)
