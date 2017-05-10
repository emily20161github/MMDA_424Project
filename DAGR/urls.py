from django.conf.urls import url

import views

urlpatterns = [
	url(r'^home$', views.home, name='home'),
    url(r'^twitter$', views.twitter, name='twitter'),
    url(r'^test$', views.test, name='test'),
    url(r'^add_metadata$', views.meta, name='meta'),
    url(r'^add_website$', views.add_website, name='add_website'),
    url(r'^query$', views.query, name='query'),
    url(r'^orphan$', views.orphan, name='orphan'),
    url(r'^sterile$', views.sterile, name='sterile'),
    url(r'^reach$', views.reach, name='reach'),
    url(r'^time$', views.time, name='time'),


]