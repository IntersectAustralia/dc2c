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
