from tardis.tardis_portal.models import *
from django.core.exceptions import ValidationError

def validate_spaces(value):
    if value.strip() == '':
        raise ValidationError(u'Value cannot be empty')

class Project(models.Model):
        
    experiment = models.ForeignKey(Experiment)
    forcode1 = models.TextField(blank=True)
    forcode2 = models.TextField(blank=True)
    forcode3 = models.TextField(blank=True)
    funded_by = models.TextField(blank=True)
    funding_code = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return 'Project for Experiment \'' + self.experiment.description + '\''
    
class Sample(models.Model):
    
    class Meta:
        verbose_name = 'Project Experiment'
        verbose_name_plural = 'Project Experiments'
        
    experiment = models.ForeignKey(Experiment)
    description = models.TextField(blank=False, validators=[validate_spaces])
    name = models.CharField(max_length=100, blank=False, validators=[validate_spaces])
    forcode1 = models.CharField(max_length=100, blank=True, default="060112 Structural Biology")
    forcode2 = models.CharField(max_length=100, blank=True, default="060199 Biochemistry and cell Biology not elsewhere classified")
    forcode3 = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return self.description

class DatasetWrapper(models.Model):
    sample = models.ForeignKey(Sample)
    name = models.CharField(max_length=100, blank=False, validators=[validate_spaces])
    description = models.TextField(blank=False, validators=[validate_spaces])
    dataset = models.ForeignKey(Dataset, null=True, blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
       if self.dataset and self.dataset.description:
           return 'wrapper for ' + self.dataset.description
       elif self.description:
           return 'wrapper: ' + self.description
       else:
           return 'wrapper for empty dataset'
       
class OwnerDetails(models.Model):
    user = models.ForeignKey(User, blank=False)
    title = models.CharField(max_length=30, blank=True, validators=[validate_spaces])
    first_name = models.CharField(max_length=200, blank=False, validators=[validate_spaces])
    last_name = models.CharField(max_length=200, blank=False, validators=[validate_spaces])
    email = models.CharField(max_length=100, blank=False, validators=[validate_spaces])
    
    def __unicode__(self):
        return 'details for ' + self.first_name + ' ' + self.last_name    

@receiver(post_save, sender=OwnerDetails)
def post_save_owner_details(sender, **kwargs):
    ownerdetails = kwargs['instance']
    experiments = Experiment.objects.filter(created_by=ownerdetails.user)
    for experiment in experiments:
        _publish_public_expt_rifcs(experiment)

@receiver(post_save, sender=Experiment)
@receiver(post_delete, sender=Experiment)
def post_save_experiment(sender, **kwargs):
    # create party and dataset rifcs too - note that the activity rifcs
    # is taken care of in the core model
    experiment = kwargs['instance']
    _publish_public_expt_rifcs(experiment)
    
@receiver(post_save, sender=DatasetWrapper)  
def post_save_datasetwrapper(sender, **kwargs):
    datasetwrapper = kwargs['instance']
    sample = datasetwrapper.sample
    experiment = sample.experiment
    _publish_public_expt_rifcs(experiment)

@receiver(post_save, sender=Project) 
@receiver(post_delete, sender=Project) 
def post_save_project(sender, **kwargs):
    project = kwargs['instance']
    experiment = project.experiment
    _publish_public_expt_rifcs(experiment)

@receiver(post_delete, sender=Project)    
def post_delete_project(sender, **kwargs):
    project = kwargs['instance']
    experiment = project.experiment
    samples = Sample.objects.filter(experiment=experiment)
    for sample in samples:
        try:
            sample.delete()
        except:
            # Do nothing if cannot delete
            continue
    experiment.delete()
    
@receiver(post_delete, sender=Sample)    
def post_delete_sample(sender, **kwargs):
    sample = kwargs['instance']
    dws = DatasetWrapper.objects.filter(sample=sample)
    for dw in dws:
        try:
            ds_id = dw.dataset.id
            dw.delete()
            _remove_deleted_collection_rifcs(sample.experiment, ds_id)  
        except:
            # Do nothing if cannot delete
            continue
    _publish_public_expt_rifcs(sample.experiment)    
    
@receiver(post_delete, sender=DatasetWrapper)
def post_delete_datasetwrapper(sender, **kwargs):
    dw = kwargs['instance']
    try:
        ds = dw.dataset
        if dw.dataset:
            sample = dw.sample
            ds_id = ds.id
            ds.delete()
            _publish_public_expt_rifcs(sample.experiment) 
            _remove_deleted_collection_rifcs(sample.experiment, ds_id)  
    except Dataset.DoesNotExist:
        # Do nothing if cannot delete
        return 
    except Sample.DoesNotExist:
        ds = dw.dataset
        ds.delete()


@receiver(post_delete, sender=Dataset_File)
def post_delete_datafile(sender, **kwargs):
    df = kwargs['instance']
    filepath = df.get_absolute_filepath()
    import os.path
    if os.path.exists(filepath):
        import os
        os.remove(filepath)
        # remove parent dir
    parent_dir = os.path.dirname(filepath)
    if os.path.exists(parent_dir):
        if len(os.listdir(parent_dir)) == 0:
            os.rmdir(parent_dir)
        

def _remove_deleted_collection_rifcs(experiment, ds_id):   
    try:
        providers = settings.RIFCS_PROVIDERS
    except:
        providers = None
    from mecat.rifcs.publishservice import CollectionPublishService
    pservice = CollectionPublishService(providers, experiment)
    pservice.remove_specific_rifcs(settings.OAI_DOCS_PATH, ds_id)
             
def _publish_public_expt_rifcs(experiment):
    try:
        providers = settings.RIFCS_PROVIDERS
    except:
        providers = None
    from mecat.rifcs.publishservice import PartyPublishService, CollectionPublishService
    # Handles party rifcs
    pservice = PartyPublishService(providers, experiment)
    pservice.manage_rifcs(settings.OAI_DOCS_PATH)
    # Handles dataset rifcs
    pservice = CollectionPublishService(providers, experiment)
    pservice.manage_rifcs(settings.OAI_DOCS_PATH)