""" Main functions regarding validations. """

import glob
import os

from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import write_csv_row
from src.modules.tester.utils_rdf import load_graph_safely
from src.modules.validation.validation_queries import QUERIES_EXCLUSIVE_TO_CWA, QUERIES_OWA_DICT_LIST


class validated_taxonomy:
    """ Class to store the results for each evaluated taxonomy. """

    def __init__(self, file_name, list_problems_queries, list_problems_count):
        self.file_name = file_name
        self.list_problems_queries = list_problems_queries
        self.list_problems_count = list_problems_count


def intersection(lst1, lst2):
    """ Simple function that returns the intersection elements of two lists. """
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


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

        # Getting number of problems for each taxonomy
        number_of_problems_both = len(taxonomy.list_problems_queries)
        number_of_problems_cwa = len(intersection(taxonomy.list_problems_queries, QUERIES_EXCLUSIVE_TO_CWA))

        # If there are no problems, write as valid in both lists.
        if number_of_problems_both == 0:
            list_valid_c.append(taxonomy.file_name)
            list_valid_n.append(taxonomy.file_name)
        # If there is at least one CWA problem, write as valid for OWA.
        elif number_of_problems_cwa > 0:
            list_valid_n.append(taxonomy.file_name)
        # If there are OWA problems, it means that it is invalid for both OWA and CWA. Hence, do not write in lists.
        else:
            continue

    # Writing list of valid taxonomies for CWA
    logger.info(f"Writing {valid_taxonomies_c_file}")
    with open(valid_taxonomies_c_file, 'w') as tfile:
        tfile.write('\n'.join(list_valid_c))

    # Writing list of valid taxonomies for OWA
    logger.info(f"Writing {valid_taxonomies_n_file}")
    with open(valid_taxonomies_n_file, 'w') as tfile:
        tfile.write('\n'.join(list_valid_n))

    logger.info(f"Lists of valid taxonomies for OWA and CWA successfully written.")


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
