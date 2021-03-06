from tardis.tardis_portal.publish.publishservice import PublishService

PARTY_RIFCS_FILENAME = "MyTARDIS-party-%s.xml"
COLLECTION_RIFCS_FILENAME = "MyTARDIS-%s-dataset-%s.xml"

class PartyPublishService(PublishService):
    def get_template(self, type):
        return self.provider.get_template(type=type)    
        
    def _remove_rifcs_from_oai_dir(self, oaipath):    
        #owner = self.experiment.created_by
        #import os
        #filename = os.path.join(oaipath, PARTY_RIFCS_FILENAME % owner.id)
        #if os.path.exists(filename):
        #    os.remove(filename)
        return 
    
    def _write_rifcs_to_oai_dir(self, oaipath):
        from tardis.tardis_portal.xmlwriter import XMLWriter
        xmlwriter = XMLWriter()
        owner = self.experiment.created_by
        xmlwriter.write_template_to_dir(oaipath, PARTY_RIFCS_FILENAME % owner.id, 
                                        self.get_template(type="party"), self.get_context())
           
class CollectionPublishService(PublishService):
   
    def get_template(self, type):
        return self.provider.get_template(type=type)
        
    def remove_specific_rifcs(self, oaipath, dataset_id):
        import os    
        filename = os.path.join(oaipath, COLLECTION_RIFCS_FILENAME % (self.experiment.id, dataset_id) )
        if os.path.exists(filename):
            os.remove(filename)
            
    def _remove_rifcs_from_oai_dir(self, oaipath):    
        import os
        datasets = self.experiment.dataset_set
        for dataset_vals in datasets.values():
            dataset_id = dataset_vals['id']
            filename = os.path.join(oaipath, COLLECTION_RIFCS_FILENAME % (self.experiment.id, dataset_id) )
            if os.path.exists(filename):
                os.remove(filename)
    
    def _write_rifcs_to_oai_dir(self, oaipath):
        from tardis.tardis_portal.xmlwriter import XMLWriter
        xmlwriter = XMLWriter()
        datasets = self.experiment.dataset_set
        for dataset_vals in datasets.values():
            dataset_id = dataset_vals['id']
            self.provider.set_dataset_id(dataset_id)
            xmlwriter.write_template_to_dir(oaipath, COLLECTION_RIFCS_FILENAME % 
                                            (self.experiment.id, dataset_id), 
                                            self.get_template(type="dataset"), 
                                            self.get_context())