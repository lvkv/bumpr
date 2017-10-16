from django.conf.urls import url, include

from . import views

urlpatterns = [
    # ex: /
    url(r'^$', views.index, name='index'),

    # ex: /register/
    url(r'^register/$', views.user_register, name='user_register'),

    # internal URL for user email confirmation
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),

    # internal URL for user email confirmation
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),

    # internal URL for Plate autocomplete (DAL)
    # url(r'^plate-autocomplete/$', views.PlateAutocomplete.as_view(), name='plate-autocomplete'),

    # ex: /accounts/...
    url(r'^accounts/', include('django.contrib.auth.urls')),

    # ex: /settings/
    url(r'^settings/$', views.user_settings, name='user_settings'),

    # ex: /profile/...
    url(r'^profile/(?P<userstring>[^/]+)/$', views.user_profile, name='user_profile'),

    # ex: /profile/juanathan/edit
    url(r'^profile/(?P<userstring>[^/]+)/edit/$', views.user_profile_edit, name='user_profile_edit'),

    # ex: /lookup
    url(r'^lookup/$', views.plate_lookup, name='plate_lookup'),

    # ex: /p/1243
    url(r'^p/(?P<pk>[0-9]+)$', views.plate_url, name='plate_url'),

    # ex: /plate/ny
    url(r'^plate/(?P<state_string>[a-z]{2})/$', views.plate_state, name='plate_state'),

    # ex: /plate/ny/yolo123
    url(r'^plate/(?P<state_string>[a-z]{2})/(?P<plate_string>[^/]+)$', views.plate_detail, name='plate_detail'),

]
