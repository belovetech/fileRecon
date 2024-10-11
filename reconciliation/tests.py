from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile


class FileUploadViewTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-upload')
        self.test_source_file = SimpleUploadedFile(
            'source.csv',
            b'ID,Name,Date,Amount\n001,John Doe,2023-01-01,100.00\n002,Jane Smith,2023-01-02,200.00'
        )
        self.test_target_file = SimpleUploadedFile(
            'target.csv',
            b'ID,Name,Date,Amount\n001,John Doe,2023-01-01,150.00\n002,Jane Smith,2023-01-02,200.00'
        )

    def test_upload_files_success(self):
        response = self.client.post(self.upload_url, {
            'source_file': self.test_source_file,
            'target_file': self.test_target_file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('id', response.data)

    def test_upload_files_invalid(self):
        response = self.client.post(self.upload_url, {
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'],
                         "Source file is not a valid CSV file.")

    def test_get_reconciliation_success(self):
        upload_response = self.client.post(self.upload_url, {
            'source_file': self.test_source_file,
            'target_file': self.test_target_file,
        }, format='multipart')

        file_id = upload_response.data['id']
        reconciliation_url = reverse(
            'reconcile-files', args=[file_id])

        response = self.client.get(reconciliation_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('missing_in_target', response.data)
        self.assertIn('missing_in_source', response.data)
        self.assertIn('discrepancies', response.data)

    def test_get_reconciliation_file_not_found(self):
        response = self.client.get(
            reverse('reconcile-files', args=[999]), format='json')  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "File not found")

    def tearDown(self):
        pass
