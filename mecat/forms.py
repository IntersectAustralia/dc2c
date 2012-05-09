from django import forms
from django.forms.util import ErrorList
from django.forms.models import inlineformset_factory
from django.forms.widgets import Textarea, TextInput
from UserDict import UserDict
from mecat.models import Sample, DatasetWrapper, OwnerDetails
from tardis.tardis_portal import models
from tardis.tardis_portal.fields import MultiValueCommaSeparatedField
from tardis.tardis_portal.widgets import CommaSeparatedInput
import logging
import re

logger = logging.getLogger(__name__)

class redict(dict):
    def __init__(self, d):
        dict.__init__(self, d)

    # return the list of keys that matches the regex
    def __getitem__(self, regex):
        r = re.compile(regex)
        mkeys = filter(r.match, self.keys())
        for i in mkeys:
            yield dict.__getitem__(self, i)

class Author_Experiment(forms.ModelForm):

    class Meta:
        model = models.Author_Experiment
        exclude = ('experiment',)

class FullSampleModel(UserDict):
    def save_m2m(self):
        """
        {
        'sample': sample, 
        'dataset_wrappers' : [(dataset_wrapper, dataset),..]
        }
        """        
        sample = self.data['sample']
        sample.save()
        for dw, ds in self.data['dataset_wrappers']:
            if not dw.immutable:
                ds.description = dw.description
                ds.save()
                dw.dataset = ds
                dw.sample = sample
                dw.save() 
                
        if hasattr(self.data['dataset_wrappers'], 'deleted_forms'):
            for dw, ds in self.data['dataset_wrappers'].deleted_forms:
                if not dw.instance.immutable:
                    dw.instance.delete() 

class FullExperimentModel(UserDict):
    """
    This is a dict wrapper that store the values returned from
    the :func:`tardis.tardis_portal.forms.FullExperiment.save` function.
    It provides a convience method for saving the model objects.
    """

    def save_m2m(self):
        """
        {'experiment': experiment,
        'author_experiments': author_experiments,
        'authors': authors,
        'samples': samples}
        """
        self.data['experiment'].save()
        for ae in self.data['author_experiments']:
            ae.experiment = ae.experiment
            ae.save()
        for smp in self.data['samples']:
            if not smp.immutable:
                smp.experiment = smp.experiment
                smp.save()

        # XXX because saving the form can be now done without
        # commit=False this won't be called during the creation
        # of new experiments.
        if hasattr(self.data['samples'], 'deleted_forms'):
            for smp in self.data['samples'].deleted_forms:
                if not smp.instance.immutable:
                    smp.instance.delete()

