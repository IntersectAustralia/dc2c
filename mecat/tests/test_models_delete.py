"""
test_models_delete
http://docs.djangoproject.com/en/dev/topics/testing/

"""
from django.test import TestCase
from mecat.models import *
from tardis.tardis_portal.models import Experiment, Dataset, Dataset_File

class ModelsDeleteTestCase(TestCase):
     def setUp(self):
        from django.contrib.auth.models import User
        user = 'tardis_user1'
        pwd = 'secret'
        email = ''
        self.user = User.objects.create_user(user, email, pwd)
        self.desc = "Some Experiment's Description"
        self.experiment = Experiment(title='test exp1', 
                             description=self.desc,
                             institution_name='usyd',
                             created_by=self.user)        
        self.experiment.save()
        
     def _prepare_project(self):
         project = Project(experiment=self.experiment)
         project.save()
         s1 = Sample(experiment=self.experiment, name="S1", description="s1 desc")
         s1.save()
         s2 = Sample(experiment=self.experiment, name="S2", description="s2 desc")
         s2.save()
         dw1 = DatasetWrapper(sample=s1, name="dw1", description="dw1 desc")
         dw2 = DatasetWrapper(sample=s1, name="dw2", description="dw2 desc")
         dw3 = DatasetWrapper(sample=s2, name="dw3", description="dw3 desc")
         ds1 = Dataset(experiment=self.experiment, description=dw1.description)
         ds2 = Dataset(experiment=self.experiment, description=dw2.description)
         ds3 = Dataset(experiment=self.experiment, description=dw3.description)
         ds1.save()
         ds2.save()
         ds3.save()
         dw1.dataset = ds1
         dw1.save()
         dw2.dataset = ds2
         dw2.save()
         dw3.dataset = ds3
         dw3.save()
         return project
        
     def test_project_cascade_delete(self):
        project = self._prepare_project()
        project.delete()
        # assert everything is deleted
        self.assertEqual(0, Project.objects.filter(pk=project.pk).count())
        self.assertEqual(0, Sample.objects.filter(name="S1").count())
        self.assertEquals(0, Sample.objects.filter(name="S2").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw1").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw2").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw3").count())
        self.assertEquals(0, Dataset.objects.filter(experiment=self.experiment).count())
        
     def test_sample_cascade_delete(self):
        project=self._prepare_project()
        sample = Sample.objects.get(name="S1")
        sample.delete()
        
        self.assertEqual(1, Project.objects.filter(pk=project.pk).count())
        self.assertEqual(0, Sample.objects.filter(name="S1").count())
        self.assertEquals(1, Sample.objects.filter(name="S2").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw1").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw2").count())
        self.assertEquals(1, DatasetWrapper.objects.filter(name="dw3").count())       
        self.assertEquals(0, Dataset.objects.filter(description="dw1 desc").count())
        self.assertEquals(0, Dataset.objects.filter(description="dw2 desc").count())
        self.assertEquals(1, Dataset.objects.filter(description="dw3 desc").count())

     def test_datasetwrapper_cascade_delete(self):
        project=self._prepare_project()
        dw = DatasetWrapper.objects.get(name="dw2")
        dw.delete()
        
        self.assertEqual(1, Project.objects.filter(pk=project.pk).count())
        self.assertEqual(1, Sample.objects.filter(name="S1").count())
        self.assertEquals(1, Sample.objects.filter(name="S2").count())
        self.assertEquals(1, DatasetWrapper.objects.filter(name="dw1").count())
        self.assertEquals(0, DatasetWrapper.objects.filter(name="dw2").count())
        self.assertEquals(1, DatasetWrapper.objects.filter(name="dw3").count())       
        self.assertEquals(1, Dataset.objects.filter(description="dw1 desc").count())
        self.assertEquals(0, Dataset.objects.filter(description="dw2 desc").count())
        self.assertEquals(1, Dataset.objects.filter(description="dw3 desc").count())
