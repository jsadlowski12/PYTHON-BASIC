import argparse

from capstone.src.config_loader import load_defaults_from_config

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
                        help=(
                            "JSON schema as a string. Can be provided in two ways:\n"
                            "1) Path to a JSON file: e.g., './schema.json'\n"
                            "2) Inline JSON string: e.g., "
                            "'{\"name\": \"str:rand\", \"age\": \"int:rand(1, 100)\", \"type\": \"str:['client','partner']\"}'\n\n"
                            "All values must follow the pattern type:instruction.\n"
                            "Supported types: str, int, timestamp.\n"
                            "Instructions include: rand, rand(from, to), list values, fixed value, or empty.\n")
                        )
    parser.add_argument('--data_lines',
                        default=defaults['data_lines'],
                        type=int,
                        help='Count of lines for each file. Default: 1000.')
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