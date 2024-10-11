import csv
import logging
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework import status, views
from rest_framework.response import Response
from reconciliation.serializers import ReconciliationFileSerializer
from reconciliation.models import ReconciliationFile
from reconciliation.utils import reconcile_files


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

    def get(self, request, file_id, format=None):
        try:
            reconciliation_file = ReconciliationFile.objects.get(id=file_id)
            source_file = reconciliation_file.source_file.path
            target_file = reconciliation_file.target_file.path

            response_data = reconcile_files(source_file, target_file)

            output_format = request.accepted_renderer.format
            output_format = format if format else output_format

            if output_format == 'csv':
                return self.generate_csv_response(**response_data)
            elif output_format == 'html':
                return Response(response_data, template_name='reconciliation_report.html')
            else:
                return Response(response_data, status=status.HTTP_200_OK)

        except ReconciliationFile.DoesNotExist:
            logger.error(f"Reconciliation file with ID {file_id} not found.")
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error during reconciliation: {e}")
            if e.args[0] == 'source and target headers do not match':
                return Response({"error": "Source and target columns do not match"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unable to reconcile files"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_csv_response(self, **response_data):
        """
        Generate CSV response with proper formatting for missing records and discrepancies.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reconciliation.csv"'
        writer = csv.writer(response)

        missing_in_target = response_data.get('missing_in_target', [])
        missing_in_source = response_data.get('missing_in_source', [])
        discrepancies = response_data.get('discrepancies', [])

        self.generate_missing_records_section(
            writer, 'Missing in Target', missing_in_target)

        self.generate_missing_records_section(
            writer, 'Missing in Source', missing_in_source)

        self.generate_discrepancies_section(writer, discrepancies)

        return response

    def generate_missing_records_section(self, writer, section_title, missing_records):
        """
        Generate a CSV section for missing records (either in target or source).

        :param writer: CSV writer object
        :param section_title: Title of the section (e.g., "Missing in Target" or "Missing in Source")
        :param missing_records: List of records missing in the target or source
        """
        writer.writerow([section_title])  # Section header
        writer.writerow(['ID', 'Name', 'Date', 'Amount'])  # Column headers
        for record in missing_records:
            writer.writerow([record.get('ID'), record.get('Name'),
                            record.get('Date'), record.get('Amount')])

        writer.writerow([])  # Empty row as a separator

    def generate_discrepancies_section(self, writer, discrepancies):
        """
        Generate a CSV section for discrepancies between source and target records.

        :param writer: CSV writer object
        :param discrepancies: List of discrepancies between source and target records
        """
        writer.writerow(['Discrepancies'])  # Section header
        writer.writerow(['ID', 'Field', 'Source Value',
                        'Target Value'])  # Column headers
        for discrepancy in discrepancies:
            discrepancy_id = discrepancy['id']
            for detail in discrepancy['discrepancy_details']:
                writer.writerow([
                    discrepancy_id,
                    detail['field'],
                    detail['source_value'],
                    detail['target_value']
                ])
