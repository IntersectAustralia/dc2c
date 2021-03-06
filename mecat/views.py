
from urllib import urlencode, urlopen
from os import path
from django.db import transaction
from tardis.tardis_portal.auth.localdb_auth import auth_key as localdb_auth_key
from tardis.tardis_portal.metsparser import parseMets
from tardis.tardis_portal.forms import RegisterExperimentForm

from django.views.decorators.cache import never_cache
from django.shortcuts import redirect
from tardis.tardis_portal.auth import decorators as authz
from django.conf import settings
from django.template import Context
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from tardis.tardis_portal.auth import auth_service
from tardis.tardis_portal.auth.localdb_auth import django_user
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from tardis.tardis_portal.shortcuts import render_response_index, \
    return_response_error, return_response_not_found, \
    render_response_search
from tardis.tardis_portal.search_query import FacetFixedSearchQuery
from tardis.tardis_portal.staging import get_full_staging_path
from tardis.tardis_portal.views import getNewSearchDatafileSelectionForm, SearchQueryString
from haystack.query import SearchQuerySet
from tardis.tardis_portal.models import Experiment, Dataset, ExperimentACL
from mecat.models import Project, Sample, DatasetWrapper, OwnerDetails
from mecat.forms import ProjectForm, SampleForm, OwnerDetailsForm
from mecat.subject_codes import FOR_CODE_LIST
import logging



logger = logging.getLogger('tardis.tardis_portal.views')

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
         Sample.objects.filter(experiment=experiment_id).order_by("id")

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
        
    return HttpResponse(render_response_index(request,
                        'tardis_portal/ajax/experiment_samples.html', c))

@never_cache
@authz.write_permissions_required
def edit_sample(request, experiment_id, sample_id):
    try:
        experiment = Experiment.safe.get(request, experiment_id)
    except PermissionDenied:
        return return_response_error(request)
    except Experiment.DoesNotExist:
        return return_response_not_found(request)
    c = Context()
    c['experiment'] = experiment
    sample = Sample.objects.get(id=sample_id)
    c['sample_count'] = sample.name
    
    if request.POST:
        form = SampleForm(request.POST, instance=sample, extra=0)
        if form.is_valid():
            full_sample = form.save(experiment_id, commit=False)
            
            full_sample.save_m2m()
            request.POST = {'status': "Sample Created."}
            return _redirect(experiment_id)
        c['status'] = "Errors exist in form."
        c["error"] = 'true'
    else:
        form = SampleForm(instance=sample, extra=0)
    
    c['form'] = form    
    c['status'] = form.errors
    return HttpResponse(render_response_index(request,
                        'tardis_portal/experiment_sample.html', c))


@never_cache
@authz.write_permissions_required
def new_sample(request, experiment_id):  
    try:
        experiment = Experiment.safe.get(request, experiment_id)
    except PermissionDenied:
        return return_response_error(request)
    except Experiment.DoesNotExist:
        return return_response_not_found(request)
    
    c = Context()
    c['experiment'] = experiment
    samples = Sample.objects.filter(experiment=experiment_id)
    c['sample_count'] = samples.count() + 1
    
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(experiment_id, commit=False)
            sample.save_m2m()
            request.POST = {'status': "Sample Created."}
            return _redirect(experiment_id)
        c['status'] = "Errors exist in form."
        c["error"] = 'true'
    else:
        form = SampleForm(extra=1)
        
    c['form'] = form    
    c['status'] = form.errors
    return HttpResponse(render_response_index(request,
                        'tardis_portal/experiment_sample.html', c))

def retrieve_datasets(request, sample_id):
    datasetwrappers = DatasetWrapper.objects.filter(sample=sample_id).order_by('pk')
    datasets = [wrapper.dataset for wrapper in datasetwrappers]
    sample = Sample.objects.get(pk=sample_id)
    has_write_permissions = \
        authz.has_write_permissions(request, sample.experiment.id)
            
    c = Context({'datasets' : datasets, 'has_write_permissions' : has_write_permissions})
    return HttpResponse(render_response_index(request,
                        'tardis_portal/ajax/dataset.html', c))

