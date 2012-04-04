from tardis.tardis_portal.models import *

class Project(Experiment):
    FORCODE1_DEFAULT = "060112 Structural Biology"
    FORCODE2_DEFAULT = "060199 Biochemistry and cell Biology not elsewhere classified"
    FUNDED_BY_CHOICES = [("Australian Research Council (ARC)", "Australian Research Council (ARC)"),
                 ("Medical Research Council (NHMRC)", "Medical Research Council (NHMRC)")]
    
    forcode1 = models.CharField(max_length=100, blank=True, default=FORCODE1_DEFAULT)
    forcode2 = models.CharField(max_length=100, blank=True, default=FORCODE2_DEFAULT)
    forcode3 = models.CharField(max_length=100, blank=True)
    funded_by = models.CharField(max_length=100, blank=True, choices=FUNDED_BY_CHOICES)
    notes = models.TextField(blank=True)

class Sample(models.Model):
    """
    This Sample class is the 2nd tier in the DC2C 4-tier model:
    Experiment -> Sample -> Dataset -> Datafile
    
    It points to the Experiment it belongs to, and it also has the 
    rif-cs information for Sample.
    """
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
    """
    This DatasetWrapper class serves as a wrapper to the existing Dataset
    model in the core MyTARDIS. This is so we can add another middle tier to
    the existing 3-tier MyTARDIS core model.
    
    It points to the Sample it belongs to, and the Dataset instance that it
    is wrapping.
    
    In DC2C, when creating a Dataset in a Sample, we must create a DatasetWrapper
    alongside the Dataset, so that we have the link between Sample and Dataset. 
    """
    sample = models.ForeignKey(Sample)
    description = models.TextField(blank=False) # temporary
    dataset = models.ForeignKey(Dataset)
    objects = OracleSafeManager()

    def __unicode__(self):
       return 'wrapper for ' + self.dataset.description



