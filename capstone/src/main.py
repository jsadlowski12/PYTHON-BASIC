import logging

from capstone.src.arguments_validators import validate_all_arguments
from capstone.src.parser import create_parser
from capstone.src.generators import generate_and_save_data

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

    parser = create_parser()
    args = parser.parse_args()
    validated_args = validate_all_arguments(args)
    generate_and_save_data(validated_args)

if __name__ == "__main__":
    main()