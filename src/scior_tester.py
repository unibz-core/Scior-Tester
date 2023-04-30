""" Main module for the OntoCatOWL-Catalog Tester. Call all functionalities (build and tests). """
import glob
import os
import random
from copy import deepcopy

from rdflib import URIRef, RDF
from scior import run_scior_tester

from src import EXCEPTIONS_LIST, CATALOG_FOLDER, CLASSES_DATA_FILE_NAME, NAMESPACE_TAXONOMY, NAMESPACE_GUFO, \
    MINIMUM_ALLOWED_NUMBER_CLASSES, PERCENTAGE_INITIAL, PERCENTAGE_FINAL, \
    NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE, PERCENTAGE_RATE, SOFTWARE_ACRONYM, SOFTWARE_NAME, SOFTWARE_VERSION, \
    SOFTWARE_URL
from src.modules.build.build_classes_stereotypes_information import collect_stereotypes_classes_information
from src.modules.build.build_directories_structure import get_list_ttl_files, create_test_directory_folders_structure, \
    create_test_results_folder, create_internal_catalog_path
from src.modules.build.build_information_classes import saves_dataset_csv_classes_data
from src.modules.build.build_taxonomy_classes_information import collect_taxonomies_information
from src.modules.build.build_taxonomy_files import create_taxonomy_ttl_files, remove_gufo_classifications
from src.modules.run.test1 import load_baseline_dictionary, remaps_to_gufo, create_inconsistency_csv_output, \
    create_classes_yaml_output, create_classes_results_csv_output, create_matrix_output, create_summary_csv_output
from src.modules.run.test2 import create_inconsistency_csv_output_t2, create_classes_yaml_output_t2
from src.modules.tester.input_arguments import treat_arguments
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely
from src.modules.validation.validation_functions import validate_gufo_taxonomies


def build_scior_tester(catalog_path: str, validate_argument: bool, gufo_argument: bool):
    """ Build function for the Scior Tester. Generates all files for the dataset that will receive the tests. """

    # Building directories structure.

    # Returns all ttl files we have with full path
    datasets = get_list_ttl_files(catalog_path, name="ontology")

    catalog_size = len(datasets)
    catalog_exclusion_list_size = len(EXCEPTIONS_LIST)
    catalog_used_datasets_size = catalog_size - catalog_exclusion_list_size

    logger.info(f"Building structure for {catalog_used_datasets_size} datasets. "
                f"Excluded {catalog_exclusion_list_size} from {catalog_size}.\n")

    internal_catalog_folder = os.path.join(os.getcwd(), CATALOG_FOLDER) + os.path.sep
    create_internal_catalog_path(internal_catalog_folder)

    for current_num, dataset in enumerate(datasets):
        current = current_num + 1

        dataset_name = dataset.split(os.path.sep)[-2]

        if dataset_name in EXCEPTIONS_LIST:
            logger.info(f"### Skipping dataset {current}/{catalog_size}: {dataset_name} in EXCEPTIONS_LIST ###\n")
        else:
            dataset_folder = internal_catalog_folder + dataset_name

            logger.info(f"### Starting dataset {current}/{catalog_size}: {dataset_name} ###")

            create_test_directory_folders_structure(dataset_folder, catalog_size, current)

            # Building taxonomies files and collecting information from classes
            taxonomy_files = create_taxonomy_ttl_files(dataset, dataset_folder)

            # Builds dataset_classes_information and collects attributes name, prefixed_name, all taxonomic information
            dataset_classes_information = collect_taxonomies_information(taxonomy_files, catalog_size, current)

            # Collects stereotype_original and stereotype_gufo for dataset_classes_information
            collect_stereotypes_classes_information(dataset, dataset_classes_information, catalog_size, current)

            saves_dataset_csv_classes_data(dataset_classes_information, dataset_folder, catalog_size, current, dataset)

            logger.info(f"Dataset {dataset_name} successfully concluded!\n")

    logger.info(f"Generation of taxonomies successfully concluded for all {catalog_size} datasets\n")

    # Validate all taxonomies (optional)
    if validate_argument:
        validate_gufo_taxonomies()

    # # Keep gUFO classifications in all taxonomies (optional)
    if not gufo_argument:
        remove_gufo_classifications()


def create_arguments(is_complete: bool) -> dict:
    """ Set Scior's arguments for the implemented Tests.
        It is important to not that these are not the Tester's arguments.
    """

    arguments_dictionary = {"is_automatic": True, "is_interactive": False, "is_cwa": is_complete,
                            "is_owa": not is_complete, "gufo_results": False, "gufo_import": False, "gufo_write": False,
                            "is_silent": False, "is_verbose": True, "is_debug": False, "ontology_path": ""}
    return arguments_dictionary


