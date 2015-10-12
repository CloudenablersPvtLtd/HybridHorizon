from django.conf.urls import patterns, url

from amazon.images.amazonimage.views import DetailView
  
VIEWS_MOD = ('amazon.images.amazonimage.views')
  
urlpatterns = patterns(VIEWS_MOD,
        url(r'^(?P<image_id>[^/]+)/$',DetailView.as_view(), name='detail',),
  
)
