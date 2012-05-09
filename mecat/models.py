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
    title = models.CharField(max_length=30, blank=False, validators=[validate_spaces])
    first_name = models.CharField(max_length=200, blank=False, validators=[validate_spaces])
    last_name = models.CharField(max_length=200, blank=False, validators=[validate_spaces])
    email = models.CharField(max_length=100, blank=False, validators=[validate_spaces])
    
    def __unicode__(self):
        return 'details for ' + self.first_name + ' ' + self.last_name    

@receiver(post_save, sender=Experiment)
@receiver(post_delete, sender=Experiment)
def post_save_experiment(sender, **kwargs):
    # create party and dataset rifcs too - note that the activity rifcs
    # is taken care of in the core model
    experiment = kwargs['instance']
    _publish_public_expt_rifcs(experiment)
    
@receiver(post_save, sender=DatasetWrapper)
@receiver(post_delete, sender=DatasetWrapper)    
def post_save_datasetwrapper(sender, **kwargs):
    datasetwrapper = kwargs['instance']


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
    experiment.delete()
    
    
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