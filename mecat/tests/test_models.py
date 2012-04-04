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
        self.desc = "Some Experiment's Description"
        from tardis.tardis_portal.models import Experiment
        self.experiment = Experiment(title='test exp1', 
                             description=self.desc,
                             institution_name='usyd',
                             created_by=self.user)        
        self.experiment.save()
        
    def test_project(self):     
        from mecat.models import Experiment, Project
        title = "Project 1"
        desc = "My Description for Project created in test_project()"
        forcode1 = "0001"
        forcode2 = "0002"
        forcode3 = "0003 - three"
        funded_by = "NHMRC"
        notes = "A note that is not that long"
        inst = 'usyd'
        project = Project(title=title, description=desc, institution_name=inst,
                          forcode1 = forcode1, forcode2 = forcode2, 
                          forcode3 = forcode3, funded_by = funded_by,
                          notes = notes, created_by=self.user)
        project.save()
        self.assertEquals(project.title, title)
        self.assertEquals(project.description, desc)
        self.assertEquals(project.institution_name, inst)
        self.assertEquals(project.created_by, self.user)
        self.assertEqual(project.forcode1, forcode1)
        self.assertEqual(project.forcode2, forcode2)
        self.assertEqual(project.forcode3, forcode3)
        self.assertEqual(project.notes, notes)
        self.assertEqual(project.funded_by, funded_by)
        
        # Check that the Experiment is created
        experiment_from_db = Experiment.objects.get(description=desc)
        self.assertEquals(experiment_from_db.title, title)
        self.assertEquals(experiment_from_db.description, desc)
        self.assertEquals(experiment_from_db.institution_name, inst)
        self.assertEquals(experiment_from_db.created_by, self.user)
        
        # Check that the Project is created        
        project_from_db = Project.objects.get(description=desc)
        # Check that the project and experiment are linked
        self.assertEquals(experiment_from_db.project.id, project_from_db.id) 
        
        
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
        
        
        