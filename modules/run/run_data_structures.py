""" Baseline dictionary definition. """
import csv
import os
import pathlib

import yaml

from modules.tester.logger_config import initialize_logger

NAMESPACE_GUFO = "http://purl.org/nemo/gufo#"
NAMESPACE_TAXONOMY = "http://taxonomy.model/"


class input_class(object):
    def __init__(self, class_name, class_stereotype):
        self.class_name = class_name
        self.class_stereotype = class_stereotype


def load_baseline_dictionary(dataset):
    list_input_classes = []

    tester_path = str(pathlib.Path().resolve())
    dataset_path = tester_path + chr(92) + "catalog" + chr(92) + dataset + chr(92)
    csv_file_full_path = dataset_path + "classes_data.csv"

    with open(csv_file_full_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        index = 0
        for row in csv_reader:
            if (index != 0) and (row[2] != "other"):
                new_class = input_class(row[0], row[2])
                list_input_classes.append(new_class)
            index += 1

    return list_input_classes


def convert_ontology_dataclass_list_to_dictionary_list(input_class, ontology_dataclass_list):
    """ Receives an ontology_dataclass_list and returns a dictionary to be printed in yaml format. """

    ontology_dictionary_list = []

    for ontology_dataclass in ontology_dataclass_list:

        input_class_long_name = NAMESPACE_TAXONOMY + input_class.class_name
        if input_class_long_name == ontology_dataclass.uri:
            input_situation = True
        else:
            input_situation = False

        short_class_name = ontology_dataclass.uri.removeprefix(NAMESPACE_TAXONOMY)

        ontology_dictionary = {
            short_class_name: {
                "input": input_situation,
                "is_type": ontology_dataclass.is_type,
                "can_type": ontology_dataclass.can_type,
                "not_type": ontology_dataclass.not_type,
                "is_incomplete": ontology_dataclass.incompleteness_info["is_incomplete"],
                "detected_in": ontology_dataclass.incompleteness_info["detected_in"]}
        }
        ontology_dictionary_list.append(ontology_dictionary)

    return ontology_dictionary_list


def create_classes_yaml_output(input_class, ontology_dataclass_list, test_results_folder, execution_name):
    """ Receives an ontology_dataclass_list and saves its information in yaml format. """

    yaml_folder = test_results_folder + "\\results"
    print(yaml_folder)
    exit(3)
    if not os.path.exists(yaml_folder):
        os.makedirs(yaml_folder)

    classes_output_filename = f"classes_{execution_name}.yaml"
    classes_output_complete_path = yaml_folder + "\\" + classes_output_filename

    ontology_dictionary_list = convert_ontology_dataclass_list_to_dictionary_list(input_class, ontology_dataclass_list)

    with open(classes_output_complete_path, 'w') as file:
        yaml.dump_all(ontology_dictionary_list, file, sort_keys=True)


def remaps_to_gufo(gufo_lower_type):
    """ Receives a gufo_lower_type and returns a valid_gufo_type """

    logger = initialize_logger()

    if gufo_lower_type == "category":
        mapped_stereotype = "Category"
    elif gufo_lower_type == "kind":
        mapped_stereotype = "Kind"
    elif gufo_lower_type == "mixin":
        mapped_stereotype = "Mixin"
    elif gufo_lower_type == "phase":
        mapped_stereotype = "Phase"
    elif gufo_lower_type == "phasemixin":
        mapped_stereotype = "PhaseMixin"
    elif gufo_lower_type == "role":
        mapped_stereotype = "Role"
    elif gufo_lower_type == "rolemixin":
        mapped_stereotype = "RoleMixin"
    elif gufo_lower_type == "subkind":
        mapped_stereotype = "SubKind"
    else:
        logger.error("Unknown gufo_lower_type. Program aborted.")
        exit(1)

    valid_gufo_type = NAMESPACE_GUFO + mapped_stereotype

    return valid_gufo_type


def create_times_csv_output(time_register, test_results_folder, execution_number, execution_name):
    times_output_filename = f"execution_times.csv"
    times_output_complete_path = test_results_folder + "\\" + times_output_filename

    time_register["execution"] = execution_number

    if execution_number == 1:
        with open(times_output_complete_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writeheader()
            writer.writerow(time_register)
    else:
        with open(times_output_complete_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writerow(time_register)


def create_csv_header():
    csv_header = []

    ### GENERAL

    csv_header.append("execution")

    ### CLASSES

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

    ### CLASSIFICATIONS

    # Classifications values before
    csv_header.append("classif_b_total_classif_types_v")
    csv_header.append("classif_b_unknown_classif_types_v")
    csv_header.append("classif_b_known_classif_types_v")

    # Classifications values after
    csv_header.append("classif_a_total_classif_types_v")
    csv_header.append("classif_a_unknown_classif_types_v")
    csv_header.append("classif_a_known_classif_types_v")

    # Classifications percentages before
    csv_header.append("classif_b_total_classif_types_p")
    csv_header.append("classif_b_unknown_classif_types_p")
    csv_header.append("classif_b_known_classif_types_p")

    # Classifications percentages after
    csv_header.append("classif_a_total_classif_types_p")
    csv_header.append("classif_a_unknown_classif_types_p")
    csv_header.append("classif_a_known_classif_types_p")

    ### DIFFERENCES

    # Classes difference values: after - before
    csv_header.append("diff_tu_classes_types_v_d")
    csv_header.append("diff_pk_classes_types_v_d")
    csv_header.append("diff_tk_classes_types_v_d")

    # Classes difference percentages: after - before
    csv_header.append("diff_tu_classes_types_p_d")
    csv_header.append("diff_pk_classes_types_p_d")
    csv_header.append("diff_tk_classes_types_p_d")

    # Classifications difference values: after - before
    csv_header.append("diff_total_classif_types_v_d")
    csv_header.append("diff_unknown_classif_types_v_d")
    csv_header.append("diff_known_classif_types_v_d")

    # Classifications difference percentages: after - before
    csv_header.append("diff_total_classif_types_p_d")
    csv_header.append("diff_unknown_classif_types_p_d")
    csv_header.append("diff_known_classif_types_p_d")

    ### INCOMPLETENESS
    csv_header.append("incomplete_classes_found")

    return csv_header


def populate_csv_row(input_class_name, consolidated_statistics, execution_number, number_incomplete_classes):
    csv_row = []

    ### GENERAL

    csv_row.append(execution_number)

    classes_b = consolidated_statistics.classes_stats_b
    classes_a = consolidated_statistics.classes_stats_a
    classif_b = consolidated_statistics.classif_stats_b
    classif_a = consolidated_statistics.classif_stats_a

    ### CLASSES

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

    ### CLASSIFICATIONS

    # Classifications values before
    csv_row.append(classif_b.total_classif_types_v)
    csv_row.append(classif_b.unknown_classif_types_v)
    csv_row.append(classif_b.known_classif_types_v)

    # Classifications values after
    csv_row.append(classif_a.total_classif_types_v)
    csv_row.append(classif_a.unknown_classif_types_v)
    csv_row.append(classif_a.known_classif_types_v)

    # Classifications percentages before
    csv_row.append(classif_b.total_classif_types_p)
    csv_row.append(classif_b.unknown_classif_types_p)
    csv_row.append(classif_b.known_classif_types_p)

    # Classifications percentages after
    csv_row.append(classif_a.total_classif_types_p)
    csv_row.append(classif_a.unknown_classif_types_p)
    csv_row.append(classif_a.known_classif_types_p)

    ### DIFFERENCES

    # Classes difference values: after - before
    csv_row.append(consolidated_statistics.tu_classes_types_v_d)
    csv_row.append(consolidated_statistics.pk_classes_types_v_d)
    csv_row.append(consolidated_statistics.tk_classes_types_v_d)

    # Classes difference percentages: after - before
    csv_row.append(consolidated_statistics.tu_classes_types_p_d)
    csv_row.append(consolidated_statistics.pk_classes_types_p_d)
    csv_row.append(consolidated_statistics.tk_classes_types_p_d)

    # Classifications difference values: after - before
    csv_row.append(consolidated_statistics.total_classif_types_v_d)
    csv_row.append(consolidated_statistics.unknown_classif_types_v_d)
    csv_row.append(consolidated_statistics.known_classif_types_v_d)

    # Classifications difference values: after - before
    csv_row.append(consolidated_statistics.total_classif_types_p_d)
    csv_row.append(consolidated_statistics.unknown_classif_types_p_d)
    csv_row.append(consolidated_statistics.known_classif_types_p_d)

    ### INCOMPLETENESS
    csv_row.append(number_incomplete_classes)

    return csv_row

def calculate_incompleteness_values(ontology_dataclass_list):

    number_incomplete_classes = 0
    for dataclass in ontology_dataclass_list:
        if dataclass.incompleteness_info["is_incomplete"] == True:
            number_incomplete_classes += 1

    return number_incomplete_classes


def create_statistics_csv_output(input_class_name, ontology_dataclass_list, consolidated_statistics, test_results_folder, execution_number):

    csv_header = create_csv_header()
    number_incomplete_classes = calculate_incompleteness_values(ontology_dataclass_list)
    csv_row = populate_csv_row(consolidated_statistics, execution_number, number_incomplete_classes)

    statistics_output_filename = f"execution_statistics.csv"
    statistics = test_results_folder + "\\" + statistics_output_filename

    if execution_number == 1:
        with open(statistics, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerow(csv_row)
    else:
        with open(statistics, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_row)


def create_summary_csv_output(test_results_folder, execution_number, input_class):

    input_class_name = input_class.name
    input_class_stereotype = input_class.class_stereotype

    csv_header = ["execution_number", "input_class_name", "input_class_stereotype"]
    csv_row = [execution_number, input_class_name, input_class_stereotype]

    statistics_output_filename = f"execution_summary.csv"
    statistics = test_results_folder + "\\" + statistics_output_filename

    if execution_number == 1:
        with open(statistics, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerow(csv_row)
    else:
        with open(statistics, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_row)
