""" Argument Treatments """

import argparse

from src import AUTOMATIC, COMPLETE
from src.modules.tester.logger_config import initialize_logger


def treat_arguments(software_acronym, software_name, software_version, software_url):
    """ Treats user's command line input arguments. """

    logger = initialize_logger()
    logger.debug("Parsing user's command line input arguments...")

    about_message = software_acronym + " - version " + software_version

    # PARSING ARGUMENTS
    arguments_parser = argparse.ArgumentParser(prog="Scior-Tester",
                                               description=software_acronym + " - " + software_name,
                                               allow_abbrev=False,
                                               epilog=software_url)

    arguments_parser.version = about_message

    # OPTIONAL ARGUMENTS

    # General arguments
    arguments_parser.add_argument("-b", "--build", action='store_true',
                                  help="Build test datasets' taxonomies and files. "
                                       "Keeps classes and generalizations only.")

    arguments_parser.add_argument("-bg", "--build_gufo", action='store_true',
                                  help="Build test datasets' taxonomies and files. "
                                       "Keeps classes, generalizations and mapped gUFO classifications.")

    arguments_parser.add_argument("-bgv", "--build_gufo_validate", action='store_true',
                                  help="Build test datasets' taxonomies and files. "
                                       "Keeps classes, generalizations and mapped gUFO classifications. "
                                       "Performs validation of the generated taxonomies.")

    arguments_parser.add_argument("-r1", "--run1", action='store_true',
                                  help="Execute the TEST_1 for the built datasets.")

    arguments_parser.add_argument("-r2", "--run2", action='store_true',
                                  help="Execute the TEST_2 for the built datasets.")

    # Automation level

    automation_group = arguments_parser.add_mutually_exclusive_group()

    automation_group.add_argument("-i", "--interactive", action='store_true',
                                  help="Execute automatic rules whenever possible. "
                                       "Execute interactive rules only if necessary (default).")

    automation_group.add_argument("-a", "--automatic", action='store_true',
                                  help="Execute only automatic rules. Interactive rules are not performed.")

    # Ontology completeness arguments

    completeness_group = arguments_parser.add_mutually_exclusive_group()

    completeness_group.add_argument("-n", "--incomplete", action='store_true',
                                    help="The loaded ontology is an incomplete model (default).")

    completeness_group.add_argument("-c", "--complete", action='store_true',
                                    help="The loaded ontology is a complete model.")

    # Automatic arguments
    arguments_parser.add_argument("-v", "--version", action="version", help="Prints the software version and exit.")

    # POSITIONAL ARGUMENT
    arguments_parser.add_argument("-p", "--catalog_path", type=str, action="store",
                                  help="The path of the catalog in which Scior is going to be tested.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    if (not arguments.automatic) and (not arguments.interactive):
        arguments.automatic = AUTOMATIC

    if (not arguments.incomplete) and (not arguments.complete):
        arguments.complete = COMPLETE

    global_configurations = {"build": arguments.build,
                             "build_gufo": arguments.build_gufo,
                             "build_gufo_validate": arguments.build_gufo_validate,
                             "run1": arguments.run1,
                             "run2": arguments.run2,
                             "is_automatic": arguments.automatic,
                             "is_complete": arguments.complete,
                             "catalog_path": arguments.catalog_path}

    logger.debug(f"Arguments Parsed. Obtained values are: {global_configurations}")

    return global_configurations