def run_scior(is_complete: bool, tname: str) -> None:
    # Creating list of taxonomies
    taxonomies = get_list_ttl_files(os.path.join(os.getcwd(), CATALOG_FOLDER))

    global_configurations = create_arguments(is_complete)
    l1 = "a"
    l2 = "c" if is_complete else "n"
    test_name = f"{tname}_{l1}{l2}"

    # Creating name for output files
    inconsistencies_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"inconsistencies_{test_name}.csv")
    consistencies_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"consistencies_{test_name}.csv")
    divergences_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"divergences_{test_name}.csv")

    if tname != "tt003":
        # For Test 1 and Test 2: test only taxonomies that are valid (validation generated in build function)
        valid_file_name = os.path.join(os.getcwd(), CATALOG_FOLDER, f"valid_taxonomies_{l2}.txt")
        with open(valid_file_name) as f:
            valid_taxonomies = [line.rstrip() for line in f]
        taxonomies = [t for t in taxonomies if '\\'.join(t.split('\\')[-2:]) in valid_taxonomies]
    else:
        # For Test 3, use all taxonomies
        taxonomies = glob.glob('catalog/**/*.ttl')

    total_taxonomies_number = len(taxonomies)

    # Delete files if they exist from previous executions
    if os.path.exists(inconsistencies_file_name):
        os.remove(inconsistencies_file_name)
    if os.path.exists(divergences_file_name):
        os.remove(divergences_file_name)
    if os.path.exists(consistencies_file_name):
        os.remove(consistencies_file_name)

    test_number = tname[-1]
    test_type = "OWA" if global_configurations["is_owa"] else "CWA"
    logger.info(f"Starting Test {test_number} for {test_type}\n")

    prev_dataset_folder = ""
    for current, taxonomy in enumerate(taxonomies):

        logger.info(f"Executing Scior for taxonomy {current + 1}/{total_taxonomies_number}: {taxonomy}\n")

        taxonomy_filename = taxonomy.split(os.path.sep)[-1]
        data_filename = CLASSES_DATA_FILE_NAME + "_" + taxonomy_filename.replace(".ttl", ".csv")
        input_classes = load_baseline_dictionary(taxonomy.replace(taxonomy_filename, data_filename))
        input_graph = load_graph_safely(taxonomy)

        dataset_folder = taxonomy.rsplit(os.path.sep, 1)[0]
        draft_file_name = data_filename[4:-10] + "_" + test_name + data_filename[-10:]
        test_results_folder = os.path.join(dataset_folder, test_name)

        if test_number != "3":
            create_test_results_folder(test_results_folder, dataset_folder != prev_dataset_folder)

        if test_number == "1":
            run_scior_test1(global_configurations, input_classes, input_graph, test_results_folder, draft_file_name,
                            inconsistencies_file_name, divergences_file_name)

        elif test_number == "2":
            run_scior_test2(global_configurations, input_classes, input_graph, test_results_folder, draft_file_name,
                            inconsistencies_file_name, divergences_file_name, taxonomy_filename)

        elif test_number == "3":
            run_scior_test3(global_configurations, input_classes, input_graph, draft_file_name,
                            inconsistencies_file_name, consistencies_file_name, taxonomy_filename)

        else:
            logger.error("Unexpected test number. Program aborted.")
            exit(1)

        if dataset_folder != prev_dataset_folder:
            if prev_dataset_folder:
                logger.info(f"TEST{tname[-1]} is finished for {prev_dataset_folder}\n")
            prev_dataset_folder = dataset_folder


def run_scior_test1(global_configurations, input_classes, input_graph, test_results_folder, draft_file_name,
                    inconsistencies_file_name, divergences_file_name) -> None:
    """ Implements Test 1 for Scior - described in: https://github.com/unibz-core/Scior-Dataset """

    test_type = "OWA" if global_configurations["is_owa"] else "CWA"
    logger.info(f"Starting Test 1 for {test_type}\n")

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
            ontology_dataclass_list, classifications_matrix, leaves_matrix = run_scior_tester(global_configurations,
                                                                                              working_graph)
        except:
            logger.error(f"INCONSISTENCY found! Test {execution_number}/{tests_total} "
                         f"for input class {input_class.name} interrupted.")
            create_inconsistency_csv_output(inconsistencies_file_name, draft_file_name, execution_number, input_class)
        else:
            logger.info(f"Test {execution_number}/{tests_total} "
                        f"for input class {input_class.name} successfully executed.")
            create_classes_yaml_output(input_class, ontology_dataclass_list, test_results_folder,
                                       file_name=f"complete{draft_file_name[:-4]}_ex{execution_number:03d}.yaml")
            create_classes_results_csv_output(input_classes, ontology_dataclass_list, test_results_folder,
                                              divergences_file_name,
                                              file_name=f"simple{draft_file_name[:-4]}_ex{execution_number:03d}.csv")
            create_matrix_output(classifications_matrix, test_results_folder,
                                 file_name=f"class_matrix{draft_file_name[:-4]}_ex{execution_number:03d}.csv")
            create_matrix_output(leaves_matrix, test_results_folder,
                                 file_name=f"leaves_matrix{draft_file_name[:-4]}_ex{execution_number:03d}.csv")
            create_summary_csv_output(test_results_folder, draft_file_name, execution_number, input_class)