@never_cache
@login_required()
def retrieve_sample_forcodes(request):
    import json
    return HttpResponse(json.dumps(FOR_CODE_LIST), mimetype='application/json')
  
@permission_required('tardis_portal.add_experiment')
@login_required
def create_experiment(request,
                      template_name='tardis_portal/create_experiment_with_samples.html'):

    """Create a new experiment view.

    :param request: a HTTP Request instance
    :type request: :class:`django.http.HttpRequest`
    :param template_name: the path of the template to render
    :type template_name: string
    :rtype: :class:`django.http.HttpResponse`
    
    """
    c = Context({
        'subtitle': 'Create Project',
        'user_id': request.user.id,
        })
    staging = get_full_staging_path(request.user.username)
    if staging:
        c['directory_listing'] = staging_traverse(staging)
        c['staging_mount_prefix'] = settings.STAGING_MOUNT_PREFIX
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            full_experiment = form.save(commit=False)

            # group/owner assignment stuff, soon to be replaced

            experiment = full_experiment['experiment']
            experiment.created_by = request.user
            full_experiment.save_m2m()

            # add defaul ACL
            acl = ExperimentACL(experiment=experiment,
                                pluginId=django_user,
                                entityId=str(request.user.id),
                                canRead=True,
                                canWrite=True,
                                canDelete=True,
                                isOwner=True,
                                aclOwnershipType=ExperimentACL.OWNER_OWNED)
            acl.save()

            request.POST = {'status': "Experiment Created."}
            # Add wrapper information
            from .experiments import ExperimentFormHandler
            ExperimentFormHandler(experiment.id).add_experiment(form.cleaned_data)
            
            return HttpResponseRedirect(reverse(
                'tardis.tardis_portal.views.view_experiment',
                args=[str(experiment.id)]) + "#created")

        c['status'] = "Errors exist in form."
        c["error"] = 'true'

    else:
        form = ProjectForm(extra=1)

    c['form'] = form
    c['default_institution'] = settings.DEFAULT_INSTITUTION
    c['status'] = form.errors   
    return HttpResponse(render_response_index(request, template_name, c))

@login_required
@permission_required('tardis_portal.change_experiment')
@authz.write_permissions_required
def edit_experiment(request, experiment_id,
                      template="tardis_portal/create_experiment_with_samples.html"):
    """Edit an existing experiment.

    :param request: a HTTP Request instance
    :type request: :class:`django.http.HttpRequest`
    :param experiment_id: the ID of the experiment to be edited
    :type experiment_id: string
    :param template_name: the path of the template to render
    :type template_name: string
    :rtype: :class:`django.http.HttpResponse`

    """
    experiment = Experiment.objects.get(id=experiment_id)

    c = Context({'subtitle': 'Edit Project',
                 'user_id': request.user.id,
                 'experiment_id': experiment_id,
              })

    staging = get_full_staging_path(
                                request.user.username)
    if staging:
        c['directory_listing'] = staging_traverse(staging)
        c['staging_mount_prefix'] = settings.STAGING_MOUNT_PREFIX
 
    from .experiments import ExperimentFormHandler
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES,
                              instance=experiment, extra=0)
        if form.is_valid():
            full_experiment = form.save(commit=False)
            experiment = full_experiment['experiment']
            experiment.created_by = request.user
            full_experiment.save_m2m()
            
            # Get Wrapper information
            ExperimentFormHandler(experiment_id).edit_experiment(form.cleaned_data, experiment_id)

            request.POST = {'status': "Experiment Saved."}
            return HttpResponseRedirect(reverse(
                'tardis.tardis_portal.views.view_experiment',
                args=[str(experiment.id)]) + "#saved")

        c['status'] = "Errors exist in form."
        c["error"] = 'true'
    else:
        experiment_handler = ExperimentFormHandler(experiment_id)
        form = ProjectForm(initial=experiment_handler.form_data(experiment_id), instance=experiment, extra=0)

    c['form'] = form
    c['status'] = form.errors   
    return HttpResponse(render_response_index(request,
                        template, c))

