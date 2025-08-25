from django import forms

class UploadCobolForm(forms.Form):
    cobol_file = forms.FileField(label='Upload COBOL File')
