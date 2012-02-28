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
        
        sample_name = cleaned_data['sample_name']
        
        new_sample = Sample(description=sample_name, experiment_id=self.experiment_id)
        new_sample.save()