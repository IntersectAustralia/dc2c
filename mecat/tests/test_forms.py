"""
test_forms.py
"""

from django.test import TestCase          
from mecat.models import Sample
from mecat.forms import SampleForm, ExperimentWrapperForm
from tardis.tardis_portal import models
from django.contrib.auth.models import User

class SampleFormTestCase(TestCase):
    
    def setUp(self):        
        user = 'tardis_user1'
        pwd = 'secret'
        email = ''
        self.user = User.objects.create_user(user, email, pwd)
        
    def _create_experiment(self): 
        exp = models.Experiment(title='my experiment',
                                institution_name='some institution',
                                description='some description',
                                created_by=User.objects.get(id=self.user.pk),
                                )
        exp.save()
        return exp
    
    def _data_to_post(self, data=None):
        from django.http import QueryDict
        experiment = self._create_experiment()
        data = data or [('name', 'test sample'),
                        ('description', 'experiment description here'),
                        ('forcode_1', '010101112 Structural Biology'),
                        ('forcode_2', '010101113 General Biology'),
                        ('notes', 'some random notes'),
                        ('dataset-MAX_NUM_FORMS', ''),
                        ('dataset-INITIAL_FORMS', '0'),
                        ('dataset-TOTAL_FORMS', '0'),
                        ('experiment', experiment.id)
                        ]
        data = QueryDict('&'.join(['%s=%s' % (k, v) for k, v in data]))
        return data     
    
    def test_validation_correct_data(self):
        post = self._data_to_post()
        f = SampleForm(post)
        self.assertTrue(f.is_valid())   
        
    def test_validation_blank_data(self):
        experiment = self._create_experiment()
        post = self._data_to_post([('name', ''),
                                    ('description', ''),
                                    ('dataset-MAX_NUM_FORMS', ''),
                                    ('dataset-INITIAL_FORMS', '0'),
                                    ('dataset-TOTAL_FORMS', '0'),
                                    ('experiment', experiment.id)
                                   ])        
        f = SampleForm(post)

        self.assertFalse(f.is_valid())
        self.assertTrue('name' in f.errors)
        self.assertTrue('description' in f.errors)
    
    def test_validation_spaces_strings(self):
        experiment = self._create_experiment()
        post = self._data_to_post([('name', '  '),
                                    ('description', '  '),
                                    ('dataset-MAX_NUM_FORMS', ''),
                                    ('dataset-INITIAL_FORMS', '0'),
                                    ('dataset-TOTAL_FORMS', '0'),
                                    ('experiment', experiment.id)
                                   ])        
        f = SampleForm(post)

        self.assertFalse(f.is_valid())
        self.assertTrue('name' in f.errors)
        self.assertTrue('description' in f.errors)
    
class ExperimentFormTestCase(TestCase):
    
    def setUp(self):
        user = 'tardis_user1'
        pwd = 'secret'
        email = ''
        self.user = User.objects.create_user(user, email, pwd)
        
    def _data_to_post(self, data=None):
        from django.http import QueryDict
        data = data or [('title', 'test experiment'),
                        ('authors', 'userA, userB'),
                        ('created_by', self.user.pk),
                        ('description', 'experiment description here'),
                        ('institution_name', 'some university'),
                        ('forcode_1', '010101112 Structural Biology'),
                        ('forcode_2', '010101113 General Biology'),
                        ('funded_by', 'Medical Research Council (NHMRC)'),
                        ('notes', 'some random notes'),
                        ('sample-MAX_NUM_FORMS', ''),
                        ('sample-INITIAL_FORMS', '0'),
                        ('sample-TOTAL_FORMS', '2'),
                        ('sample-0-id', ''),
                        ('sample-0-name', 'first sample name'),
                        ('sample-0-description', 'first sample decription'),
                        ('sample-0-immutable', 'False'),
                        ('sample-1-id', ''),
                        ('sample-1-name', 'first sample description'),
                        ('sample-1-description', 'second sample description'),
                        ('sample-1-immutable', 'False')
                        ]
        data = QueryDict('&'.join(['%s=%s' % (k, v) for k, v in data]))
        return data  
    
    def _create_authors(self, data, exp):
        for i, a in enumerate(data['authors'].split(', ')):
            ae = models.Author_Experiment(experiment=exp,
                                          author=a,
                                          order=i)
            ae.save()
            
    def _create_samples(self, exp):
        sample_desc = {'s1 name': 's1 desc',
                       's2 name': 's2 desc'}
        for name, desc in sample_desc.items():
            sample = Sample(name=name, description=desc,
                            experiment=exp)
            sample.save()
    
    def _create_experiment(self, data=None):    
        data = self._data_to_post(data)
        exp = models.Experiment(title=data['title'],
                                institution_name=data['institution_name'],
                                description=data['description'],
                                created_by=User.objects.get(id=data['created_by']),
                                )
        exp.save()
        self._create_authors(data, exp)
        self._create_samples(exp)
        return exp
        
    def test_validation_correct_data(self):
        post = self._data_to_post()
        f = ExperimentWrapperForm(post)
        self.assertTrue(f.is_valid())   
        
    def test_validation_instance_data(self):   
        exp = self._create_experiment()  
        f = ExperimentWrapperForm(instance=exp)
        # WIP
        #f.is_valid()
        #raise Exception(f)
        #self.assertTrue(f.is_valid())
    
    def test_validation_blank_data(self):
        post = self._data_to_post([('authors', ''),
                                   ('created_by', ''),
                                   ('description', ''),
                                   ('institution_name', ''),
                                   ('title', ''),
                                   ('sample-MAX_NUM_FORMS', ''),
                                   ('sample-INITIAL_FORMS', '0'),
                                   ('sample-TOTAL_FORMS', '0'),
                                   ])        
        f = ExperimentWrapperForm(post)

        self.assertFalse(f.is_valid())
        self.assertTrue('authors' in f.errors)
        #self.assertTrue('description' in f.errors)
        self.assertTrue('institution_name' in f.errors)
        self.assertTrue('title' in f.errors)
    