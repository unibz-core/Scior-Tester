""" Baseline dictionary definition. """
import csv
import os
import platform

import psutil
import yaml

from src import NAMESPACE_TAXONOMY, NAMESPACE_GUFO, MINIMUM_ALLOWED_NUMBER_CLASSES, PERCENTAGE_INITIAL, \
    PERCENTAGE_FINAL, PERCENTAGE_RATE, NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE
from src.modules.build.build_directories_structure import create_folder
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import write_csv_row, write_dictionary


class ClassDef(object):
    def __init__(self, class_name, class_stereotype):
        self.name = class_name
        self.stereotype = class_stereotype


def load_baseline_dictionary(csv_file_name):
    list_input_classes = []

    with open(csv_file_name, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            if row[2] != "other":
                list_input_classes.append(ClassDef(row[0], row[2]))

    return list_input_classes


def save_platform_information(dataset_folder, file_name, software_version, env_vars=False):
    """ Saves platform information into the file """
    csv_header = ["scior_version", "python_version", "operating_system", "processor", "installed_ram"]
    csv_row = [software_version,
               platform.python_version(),
               f"{platform.system()} {platform.release()} - v{platform.version()}",
               f"{platform.processor()} ({platform.machine()})",
               round(psutil.virtual_memory().total / (1024.0 ** 3))]
    if env_vars:
        csv_header += ["minimum_allowed_number_classes", "percentage_initial", "percentage_final",
                       "percentage_rate", "number_of_executions_per_dataset_per_percentage"]
        csv_row += [MINIMUM_ALLOWED_NUMBER_CLASSES, PERCENTAGE_INITIAL, PERCENTAGE_FINAL,
                    PERCENTAGE_RATE, NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE]

    with open(os.path.join(dataset_folder, file_name), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerow(csv_row)


def remaps_to_gufo(class_name, gufo_lower_type: str, no_namespace: bool = False):
    """ Receives a gufo_lower_type and returns a valid_gufo_type """

    logger = initialize_logger()

    mapped_stereotype = ""
    list_for_capitalization = ["category", "kind", "mixin", "phase", "role", "sortal"]
    dict_for_mapping = {"phasemixin": "PhaseMixin", "rolemixin": "RoleMixin", "subkind": "SubKind",
                        "nonsortal": "NonSortal", "rigidtype": "RigidType", "nonrigidtype": "NonRigidType"}

    if gufo_lower_type in list_for_capitalization:
        mapped_stereotype = gufo_lower_type.capitalize()
    elif gufo_lower_type in dict_for_mapping:
        mapped_stereotype = dict_for_mapping[gufo_lower_type]
    else:
        logger.error(f"Unknown gufo_lower_type {gufo_lower_type} in class {class_name}. Program aborted.")
        exit(1)

    return mapped_stereotype if no_namespace else NAMESPACE_GUFO + mapped_stereotype


def create_inconsistency_csv_output(inconsistencies_file_name, file_name, execution_number, input_class):
    """ Creates and updates a CSV file with a list of all inconsistent classes and their stereotypes. """
    csv_header = ["taxonomy_name", "execution_number", "inconsistent_class_name", "inconsistent_class_classification"]
    csv_row = [file_name[1:-18] + file_name[-9:-4] + ".ttl", execution_number, input_class.name, input_class.stereotype]
    write_csv_row(inconsistencies_file_name, csv_header, csv_row)


def create_summary_csv_output(test_results_folder, file_name, execution_number, input_class):
    """ Creates and updates a CSV file with a list of all executions, the respective input classes
    and their stereotypes. """
    csv_header = ["execution_number", "input_class_name", "input_class_stereotype"]
    csv_row = [execution_number, input_class.name, input_class.stereotype]
    statistics = os.path.join(test_results_folder, f"summary{file_name}")
    write_csv_row(statistics, csv_header, csv_row)


def create_statistics_csv_output(ontology_dataclass_list, consolidated_statistics, test_results_folder,
                                 file_name, execution_number):
    csv_header = create_csv_header()
    number_incomplete_classes = calculate_incompleteness_values(ontology_dataclass_list)
    csv_row = populate_csv_row(consolidated_statistics, execution_number, number_incomplete_classes)
    statistics = os.path.join(test_results_folder, f"statistics{file_name}")
    write_csv_row(statistics, csv_header, csv_row)


def calculate_incompleteness_values(ontology_dataclass_list):
    return sum([1 for dataclass in ontology_dataclass_list if dataclass.incompleteness_info["is_incomplete"]])


def create_times_csv_output(time_register, test_results_folder, file_name, execution_number):
    times_output_complete_path = os.path.join(test_results_folder, f"times{file_name}")
    time_keys = list(time_register.keys())
    time_keys.sort()
    time_keys = ["execution"] + time_keys
    time_register["execution"] = execution_number
    write_dictionary(times_output_complete_path, time_keys, time_register)


def create_classes_yaml_output(input_class, ontology_dataclass_list, test_results_folder, file_name):
    """ Receives an ontology_dataclass_list and saves its information in yaml format. """

    yaml_folder = os.path.join(test_results_folder, "results")
    create_folder(yaml_folder, "Results directory created")
    classes_output_complete_path = os.path.join(yaml_folder, file_name)

    ontology_dictionary_list = convert_ontology_dataclass_list_to_dictionary_list(
        [input_class], ontology_dataclass_list)

    with open(classes_output_complete_path, 'w', encoding='utf-8') as file:
        yaml.dump_all(ontology_dictionary_list, file, sort_keys=True)


def convert_ontology_dataclass_list_to_dictionary_list(input_class_list, ontology_dataclass_list):
    """ Receives an ontology_dataclass_list and returns a dictionary to be printed in yaml format. """

    ontology_dictionary_list = []
    input_long_names = [NAMESPACE_TAXONOMY + input_class.name for input_class in input_class_list]

    for ontology_dataclass in ontology_dataclass_list:
        short_dataclass_name = ontology_dataclass.uri.removeprefix(NAMESPACE_TAXONOMY)
        ontology_dictionary = {short_dataclass_name: {
            "input": ontology_dataclass.uri in input_long_names,
            "is_type": ontology_dataclass.is_type,
            "can_type": ontology_dataclass.can_type,
            "not_type": ontology_dataclass.not_type,
            "is_incomplete": ontology_dataclass.incompleteness_info["is_incomplete"],
            "detected_in": ontology_dataclass.incompleteness_info["detected_in"]
        }
        }
        ontology_dictionary_list.append(ontology_dictionary)

    return ontology_dictionary_list


def get_final_list(class_name_prefixed, class_gufo_stereotype, ontology_dataclass_list):
    final_list = "undeclared"
    logger = initialize_logger()

    for dataclass in ontology_dataclass_list:
        if dataclass.uri == class_name_prefixed:
            if class_gufo_stereotype in dataclass.is_type:
                final_list = "is"
            elif class_gufo_stereotype in dataclass.can_type:
                final_list = "can"
            elif class_gufo_stereotype in dataclass.not_type:
                final_list = "not"
            else:
                logger.error("Not found in any list.")
                exit(1)

    return final_list


def create_classes_results_csv_output(input_classes_list, ontology_dataclass_list, test_folder,
                                      divergences_file_name, file_name):
    final_row_list = []
    has_divergency = False

    for input_class in input_classes_list:
        class_name_prefixed = NAMESPACE_TAXONOMY + input_class.name
        class_gufo_stereotype = "gufo:" + remaps_to_gufo(input_class.name, input_class.stereotype, True)
        final_list = get_final_list(class_name_prefixed, class_gufo_stereotype, ontology_dataclass_list)
        final_row = [input_class.name, input_class.stereotype, final_list]
        if final_list == "not":
            has_divergency = True
        final_row_list.append(final_row)

    classes_output_complete_path = os.path.join(test_folder, "results", file_name)
    csv_header = ["class_name", "class_original_classification", "classification_final_list"]
    with open(classes_output_complete_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for final_row in final_row_list:
            writer.writerow(final_row)

    if has_divergency:
        write_csv_row(divergences_file_name,
                      ["taxonomy_name", "result_file"],
                      [file_name.split("_")[1] + "_" + file_name.split("_")[4][0:5] + ".ttl", file_name])


def create_matrix_output(knowledge_matrix, test_folder, file_name):
    knowledge_matrix_path = os.path.join(test_folder, "results", file_name)

    with open(knowledge_matrix_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(knowledge_matrix)


"""
--------------------------------
Functions for statistics
--------------------------------
"""


def create_csv_header():
    csv_header = ["execution"]

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


def populate_csv_row(consolidated_statistics, execution_number, number_incomplete_classes):
    csv_row = [execution_number]

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
