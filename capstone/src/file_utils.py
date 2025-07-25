import logging
import os
import glob
import sys
import json

def clear_existing_files(path_to_save_files: str, file_name: str) -> None:
    pattern = os.path.join(path_to_save_files, f"{file_name}*.json")
    existing_files = glob.glob(pattern)

    if existing_files:
        logging.info(f"Clearing {len(existing_files)} existing files matching pattern: {file_name}*.json")
        for file_path in existing_files:
            try:
                os.remove(file_path)
                logging.debug(f"Deleted file: {file_path}")
            except OSError as e:
                logging.error(f"Failed to delete file {file_path}: {e}")
                sys.exit(1)
        logging.info(f"Successfully cleared {len(existing_files)} existing files")
    else:
        logging.info(f"No existing files found matching pattern: {file_name}*.json")


def print_data_to_console(data: list[dict]) -> None:
    try:
        for record in data:
            print(json.dumps(record, indent=2))
    except (TypeError, ValueError) as e:
        logging.error(f"Error printing data to console: {e}")
        sys.exit(1)


def save_data_to_file(data: list[dict], file_path: str) -> None:
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully saved {len(data)} records to: {file_path}")
    except (OSError, TypeError, ValueError) as e:
        logging.error(f"Error saving data to file {file_path}: {e}")
        sys.exit(1)