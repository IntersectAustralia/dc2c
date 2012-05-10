from tardis.tardis_portal.publish.publishservice import PublishService

PARTY_RIFCS_FILENAME = "MyTARDIS-%s-party.xml"
COLLECTION_RIFCS_FILENAME = "MyTARDIS-%s-dataset.xml"

class PartyPublishService(PublishService):
    def get_template(self, type):
        return self.provider.get_template(type)    
        
    def _remove_rifcs_from_oai_dir(self, oaipath):    
        import os
        filename = os.path.join(oaipath, PARTY_RIFCS_FILENAME % self.experiment.id)
        if os.path.exists(filename):
            os.remove(filename)
    
    def _write_rifcs_to_oai_dir(self, oaipath):
        from tardis.tardis_portal.xmlwriter import XMLWriter
        xmlwriter = XMLWriter()
        xmlwriter.write_template_to_dir(oaipath, PARTY_RIFCS_FILENAME % self.experiment.id, 
                                        self.get_template(type="party"), self.get_context())
        
        
class CollectionPublishService(PublishService):
    def get_template(self, type):
        return self.provider.get_template(type)
        
    def _remove_rifcs_from_oai_dir(self, oaipath):    
        import os
        filename = os.path.join(oaipath, PARTY_RIFCS_FILENAME % self.experiment.id)
        if os.path.exists(filename):
            os.remove(filename)
    
    def _write_rifcs_to_oai_dir(self, oaipath):
        from tardis.tardis_portal.xmlwriter import XMLWriter
        xmlwriter = XMLWriter()
        xmlwriter.write_template_to_dir(oaipath, COLLECTION_RIFCS_FILENAME % self.experiment.id, 
                                        self.get_template(type="dataset"), self.get_context())