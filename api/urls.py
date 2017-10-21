from django.conf.urls import url
from django.views.generic import TemplateView

from api import views

urlpatterns = [
    url(r'register/$', views.RegisterView.as_view(), name='register'),
    url(r'tickets/$', views.TicketsView.as_view(), name='register'),
    url(r'servers/$', views.ServersView.as_view(), name='servers'),

]