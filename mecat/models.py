from tardis.tardis_portal.models import *
  

class Sample(models.Model):
    experiment = models.ForeignKey(Experiment)
    description = models.TextField(blank=True)
    immutable = models.BooleanField(default=False)
    objects = OracleSafeManager()

    def __unicode__(self):
        return self.description


class DatasetWrapper(models.Model):
    sample = models.ForeignKey(Sample)
    dataset = models.ForeignKey(Dataset)
    objects = OracleSafeManager()

    def __unicode__(self):
       return 'wrapper for' + dataset.description



