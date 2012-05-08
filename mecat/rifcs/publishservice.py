from tardis.tardis_portal.publish.publishservice import PublishService

PARTY_RIFCS_FILENAME = "MyTARDIS-%s-party.xml"
COLLECTION_RIFCS_FILENAME = "MyTARDIS-%s-collection.xml"

class PartyPublishService(PublishService):
        
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
        
    def _remove_rifcs_from_oai_dir(self, oaipath):    
        import os
        filename = os.path.join(oaipath, PARTY_RIFCS_FILENAME % self.experiment.id)
        if os.path.exists(filename):
            os.remove(filename)
    
    def _write_rifcs_to_oai_dir(self, oaipath):
        from tardis.tardis_portal.xmlwriter import XMLWriter
        xmlwriter = XMLWriter()
        xmlwriter.write_template_to_dir(oaipath, PARTY_RIFCS_FILENAME % self.experiment.id, 
                                        self.get_template(type="collection"), self.get_context())