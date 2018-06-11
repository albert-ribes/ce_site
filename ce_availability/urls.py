from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^list/$', views.list, name='list'),
    url(r'^list/(?P<ce>[-\w]+)/(?P<unavailability>[-\w]+)/(?P<category>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/(?P<week>[-\w]+)/', views.list_filter, name='list_filter'),
    url(r'^calendar_edit/$', views.calendar_edit, name='calendar_edit'),
    url(r'^calendar_edit/(?P<location>[-\w]+)/(?P<kindofday>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/', views.calendar_edit_filter, name='calendar_edit_filter'),
    url(r'^calendar/(?P<mode>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/$', views.calendar_filter, name='calendar'),
    url(r'^registers/(?P<ce>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/(?P<day>[-\w]+)/$', views.registers_ce_day, name='registers_ce_day'),
    url(r'^day_info/(?P<ce>[-\w]+)/(?P<year>[-\w]+)/(?P<month>[-\w]+)/(?P<day>[-\w]+)/$', views.day_info, name='day_info'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^details/(?P<pk>\d+)/$', views.register_details, name='register_details'),
    url(r'^details_popup/(?P<pk>\d+)/$', views.register_details_popup, name='register_details_popup'),
    url(r'^delete/(?P<pk>\d+)/$', views.register_delete, name='register_delete'),
    url(r'^delete_popup/(?P<pk>\d+)/$', views.register_delete_popup, name='register_delete_popup'),
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

