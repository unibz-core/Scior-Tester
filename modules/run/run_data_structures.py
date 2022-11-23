""" Baseline dictionary definition. """
import csv
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
            short_class_name : {
            "input": input_situation,
            "is_type": ontology_dataclass.is_type,
            "can_type": ontology_dataclass.can_type,
            "not_type": ontology_dataclass.not_type,
            "is_incomplete": ontology_dataclass.incompleteness_info["is_incomplete"],
            "detected_in": ontology_dataclass.incompleteness_info["detected_in"] }
        }
        ontology_dictionary_list.append(ontology_dictionary)

    return ontology_dictionary_list


def create_yaml_classes_output(input_class, ontology_dataclass_list, test_results_folder, execution_name):
    """ Receives an ontology_dataclass_list and saves its information in yaml format. """

    classes_output_filename = f"classes{execution_name}.yaml"
    classes_output_complete_path = test_results_folder + "\\" + classes_output_filename

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


def generate_times_csv_output(time_register):
    pass