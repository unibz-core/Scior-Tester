""" Functions related to OS files and strings used for general purposes. """
import os
import glob

from src.modules.tester.logger_config import initialize_logger


def get_list_ttl_files(directory_path) -> list:
    """ Receives the path of a directory and returns a list of all its unhidden subdirectories (only first level). """
    logger = initialize_logger()
    file_names = []

    # checking whether folder/directory exists
    if not os.path.exists(directory_path):
        logger.error(f"OntoUML/UFO Catalog directory {directory_path} does not exist. Exiting program.")
        exit(1)
    else:  # if yes, collect all ttl files we have
        file_names = []
        for file in glob.glob(directory_path + "/*/ontology.ttl"):
            file_names.append(file)

    return file_names


def create_folder(path, message):
    logger = initialize_logger()

    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logger.info(f"{message}: {path}.")
        except OSError as error:
            logger.error(f"Directory {path} could not be created. Program aborted.\n"
                         f"System error reported: {error}")


def create_internal_catalog_path(catalog_path):
    create_folder(catalog_path, "Internal catalog directory created")


def create_test_results_folder(test_results_folder):
    create_folder(test_results_folder, "Test results directory created")


def create_test_directory_folders_structure(dataset_folder, catalog_size, current):
    logger = initialize_logger()

    try:
        # Create dataset folders in tester_catalog_folder
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)
            logger.info(f"Directory {current}/{catalog_size} created: {dataset_folder}.")
        else:
            logger.info(f"Directory {current}/{catalog_size} already exists: {dataset_folder}.")
    except OSError as error:
        logger.error(f"Directory {dataset_folder} could not be created. Program aborted.\n"
                     f"System error reported: {error}")
