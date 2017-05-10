from django.conf.urls import url

import views

urlpatterns = [
    url(r'^twitter$', views.home, name='home'),
    url(r'^test$', views.test, name='test'),
    url(r'^add_metadata$', views.meta, name='meta')
]