""" Main module for the OntoCatOWL-Catalog Tester. """
from modules.build.build_classes_stereotypes_information import collect_stereotypes_classes_information
from modules.build.build_directories_structure import get_list_unhidden_directories, \
    create_test_directory_folders_structure
from modules.build.build_information_classes import saves_dataset_csv_classes_data
from modules.build.build_taxonomy_classes_information import collect_taxonomy_information
from modules.build.build_taxonomy_files import create_taxonomy_files
from modules.input_arguments import treat_arguments
from modules.logger_config import initialize_logger

SOFTWARE_ACRONYM = "OntCatOWL Tester"
SOFTWARE_NAME = "Tester for the Identification of Ontological Categories for OWL Ontologies"
SOFTWARE_VERSION = "0.22.11.17"
SOFTWARE_URL = "https://github.com/unibz-core/OntCatOWL-Tester"


def build_ontcatowl_tester(catalog_path):
    """ Build function for the OntoCatOWL-Catalog Tester. """

    # DATA GENERATION FOR TESTS

    # Building directories structure
    list_datasets = get_list_unhidden_directories(catalog_path)
    create_test_directory_folders_structure(list_datasets)

    # Building taxonomies files and collecting information from classes
    create_taxonomy_files(catalog_path, list_datasets)
    catalog_information = collect_taxonomy_information(list_datasets)

    # Building classes information files
    catalog_information = collect_stereotypes_classes_information(catalog_path, list_datasets, catalog_information)
    saves_dataset_csv_classes_data(catalog_information)


def run_ontcatowl_tester(catalog_path):
    pass


if __name__ == '__main__':

    logger = initialize_logger()

    arguments = treat_arguments(SOFTWARE_ACRONYM, SOFTWARE_NAME, SOFTWARE_VERSION, SOFTWARE_URL)

    # Execute in BUILD only mode.
    if arguments["build"]:
        build_ontcatowl_tester(arguments["catalog_path"])

    # Execute in RUN only mode.
    # if arguments["run"]:
    # run_ontcatowl_tester(arguments["catalog_path"])

    # Execute in BUILD + RUN mode. Default option.
    if not (arguments["build"] or arguments["run"]):
        build_ontcatowl_tester(arguments["catalog_path"])  # run_ontcatowl_tester(arguments["catalog_path"])

# TODO (@pedropaulofb): VERIFY
# Are there any classes with more than one stereotype?
# Try to clean garbage classes for creating better statistics


# TODO (@pedropaulofb): CORRECT
# The following datasets don't have any taxonomy and were removed by hand:
# - chartered-service, experiment2013, gailly2016value, pereira2020ontotrans, zhou2017hazard-ontology-robotic-strolling, zhou2017hazard-ontology-train-control
