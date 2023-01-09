""" Functions related to Test 2 """
import csv
import os

import yaml

from src.modules.run.test1 import remaps_to_gufo, get_final_list, calculate_incompleteness_values
from src.modules.tester.hash_functions import register_sha256_hash_information
from src.modules.tester.logger_config import initialize_logger

NAMESPACE_TAXONOMY = "http://taxonomy.model/"


def create_percentage_results_folder(dataset_folder):
    logger = initialize_logger()

    try:
        # Create dataset folders in tester_catalog_folder
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)
            logger.info(f"Directory created: {dataset_folder}.")
        else:
            logger.info(f"Directory already exists: {dataset_folder}.")
    except OSError as error:
        logger.error(f"Directory {dataset_folder} could not be created. Program aborted.\n"
                     f"System error reported: {error}")


def create_inconsistency_csv_output_t2(test_results_folder, percentage_number, execution_number, initial_percentage):
    """ Creates and updates a CSV file with a list of percentages and executions that reported inconsistencies. """

    csv_header = ["percentage_test", "execution_number"]
    csv_row = [percentage_number, execution_number]

    inconsistencies_output_filename = f"inconsistencies_found.csv"
    inconsistencies = test_results_folder + "\\" + inconsistencies_output_filename
    file_exists = os.path.exists(inconsistencies)

    # If not file or first case (initial percentage and first execution), then create. Else, append.
    if (not file_exists) or (percentage_number == initial_percentage and execution_number == 1):
        with open(inconsistencies, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerow(csv_row)
    else:
        with open(inconsistencies, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_row)


def convert_ontology_dataclass_list_to_dictionary_list_t2(input_class_list, ontology_dataclass_list):
    """ Receives an ontology_dataclass_list and returns a dictionary to be printed in yaml format. """

    ontology_dictionary_list = []

    list_input_long_names = []

    for input_class in input_class_list:
        input_class_long_name = NAMESPACE_TAXONOMY + input_class.class_name
        list_input_long_names.append(input_class_long_name)

    for ontology_dataclass in ontology_dataclass_list:

        if ontology_dataclass.uri in list_input_long_names:
            input_situation = True
        else:
            input_situation = False

        short_dataclass_name = ontology_dataclass.uri.removeprefix(NAMESPACE_TAXONOMY)

        ontology_dictionary = {
            short_dataclass_name: {
                "input": input_situation,
                "is_type": ontology_dataclass.is_type,
                "can_type": ontology_dataclass.can_type,
                "not_type": ontology_dataclass.not_type,
                "is_incomplete": ontology_dataclass.incompleteness_info["is_incomplete"],
                "detected_in": ontology_dataclass.incompleteness_info["detected_in"]}
        }
        ontology_dictionary_list.append(ontology_dictionary)

    return ontology_dictionary_list


def create_classes_yaml_output_t2(input_class_list, ontology_dataclass_list, test_results_folder, percentage_number,
                                  execution_number, dataset_taxonomy):
    """ Receives the final ontology_dataclass_list and saves its information in yaml format. """

    logger = initialize_logger()

    yaml_folder = test_results_folder + "\\results"
    if not os.path.exists(yaml_folder):
        try:
            os.makedirs(yaml_folder)
        except OSError as error:
            logger.error(f"Directory {yaml_folder} could not be created. Program aborted.\n"
                         f"System error reported: {error}")

    classes_output_filename = f"classes_per_{percentage_number}_exec_{execution_number}.yaml"
    classes_output_complete_path = yaml_folder + "\\" + classes_output_filename

    ontology_dictionary_list = convert_ontology_dataclass_list_to_dictionary_list_t2(input_class_list,
                                                                                     ontology_dataclass_list)

    with open(classes_output_complete_path, 'w', encoding='utf-8') as file:
        yaml.dump_all(ontology_dictionary_list, file, sort_keys=True)

    register_sha256_hash_information(classes_output_complete_path, dataset_taxonomy)


def create_classes_results_csv_output_t2(input_classes_list, ontology_dataclass_list, test_results_folder,
                                         percentage_number, execution_number, dataset_taxonomy):
    """ Create a csv file for each class, its original stereotype,
    and the list in which this stereotype is located after the execution of Scior. """

    final_row_list = []

    for input_class in input_classes_list:
        class_name_prefixed = NAMESPACE_TAXONOMY + input_class.class_name
        class_gufo_stereotype = remaps_to_gufo(input_class.class_name, input_class.class_stereotype, True)
        class_gufo_stereotype = "gufo:" + class_gufo_stereotype
        final_list = get_final_list(class_name_prefixed, class_gufo_stereotype, ontology_dataclass_list)
        final_row = [input_class.class_name, input_class.class_stereotype, final_list]
        final_row_list.append(final_row)

    csv_folder = test_results_folder + "\\results"

    classes_output_filename = f"results_per_{percentage_number}_exec_{execution_number}.csv"
    classes_output_complete_path = csv_folder + "\\" + classes_output_filename

    csv_header = ["class_name", "class_original_stereotype", "stereotype_final_list"]

    with open(classes_output_complete_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for final_row in final_row_list:
            writer.writerow(final_row)

    register_sha256_hash_information(classes_output_complete_path, dataset_taxonomy)


def create_times_csv_output_t2(time_register, test_results_folder, percentage_number, execution_number,
                               initial_percentage):
    times_output_filename = f"execution_times.csv"
    times_output_complete_path = test_results_folder + "\\" + times_output_filename

    time_register["percentage"] = percentage_number
    time_register["execution"] = execution_number

    items = list(time_register.items())
    items.insert(0, ("percentage", percentage_number))
    time_register = dict(items)


    file_exists = os.path.exists(times_output_complete_path)

    # If not file or first case (initial percentage and first execution), then create. Else, append.
    if (not file_exists) or (percentage_number == initial_percentage and execution_number == 1):
        with open(times_output_complete_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writeheader()
            writer.writerow(time_register)
    else:
        with open(times_output_complete_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writerow(time_register)

    return times_output_complete_path


def create_csv_header_t2():
    csv_header = []

    # GENERAL

    csv_header.append("percentage")
    csv_header.append("execution")

    # CLASSES

    # Classes values before
    csv_header.append("classes_b_total_classes_number")
    csv_header.append("classes_b_tu_classes_types_v")
    csv_header.append("classes_b_pk_classes_types_v")
    csv_header.append("classes_b_tk_classes_types_v")

    # Classes percentages before
    csv_header.append("classes_b_tu_classes_types_p")
    csv_header.append("classes_b_pk_classes_types_p")
    csv_header.append("classes_b_tk_classes_types_p")

    # Classes values after
    csv_header.append("classes_a_total_classes_number")
    csv_header.append("classes_a_tu_classes_types_v")
    csv_header.append("classes_a_pk_classes_types_v")
    csv_header.append("classes_a_tk_classes_types_v")

    # Classes percentages after
    csv_header.append("classes_a_tu_classes_types_p")
    csv_header.append("classes_a_pk_classes_types_p")
    csv_header.append("classes_a_tk_classes_types_p")

    # CLASSIFICATIONS

    # Classifications values before
    csv_header.append("classif_b_total_classif_types_v")
    csv_header.append("classif_b_unknown_classif_types_v")
    csv_header.append("classif_b_known_classif_types_v")

    # Classifications values after
    csv_header.append("classif_a_total_classif_types_v")
    csv_header.append("classif_a_unknown_classif_types_v")
    csv_header.append("classif_a_known_classif_types_v")

    # Classifications percentages before
    csv_header.append("classif_b_unknown_classif_types_p")
    csv_header.append("classif_b_known_classif_types_p")

    # Classifications percentages after
    csv_header.append("classif_a_unknown_classif_types_p")
    csv_header.append("classif_a_known_classif_types_p")

    # DIFFERENCES

    # Classes difference values: after - before
    csv_header.append("diff_tu_classes_types_v")
    csv_header.append("diff_pk_classes_types_v")
    csv_header.append("diff_tk_classes_types_v")

    # Classes difference percentages: after - before
    csv_header.append("diff_tu_classes_types_p")
    csv_header.append("diff_pk_classes_types_p")
    csv_header.append("diff_tk_classes_types_p")

    # Classifications difference values: after - before
    csv_header.append("diff_unknown_classif_types_v")
    csv_header.append("diff_known_classif_types_v")

    # Classifications difference percentages: after - before
    csv_header.append("diff_unknown_classif_types_p")
    csv_header.append("diff_known_classif_types_p")

    # INCOMPLETENESS
    csv_header.append("incomplete_classes_found")

    return csv_header


def populate_csv_row_t2(consolidated_statistics, percentage_number, execution_number, number_incomplete_classes):
    csv_row = []

    # GENERAL

    csv_row.append(percentage_number)
    csv_row.append(execution_number)

    classes_b = consolidated_statistics.classes_stats_b
    classes_a = consolidated_statistics.classes_stats_a
    classif_b = consolidated_statistics.classif_stats_b
    classif_a = consolidated_statistics.classif_stats_a

    # CLASSES

    # Classes values before
    csv_row.append(classes_b.total_classes_number)
    csv_row.append(classes_b.tu_classes_types_v)
    csv_row.append(classes_b.pk_classes_types_v)
    csv_row.append(classes_b.tk_classes_types_v)

    # Classes percentages before
    csv_row.append(classes_b.tu_classes_types_p)
    csv_row.append(classes_b.pk_classes_types_p)
    csv_row.append(classes_b.tk_classes_types_p)

    # Classes values after
    csv_row.append(classes_a.total_classes_number)
    csv_row.append(classes_a.tu_classes_types_v)
    csv_row.append(classes_a.pk_classes_types_v)
    csv_row.append(classes_a.tk_classes_types_v)

    # Classes percentages after
    csv_row.append(classes_a.tu_classes_types_p)
    csv_row.append(classes_a.pk_classes_types_p)
    csv_row.append(classes_a.tk_classes_types_p)

    # CLASSIFICATIONS

    # Classifications values before
    csv_row.append(classif_b.total_classif_types_v)
    csv_row.append(classif_b.unknown_classif_types_v)
    csv_row.append(classif_b.known_classif_types_v)

    # Classifications values after
    csv_row.append(classif_a.total_classif_types_v)
    csv_row.append(classif_a.unknown_classif_types_v)
    csv_row.append(classif_a.known_classif_types_v)

    # Classifications percentages before
    csv_row.append(classif_b.unknown_classif_types_p)
    csv_row.append(classif_b.known_classif_types_p)

    # Classifications percentages after
    csv_row.append(classif_a.unknown_classif_types_p)
    csv_row.append(classif_a.known_classif_types_p)

    # DIFFERENCES

    # Classes difference values: after - before
    csv_row.append(consolidated_statistics.tu_classes_types_v_d)
    csv_row.append(consolidated_statistics.pk_classes_types_v_d)
    csv_row.append(consolidated_statistics.tk_classes_types_v_d)

    # Classes difference percentages: after - before
    csv_row.append(consolidated_statistics.tu_classes_types_p_d)
    csv_row.append(consolidated_statistics.pk_classes_types_p_d)
    csv_row.append(consolidated_statistics.tk_classes_types_p_d)

    # Classifications difference values: after - before
    csv_row.append(consolidated_statistics.unknown_classif_types_v_d)
    csv_row.append(consolidated_statistics.known_classif_types_v_d)

    # Classifications difference values: after - before
    csv_row.append(consolidated_statistics.unknown_classif_types_p_d)
    csv_row.append(consolidated_statistics.known_classif_types_p_d)

    # INCOMPLETENESS
    csv_row.append(number_incomplete_classes)

    return csv_row


def create_statistics_csv_output_t2(ontology_dataclass_list, consolidated_statistics, test_results_folder,
                                    percentage_number, execution_number, initial_percentage):
    csv_header = create_csv_header_t2()
    number_incomplete_classes = calculate_incompleteness_values(ontology_dataclass_list)
    csv_row = populate_csv_row_t2(consolidated_statistics, percentage_number, execution_number,
                                  number_incomplete_classes)

    statistics_output_filename = f"execution_statistics.csv"
    statistics_complete_path = test_results_folder + "\\" + statistics_output_filename

    file_exists = os.path.exists(statistics_complete_path)

    # If not file or first case (initial percentage and first execution), then create. Else, append.
    if (not file_exists) or (percentage_number == initial_percentage and execution_number == 1):
        with open(statistics_complete_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerow(csv_row)
    else:
        with open(statistics_complete_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_row)

    return statistics_complete_path
