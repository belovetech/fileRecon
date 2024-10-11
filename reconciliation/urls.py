from django.urls import path
from reconciliation.views import FileUploadView, FileReconciliationView
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('reconcile/<int:file_id>/',
         FileReconciliationView.as_view(), name='reconcile-files'),
]

urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'html', "csv"])
