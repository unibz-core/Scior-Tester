""" Main module for the OntoCatOWL-Catalog Tester. """
import os
import pandas as pd
import random

from copy import deepcopy
from rdflib import URIRef, RDF

from src import *
from modules.run.test1 import *
from modules.run.test2 import *
from src.modules.build.build_classes_stereotypes_information import collect_stereotypes_classes_information
from src.modules.build.build_directories_structure import get_list_ttl_files, \
    create_test_directory_folders_structure, create_test_results_folder, create_internal_catalog_path
from src.modules.build.build_information_classes import saves_dataset_csv_classes_data
from src.modules.build.build_taxonomy_classes_information import collect_taxonomies_information
from src.modules.build.build_taxonomy_files import create_taxonomy_ttl_files
from scior import run_scior_tester
from src.modules.tester.hash_functions import write_sha256_hash_register
from src.modules.tester.input_arguments import treat_arguments
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely


def build_scior_tester(catalog_path):
    """ Build function for the Scior-Catalog Tester. Generates all the needed data."""

    # Building directories structure
    datasets = get_list_ttl_files(catalog_path, name="ontology")  # returns all ttl files we have with full path
    catalog_size = len(datasets)
    logger.info(f"The catalog contains {catalog_size} datasets.\n")
    internal_catalog_folder = os.path.join(os.getcwd(), CATALOG_FOLDER) + os.path.sep
    create_internal_catalog_path(internal_catalog_folder)
    hash_register = pd.DataFrame(columns=["file_name", "file_hash", "source_file_name", "source_file_hash"])

    for (current, dataset) in enumerate(datasets):
        dataset_name = dataset.split(os.path.sep)[-2]
        if dataset_name not in EXCEPTIONS_LIST:
            dataset_folder = internal_catalog_folder + dataset_name
            logger.info(f"### Starting dataset {current}/{catalog_size}: {dataset_name} ###\n")

            create_test_directory_folders_structure(dataset_folder, catalog_size, current)

            # Building taxonomies files and collecting information from classes
            taxonomy_files, hash_register = create_taxonomy_ttl_files(dataset, dataset_folder, hash_register)
            # Builds dataset_classes_information and collects attributes name, prefixed_name, and all taxonomic information
            dataset_classes_information = collect_taxonomies_information(taxonomy_files, catalog_size, current)
            # Collects stereotype_original and stereotype_gufo for dataset_classes_information
            collect_stereotypes_classes_information(dataset, dataset_classes_information, catalog_size, current)

            hash_register = saves_dataset_csv_classes_data(dataset_classes_information, dataset_folder,
                                                           catalog_size, current, dataset, hash_register)

    write_sha256_hash_register(hash_register, internal_catalog_folder + HASH_FILE_NAME)


