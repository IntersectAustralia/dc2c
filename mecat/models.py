from tardis.tardis_portal.models import *

class ExperimentWrapper(models.Model):
    experiment = models.ForeignKey(Experiment)
    forcode1 = models.TextField(blank=True)
    forcode2 = models.TextField(blank=True)
    forcode3 = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return 'wrapper for ' + self.experiment.description
    
class Sample(models.Model):
    experiment = models.ForeignKey(Experiment)
    description = models.TextField(blank=True)
    name = models.TextField(blank=True)
    forcode1 = models.TextField(blank=True)
    forcode2 = models.TextField(blank=True)
    forcode3 = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return self.description


class DatasetWrapper(models.Model):
    sample = models.ForeignKey(Sample)
    description = models.TextField(blank=True) # temporary
    dataset = models.ForeignKey(Dataset)
    objects = OracleSafeManager()

    def __unicode__(self):
       return 'wrapper for ' + self.dataset.description



