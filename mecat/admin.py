from django.contrib import admin
from django.forms import TextInput
from mecat.models import Sample
import django.db

class SampleAdmin(admin.ModelAdmin):
    search_fields = ['description', 'experiment__id']
    
admin.site.register(Sample, SampleAdmin)