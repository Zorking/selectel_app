from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'register/$', views.RegisterView.as_view(), name='register')
]