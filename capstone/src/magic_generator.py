import argparse
import logging
import sys
import os
import configparser

def create_parser() -> argparse.ArgumentParser:
    defaults = load_defaults_from_config()

    parser = argparse.ArgumentParser(prog='magicgenerator',
                            description='A console utility for generating test data based on data schema',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--path_to_save_files',
                        default=defaults['path_to_save_files'],
                        help='Path to where the files are saved.')
    parser.add_argument('--files_count',
                        default=defaults['files_count'],
                        type=int,
                        help='How many JSON files to generate. '
                        'Count must be greater or equal to 0. If equal to 0 the output will be printed to console.')
    parser.add_argument('--file_name',
                        default=defaults['file_name'],
                        help='Base file_name. If there is no prefix, the final file name will be file_name.json. '
                             'With prefix full file name will be file_name_file_prefix.json')
    parser.add_argument('--file_prefix',
                        default=defaults['file_prefix'],
                        choices=['count', 'random', 'uuid'],
                        help='What prefix for file name to use if more than 1 file needs to be generated')
    parser.add_argument('--data_schema',
                        required=True,
                        type=str,
                        help='It’s a string with json schema. '
                             'It could be loaded in two ways: '
                            '1) With path to json file with schema 2) with schema entered to command line.')
    parser.add_argument('--data_lines',
                        default=defaults['data_lines'],
                        type=int,
                        help='Count of lines for each file. Default, for example: 1000.')
    parser.add_argument('--clear_path',
                        default=defaults['clear_path'],
                        action='store_true',
                        help='If this flag is on, before the script starts creating new data files, '
                             'all files in path_to_save_files that match file_name will be deleted.')
    parser.add_argument('--multiprocessing',
                        default=defaults['multiprocessing'],
                        type=int,
                        help='The number of processes used to create files. '
                             'Divides the “files_count” value equally and starts N processes '
                             'to create an equal number of files in parallel.')

    return parser

def load_defaults_from_config(config_file='default.ini'):
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

def validate_path_to_save_files(path_input: str) -> str:
    if not path_input:
        logging.error("path_to_save_files is required")
        sys.exit(1)

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
    if files_count is None:
        logging.error("files_count is required. For more information type the command with --help argument")
        sys.exit(1)

    if files_count < 0:
        logging.error(f"files_count can't be a negative number: {files_count}. "
                      f"Check --help for more information about expected value.")
        sys.exit(1)

    return files_count



def validate_all_arguments(args: argparse.Namespace) -> dict:
    validated_path = validate_path_to_save_files(args.path_to_save_files)
    logging.info(f"Provided path: {validated_path} meets the expected criteria")

    validated_files_count = validate_files_count(args.files_count)
    logging.info(f"Provided files_count: {validated_files_count} meets the expected criteria")

    return {'path_to_save_files': validated_path, 'files_count': validated_files_count}

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = create_parser()
    args = parser.parse_args()

    validated_args = validate_all_arguments(args)

    logging.info(f"Files will be saved to: {validated_args['path_to_save_files']}")
    logging.info(f"There will be {validated_args['files_count']} files created.")

if __name__ == "__main__":
    main()