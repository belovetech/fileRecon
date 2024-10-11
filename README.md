# fileRecon

This project compares two CSV files to identify missing records and discrepancies between them. It generates a comprehensive report that highlights differences, allowing users to easily spot inconsistencies and ensure data integrity.

## Setup Instructions

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the migrations: `python manage.py migrate`
5. Start the development server: `python manage.py runserver`

## Usage

BASE URL`http://localhost:8000/api/`

1. Upload files at `upload/`.
2. Reconcile files at `api/reconcile/<file_id>?format=json|csv|html`.

# Run tests

` python manage.py test reconciliation`
