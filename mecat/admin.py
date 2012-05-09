from django.contrib import admin
from django.forms import TextInput
from mecat.models import Sample
from mecat.models import DatasetWrapper
from mecat.models import Project
from mecat.models import OwnerDetails
import django.db

class SampleAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
class DatasetWrapperAdmin(admin.ModelAdmin):
    search_fields = ['dataset__id', 'sample__id']
    
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
class OwnerDetailsAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'email', 'user__id']
    
admin.site.register(Sample, SampleAdmin)
admin.site.register(DatasetWrapper, DatasetWrapperAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(OwnerDetails, OwnerDetailsAdmin)