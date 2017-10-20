from django.conf.urls import url
from django.views.generic import TemplateView

from api import views

urlpatterns = [
    url(r'/$', TemplateView.as_view(), name='index'),
    url(r'register/$', views.RegisterView.as_view(), name='register'),
    url(r'tickets/$', views.TicketsView.as_view(), name='register'),
]