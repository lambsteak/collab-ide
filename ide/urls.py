
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.default, name='default'),
    url(r'^guestpage/$', views.guestpage, name='guestpage'),
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^welcome/$', views.welcome, name='welcome'),
    url(r'^([0-9]+)/$', views.index, name='index'),
    url(r'new_project/$', views.new_project, name='new_project'),
    url(r'^join_project/$', views.join_project, name='join_project'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^new_channel/([0-9]+)/$', views.new_channel, name='new_channel')
]
