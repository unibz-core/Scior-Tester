""" Functions related to OS files and strings used for general purposes. """
import os
import pathlib

from modules.logger_config import initialize_logger


def get_list_unhidden_directories(directory_path):
    """ Receives the path of a directory and returns a list of all its unhidden subdirectories (only first level). """
    list_directories = []

    logger = initialize_logger()

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


def create_test_directory_structure(directory_path):
    logger = initialize_logger()

    tester_catalog_folder = str(pathlib.Path().resolve()) + "\catalog"

    list_datasets = get_list_unhidden_directories(directory_path)

    for dataset in list_datasets:
        print(dataset)

    for dataset in list_datasets:
        dataset_folder = tester_catalog_folder + "\\" + dataset
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)

    # Create dataset folders in tester_catalog_folder

    logger.info(f"Test directory structure successfully created in {tester_catalog_folder}")
