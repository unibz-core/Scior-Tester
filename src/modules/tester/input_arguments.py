""" Argument Treatments """

import argparse

from src.modules.tester.logger_config import initialize_logger


def treat_arguments(software_acronym, software_name, software_version, software_url):
    """ Treats user's command line input arguments. """

    logger = initialize_logger()
    logger.debug("Parsing user's command line input arguments...")

    about_message = software_acronym + " - version " + software_version

    # PARSING ARGUMENTS
    arguments_parser = argparse.ArgumentParser(prog="OntCatOWL",
                                               description=software_acronym + " - " + software_name,
                                               allow_abbrev=False,
                                               epilog=software_url)

    arguments_parser.version = about_message

    # OPTIONAL ARGUMENTS

    # General arguments
    arguments_parser.add_argument("-b", "--build", action='store_true',
                                  help="Build test datasets' structure and files.")

    arguments_parser.add_argument("-r", "--run", action='store_true',
                                  help="Execute the tester for the build datasets.")

    # Automatic arguments
    arguments_parser.add_argument("-v", "--version", action="version", help="Prints the software version and exit.")

    # POSITIONAL ARGUMENT
    arguments_parser.add_argument("catalog_path", type=str, action="store", help="The path of the catalog in which "
                                                                                 "OntCatOWL is going to be tested.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    global_configurations = {"build": arguments.build,
                             "run": arguments.run,
                             "catalog_path": arguments.catalog_path}

    logger.debug(f"Arguments Parsed. Obtained values are: {global_configurations}")

    return global_configurations
