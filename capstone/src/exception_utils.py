import sys
import logging

def error_and_exit(msg: str) -> None:
    logging.error(msg)
    sys.exit(1)