from django.db import models

class UploadedFile(models.Model):
    cobol_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    logs = models.TextField(blank=True, null=True)
