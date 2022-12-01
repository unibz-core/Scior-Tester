""" Logging configurations. """

import logging
import os

from src.modules.tester.utils_general import get_date_time


def initialize_logger():
    """ Initialize OntCatOWL Tester Logger. """

    # Create a custom logger
    new_logger = logging.getLogger("OntCatOWL Tester")
    new_logger.setLevel(logging.DEBUG)

    # Creates a new logger only if OntCatOWLTester does not exist
    if not logging.getLogger("OntCatOWL Tester").hasHandlers():

        # Creating CONSOLE handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # If directory "/log" does not exist, create it
        log_dir = "logs/"
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as error:
                print(f"Directory {log_dir} could not be created. Program aborted.\n"
                      f"System error reported: {error}")

        # Creating FILE handler
        # TODO: change only after the end of debug
        # file_handler = logging.FileHandler(f"{log_dir}{get_date_time()}.log")
        file_handler = logging.FileHandler(f"{log_dir}current.log")
        file_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s [func: %(funcName)s '
                                        'in %(filename)s]')
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)

        # Add handlers to the logger
        new_logger.addHandler(console_handler)
        new_logger.addHandler(file_handler)

    return new_logger
