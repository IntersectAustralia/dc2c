from django.conf.urls.defaults import patterns, include
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import Http404
admin.autodiscover()


def no_view(request, *args, **kwargs):
    raise Http404

embargo_urls = patterns('mecat.embargo',
                        (r'^$', 'index'),
                        (r'^search/$', 'search'),
                        (r'^default_expiry/(?P<experiment_id>\d+)/$', 'default_expiry'),
                        (r'^prevent_expiry/(?P<experiment_id>\d+)/$', 'prevent_expiry'),
                        (r'^set_expiry/(?P<experiment_id>\d+)/$', 'set_expiry'),
                        )

urlpatterns = patterns('',
                       (r'^$', 'tardis.tardis_portal.views.experiment_index'),
                       (r'^partners/$', 'mecat.views.partners'),
                       (r'^mydetails/$', 'mecat.views.mydetails'),
                       (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /vbl/", mimetype="text/plain")),
                       (r'^vbl/experiment/register/$', 'mecat.register.register_metaman'),
                       (r'^vbl/download/datafile/(?P<datafile_id>\d+)/$', 'mecat.download.download_datafile'),
                       (r'^vbl/download/experiment/(?P<experiment_id>\d+)/(?P<comptype>[a-z]{3})/$', 'mecat.download.download_experiment'),
                       (r'^vbl/download/datafiles/$', 'mecat.download.download_datafiles'),
                       (r'^rif_cs/', no_view),
                       (r'^accounts/manage_auth_methods/', no_view),
                       (r'^accounts/register/', no_view),
                       (r'^accounts/password/$', 'mecat.views.change_password'),
                       (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       (r'^accounts/password/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       (r'^accounts/', 'tardis.tardis_portal.views.experiment_index'), 
                       #(r'^accounts/login/$', 'login', {'next_page': '/'}),
                       (r'^experiment/newsample/(?P<experiment_id>\d+)/$', 'mecat.views.new_sample'),
                       (r'^experiment/(?P<experiment_id>\d+)/edit_sample/(?P<sample_id>\d+)/$', 'mecat.views.edit_sample'),
                       (r'^experiment/create/$', 'mecat.views.create_experiment'),
                       (r'^experiment/edit/(?P<experiment_id>\d+)/$', 'mecat.views.edit_experiment'),
                       (r'^experiment/view/(?P<experiment_id>\d+)/publish/', no_view),
                       (r'^experiment/view/(?P<experiment_id>\d+)/rifcs/party/$', 'mecat.views.view_party_rifcs'),
                       (r'^ajax/experiment_samples/(?P<experiment_id>\d+)/$', 'mecat.views.experiment_samples'),
                       (r'^ajax/sample_datasets/(?P<sample_id>\d+)/$', 'mecat.views.retrieve_datasets'),
                       (r'^ajax/sample_forcode_list/$', 'mecat.views.retrieve_sample_forcodes'),
                       (r'^ansto_media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.ANSTO_MEDIA_ROOT}),
                       (r'^embargo/', include(embargo_urls)),
                       )

from tardis.urls import urlpatterns as tardisurls
urlpatterns += tardisurls
