from django.template import Context 
from tardis.tardis_portal.models import Dataset, ExperimentParameter, ParameterName, Schema  
from django.conf import settings
import tardis.tardis_portal.publish.provider.rifcsprovider as rifcsprovider
from mecat.models import *
    
SERVER_URL = "https://nswtardis.intersect.org.au"
HARVEST_URL = "https://nswtardis.intersect.org.au/oai/provider"

    
class DC2CRifCsProvider(rifcsprovider.RifCsProvider):      
    
    def __init__(self):
        super(DC2CRifCsProvider, self).__init__()
        self.dataset_id = None

    def _is_mediated(self, experiment):
        import tardis.apps.ands_register.publishing as publishing
        from tardis.apps.ands_register.publishing import PublishHandler      
        phandler = PublishHandler(experiment.id) 
        return phandler.access_type() == publishing.MEDIATED

    def can_publish(self, experiment):       
        return experiment.public or self._is_mediated(experiment)
        
    def set_dataset_id(self, dataset_id):
        self.dataset_id = dataset_id
        
    def get_template(self, experiment=None, type="activity"):
        return settings.RIFCS_TEMPLATE_DIR + "%s.xml" % type  
      
    def get_description(self, experiment):
        from tardis.apps.ands_register.publishing import PublishHandler        
        phandler = PublishHandler(experiment.id) 
        desc = phandler.custom_description()
        if not desc:
            desc = experiment.description
        return super(DC2CRifCsProvider, self).format_desc(desc)
        
    def get_originating_source(self):
        return HARVEST_URL
    
    def get_uri(self, experiment):
        if experiment.public and not self._is_mediated(experiment):
            return "%s/experiment/view/%s" % (SERVER_URL, experiment.id)
        
    def get_activity_key(self, experiment):
        return "mytardis-nsw-activity-%s" % experiment.id
 
    def get_party_key(self, experiment):
        user = experiment.created_by
        return "mytardis-nsw-party-%s" % user.id
        
    def get_dataset_key(self):
        return "mytardis-nsw-dataset-%s" % self.dataset_id
    
    def get_dataset(self):
        if not self.dataset_id:
            return None
        ds = Dataset.objects.get(pk=self.dataset_id)
        return DatasetWrapper.objects.get(dataset=ds)
        
    def get_notes(self, experiment):
        project = Project.objects.get(experiment=experiment)
        return project.notes
    
    def get_dataset_notes(self, experiment):
        if not self.dataset_id:
            return None
        ds = Dataset.objects.get(pk=self.dataset_id)
        dw = DatasetWrapper.objects.get(dataset=ds)
        return dw.sample.notes
    
    def get_owner_details(self, experiment):
        user = experiment.created_by
        return OwnerDetails.objects.get(user=user)
    
    def get_owners(self, experiment):
        # for now there will only be 1 owner
        user = experiment.created_by
        return ["mytardis-nsw-party-%s" % user.id]

    
    def get_related_projects(self, experiment):
        project = Project.objects.get(experiment=experiment)
        return ["mytardis-nsw-activity-%s" % project.id]

    def get_related_activities(self, experiment):
        activity_keys = []
        user = experiment.created_by
        experiments = user.experiment_set
        for experiment_vals in experiments.values():
            e_id = experiment_vals['id']
            project = Project.objects.get(experiment__id=e_id)
            activity_keys.append("mytardis-nsw-activity-%s" % project.id)
        return activity_keys
    
    def get_related_datasets(self, experiment):
        dataset_keys = []
        for dataset_vals in experiment.dataset_set.values():
            dataset_keys.append('mytardis-nsw-dataset-%s' % dataset_vals['id'])
        return dataset_keys
    
    def get_funded_by(self, experiment):
        project = Project.objects.get(experiment=experiment)
        funded_by = project.funded_by
        if funded_by == "Australian Research Council (ARC)":
            return ["http://purl.org/au-research/grants/arc/DP0559024"]
        elif funded_by == "Medical Research Council (NHMRC)":
            return ["http://purl.org/au-research/grants/nhmrc/100009"]
    
    def get_dataset_forcodes(self, experiment):
        if not self.dataset_id:
            return None
        ds = Dataset.objects.get(pk=self.dataset_id)
        dw = DatasetWrapper.objects.get(dataset=ds)
        sample = dw.sample
        forcodes = []
        forcode1 = sample.forcode1
        if forcode1 and forcode1 != '':
            forcodes.append(forcode1[:forcode1.index(' ')])
        forcode2 = sample.forcode2
        if forcode2 and forcode2 != '':
            forcodes.append(forcode2[:forcode2.index(' ')])
        forcode3 = sample.forcode3
        if forcode3 and forcode3 != '':
            forcodes.append(forcode3[:forcode3.index(' ')])            
        return forcodes       
    
    def get_forcodes(self, experiment):
        project = Project.objects.get(experiment=experiment)
        forcodes = []
        forcode1 = project.forcode1
        if forcode1 and forcode1 != '':
            forcodes.append(forcode1[:forcode1.index(' ')])
        forcode2 = project.forcode2
        if forcode2 and forcode2 != '':
            forcodes.append(forcode2[:forcode2.index(' ')])
        forcode3 = project.forcode3
        if forcode3 and forcode3 != '':
            forcodes.append(forcode3[:forcode3.index(' ')])            
        return forcodes

    def get_rights(self, experiment):
        from tardis.tardis_portal.publish.provider.schemarifcsprovider import SchemaRifCsProvider
        srp = SchemaRifCsProvider()        
        if srp.get_license_uri(experiment):
            return None
        return [('This information is supplied on the condition that the '
                'primary investigators are credited in any publications '
                'that use the data.')]

    def get_related_info_list(self, experiment):
        from tardis.tardis_portal.publish.provider.schemarifcsprovider import SchemaRifCsProvider
        srp = SchemaRifCsProvider()   
        return srp.get_related_info_list(experiment)

    def get_access_rights(self, experiment):
        if self._is_mediated(experiment):
           return "This Dataset is available via mediated access by contacting the researcher"
       
        from tardis.tardis_portal.publish.provider.schemarifcsprovider import SchemaRifCsProvider
        srp = SchemaRifCsProvider()         
        if srp.get_license_uri(experiment):
            return None
        return [('This collection of data is released as-is. Where data is '
                'publicly accessible, data will no longer be subject to embargo '
                'and can be used freely provided attribution for the source is '
                'given. It is encouraged that persons interested in using the '
                'data contact the parties listed for this record to obtain '
                'guidance and context in applying this data set and to stay '
                'informed about upcoming revisions and related releases of '
                'interest.')]

    def get_license_uri(self, experiment):
        from tardis.tardis_portal.publish.provider.schemarifcsprovider import SchemaRifCsProvider
        srp = SchemaRifCsProvider()        
        
        if srp.get_license_uri(experiment):
            return srp.get_license_uri(experiment)
        else:
            return None
        
    def get_rifcs_context(self, experiment):
        c = super(DC2CRifCsProvider, self).get_rifcs_context(experiment)
        c['unique_party_key'] = self.get_party_key(experiment)
        c['unique_activity_key'] = self.get_activity_key(experiment)
        c['unique_dataset_key'] = self.get_dataset_key()
        c['originating_source'] = self.get_originating_source()
        c['unique_activity_key'] = self.get_activity_key(experiment)
        c['anzsrcfor'] = self.get_forcodes(experiment)
        c['dataset_anzsrc-for'] = self.get_dataset_forcodes(experiment)
        c['funded_by'] = self.get_funded_by(experiment)
        c['notes']= self.get_notes(experiment)
        c['dataset'] = self.get_dataset()
        c['dataset_notes']=self.get_dataset_notes(experiment)
        c['related_projects'] = self.get_related_projects(experiment)
        c['related_activities'] = self.get_related_activities(experiment)
        c['related_datasets'] = self.get_related_datasets(experiment)
        c['owners'] = self.get_owners(experiment)
        c['rights'] = self.get_rights(experiment)
        c['access_rights'] = self.get_access_rights(experiment)
        c['ownerdetails'] = self.get_owner_details(experiment)
        c['license_uri'] = self.get_license_uri(experiment)
        c['related_info_list'] = self.get_related_info_list(experiment)
        c['uri'] = self.get_uri(experiment)
        return c
