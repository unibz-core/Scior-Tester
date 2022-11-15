""" Main module for the OntoCatOWL-Catalog Tester. """
from modules.tester_file_generations import generate_catalog_data_files
from modules.tester_file_structure import create_test_directory_folders_structure, get_list_unhidden_directories


def run_ontcatowl_tester():
    """ Main function for the OntoCatOWL-Catalog Tester. """

    # Create folders for each dataset of the catalog and copy the corresponding ontology.ttl files

    # TODO (@pedropaulofb): Receive catalog_path as argument.
    catalog_path = r"C:\Users\PFavatoBarcelos\Dev\Work\ontouml-models"

    # TODO (@pedropaulofb): Create specific argument for generate data only.
    # DATA GENERATION FOR TESTS
    list_datasets = get_list_unhidden_directories(catalog_path)
    create_test_directory_folders_structure(list_datasets)
    generate_catalog_data_files(catalog_path, list_datasets)

    # TODO (@pedropaulofb): Create specific argument for execution only.
    # TESTS EXECUTION


if __name__ == '__main__':
    run_ontcatowl_tester()