def run_scior(is_automatic: bool, is_complete: bool, tname: str):

    # Creating list of taxonomies
    taxonomies = get_list_ttl_files(os.path.join(os.getcwd(), CATALOG_FOLDER))
    total_taxonomies_number = len(taxonomies)

    global_configurations = {"is_automatic": is_automatic, "is_complete": is_complete}
    l1 = "a" if is_automatic else "i"
    l2 = "c" if is_complete else "n"
    test_name = f"{tname}_{l1}{l2}"
    inconsistencies_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"inconsistencies_{test_name}.csv")
    divergences_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"divergences_{test_name}.csv")
    if os.path.exists(inconsistencies_file_name):
        os.remove(inconsistencies_file_name)
    if os.path.exists(divergences_file_name):
        os.remove(divergences_file_name)

    prev_dataset_folder = ""
    for (current, taxonomy) in enumerate(taxonomies):
        logger.info(f"Executing Scior for taxonomy {current + 1}/{total_taxonomies_number}: {taxonomy}\n")

        taxonomy_filename = taxonomy.split(os.path.sep)[-1]
        data_filename = CLASSES_DATA_FILE_NAME + "_" + taxonomy_filename.replace(".ttl", ".csv")
        input_classes = load_baseline_dictionary(taxonomy.replace(taxonomy_filename, data_filename))
        input_graph = load_graph_safely(taxonomy)

        dataset_folder = taxonomy.rsplit(os.path.sep, 1)[0]
        draft_file_name = data_filename[4:-10] + "_" + test_name + data_filename[-10:]
        test_results_folder = os.path.join(dataset_folder, test_name)
        create_test_results_folder(test_results_folder, dataset_folder != prev_dataset_folder)

        if tname.endswith("1"):
            run_scior_test1(global_configurations, input_classes, input_graph, test_results_folder,
                            draft_file_name, inconsistencies_file_name, divergences_file_name)

        if tname.endswith("2"):
            run_scior_test2(global_configurations, input_classes, input_graph, test_results_folder,
                            draft_file_name, inconsistencies_file_name, divergences_file_name, taxonomy_filename)

        if dataset_folder != prev_dataset_folder:
            if prev_dataset_folder:
                logger.info(f"TEST{tname[-1]} is finished for {prev_dataset_folder}\n")
            prev_dataset_folder = dataset_folder


def run_scior_test1(global_configurations, input_classes, input_graph, test_results_folder,
                    draft_file_name, inconsistencies_file_name, divergences_file_name):
    # Test 1 for Scior - described in: https://github.com/unibz-core/Scior-Dataset
    tests_total = len(input_classes)

    # Executions of the test
    for idx, input_class in enumerate(input_classes):
        execution_number = idx + 1

        working_graph = deepcopy(input_graph)
        triple_subject = URIRef(NAMESPACE_TAXONOMY + input_class.name)
        class_gufo_type = remaps_to_gufo(input_class.name, input_class.stereotype)
        triple_object = URIRef(class_gufo_type)
        working_graph.add((triple_subject, RDF.type, triple_object))
        working_graph.bind("gufo", NAMESPACE_GUFO)

        try:
            ontology_dataclass_list, time_register, consolidated_statistics, knowledge_matrix, software_version = \
                run_scior_tester(global_configurations, working_graph)
        except:
            logger.error(f"INCONSISTENCY found! Test {execution_number}/{tests_total} "
                         f"for input class {input_class.name} interrupted.")
            create_inconsistency_csv_output(inconsistencies_file_name, draft_file_name, execution_number, input_class)
        else:
            logger.info(f"Test {execution_number}/{tests_total} "
                        f"for input class {input_class.name} successfully executed.")
            # Creating resulting files
            if execution_number == 1:
                save_platform_information(test_results_folder,
                                          f"settings{draft_file_name[:-10]}.csv", software_version)
            create_classes_yaml_output(input_class, ontology_dataclass_list, test_results_folder,
                                       file_name=f"complete{draft_file_name[:-4]}_ex{execution_number:03d}.yaml")
            create_classes_results_csv_output(input_classes, ontology_dataclass_list,
                                              test_results_folder, divergences_file_name,
                                              file_name=f"simple{draft_file_name[:-4]}_ex{execution_number:03d}.csv")
            create_matrix_output(knowledge_matrix, test_results_folder,
                                 file_name=f"matrix{draft_file_name[:-4]}_ex{execution_number:03d}.csv")
            create_times_csv_output(time_register, test_results_folder, draft_file_name, execution_number)
            create_statistics_csv_output(ontology_dataclass_list, consolidated_statistics, test_results_folder,
                                         draft_file_name, execution_number)
            create_summary_csv_output(test_results_folder, draft_file_name, execution_number, input_class)