@login_required
def mydetails(request):
    c = Context()
    existing_details = OwnerDetails.objects.filter(user=request.user)
    if existing_details.count() == 1:
        owner_details = existing_details[0]
    else:
        owner_details = None
    if request.method == 'POST':
        form = OwnerDetailsForm(request.POST, instance=owner_details)
        if form.is_valid():
            form.save()
            request.POST = {'status': 'Details Saved'}
            c['status'] = 'Details Saved'
        else:
            c['status'] = "Errors exist in form."
            c["error"] = 'true'
        #return redirect(reverse('tardis.tardis_portal.views.experiment_index'))
    else:
        if not owner_details:
            owner_details = OwnerDetails(user=request.user, 
                                    first_name=request.user.first_name, 
                                    last_name=request.user.last_name, 
                                    email=request.user.email)
        form = OwnerDetailsForm(instance=owner_details)
    
    c['form'] = form    
    return HttpResponse(render_response_index(request,
                        'tardis_portal/rif-cs/mydetails.html', c))
    
        
def partners(request):

    c = Context({'subtitle': 'Partners',
                 'about_pressed': True,
                 'nav': [{'name': 'Partners', 'link': '/partners/'}]})
    return HttpResponse(render_response_index(request,
                        'tardis_portal/partners.html', c))    

@login_required
def change_password(request):
    from django.contrib.auth.views import password_change
    return password_change(request)
    
@authz.experiment_access_required
def view_party_rifcs(request, experiment_id):
    """View the rif-cs of an existing experiment.

    :param request: a HTTP Request instance
    :type request: :class:`django.http.HttpRequest`
    :param experiment_id: the ID of the experiment to be viewed
    :type experiment_id: string
    :rtype: :class:`django.http.HttpResponse`

    """
    try:
        experiment = Experiment.safe.get(request, experiment_id)
    except PermissionDenied:
        return return_response_error(request)
    except Experiment.DoesNotExist:
        return return_response_not_found(request)

    try:
        rifcs_provs = settings.RIFCS_PROVIDERS
    except AttributeError:
        rifcs_provs = ()

    from mecat.rifcs.publishservice import PartyPublishService
    pservice = PartyPublishService(rifcs_provs, experiment)
    context = pservice.get_context()
    if context is None:
        # return error page or something
        return return_response_error(request)
    
    template = pservice.get_template(type="party")
    return HttpResponse(render_response_index(request,
                        template, context), mimetype="text/xml")

def _create_wrappers_for_datasets(sample, experiment):
    datasets = experiment.dataset_set.values()
    for ds_details in datasets:
        ds_id = ds_details['id']
        # Create DatasetWrapper and assign dataset it to it
        ds = Dataset.objects.get(pk=ds_id)
        dw = DatasetWrapper(dataset=ds, sample=sample)
        dw.save()

