from django.template import Context 
from tardis.tardis_portal.models import ExperimentParameter, ParameterName, Schema  

import tardis.tardis_portal.publish.provider.rifcsprovider as rifcsprovider
    
SERVER_URL = "https://dc2c.server.gov.au"
HARVEST_URL = "http://dc2c.server.gov.au/oai/provider"

    
class DC2CRifCsProvider(rifcsprovider.RifCsProvider):      
    
    def __init__(self):
        super(DC2CRifCsProvider, self).__init__()
      
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
        return "research-data.ansto.gov.au/collection/bragg/%s" % (experiment.id)  
         
    def get_url(self, experiment, url):
        return url + "/" + str(experiment.id)

    def get_produced_bys(self):
        return None
    
    def get_forcodes(self):
        return "123445566"

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
        c['blnoun'] = 'instrument'
        c['originating_source'] = self.get_originating_source()
        c['key'] = self.get_key(experiment)
        c['url'] = self.get_url(experiment, SERVER_URL)
        c['produced_bys'] = self.get_produced_bys()
        c['anzsrcfor'] = self.get_forcodes()
        #c['rights'] = self.get_rights(experiment)
        #c['access_rights'] = self.get_access_rights(experiment)
        return c
