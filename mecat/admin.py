from django.contrib import admin
from django.forms import TextInput
from mecat.models import Project, Sample, DatasetWrapper
import django.db

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description', 'project__id']

class SampleAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
class DatasetWrapperAdmin(admin.ModelAdmin):
    search_fields = ['dataset__id', 'sample__id']
    
    
admin.site.register(Project, ProjectAdmin)    
admin.site.register(Sample, SampleAdmin)
admin.site.register(DatasetWrapper, SampleAdmin)