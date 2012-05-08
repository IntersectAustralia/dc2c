from django.template import Context 
from tardis.tardis_portal.models import ExperimentParameter, ParameterName, Schema  
from django.conf import settings
import tardis.tardis_portal.publish.provider.rifcsprovider as rifcsprovider
    
SERVER_URL = "https://dc2c.server.gov.au"
HARVEST_URL = "http://dc2c.server.gov.au/oai/provider"

    
class DC2CRifCsProvider(rifcsprovider.RifCsProvider):      
    
    def __init__(self):
        super(DC2CRifCsProvider, self).__init__()
      
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
        
    def get_key(self, experiment):
        return "mytardis-nsw-activity-%s" % (experiment.id)  
        
    def get_notes(self, experiment):
        # TODO
        return "Some notes"
    
    def get_owners(self, experiment):
        # TODO
        return ["Some owner key"]

    def get_related_datasets(self, experiment):
        # TODO
        return ["dataset key 1", "dataset key 2"]
    
    
    def get_funded_by(self, experiment):
        # TODO
        return ["http://purl.org/au-research/grants/nhmrc/100009",
                "http://purl.org/au-research/grants/arc/DP0559024"]
    
    def get_forcodes(self, experiment):
        # TODO
        return ["1103", "1117"]

    def get_rights(self, experiment):
        if self.get_license_uri(experiment):
            return []
        return [('This information is supplied on the condition that the '
                'primary investigators are credited in any publications '
                'that use the data.')]

    def get_access_rights(self, experiment):
        if self.get_license_uri(experiment):
            return []
        return [('This collection of data is released as-is. Where data is '
                'publicly accessible, data will no longer be subject to embargo '
                'and can be used freely provided attribution for the source is '
                'given. It is encouraged that persons interested in using the '
                'data contact the parties listed for this record to obtain '
                'guidance and context in applying this data set and to stay '
                'informed about upcoming revisions and related releases of '
                'interest.')]

    def get_rifcs_context(self, experiment):
        c = super(DC2CRifCsProvider, self).get_rifcs_context(experiment)
        c['originating_source'] = self.get_originating_source()
        c['key'] = self.get_key(experiment)
        c['anzsrcfor'] = self.get_forcodes(experiment)
        c['funded_by'] = self.get_funded_by(experiment)
        c['notes']= self.get_notes(experiment)
        c['related_datasets'] = self.get_related_datasets(experiment)
        c['owners'] = self.get_owners(experiment)
        return c
