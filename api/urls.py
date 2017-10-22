from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'register/$', views.RegisterView.as_view(), name='register'),
    url(r'tickets/$', views.TicketsView.as_view(), name='register'),
    url(r'servers/$', views.ServersView.as_view(), name='servers'),
    url(r'servers/(?P<server_id>[\w\-]+)/reboot/hard/$', views.ServerHardReboot.as_view(), name='server-hard-reboot'),
    url(r'servers/(?P<server_id>[\w\-]+)/reboot/soft/$', views.ServerSoftReboot.as_view(), name='server-soft-reboot'),
    url(r'servers/(?P<server_id>[\w\-]+)/pause/$', views.ServerPause.as_view(), name='server-pause'),
    url(r'servers/(?P<server_id>[\w\-]+)/unpause/$', views.ServerUnpause.as_view(), name='server-unpause'),
    url(r'servers/(?P<server_id>[\w\-]+)/start/$', views.ServerStart.as_view(), name='server-start'),
    url(r'servers/(?P<server_id>[\w\-]+)/stop/$', views.ServerStop.as_view(), name='server-stop'),
    url(r'servers/detail/$', views.ServerDetailView.as_view(), name='servers-detail'),

]