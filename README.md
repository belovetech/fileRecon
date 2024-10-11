# fileRecon

This project compares two CSV files to identify missing records and discrepancies between them. It generates a comprehensive report that highlights differences, allowing users to easily spot inconsistencies and ensure data integrity.

## Setup Instructions

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the migrations: `python manage.py migrate`
5. Start the development server: `DEBUG=0 python manage.py runserver 0.0.0.0:8000`

## Usage

BASE URL`http://localhost:8000/api/`

1. Upload files at `upload/`.
2. Reconcile files at `api/reconcile/<id>?format=json|csv|html`. id is the id you get after uploading the files.

# Run tests

` python manage.py test`

## Docker Setup

1. Run `docker-compose up --build` to start the containers.
