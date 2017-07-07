from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'imageManagement'

urlpatterns = [
    url(r'^post/$', views.Index.as_view(), name='index'),
    url(r'^getImages/$', views.get_images, name='get_images'),
    url(r'^getImage/(?P<image_name>[a-zA-Z0-9._-]+)/$', views.get_images, name='get_images'),
    url(r'^delete/(?P<image_name>[a-zA-Z0-9._-]+)/$', views.delete, name='delete'),
    url(r'^patch/(?P<image_name_delete>[a-zA-Z0-9._-]+)$', views.patch, name='patch'),
    url(r'^generateToken/$', views.generate_token, name='generate_token'),
]

    

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = [
#     # ex: /polls/
#     url(r'^$', views.index, name='index'),
#     # ex: /polls/5/
#     url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
#     # ex: /polls/5/results/
#     url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
#     # ex: /polls/5/vote/
#     url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
# ]

