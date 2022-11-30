""" Functions related to the statistics building, collection and saving. """
import csv
import operator
import pathlib

from modules.tester.hash_functions import register_sha256_hash_information
from modules.tester.logger_config import initialize_logger


class class_information_structure(object):
    """ Used for storing information about a class in a dataset. """

    def __init__(self, name, stereotype_original=None, stereotype_gufo=None, is_root=None, is_leaf=None,
                 is_intermediate=None, number_superclasses=None, number_subclasses=None,
                 number_reachable_classes=None):
        # General attributes
        self.name = name
        self.prefixed_name = "http://taxonomy.model/" + name

        # Stereotypes attributes
        self.stereotype_original = stereotype_original
        self.stereotype_gufo = stereotype_gufo

        # Taxonomy position attributes
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.is_intermediate = is_intermediate

        # Taxonomy relations attributes
        self.number_superclasses = number_superclasses
        self.number_subclasses = number_subclasses
        self.number_reachable_classes = number_reachable_classes


def saves_dataset_csv_classes_data(catalog_information, dataset_path, catalog_size, current, source_owl_file_path):
    """ Saves dataset classes information in CSV format. """

    logger = initialize_logger()
    csv_header = ["class_name", "stereotype_original", "stereotype_gufo", "is_root", "is_leaf", "is_intermediate",
                  "number_superclasses", "number_subclasses", "number_reachable_classes"]

    csv_file_full_path = dataset_path + "\\classes_data.csv"

    sorted_catalog_information = sorted(catalog_information, key=operator.attrgetter('name'))

    try:
        with open(csv_file_full_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)

            for class_information in sorted_catalog_information:
                csv_row = []

                csv_row.append(class_information.name)
                csv_row.append(class_information.stereotype_original)
                csv_row.append(class_information.stereotype_gufo)
                csv_row.append(class_information.is_root)
                csv_row.append(class_information.is_leaf)
                csv_row.append(class_information.is_intermediate)
                csv_row.append(class_information.number_superclasses)
                csv_row.append(class_information.number_subclasses)
                csv_row.append(class_information.number_reachable_classes)

                writer.writerow(csv_row)

        logger.info(f"CSV file {current}/{catalog_size} saved: {csv_file_full_path}\n")
    except OSError as error:
        logger.error(f"Could not save {csv_file_full_path} csv file. Exiting program."
                     f"System error reported: {error}")
        exit(1)

    current += 1

    register_sha256_hash_information(csv_file_full_path, source_owl_file_path)

    return csv_file_full_path
