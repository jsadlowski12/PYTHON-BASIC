import logging
import sys
import os
import configparser

def load_defaults_from_config(config_file='capstone/resources/default.ini'):
    if not os.path.exists(config_file):
        logging.error(f"Required configuration file '{config_file}' not found.")
        sys.exit(1)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        logging.info(f"Default configuration successfully loaded from '{config_file}'")

        path_to_save_files = config.get('DEFAULT', 'path_to_save_files')
        logging.info(f"Loaded path_to_save_files: {path_to_save_files}")

        files_count = config.getint('DEFAULT', 'files_count')
        logging.info(f"Loaded files_count: {files_count}")

        file_name = config.get('DEFAULT', 'file_name')
        logging.info(f"Loaded file_name: {file_name}")

        file_prefix = config.get('DEFAULT', 'file_prefix')
        logging.info(f"Loaded file_prefix: {file_prefix}")

        data_lines = config.getint('DEFAULT', 'data_lines')
        logging.info(f"Loaded data_lines: {data_lines}")

        clear_path = config.getboolean('DEFAULT', 'clear_path')
        logging.info(f"Loaded clear_path: {clear_path}")

        multiprocessing = config.getint('DEFAULT', 'multiprocessing')
        logging.info(f"Loaded multiprocessing: {multiprocessing}")

        return {
            'path_to_save_files': path_to_save_files,
            'files_count': files_count,
            'file_name': file_name,
            'file_prefix': file_prefix,
            'data_lines': data_lines,
            'clear_path': clear_path,
            'multiprocessing': multiprocessing
        }

    except (configparser.Error, ValueError, KeyError) as e:
        logging.error(f"Invalid configuration in '{config_file}': {e}")
        sys.exit(1)