# TODO removed username from arguments
@transaction.commit_on_success
def _registerExperimentDocument(filename, created_by, expid=None,
                                owners=[], username=None):
    '''
    Register the experiment document and return the experiment id.

    :param filename: path of the document to parse (METS or notMETS)
    :type filename: string
    :param created_by: a User instance
    :type created_by: :py:class:`django.contrib.auth.models.User`
    :param expid: the experiment ID to use
    :type expid: int
    :param owners: a list of owners
    :type owner: list
    :param username: **UNUSED**
    :rtype: int

    '''

    f = open(filename)
    firstline = f.readline()
    f.close()

    if firstline.startswith('<experiment'):
        logger.debug('processing simple xml')
        processExperiment = ProcessExperiment()
        eid = processExperiment.process_simple(filename, created_by, expid)

    else:
        logger.debug('processing METS')
        eid = parseMets(filename, created_by, expid)
 
    # Create a DatasetWrapper for each Dataset
    experiment = Experiment.objects.get(pk=eid)
    sample = Sample(experiment=experiment, name="Default Sample", 
                    description="A default sample for %s" % experiment.title)
    sample.save()
    _create_wrappers_for_datasets(sample, experiment)  
    
    # Create a Project to wraps the experiment, then create a Sample that
    # points to the experiment  
    project = Project(experiment=experiment)
    project.save()
    
    auth_key = ''
    try:
        auth_key = settings.DEFAULT_AUTH
    except AttributeError:
        logger.error('no default authentication for experiment ownership set (settings.DEFAULT_AUTH)')

    force_user_create = False
    try:
        force_user_create = settings.DEFAULT_AUTH_FORCE_USER_CREATE
    except AttributeError:
        pass

    if auth_key:
        for owner in owners:
            logger.debug('** Owner : %s' %owner)
            # for each PI
            if not owner:
                continue

            owner_username = None
            if '@' in owner:
                logger.debug('** Email as username **')
                owner_username = auth_service.getUsernameByEmail(auth_key,
                                    owner)
            if not owner_username:
                logger.debug('** No existing user!! **')
                owner_username = owner

            owner_user = auth_service.getUser(auth_key, owner_username,
                      force_user_create=force_user_create)
            if owner_user:
                # if exist, create ACL
                logger.debug('registering owner: ' + owner)
                e = Experiment.objects.get(pk=eid)

                acl = ExperimentACL(experiment=e,
                                    pluginId=django_user,
                                    entityId=str(owner_user.id),
                                    canRead=True,
                                    canWrite=True,
                                    canDelete=True,
                                    isOwner=True,
                                    aclOwnershipType=ExperimentACL.OWNER_OWNED)
                acl.save()
                # Also update email
                if '@' in owner:
                    owner_user.email = owner
                    owner_user.save()

    return eid

# web service (overiding the existing one in tardis core view)
def register_experiment_ws_xmldata(request):

    status = ''
    if request.method == 'POST':  # If the form has been submitted...

        # A form bound to the POST data
        form = RegisterExperimentForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass

            xmldata = request.FILES['xmldata']
            username = form.cleaned_data['username']
            origin_id = form.cleaned_data['originid']
            from_url = form.cleaned_data['from_url']

            user = auth_service.authenticate(request=request,
                                             authMethod=localdb_auth_key)
            if user:
                if not user.is_active:
                    return return_response_error(request)
            else:
                return return_response_error(request)

            e = Experiment(
                title='Placeholder Title',
                approved=True,
                created_by=user,
                )
            e.save()
            eid = e.id

            filename = path.join(e.get_or_create_directory(),
                                 'mets_upload.xml')
            f = open(filename, 'wb+')
            for chunk in xmldata.chunks():
                f.write(chunk)
            f.close()

            logger.info('=== processing experiment: START')
            owners = request.POST.getlist('experiment_owner')
            try:
                _registerExperimentDocument(filename=filename,
                                            created_by=user,
                                            expid=eid,
                                            owners=owners,
                                            username=username)
                logger.info('=== processing experiment %s: DONE' % eid)
            except:
                logger.exception('=== processing experiment %s: FAILED!' % eid)
                return return_response_error(request)

            if from_url:
                logger.debug('=== sending file request')
                logger.info('Sending received_remote signal')
                from tardis.tardis_portal.signals import received_remote
                received_remote.send(sender=Experiment,
                        instance=e,
                        uid=origin_id,
                        from_url=from_url)

            response = HttpResponse(str(eid), status=200)
            response['Location'] = request.build_absolute_uri(
                '/experiment/view/' + str(eid))
            return response
    else:
        form = RegisterExperimentForm()  # An unbound form

    c = Context({
        'form': form,
        'status': status,
        'subtitle': 'Register Experiment',
        'searchDatafileSelectionForm': getNewSearchDatafileSelectionForm()})
    return HttpResponse(render_response_index(request,
                        'tardis_portal/register_experiment.html', c))
