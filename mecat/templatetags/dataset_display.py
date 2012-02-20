from django import template
from mecat.models import DatasetWrapper

register = template.Library()

@register.inclusion_tag('inclusion_tags/dataset.html')
def display_dataset(sample_id):
    inclusion_context = {}
    datasetwrappers = DatasetWrapper.objects.filter(sample=sample_id)
    datasets = [wrapper.dataset for wrapper in datasetwrappers]
    inclusion_context = {'datasets' : datasets}
    return inclusion_context