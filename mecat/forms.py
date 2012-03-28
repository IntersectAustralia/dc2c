from django import forms
from django.forms.util import ErrorList
from django.forms.models import inlineformset_factory
from django.forms.widgets import Textarea, TextInput
from UserDict import UserDict
from mecat.models import Sample, DatasetWrapper
from tardis.tardis_portal import models
from tardis.tardis_portal.fields import MultiValueCommaSeparatedField
from tardis.tardis_portal.widgets import CommaSeparatedInput
import logging

logger = logging.getLogger(__name__)

class Author_Experiment(forms.ModelForm):

    class Meta:
        model = models.Author_Experiment
        exclude = ('experiment',)

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
            if field.name == 'description':
                return field.formfield(
                    widget=TextInput(attrs={'size': '80'}))
            else:
                return field.formfield()
                    
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
        
class ExperimentWrapperForm(ExperimentForm):
    forcode_1 = forms.CharField(max_length=100, required=False, initial="060112 Structural Biology", widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_2 = forms.CharField(max_length=100, required=False, initial="060199 Biochemistry and cell Biology not elsewhere classified", widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_3 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    notes = forms.CharField(required=False, widget=Textarea)    
    
class SampleForm(forms.ModelForm):

    class Meta:
        model = Sample
        
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
            if field.name == 'description':
                return field.formfield(
                    widget=TextInput(attrs={'size': '80'}))
            else:
                return field.formfield()             
                    
        # initialise formsets
        if instance == None or instance.dataset_set.count() == 0:
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
                
        
            
    def save(self, experiment_id, commit=True):   
        # remove m2m field before saving
        sample = super(SampleForm, self).save(commit)
        datasets = []
        for key, dataset in enumerate(self.datasets.forms):
            #if dataset not in self.datasets.deleted_forms:
            # XXX for some random reason the link between
            # the instance needs
            # to be reinitialised
            dataset.instance.sample = sample
            exp = models.Experiment.objects.get(pk=experiment_id)
            real_dataset = models.Dataset(experiment=exp, description="dummy")
            real_dataset.save()
            dataset.instance.dataset = real_dataset
            o_dataset = dataset.save(commit)
            datasets.append(o_dataset)
            mutable = True
            if 'immutable' in dataset.initial:
                if dataset.initial['immutable']:
                    mutable = False
        
        if hasattr(self.datasets, 'deleted_forms'):
            for ds in self.datasets.deleted_forms:
                if not ds.instance.immutable:
                    ds.instance.delete()
              
class DatasetWrapperForm(forms.ModelForm):
    class Meta:
            model = DatasetWrapper
            
    def __init__(self, data=None, files=None, auto_id='%s', prefix=None,
             initial=None, error_class=ErrorList, label_suffix=':',
             empty_permitted=False, instance=None, extra=0):
        self.datasets = {}
        super(DatasetWrapperForm, self).__init__(data=data,
                                             files=files,
                                             auto_id=auto_id,
                                             prefix=prefix,
                                             initial=initial,
                                             instance=instance,
                                             error_class=error_class,
                                             label_suffix=label_suffix,
                                             empty_permitted=False)
    
class RegisterMetamanForm(forms.Form):
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
