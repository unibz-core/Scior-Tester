""" Main functions regarding validations. """

import glob
import os

from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import write_csv_row
from src.modules.tester.utils_rdf import load_graph_safely
from src.modules.validation.validation_queries import QUERIES_LIST


class validated_taxonomy:
    """ Class to store the results for each evaluated taxonomy. """

    def __init__(self, file_name, list_problems, problems_bool):
        self.file_name = file_name
        self.list_problems = list_problems
        self.problems_bool = problems_bool


def save_csv_validation(queries_list, evaluated_taxonomies):
    """ Saves the results of the validation of the taxonomies into a csv file. """

    file_name = 'validation.csv'

    # Creating header
    csv_header = [i for i in queries_list]
    csv_header.insert(0, "file_name")

    for taxonomy_item in evaluated_taxonomies:
        row = taxonomy_item.problems_bool
        row.insert(0, taxonomy_item.file_name)
        write_csv_row(file_name, csv_header, row)


def validate_gufo_taxonomies():
    """ Performs validation on all generated gufo taxonomies and generates a csv output file with the results. """

    logger = initialize_logger()

    # Iterate over all taxonomy files with gUFO classifications
    os.chdir("catalog")
    list_all_files = glob.glob("**/*.ttl", recursive=True)

    logger.info(f"Starting validation of {len(list_all_files)} taxonomies.\n")
    evaluated_taxonomies = []

    for index, file in enumerate(list_all_files):
        current = index + 1
        current_taxonomy = validated_taxonomy(file, [], [])
        evaluated_taxonomies.append(current_taxonomy)

        # Loading file
        logger.info(f"Loading taxonomy {current}/{len(list_all_files)}: {file}")
        taxonomy_graph = load_graph_safely(file)

        # Performing queries
        for validation_query in QUERIES_LIST:
            query_result = taxonomy_graph.query(QUERIES_LIST[validation_query])
            problems_found = len(query_result)
            current_taxonomy.problems_bool.append(problems_found)

            if problems_found > 0:
                current_taxonomy.list_problems.append(validation_query)

        if len(current_taxonomy.list_problems) > 0:
            logger.warning(f"Constraint violated: {current_taxonomy.list_problems}")

    save_csv_validation(QUERIES_LIST, evaluated_taxonomies)
