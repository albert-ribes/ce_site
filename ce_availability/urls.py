from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^list/$', views.list, name='list'),
    url(r'^list/filter/(?P<ce>[-\w]+)/(?P<unavailability>[-\w]+)/(?P<category>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/(?P<week>[-\w]+)/', views.list_filter, name='list_filter'),
    url(r'^details/(?P<pk>\d+)/$', views.register_details, name='register_details'),
    url(r'^delete/(?P<pk>\d+)/$', views.register_delete, name='register_delete'),
    url(r'^edit/', views.edit, name='edit'),
    url(r'^insert/', views.insert, name='insert'),
    url(r'^user_settings/', views.user_settings, name='user_settings'),
    url(r'^user_details/', views.user_details, name='user_details'),
    url('^change_password/$', views.change_password, name='change_password'),
    url(r'^login/', auth_views.login, name='login', kwargs={'redirect_authenticated_user': True}),
    url(r'^logout/', auth_views.logout, name='logout', kwargs={'next_page': '/ce_availability'}),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]

