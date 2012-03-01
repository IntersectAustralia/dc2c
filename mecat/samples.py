import logging

from django.conf import settings
from django.db import transaction

from mecat.models import Sample, DatasetWrapper

logger = logging.getLogger(__name__)

class SampleFormHandler(object):
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        
    @transaction.commit_on_success
    def add_sample(self, cleaned_data):
        logger.debug('adding sample')
        logger.debug(cleaned_data)
        
        sample_name = cleaned_data['name']
        sample_description = cleaned_data['description']
        sample_forcode1 = cleaned_data['forcode_1']
        sample_forcode2 = cleaned_data['forcode_2']
        sample_forcode3 = cleaned_data['forcode_3']
        sample_notes = cleaned_data['notes']
        
        new_sample = Sample(experiment_id=self.experiment_id,
                            name=sample_name,
                            description=sample_description,
                            forcode1=sample_forcode1,
                            forcode2=sample_forcode2,
                            forcode3=sample_forcode3,
                            notes=sample_notes)
        new_sample.save()
    
    @transaction.commit_on_success
    def edit_sample(self, cleaned_data, sample_id):
        logger.debug('editing sample')
        logger.debug(cleaned_data)
        
        sample_name = cleaned_data['name']
        sample_description = cleaned_data['description']
        sample_forcode1 = cleaned_data['forcode_1']
        sample_forcode2 = cleaned_data['forcode_2']
        sample_forcode3 = cleaned_data['forcode_3']
        sample_notes = cleaned_data['notes']
        
        sample = Sample.objects.get(id=sample_id)
        sample.name = sample_name
        sample.description = sample_description
        sample.forcode1 = sample_forcode1
        sample.forcode2 = sample_forcode2
        sample.forcode3 = sample_forcode3
        sample.notes = sample_notes
        
        sample.save()
    
    def form_data(self, sample_id):
        sample = Sample.objects.get(id=sample_id)
        data = {}
        data['name'] = sample.name
        data['description'] = sample.description
        data['forcode_1'] = sample.forcode1
        data['forcode_2'] = sample.forcode2
        data['forcode_3'] = sample.forcode3
        data['notes'] = sample.notes
        return data
        
        