def run_scior_test2(global_configurations, input_classes, input_graph, test_results_folder, draft_file_name,
                    inconsistencies_file_name, divergences_file_name, taxonomy_filename):
    """ Implements Test 2 for Scior - described in: https://github.com/unibz-core/Scior-Dataset """

    test_type = "OWA" if global_configurations["is_owa"] else "CWA"
    logger.info(f"Starting Test 2 for {test_type}\n")

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
                ontology_dataclass_list, classifications_matrix, leaves_matrix = run_scior_tester(global_configurations,
                                                                                                  working_graph)
            except:
                logger.error(f"INCONSISTENCY found: {taxonomy_filename} "
                             f"- percentage {current_percentage} - execution {current_execution}. "
                             f"Current execution interrupted.{end}")
                create_inconsistency_csv_output_t2(inconsistencies_file_name, draft_file_name, current_percentage,
                                                   current_execution)
            else:
                logger.info(f"Test dataset {taxonomy_filename} - percentage {current_percentage} - "
                            f"execution {current_execution} successfully executed "
                            f"({number_of_input_classes} input classes).{end}")
                create_classes_yaml_output_t2(sample_list, ontology_dataclass_list, test_results_folder,
                                              file_name=f"complete{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.yaml")
                create_classes_results_csv_output(input_classes, ontology_dataclass_list, test_results_folder,
                                                  divergences_file_name,
                                                  file_name=f"simple{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.csv")
                create_matrix_output(classifications_matrix, test_results_folder,
                                     file_name=f"class_matrix{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.csv")
                create_matrix_output(leaves_matrix, test_results_folder,
                                     file_name=f"leaves_matrix{draft_file_name[:-4]}_ex{current_execution:03d}_pc{current_percentage:03d}.csv")
            current_execution += 1

        current_percentage += PERCENTAGE_RATE


def run_scior_test3(global_configurations, input_classes, input_graph, draft_file_name, inconsistencies_file_name,
                    consistencies_file_name, taxonomy_filename):
    """ Implements Scior-Tester's Test 3: all information of a model is provided to Scior, so it can evaluate
        which models are valid and which are not.
    """

    working_graph = deepcopy(input_graph)
    working_graph.bind("gufo", NAMESPACE_GUFO)
    for input_class in input_classes:
        triple_subject = URIRef(NAMESPACE_TAXONOMY + input_class.name)
        class_gufo_type = remaps_to_gufo(input_class.name, input_class.stereotype)
        triple_object = URIRef(class_gufo_type)
        working_graph.add((triple_subject, RDF.type, triple_object))

    try:
        run_scior_tester(global_configurations, working_graph)
    except:
        logger.error(f"INCONSISTENCY found: {taxonomy_filename} Current execution interrupted.\n")
        create_inconsistency_csv_output_t2(inconsistencies_file_name, draft_file_name, 100, 1)
    else:
        create_inconsistency_csv_output_t2(consistencies_file_name, draft_file_name, 100, 1)
        logger.info(f"Test dataset {taxonomy_filename} successfully executed.\n")


if __name__ == '__main__':

    logger = initialize_logger()

    arguments = treat_arguments(SOFTWARE_ACRONYM, SOFTWARE_NAME, SOFTWARE_VERSION, SOFTWARE_URL)

    # Execute in BUILD mode.
    if arguments["build"]:
        build_scior_tester(arguments["catalog_path"], arguments["validate"], arguments["gufo"])

    # Execute in RUN mode.
    if arguments["run1"]:
        run_scior(arguments["is_complete"], tname="tt001")

    if arguments["run2"]:
        run_scior(arguments["is_complete"], tname="tt002")

    if arguments["run3"]:
        run_scior(arguments["is_complete"], tname="tt003")
