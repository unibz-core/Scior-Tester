""" Main module for the OntoCatOWL-Catalog Tester. """

from modules.tester_file_structure import create_test_directory_structure


def run_ontcatowl_tester():
    """ Main function for the OntoCatOWL-Catalog Tester. """

    # Create folders for each dataset of the catalog and copy the corresponding ontology.ttl files

    # TODO (@pedropaulofb): Receive catalog_path as argument.
    catalog_path = r"C:\Users\PFavatoBarcelos\Dev\Work\OntoUML Repository\ontouml-models"

    create_test_directory_structure(catalog_path)


if __name__ == '__main__':
    run_ontcatowl_tester()
