""" Functions related to OS files and strings used for general purposes. """
import os

from modules.tester.logger_config import initialize_logger


def create_internal_catalog_path(catalog_path):
    logger = initialize_logger()

    if not os.path.exists(catalog_path):
        os.makedirs(catalog_path)

    # Create dataset folders in tester_catalog_folder

    logger.info(f"Internal catalog directory created: {catalog_path}.")

def get_list_unhidden_directories(directory_path):
    """ Receives the path of a directory and returns a list of all its unhidden subdirectories (only first level). """
    logger = initialize_logger()

    list_directories = []

    # checking whether folder/directory exists
    if not os.path.exists(directory_path):
        logger.error(f"OntoUML/UFO Catalog directory {directory_path} does not exist. Exiting program.")
        exit(1)
    else:
        # Iterate directory
        for path in os.listdir(directory_path):
            # check if current path is a non-hidden directory
            if os.path.isdir(os.path.join(directory_path, path)) and path[0] != ".":
                list_directories.append(path)

    return list_directories


def create_test_directory_folders_structure(dataset_folder, catalog_size, current):
    logger = initialize_logger()

    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    # Create dataset folders in tester_catalog_folder

    logger.info(f"Directory {current}/{catalog_size} created: {dataset_folder}.")


def create_test_results_folder(test_results_folder):
    logger = initialize_logger()

    if not os.path.exists(test_results_folder):
        os.makedirs(test_results_folder)

    # Create dataset folders in tester_catalog_folder

    logger.debug(f"Test results directory created: {test_results_folder}.")
