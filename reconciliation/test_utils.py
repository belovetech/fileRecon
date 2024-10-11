import unittest
from io import StringIO
from .utils import normalize_data, find_missing_records, find_discrepancies, read_csv_file, reconcile_files, validate_target_source_header
from unittest.mock import mock_open, patch


class TestUtils(unittest.TestCase):

    def test_normalize_data(self):
        record = {'ID': ' 001 ', 'Name': '  John Doe ',
                  'Date': ' 2023-01-01 ', 'Amount': '  100.00 '}
        expected = {'ID': '001', 'Name': 'John Doe',
                    'Date': '2023-01-01', 'Amount': '100.00'}
        self.assertEqual(normalize_data(record), expected)

    def test_validate_target_source_header(self):
        source_headers = ['ID', 'Name', 'Date', 'Amount']
        target_headers = ['ID', 'Name', 'Date', 'Amount']
        self.assertTrue(validate_target_source_header(
            source_headers, target_headers))

        target_headers = ['ID', 'Name', 'Date']
        with self.assertRaises(Exception):
            validate_target_source_header(source_headers, target_headers)

        target_headers = ['ID', 'Name', 'Amount', 'Date']
        with self.assertRaises(Exception):
            validate_target_source_header(source_headers, target_headers)

    def test_find_missing_records(self):
        source_dict = {'001': {'ID': '001', 'Name': 'John Doe'},
                       '002': {'ID': '002', 'Name': 'Jane Smith'}}
        target_dict = {'002': {'ID': '002', 'Name': 'Jane Smith'}}

        expected_missing_in_target = [{'ID': '001', 'Name': 'John Doe'}]
        self.assertEqual(find_missing_records(
            source_dict, target_dict), expected_missing_in_target)

        expected_missing_in_source = []
        self.assertEqual(find_missing_records(
            target_dict, source_dict), expected_missing_in_source)

    def test_find_discrepancies(self):
        source_dict = {'001': {'ID': '001', 'Name': 'John Doe', 'Amount': '100.00'}, '002': {
            'ID': '002', 'Name': 'Jane Smith', 'Amount': '200.00'}}
        target_dict = {'001': {'ID': '001', 'Name': 'John Doe', 'Amount': '150.00'}, '002': {
            'ID': '002', 'Name': 'Jane Doe', 'Amount': '200.00'}}

        expected_discrepancies = [
            {
                'id': '001',
                'discrepancy_details': [
                    {'field': 'Amount', 'source_value': '100.00',
                        'target_value': '150.00'}
                ]
            },
            {
                'id': '002',
                'discrepancy_details': [
                    {'field': 'Name', 'source_value': 'Jane Smith',
                        'target_value': 'Jane Doe'}
                ]
            }
        ]
        self.assertEqual(find_discrepancies(
            source_dict, target_dict), expected_discrepancies)

    @patch("builtins.open", new_callable=mock_open, read_data="ID,Name,Date,Amount\n001,John Doe,2023-01-01,100.00\n002,Jane Smith,2023-01-02,200.00")
    def test_read_csv_file(self, mock_file):
        expected_data = {
            '001': {'ID': '001', 'Name': 'John Doe', 'Date': '2023-01-01', 'Amount': '100.00'},
            '002': {'ID': '002', 'Name': 'Jane Smith', 'Date': '2023-01-02', 'Amount': '200.00'}
        }
        result = read_csv_file('mock_source.csv')
        source_headers = ['ID', 'Name', 'Date', 'Amount']
        self.assertEqual(result[0], source_headers)
        self.assertEqual(result[1], expected_data)

    @patch("builtins.open", new_callable=mock_open)
    def test_reconcile_files(self, mock_file):
        # Set the side effect to return different data based on the file name
        mock_file.side_effect = [
            StringIO(
                "ID,Name,Date,Amount\n001,John Doe,2023-01-01,100.00\n002,Jane Smith,2023-01-02,200.00"),
            # Target CSV
            StringIO(
                "ID,Name,Date,Amount\n001,John Doe,2023-01-01,150.00\n002,Jane Smith,2023-01-02,200.00")
        ]

        response = reconcile_files('source.csv', 'target.csv')

        self.assertEqual(response["missing_in_target"], [])
        self.assertEqual(response["missing_in_source"], [])

        expected_discrepancies = [
            {
                'id': '001',
                'discrepancy_details': [
                    {'field': 'Amount', 'source_value': '100.00',
                        'target_value': '150.00'}
                ]
            }
        ]
        self.assertEqual(response["discrepancies"], expected_discrepancies)


if __name__ == "__main__":
    unittest.main()
