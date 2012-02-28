
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect
from tardis.tardis_portal.auth import decorators as authz
from django.template import Context
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from tardis.tardis_portal.shortcuts import render_response_index, \
    return_response_error, return_response_not_found, \
    render_response_search
from tardis.tardis_portal.search_query import FacetFixedSearchQuery

from tardis.tardis_portal.views import getNewSearchDatafileSelectionForm, SearchQueryString
from haystack.query import SearchQuerySet
from tardis.tardis_portal.models import Experiment, Dataset
from mecat.models import Sample, DatasetWrapper
from . import forms

def _redirect(experiment_id):
    return redirect(reverse('tardis.tardis_portal.views.view_experiment', args=[experiment_id]))

@never_cache
@authz.experiment_access_required
def experiment_samples(request, experiment_id):

    """View a listing of dataset of an existing experiment as ajax loaded tab.

    :param request: a HTTP Request instance
    :type request: :class:`django.http.HttpRequest`
    :param experiment_id: the ID of the experiment to be edited
    :type experiment_id: string
    :param template_name: the path of the template to render
    :type template_name: string
    :rtype: :class:`django.http.HttpResponse`

    """
    c = Context({'upload_complete_url':
                     reverse('tardis.tardis_portal.views.upload_complete'),
                 'searchDatafileSelectionForm':
                     getNewSearchDatafileSelectionForm(),
                 })

    try:
        experiment = Experiment.safe.get(request, experiment_id)
    except PermissionDenied:
        return return_response_error(request)
    except Experiment.DoesNotExist:
        return return_response_not_found(request)

    c['experiment'] = experiment
    if 'query' in request.GET:

        # We've been passed a query to get back highlighted results.
        # Only pass back matching datafiles
        #
        search_query = FacetFixedSearchQuery(backend=HighlightSearchBackend())
        sqs = SearchQuerySet(query=search_query)
        query = SearchQueryString(request.GET['query'])
        facet_counts = sqs.raw_search(query.query_string() + ' AND experiment_id_stored:%i' % (int(experiment_id)), end_offset=1).facet('dataset_id_stored').highlight().facet_counts()
        if facet_counts:
            dataset_id_facets = facet_counts['fields']['dataset_id_stored']
        else:
            dataset_id_facets = []

        c['highlighted_datasets'] = [ int(f[0]) for f in dataset_id_facets ]
        c['file_matched_datasets'] = []
        c['search_query'] = query

        # replace '+'s with spaces
    elif 'datafileResults' in request.session and 'search' in request.GET:
        c['highlighted_datasets'] = None
        c['highlighted_dataset_files'] = [r.pk for r in request.session['datafileResults']]
        c['file_matched_datasets'] = \
            list(set(r.dataset.pk for r in request.session['datafileResults']))
        c['search'] = True

    else:
        c['highlighted_datasets'] = None
        c['highlighted_dataset_files'] = None
        c['file_matched_datasets'] = None

    c['samples'] = \
         Sample.objects.filter(experiment=experiment_id)

    c['datasets'] = \
         Dataset.objects.filter(experiment=experiment_id)

    c['has_write_permissions'] = \
        authz.has_write_permissions(request, experiment_id)

    c['protocol'] = []
    download_urls = experiment.get_download_urls()
    for key, value in download_urls.iteritems():
        c['protocol'] += [[key, value]]

    if 'status' in request.GET:
        c['status'] = request.GET['status']
    if 'error' in request.GET:
        c['error'] = request.GET['error']
        
    if len(c['samples']) is 0:
        return HttpResponse(render_response_index(request,
                        'tardis_portal/ajax/experiment_datasets.html', c))
        
    return HttpResponse(render_response_index(request,
                        'tardis_portal/ajax/experiment_samples.html', c))

def new_sample(request, experiment_id):
    c = Context()
    try:
        experiment = Experiment.safe.get(request, experiment_id)
    except PermissionDenied:
        return return_response_error(request)
    except Experiment.DoesNotExist:
        return return_response_not_found(request)
    c['experiment'] = experiment
    samples = Sample.objects.filter(experiment=experiment_id)
    c['sample_count'] = len(samples) + 1

    if request.POST:
        form = forms.SampleForm(request.POST)
        if form.is_valid():
            from .samples import SampleFormHandler
            SampleFormHandler(experiment_id).add_sample(form.cleaned_data)
            return _redirect(experiment_id)
        else:
            form = forms.SampleForm()
        
    return HttpResponse(render_response_index(request,
                        'tardis_portal/experiment_sample.html', c))

def retrieve_datasets(request, sample_id):
    datasetwrappers = DatasetWrapper.objects.filter(sample=sample_id)
    datasets = [wrapper.dataset for wrapper in datasetwrappers]
    c = Context({'datasets' : datasets})
    return HttpResponse(render_response_index(request,
                        'tardis_portal/ajax/dataset.html', c))