def run_scior_test2(global_configurations, input_classes, input_graph, test_results_folder,
                    draft_file_name, inconsistencies_file_name, divergences_file_name, taxonomy_filename):
    # Test 2 for Scior - described in: https://github.com/unibz-core/Scior-Dataset
    model_size = len(input_classes)
    # Consider only datasets that have at least 20 classes. If less, skip.
    if model_size < MINIMUM_ALLOWED_NUMBER_CLASSES:
        logger.warning(f"The dataset has only {model_size} classes (less than minimum number) and was skipped.\n")
        return

    current_percentage = PERCENTAGE_INITIAL
    while current_percentage <= PERCENTAGE_FINAL:
        number_of_input_classes = round(model_size * current_percentage / 100)

        current_execution = 1
        while current_execution <= NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE:
            end = "\n" if current_execution == NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE else ""
            working_graph = deepcopy(input_graph)
            working_graph.bind("gufo", NAMESPACE_GUFO)

            sample_list = random.sample(input_classes, number_of_input_classes)
            for input_class in sample_list:
                triple_subject = URIRef(NAMESPACE_TAXONOMY + input_class.name)
                class_gufo_type = remaps_to_gufo(input_class.name, input_class.stereotype)
                triple_object = URIRef(class_gufo_type)
                working_graph.add((triple_subject, RDF.type, triple_object))

            try:
                ontology_dataclass_list, time_register, consolidated_statistics, knowledge_matrix, software_version =\
                    run_scior_tester(global_configurations, working_graph)
            except:
                logger.error(f"INCONSISTENCY found: {taxonomy_filename} "
                             f"- percentage {current_percentage} - excecution {current_execution}. "
                             f"Current execution interrupted.{end}")
                create_inconsistency_csv_output_t2(inconsistencies_file_name, draft_file_name, current_percentage,
                                                   current_execution)
            else:
                logger.info(f"Test dataset {taxonomy_filename} - percentage {current_percentage} - "
                            f"excecution {current_execution} successfully executed "
                            f"({number_of_input_classes} input classes).{end}")
                # Creating resulting files
                if (current_execution == 1) and (current_percentage == PERCENTAGE_INITIAL):
                    save_platform_information(test_results_folder, f"settings{draft_file_name[:-10]}.csv",
                                              software_version, env_vars=True)
                create_classes_yaml_output_t2(sample_list, ontology_dataclass_list, test_results_folder,
                  file_name=f"complete{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.yaml")
                create_classes_results_csv_output(input_classes, ontology_dataclass_list,
                                                  test_results_folder, divergences_file_name,
                    file_name=f"simple{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.csv")
                create_matrix_output(knowledge_matrix, test_results_folder,
                    file_name=f"matrix{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.csv")
                create_times_csv_output_t2(time_register, test_results_folder, draft_file_name,
                                           current_percentage, current_execution)
                create_statistics_csv_output_t2(ontology_dataclass_list, consolidated_statistics,
                                                test_results_folder, draft_file_name, current_percentage,
                                                current_execution)
            current_execution += 1

        current_percentage += PERCENTAGE_RATE


if __name__ == '__main__':

    logger = initialize_logger()

    arguments = treat_arguments(SOFTWARE_ACRONYM, SOFTWARE_NAME, SOFTWARE_VERSION, SOFTWARE_URL)

    # Execute in BUILD mode.
    if arguments["build"]:
        build_scior_tester(arguments["catalog_path"])

    # Execute in RUN mode.
    if arguments["run1"]:
        run_scior(arguments["is_automatic"], arguments["is_complete"], tname="tt001")

    if arguments["run2"]:
        run_scior(arguments["is_automatic"], arguments["is_complete"], tname="tt002")

# TODO (@pedropaulofb): VERIFY
# Are there any classes with more than one stereotype?
# Try to clean garbage classes for creating better statistics
# The following datasets don't have any taxonomy and were removed by hand:
# - chartered-service, experiment2013, gailly2016value, pereira2020ontotrans, zhou2017hazard-ontology-robotic-strolling, zhou2017hazard-ontology-train-control
# van-ee2021modular - RecursionError: maximum recursion depth exceeded while calling a Python object
