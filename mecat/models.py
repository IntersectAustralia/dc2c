from tardis.tardis_portal.models import *

class ExperimentWrapper(models.Model):
    experiment = models.ForeignKey(Experiment)
    forcode1 = models.TextField(blank=True)
    forcode2 = models.TextField(blank=True)
    forcode3 = models.TextField(blank=True)
    funded_by = models.TextField(blank=True)
    notes = models.CharField(blank=True, max_length=100)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return 'wrapper for ' + self.experiment.description
    
class Sample(models.Model):
    experiment = models.ForeignKey(Experiment)
    description = models.TextField(blank=False)
    name = models.CharField(max_length=100, blank=False)
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
    description = models.TextField(blank=False) # temporary
    dataset = models.ForeignKey(Dataset)
    objects = OracleSafeManager()

    def __unicode__(self):
       return 'wrapper for ' + self.dataset.description



