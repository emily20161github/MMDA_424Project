from django.conf.urls import url

import views

urlpatterns = [
    url(r'^/twitter$', views.home, name='home'),
]