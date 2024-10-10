from rest_framework import serializers
from .models import ReconciliationFile


class ReconciliationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationFile
        fields = ['source_file', 'target_file']
