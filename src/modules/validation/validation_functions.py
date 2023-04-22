""" Main functions regarding validations. """

import glob
import os

from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import write_csv_row
from src.modules.tester.utils_rdf import load_graph_safely
from src.modules.validation.validation_queries import QUERIES_OWA_DICT_LIST, QUERIES_CWA_LIST


class validated_taxonomy:
    """ Class to store the results for each evaluated taxonomy. """

    def __init__(self, file_name, list_problems_queries, list_problems_count):
        self.file_name = file_name
        self.list_problems_queries = list_problems_queries
        self.list_problems_count = list_problems_count


def save_csv_validation(queries_list, evaluated_taxonomies):
    """ Saves the results of the validation of the taxonomies into a csv file. """

    file_name = 'validation.csv'

    # if previous validation.csv file exists, it is deleted
    if os.path.exists(file_name):
        os.remove(file_name)

    # Creating header
    csv_header = [i for i in queries_list]
    csv_header.insert(0, "file_name")

    for taxonomy_item in evaluated_taxonomies:
        row = taxonomy_item.list_problems_count
        row.insert(0, taxonomy_item.file_name)
        write_csv_row(file_name, csv_header, row)


def create_valid_lists(evaluated_taxonomies):
    """ Generates two files:
    valid_taxonomies_c.txt: list of all valid taxonomies considering closed-world assumption (complete models)
    valid_taxonomies_n.txt: list of all valid taxonomies considering open-world assumption (incomplete models)
    """

    logger = initialize_logger()

    valid_taxonomies_c_file = "valid_taxonomies_c.txt"
    valid_taxonomies_n_file = "valid_taxonomies_n.txt"

    list_valid_c = []
    list_valid_n = []

    for taxonomy in evaluated_taxonomies:
        if not taxonomy.list_problems_queries:
            list_valid_c.append(taxonomy.file_name)
            list_valid_n.append(taxonomy.file_name)
        # Below are the rules that can only be applied to OWA. I.e., that cannot be applied to CWA.
        elif taxonomy.list_problems_queries in QUERIES_CWA_LIST:
            list_valid_n.append(taxonomy.file_name)

    logger.info(f"Writing {valid_taxonomies_c_file}")
    with open(valid_taxonomies_c_file, 'w') as tfile:
        tfile.write('\n'.join(list_valid_c))
    logger.info(f"Writing {valid_taxonomies_n_file}")
    with open(valid_taxonomies_n_file, 'w') as tfile:
        tfile.write('\n'.join(list_valid_n))
    logger.info(f"List of valid taxonomies successfully written")


def validate_gufo_taxonomies():
    """ Performs validation on all generated gufo taxonomies and generates a csv output file with the results. """

    logger = initialize_logger()

    # Iterate over all taxonomy files with gUFO classifications
    os.chdir("catalog")
    list_all_files = glob.glob("**/*.ttl", recursive=True)

    logger.info(f"### Starting validation of {len(list_all_files)} taxonomies ###\n")
    evaluated_taxonomies = []

    for index, file in enumerate(list_all_files):

        current = index + 1
        current_taxonomy = validated_taxonomy(file, [], [])
        evaluated_taxonomies.append(current_taxonomy)

        # Loading file
        logger.info(f"Validating taxonomy {current}/{len(list_all_files)}: {file}")
        taxonomy_graph = load_graph_safely(file)

        # Performing queries
        for validation_query in QUERIES_OWA_DICT_LIST:
            query_result = taxonomy_graph.query(QUERIES_OWA_DICT_LIST[validation_query])
            number_problems_found = len(query_result)
            current_taxonomy.list_problems_count.append(number_problems_found)

            if number_problems_found > 0:
                current_taxonomy.list_problems_queries.append(validation_query)

        if len(current_taxonomy.list_problems_queries) > 0:
            logger.warning(f"Identified violation(s) of constraint(s): {current_taxonomy.list_problems_queries}")

    logger.info(f"Validation of {len(list_all_files)} taxonomies successfully concluded\n")

    # Creating file validation.csv
    save_csv_validation(QUERIES_OWA_DICT_LIST, evaluated_taxonomies)
    # Creating files valid_taxonomies_c.csv and valid_taxonomies_n.csv
    create_valid_lists(evaluated_taxonomies)
