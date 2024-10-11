import logging
from django.core.exceptions import ValidationError
from rest_framework import status, views
from rest_framework.response import Response
from reconciliation.serializers import ReconciliationFileSerializer


logger = logging.getLogger(__name__)


class FileUploadView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = ReconciliationFileSerializer(data=request.data)
            if serializer.is_valid():
                source_file = request.FILES.get('source_file')
                target_file = request.FILES.get('target_file')

                if not self.is_csv_file(source_file):
                    return Response({"error": "Source file is not a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

                if not self.is_csv_file(target_file):
                    return Response({"error": "Target file is not a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

                file_instance = serializer.save()
                logger.info(f"File {file_instance.id} uploaded successfully.")
                return Response({"message": "Files uploaded successfully", "id": file_instance.id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def is_csv_file(self, file):
        """
        Check if the uploaded file is a CSV file based on its content type.
        """
        if file is None:
            return False
        return file.name.endswith('.csv') or file.content_type == 'text/csv'
