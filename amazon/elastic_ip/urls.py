from django.conf.urls import patterns, url
from .views  import IndexView, AllocateAddressView, AssociateAddressView,\
DisassociateAddressView, DetailView


urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^allocate/$',  AllocateAddressView.as_view(), name='allocate'),
                       url(r'^(?P<id>[^/]+)/(?P<domain>[^/]+)/associate/$',  
                           AssociateAddressView.as_view(),name='associate'),
                       url(r'^(?P<id>[^/]+)/disassociate/$',
                           DisassociateAddressView.as_view(),name='disassociate'),
                       url(r'^(?P<id>[^/]+)$',
                            DetailView.as_view(),name='detail'),
                        )

