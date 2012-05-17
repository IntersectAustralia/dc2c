from django.test import TestCase
from tardis.tardis_portal.models import User, Experiment
import mecat.rifcs.provider.dc2crifcsprovider as dc2crifcsprovider
from mecat.rifcs.provider.dc2crifcsprovider import DC2CRifCsProvider
from tardis.apps.ands_register.publishing import PublishHandler
from mecat.models import Project

class DC2CRifCsProviderTestCase(TestCase):
    
    custom_description_key = 'custom_description'
    custom_authors_key = 'custom_authors'
    access_type_key = 'access_type'
    random_custom_description = 'a custom description'
    
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser',
                                             email='user@test.com',
                                             password='secret')
        self.e1 = Experiment(title="Experiment 1", created_by=self.user, public=False)
        self.e1.save()
        self.p1 = Project(experiment=self.e1, forcode1="1234 qwe", forcode2="5678 234", funded_by="me", funding_code="0000")
        self.p1.save()
        self.provider = DC2CRifCsProvider()
        self.publish_data = { 
                    self.custom_authors_key: "",
                    self.custom_description_key: "",
                    self.access_type_key: "public"
                   }       
 
 
    def testInitialisation(self):
        self.assertIsNotNone(self.provider)


    def testCanPublishNotPublicAndUnpublished(self):
        # (experiment.public : False, access type : Unpublished) -> FALSE
        self.assertFalse(self.provider.can_publish(self.e1))    


''' 
    def testCanPublishNotPublicAndMediated(self):     
        # (experiment public: False, access type: mediated) -> True
        self.publish_data[self.access_type_key] = "mediated"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertTrue(self.provider.can_publish(self.e1))      
       
    def testCanPublishNotPublicAndPrivate(self):  
        # (experiment public: False, access type: private) -> True
        self.publish_data[self.access_type_key] = "private"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertFalse(self.provider.can_publish(self.e1))            
     
     
              
    def testCanPublishPublicAndMediated(self):    
        # (experiment public: True, access type: mediated) -> True
        self.e1.public = True
        self.e1.save()
        self.publish_data[self.access_type_key] = "mediated"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertTrue(self.provider.can_publish(self.e1))
                
    def testCanPublishNotPublicAndUnpublished(self):
        # (experiment.public : False, access type : Unpublished) -> FALSE
        self.assertFalse(self.provider.can_publish(self.e1))
        
    def testCanPublishNotPublicAndPrivate(self):  
        # (experiment public: False, access type: private) -> True
        self.publish_data[self.access_type_key] = "private"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)      
        self.assertFalse(self.provider.can_publish(self.e1))
       

             
    def testCanPublishPublicAndPublished(self):
        # (experiment public: True, access type: published) -> True
        self.e1.public = True
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertTrue(self.provider.can_publish(self.e1))
        
    def testCanPublishPublicAndPrivate(self):
        # (experiment public: True, access type: private) -> True
        self.e1.public = True
        self.publish_data[self.access_type_key] = "private"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertTrue(self.provider.can_publish(self.e1))    
        
    def testCanPublishPublicAndUnpublished(self):
        # (experiment public: True, access type: unpublished) -> False
        self.e1.public = True
        self.publish_data[self.access_type_key] = "unpublished"
        ph = PublishHandler(self.e1.id, create=True)
        ph.update(self.publish_data)
        self.assertTrue(self.provider.can_publish(self.e1))       
    
'''