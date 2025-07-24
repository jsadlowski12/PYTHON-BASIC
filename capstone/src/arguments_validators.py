import logging
import os
import sys
import argparse

from capstone.src.data_schema import load_json_data_schema, validate_data_schema

def validate_path_to_save_files(path_input: str) -> str:
    if path_input == '.':
        return os.getcwd()

    if os.path.isabs(path_input):
        absolute_path = path_input
    else:
        absolute_path = os.path.abspath(path_input)

    if not os.path.exists(absolute_path):
        logging.error(f"Path does not exist: {absolute_path}")
        sys.exit(1)

    if not os.path.isdir(absolute_path):
        logging.error(f"Path exists but is not a directory: {absolute_path}")
        sys.exit(1)

    if not os.access(absolute_path, os.W_OK):
        logging.error(f"No write permission for directory: {absolute_path}")
        sys.exit(1)

    return absolute_path

def validate_files_count(files_count: int) -> int:
    if files_count < 0:
        logging.error(f"files_count can't be a negative number: {files_count}. "
                      f"Check --help for more information about expected value.")
        sys.exit(1)

    return files_count

def validate_data_lines(data_lines: int) -> int:
    if data_lines <= 0:
        logging.error(f"data_lines argument can't be a negative number or zero: {data_lines}")
        sys.exit(1)

    return data_lines

def validate_multiprocessing(multiprocessing: int) -> int:
    if multiprocessing < 0:
        logging.error(f"multiprocessing argument can't be a negative number: {multiprocessing}")
        sys.exit(1)

    cpu_count = os.cpu_count()
    if multiprocessing > cpu_count:
        logging.warning(f"multiprocessing argument value {multiprocessing} is greater than CPU count {cpu_count}, "
                        f"using {cpu_count} instead")
        return cpu_count

    return multiprocessing

def validate_all_arguments(args: argparse.Namespace) -> dict:
    validated_path = validate_path_to_save_files(args.path_to_save_files)
    logging.info(f"Provided path argument: {validated_path} is valid.")

    validated_files_count = validate_files_count(args.files_count)
    logging.info(f"Provided files_count argument: {validated_files_count} is valid.")

    validated_data_lines = validate_data_lines(args.data_lines)
    logging.info(f"Provided data_lines argument: {validated_data_lines} is valid.")

    data_schema = load_json_data_schema(args.data_schema)
    validated_data_schema = validate_data_schema(data_schema)
    logging.info(f"Provided data_schema argument: {validated_data_schema} is valid.")

    validated_multiprocessing = validate_multiprocessing(args.multiprocessing)
    logging.info(f"Provided multiprocessing argument: {validated_multiprocessing} is valid.")

    return {'path_to_save_files': validated_path,
            'file_name': args.file_name,
            'file_prefix': args.file_prefix,
            'files_count': validated_files_count,
            'data_lines': validated_data_lines,
            'data_schema': validated_data_schema,
            'clear_path': args.clear_path,
            'multiprocessing': validated_multiprocessing
            }