class ExperimentForm(forms.ModelForm):
    """
    This handles the complex experiment forms.

    """

    class Meta:
        model = models.Experiment
        exclude = ('authors', 'handle', 'approved', 'created_by')
    
    def __init__(self, data=None, files=None, auto_id='%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None, extra=0):
        self.author_experiments = []
        self.samples = {}
        super(ExperimentForm, self).__init__(data=data,
                                             files=files,
                                             auto_id=auto_id,
                                             prefix=prefix,
                                             initial=initial,
                                             instance=instance,
                                             error_class=error_class,
                                             label_suffix=label_suffix,
                                             empty_permitted=False)
        def custom_sample_field(field):
            if field.name == 'description' or field.name == 'name':
                return field.formfield(
                    widget=TextInput(attrs={'size': '80'}))
            return None
                    
        # initialise formsets
        if instance == None or instance.sample_set.count() == 0:
            extra = 1
        sample_formset = inlineformset_factory(
            models.Experiment,
            Sample,
            formfield_callback=custom_sample_field,
            extra=extra, can_delete=True) 
        
        # fix up experiment form
        post_authors = self._parse_authors(data)
        self._fill_authors(post_authors)
        if instance:
            authors = instance.author_experiment_set.all()
            self.authors_experiments = [Author_Experiment(instance=a) for a
                                        in authors]
            self.initial['authors'] = ', '.join([a.author for a in authors])
            self.fields['authors'] = \
                MultiValueCommaSeparatedField([author.fields['author'] for
                                            author in self.author_experiments],
                                            widget=CommaSeparatedInput())
    
        # fill formsets
        self.samples = sample_formset(data=data,
                                        instance=instance,
                                        prefix="sample")
        
        for i, smp in enumerate(self.samples.forms):
            if 'immutable' in smp.initial:
                if smp.initial['immutable']:
                    smp.fields['description'].widget.attrs['readonly'] = True
                    smp.fields['description'].editable = False
                    smp.fields['immutable'].editable = False
                    smp.fields['immutable'].widget.attrs['readonly'] = True
 
    def _parse_authors(self, data=None):
        """
        create a dictionary containing each of the sub form types.
        """
        authors = []
        if not data:
            return authors
        if 'authors' in data:
            authors = [a.strip() for a in
                       data.get('authors').split(',')]
        return authors
    
    def _fill_authors(self, authors):
        if self.instance:
            o_author_experiments = \
                self.instance.author_experiment_set.all()
        else:
            o_author_experiments = []
        for num, author in enumerate(authors):
            try:
                o_ae = o_author_experiments[num]
            except IndexError:
                o_ae = models.Author_Experiment()
                o_ae.experiment = self.instance
            f = Author_Experiment(data={'author': author,
                                        'order': num},
                                  instance=o_ae)
            self.author_experiments.append(f)

        self.fields['authors'] = \
            MultiValueCommaSeparatedField([author.fields['author'] for
                                        author in self.author_experiments],
                                        widget=CommaSeparatedInput())
    def get_samples(self):
        """
        Return samples
        """
        for number, form in enumerate(self.samples.forms):
            yield form
            
    def _is_samples_valid(self):
        for key, sample in enumerate(self.samples.forms):
            if not sample.is_valid():
                return False           
        return True
      
    def is_valid(self):
        experiment_fields_valid = super(ExperimentForm, self).is_valid()
        samples_valid = self._is_samples_valid()     
        return experiment_fields_valid and samples_valid  


    def save(self, commit=True):
        # remove m2m field before saving
        del self.cleaned_data['authors']
        experiment = super(ExperimentForm, self).save(commit)
        authors = []
        author_experiments = []
        samples = []
        
        for ae in self.author_experiments:
            ae.instance.experiment = ae.instance.experiment
            o_ae = ae.save(commit=commit)
            author_experiments.append(o_ae)
     
        for key, sample in enumerate(self.samples.forms):
            if sample.is_valid(): 
                if sample not in self.samples.deleted_forms:
                    # XXX for some random reason the link between
                    # the instance needs
                    # to be reinitialised
                    sample.instance.experiment = experiment
                    o_sample = sample.save(commit)
                    samples.append(o_sample)
                    # save any datafiles if the data set has any
                    mutable = True
                    if 'immutable' in sample.initial:
                        if sample.initial['immutable']:
                            mutable = False
        
        if hasattr(self.samples, 'deleted_forms'):
            for smp in self.samples.deleted_forms:
                if not smp.instance.immutable:
                    smp.instance.delete()
                    
        return FullExperimentModel({'experiment': experiment,
                                    'author_experiments': author_experiments,
                                    'authors': authors,
                                    'samples': samples})
        
class ProjectForm(ExperimentForm):
    FUNDED_BY = [(None, u''),
                 ("Australian Research Council (ARC)", "Australian Research Council (ARC)"),
                 ("Medical Research Council (NHMRC)", "Medical Research Council (NHMRC)")]
    
    forcode_1 = forms.CharField(max_length=100, required=False, initial="060112 Structural Biology", widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_2 = forms.CharField(max_length=100, required=False, initial="060199 Biochemistry and cell Biology not elsewhere classified", widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_3 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    funded_by = forms.ChoiceField(initial=None, choices=FUNDED_BY, required=False)
    funding_code = forms.CharField(max_length=100, required=False)
    notes = forms.CharField(required=False, widget=Textarea)    
    
    
class OwnerDetailsForm(forms.ModelForm):
    class Meta:
        model = OwnerDetails    


class SampleForm(forms.ModelForm):

    class Meta:
        model = Sample
        exclude = ('user')
        
    def __init__(self, data=None, files=None, auto_id='%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None, extra=0):
        self.datasets = {}
        super(SampleForm, self).__init__(data=data,
                                             files=files,
                                             auto_id=auto_id,
                                             prefix=prefix,
                                             initial=initial,
                                             instance=instance,
                                             error_class=error_class,
                                             label_suffix=label_suffix,
                                             empty_permitted=False)

          
        def custom_dataset_field(field):
            if field.name == 'description' or field.name == 'name':
                return field.formfield(required=True, 
                    widget=TextInput(attrs={'size': '80'}))
            elif field.name == 'dataset':
                return None
            else:
                return field.formfield()             
                    
        # initialise formsets
        if instance == None or instance.datasetwrapper_set.count() == 0:
            extra = 1
        dataset_formset = inlineformset_factory(
            Sample,
            DatasetWrapper,
            formfield_callback=custom_dataset_field, 
            extra=extra, can_delete=True) 
    
        # fill formsets
        self.datasets = dataset_formset(data=data,
                                        instance=instance,
                                        prefix="dataset")      
        
        for i, ds in enumerate(self.datasets.forms):
            if 'immutable' in ds.initial:
                if ds.initial['immutable']:
                    ds.fields['description'].widget.attrs['readonly'] = True
                    ds.fields['description'].editable = False
                    ds.fields['immutable'].editable = False
                    ds.fields['immutable'].widget.attrs['readonly'] = True                   
        
    def get_datasets(self):
        """
        Return datasets
        """
        for number, form in enumerate(self.datasets.forms):
            yield form
                
    def _is_datasets_valid(self):
        for key, dataset in enumerate(self.datasets.forms):
            if not dataset.is_valid() or self._description_or_name_is_empty(dataset):  
                if not (self.errors.has_key("Dataset Description is required ")) and \
                   not (self.errors.has_key("Dataset Name is required ")):
                    self.errors["Errors in "] = "Dataset Fields"  
                return False           
        return True
      
    def is_valid(self):  
        sample_fields_valid = super(SampleForm, self).is_valid()
        datasets_valid = self._is_datasets_valid()
        return sample_fields_valid and datasets_valid    

    def _description_or_name_is_empty(self, dw_form):
        data = redict(dw_form.data)
        empty = False
        matching_vals = data[r"dataset-.*-description"]
        for val in matching_vals:  
            if val[0] is u'' or val is None:
                self.errors["Dataset Description is required "] = ""
                empty = True
                break
        matching_vals = data[r"dataset-.*-name"]
        for val in matching_vals:      
            if val[0] is u'' or val is None:
                self.errors["Dataset Name is required"] = ""
                empty = True
                break
        return empty
        
    
    def save(self, experiment_id, commit=True): 
        sample = super(SampleForm, self).save(commit)
        dataset_wrappers = []
        for key, dw_form in enumerate(self.datasets.forms):
            if dw_form.is_valid():
                if dw_form not in self.datasets.deleted_forms:
                    dw_form.instance.sample = sample
                    exp = models.Experiment.objects.get(pk=experiment_id)
                    # create real dataset wrapper IF the description is not 
                    # empty
                    real_dataset = models.Dataset(experiment=exp)
                    real_dataset.save(commit)
                    dw_instance = dw_form.save(commit)  
                    dataset_wrappers.append((dw_instance,real_dataset))
            
        if hasattr(self.datasets, 'deleted_forms'):
            for dw_form in self.datasets.deleted_forms:
                if not dw_form.instance.immutable:
                    dw_form.instance.delete() 
        
        return FullSampleModel({'sample': sample, 'dataset_wrappers': dataset_wrappers})      
              
    
class RegisterMetamanForm(forms.Form):
    '''
    This is needed for the experiment register feature
    '''
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True,
                               widget=forms.PasswordInput)
    metaman = forms.FileField(required=True)
    principal_investigator = forms.CharField(required=False)
    researchers = forms.CharField(required=False)
    # ldap login!
    experiment_owner = forms.CharField(required=False)
    institution_name = forms.CharField(max_length=400, required=True)
    program_id = forms.CharField(max_length=30, required=False)
    epn = forms.CharField(max_length=30, required=True)
    start_time = forms.DateTimeField(required=False)
    end_time = forms.DateTimeField(required=False)
    title = forms.CharField(max_length=400, required=True)
    description = forms.CharField(required=False)
    beamline = forms.CharField(required=True)
    instrument_url = forms.CharField(required=False)
    instrument_scientists = forms.CharField(required=False)
    # holding sample information
    sample = forms.FileField(required=False)
