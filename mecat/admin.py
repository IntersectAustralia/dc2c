from django.contrib import admin
from django.forms import TextInput
from mecat.models import Sample, DatasetWrapper, ExperimentWrapper
import django.db

class SampleAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
class DatasetWrapperAdmin(admin.ModelAdmin):
    search_fields = ['dataset__id', 'sample__id']
    
class ExperimentWrapperAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
admin.site.register(Sample, SampleAdmin)
admin.site.register(DatasetWrapper, SampleAdmin)
admin.site.register(ExperimentWrapper, SampleAdmin)