from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'register/$', views.RegisterView.as_view(), name='register'),
    url(r'tickets/$', views.TicketsView.as_view(), name='register'),
    url(r'servers/$', views.ServersView.as_view(), name='servers'),
    url(r'servers/detail/$', views.ServerDetailView.as_view(), name='servers-detail'),

]