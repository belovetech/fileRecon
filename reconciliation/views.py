import csv
import logging
from django.http import HttpResponse, Http404, JsonResponse
from rest_framework import status,  generics
from rest_framework.response import Response
from reconciliation.serializers import ReconciliationFileSerializer
from reconciliation.models import ReconciliationFile
from reconciliation.utils import reconcile_files


logger = logging.getLogger(__name__)


class FileUploadView(generics.CreateAPIView):
    queryset = ReconciliationFile.objects.all()
    serializer_class = ReconciliationFileSerializer

    def create(self, request, *args, **kwargs):
        """
        Overriding the create method to handle file validation and provide custom response.
        """
        source_file = request.FILES.get('source_file')
        target_file = request.FILES.get('target_file')

        if not self.is_csv_file(source_file):
            return Response({"error": "Source file is not a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)
        if not self.is_csv_file(target_file):
            return Response({"error": "Target file is not a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_instance = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Files uploaded successfully", "id": file_instance.id},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """
        Save the file instance and return it.
        """
        return serializer.save()

    def is_csv_file(self, file):
        """
        Check if the uploaded file is a CSV file based on its content type.
        """
        if file is None:
            return False
        return file.name.endswith('.csv') or file.content_type == 'text/csv'


class FileReconciliationView(generics.RetrieveAPIView):
    queryset = ReconciliationFile.objects.all()
    serializer_class = ReconciliationFileSerializer
    lookup_field = 'id'

    def get_object(self):
        """
        Override get_object to explicitly handle the DoesNotExist exception
        and return a custom 'File not found' error response.
        """
        try:
            file_id = self.kwargs.get(self.lookup_field)
            return ReconciliationFile.objects.get(id=file_id)
        except ReconciliationFile.DoesNotExist:
            logger.error(f"Reconciliation file with ID {file_id} not found.")
            raise Http404

    def get(self, request, *args, **kwargs):
        """
            Overriding get method to handle file validation and logging.
        """
        try:
            format = kwargs.get('format')
            reconciliation_file = self.get_object()
            source_file = reconciliation_file.source_file.path
            target_file = reconciliation_file.target_file.path

            response_data = reconcile_files(source_file, target_file)
            response_format = request.query_params.get('format', 'json')
            response_format = format if format else response_format

            if response_format == 'csv':
                return self.generate_csv_response(**response_data)
            elif response_format == 'html':
                return Response(response_data, template_name='reconciliation_report.html')
            else:
                return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            logger.error(f"Error during reconciliation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error during reconciliation: {e}")
            return Response({"error": "Unable to reconcile files"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_csv_response(self, **response_data):
        """
        Generate CSV response with proper formatting for missing records and discrepancies.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reconciliation.csv"'
        writer = csv.writer(response)

        self.generate_missing_records_section(
            writer, 'Missing in Target', response_data.get('missing_in_target', []))
        self.generate_missing_records_section(
            writer, 'Missing in Source', response_data.get('missing_in_source', []))
        self.generate_discrepancies_section(
            writer, response_data.get('discrepancies', []))

        return response

    def generate_missing_records_section(self, writer, section_title, missing_records):
        """
        Generate a CSV section for missing records (either in target or source).
        """
        writer.writerow([section_title])
        writer.writerow(['ID', 'Name', 'Date', 'Amount'])
        for record in missing_records:
            writer.writerow([record.get('ID'), record.get(
                'Name'), record.get('Date'), record.get('Amount')])
        writer.writerow([])

    def generate_discrepancies_section(self, writer, discrepancies):
        """
        Generate  a CSV section for discrepancy records
        """
        writer.writerow(['Discrepancies'])
        writer.writerow(['ID', 'Field', 'Source Value', 'Target Value'])
        for discrepancy in discrepancies:
            discrepancy_id = discrepancy['id']
            for detail in discrepancy['discrepancy_details']:
                writer.writerow([
                    discrepancy_id,
                    detail['field'],
                    detail['source_value'],
                    detail['target_value']
                ])


def custom_404(request, exception):
    response_data = {
        "error": "The resource you requested was not found",
        "status_code": 404
    }
    return JsonResponse(response_data, status=404)
