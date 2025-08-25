import os
from django.shortcuts import render
from django.conf import settings
from .forms import UploadCobolForm
from .conversion import convert_cobol_to_java

def home(request):
    cobol_code = ''
    java_code = ''
    logs = ''
    if request.method == 'POST':
        form = UploadCobolForm(request.POST, request.FILES)
        if form.is_valid():
            cobol_file = form.cleaned_data['cobol_file']
            cobol_code = cobol_file.read().decode('utf-8')
            java_code, logs = convert_cobol_to_java(cobol_code)
    else:
        form = UploadCobolForm()
    return render(request, 'cobol_converter/home.html', {
        'form': form,
        'cobol_code': cobol_code,
        'java_code': java_code,
        'logs': logs,
    })
