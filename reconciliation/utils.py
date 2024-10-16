import csv


def normalize_data(record: dict[str, str]) -> dict[str, str]:
    """
    Normalize the data in the record by stripping leading/trailing whitespaces and converting to lowercase.
    """
    normalized_data = {}
    for key, value in record.items():
        lower_key = key.lower()
        if 'name' in lower_key:
            normalized_data[key] = str(value).strip().title()
        else:
            normalized_data[key] = str(value).strip().lower()
    return normalized_data


def find_missing_records(source_dict: dict[str, dict], target_dict: dict[str, dict]) -> list[dict]:
    """
    Find records present in the source_dict but missing in the target_dict.

    source_dict: dictionary containing source records
    target_dict: dictionary containing target records
    """
    return [record for record_id, record in source_dict.items() if record_id not in target_dict]


def find_discrepancies(source_dict: dict[str, dict], target_dict: dict[str, dict]) -> list[dict]:
    """
    Find discrepancies between the source and target dictionaries.
    """
    discrepancies = []
    for record_id, source_record in source_dict.items():
        if record_id in target_dict:
            target_record = target_dict[record_id]
            discrepancy_details = []  # Collect discrepancies as a list
            for key in source_record:
                if source_record[key] != target_record[key]:
                    discrepancy_details.append({
                        'field': key,
                        'source_value': source_record[key],
                        'target_value': target_record[key]
                    })

            if discrepancy_details:
                discrepancies.append({
                    'id': record_id,
                    'discrepancy_details': discrepancy_details
                })

    return discrepancies


def validate_target_source_header(source_headers: list[str], target_headers: list[str]) -> bool:
    """
        Validate if the source and target headers match.
    """
    source_set, target_set, = set(source_headers), set(target_headers)

    missing_source = target_set - source_set
    missing_target = source_set - target_set

    if missing_source or missing_target:
        error_data = {
            'missing_in_source': ", ".join(missing_source),
            'missing_in_target': ", ".join(missing_target)
        }
        raise ValueError(
            f"source and target headers do not match: {error_data}")

    if source_headers != target_headers:
        raise ValueError(f"Source and target headers do not match in order")

    return True


def read_csv_file(file_path: str) -> dict[str, dict]:
    """
    Read a CSV file and return its normalized data as a dictionary keyed by the specified id_field.

    file_path: path to the CSV file
    """

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            data_dict = {}
            for row in reader:
                normalized_row = normalize_data(row)
                data_dict[normalized_row[headers[0]]] = normalized_row

            return headers, data_dict
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def reconcile_files(source_file: str, target_file: str) -> dict[str, list[dict]]:
    """
    Reconcile the source and target CSV files and return the missing records and discrepancies.

    source_file: path to the source CSV file
    target_file: path to the target CSV file
    """

    source_headers, source_dict = read_csv_file(source_file)
    target_headers, target_dict = read_csv_file(target_file)
    validate_target_source_header(source_headers, target_headers)

    missing_in_target = find_missing_records(source_dict, target_dict)
    missing_in_source = find_missing_records(target_dict, source_dict)
    discrepancies = find_discrepancies(source_dict, target_dict)

    response_data = {
        "missing_in_target": missing_in_target,
        "missing_in_source": missing_in_source,
        "discrepancies": discrepancies,
    }

    return response_data
