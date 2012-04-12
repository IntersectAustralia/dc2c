import logging

from django.conf import settings
from django.db import transaction

from mecat.models import Project

logger = logging.getLogger(__name__)

class ExperimentFormHandler(object):
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        
    @transaction.commit_on_success
    def add_experiment(self, cleaned_data):
        logger.debug('adding experiment')
        logger.debug(cleaned_data)
        
        experiment_forcode1 = cleaned_data['forcode_1']
        experiment_forcode2 = cleaned_data['forcode_2']
        experiment_forcode3 = cleaned_data['forcode_3']
        experiment_funded_by = cleaned_data['funded_by']
        experiment_notes = cleaned_data['notes']
        
        new_exp_wrapper= Project(experiment_id=self.experiment_id,
                            forcode1=experiment_forcode1,
                            forcode2=experiment_forcode2,
                            forcode3=experiment_forcode3,
                            funded_by=experiment_funded_by,
                            notes=experiment_notes)
        new_exp_wrapper.save()
    
    @transaction.commit_on_success
    def edit_experiment(self, cleaned_data, experiment_id):
        logger.debug('editing experiment')
        logger.debug(cleaned_data)
        
        experiment_forcode1 = cleaned_data['forcode_1']
        experiment_forcode2 = cleaned_data['forcode_2']
        experiment_forcode3 = cleaned_data['forcode_3']
        experiment_funded_by = cleaned_data['funded_by']
        experiment_notes = cleaned_data['notes']
        
        experiment = Project.objects.get(experiment=experiment_id)
        experiment.forcode1 = experiment_forcode1
        experiment.forcode2 = experiment_forcode2
        experiment.forcode3 = experiment_forcode3
        experiment.funded_by = experiment_funded_by
        experiment.notes = experiment_notes
        
        experiment.save()
    
    def form_data(self, experiment_id):
        experiment = Project.objects.get(experiment=experiment_id)
        data = {}
        data['forcode_1'] = experiment.forcode1
        data['forcode_2'] = experiment.forcode2
        data['forcode_3'] = experiment.forcode3
        data['funded_by']= experiment.funded_by
        data['notes'] = experiment.notes
        return data

