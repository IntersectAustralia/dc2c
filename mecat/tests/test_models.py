"""
test_models.py
http://docs.djangoproject.com/en/dev/topics/testing/

"""
from django.test import TestCase

class ModelTestCase(TestCase):
    
    def setUp(self):
        from django.contrib.auth.models import User
        user = 'tardis_user1'
        pwd = 'secret'
        email = ''
        self.user = User.objects.create_user(user, email, pwd)
        from tardis.tardis_portal.models import Experiment
        self.experiment = Experiment(title='test exp1', 
                             institution_name='usyd',
                             created_by=self.user)        
        self.experiment.save()
        
    def test_sample(self):
        from mecat.models import Sample
        desc = "My Description for Sample created in test_sample()"
        sample = Sample(experiment=self.experiment, description=desc)
        name = "Sample 1"
        forcode1 = "0001"
        forcode2 = "0002"
        forcode3 = "0003 - three"
        notes = "A note that is not that long"
        sample.name = name
        sample.forcode1 = forcode1
        sample.forcode2 = forcode2
        sample.forcode3 = forcode3
        sample.notes = notes
        sample.save()
        self.assertEqual(sample.description, desc)
        self.assertEqual(sample.experiment, self.experiment)
        self.assertEqual(sample.name, name)
        self.assertEqual(sample.forcode1, forcode1)
        self.assertEqual(sample.forcode2, forcode2)
        self.assertEqual(sample.forcode3, forcode3)
        self.assertEqual(sample.notes, notes)
        
        sample_from_db = Sample.objects.get(description=desc)
        self.assertEqual(sample_from_db.experiment, self.experiment)
        
        
    def test_datasetwrapper(self):
        from mecat.models import DatasetWrapper, Sample
        sample_desc = "My Description for Sample created in test_datasetwrapper()"
        
        sample = Sample(experiment=self.experiment, description=sample_desc)
        sample.save()
        self.assertEqual(sample.description, sample_desc)
        self.assertEqual(sample.experiment, self.experiment)
         
        from tardis.tardis_portal.models import Dataset
        dataset_desc = "My Description for Dataset created in test_datasetwrapper()"       
        dataset = Dataset(description=dataset_desc, experiment=self.experiment)
        dataset.save()
        sample_from_db = Sample.objects.get(description=sample_desc)
        dataset_from_db = Dataset.objects.get(description=dataset_desc)
        datasetwrapper = DatasetWrapper(sample=sample_from_db, dataset=dataset_from_db)
        datasetwrapper.save()
        self.assertEqual(datasetwrapper.sample, sample_from_db)
        self.assertEqual(datasetwrapper.dataset, dataset_from_db)
        
        datasetwrapper_from_db = DatasetWrapper.objects.get(sample__description=sample_desc)
        self.assertEqual(datasetwrapper_from_db.dataset.pk, dataset_from_db.pk)
        
        
        