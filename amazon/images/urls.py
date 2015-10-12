
from django.conf.urls import include, patterns, url
from amazon.images.ownedimage \
    import urls as ownedimage_urls
from amazon.images.amazonimage \
    import urls as amazonimage_urls
from amazon.images import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'', include(ownedimage_urls, namespace='ownedimage')),
    url(r'', include(amazonimage_urls, namespace='amazonimage')),

)
