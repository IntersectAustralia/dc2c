from django import forms
from django.forms.widgets import Textarea

class SampleForm(forms.Form):
    name = forms.CharField(max_length=40, required=True)
    description = forms.CharField(required=True, widget=Textarea)
    forcode_1 = forms.CharField(max_length=40, required=False, widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_2 = forms.CharField(max_length=40, required=False, widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    forcode_3 = forms.CharField(max_length=40, required=False, widget=forms.TextInput(attrs={'class':'sample_forcode'}))
    notes = forms.CharField(required=False, widget=Textarea)
    

class RegisterMetamanForm(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True,
                               widget=forms.PasswordInput)
    metaman = forms.FileField(required=True)
    principal_investigator = forms.CharField(required=False)
    researchers = forms.CharField(required=False)
    # ldap login!
    experiment_owner = forms.CharField(required=False)
    institution_name = forms.CharField(max_length=400, required=True)
    program_id = forms.CharField(max_length=30, required=False)
    epn = forms.CharField(max_length=30, required=True)
    start_time = forms.DateTimeField(required=False)
    end_time = forms.DateTimeField(required=False)
    title = forms.CharField(max_length=400, required=True)
    description = forms.CharField(required=False)
    beamline = forms.CharField(required=True)
    instrument_url = forms.CharField(required=False)
    instrument_scientists = forms.CharField(required=False)
    # holding sample information
    sample = forms.FileField(required=False)
