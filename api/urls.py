from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^update_state/([0-9]+)/$', views.update_state, name='update_state'),
    url(r'^fetch_state/([0-9]+)/$', views.fetch_state, name='fetch_state'),
    url(
        r'^update_channel/([0-9]+)/$',
        views.update_channel,
        name='update_channel'),
    url(r'^add_message/([0-9]+)/$', views.add_message, name='add_message'),
    url(r'^view_files/([0-9]+)/$', views.view_files, name='view_files')
]
