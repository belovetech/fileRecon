from django.db import models


class ReconciliationFile(models.Model):
    source_file = models.FileField(upload_to='uploads/')
    target_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
