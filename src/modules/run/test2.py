""" Functions related to Test 2 """
import csv
import os

import src.modules.run.test1 as test1

from src import NAMESPACE_TAXONOMY


def _write_file(file_name, percentage_number, initial_percentage, execution_number):
    return ((not os.path.exists(file_name)) or
            (percentage_number == initial_percentage and execution_number == 1))


def create_inconsistency_csv_output_t2(test_results_folder, file_name, percentage_number, execution_number,
                                       initial_percentage):
    """ Creates and updates a CSV file with a list of percentages and executions that reported inconsistencies. """

    csv_header = ["percentage", "execution_number"]
    csv_row = [percentage_number, execution_number]

    inconsistencies = os.path.join(test_results_folder, f"inconsistencies{file_name}")
    test1.write_csv_row(inconsistencies, csv_header, csv_row,
                        _write_file(inconsistencies, percentage_number, initial_percentage, execution_number))


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


def create_times_csv_output_t2(time_register, test_results_folder, file_name, percentage_number, execution_number,
                               initial_percentage):
    times_output_complete_path = os.path.join(test_results_folder,
                                    f"times{file_name[:-4]}_ex{execution_number:03d}_pc{percentage_number:03d}.csv")
    time_keys = ["percentage", "execution"] + list(time_register.keys())
    time_register["percentage"] = percentage_number
    time_register["execution"] = execution_number

    # If not file or first case (initial percentage and first execution), then create. Else, append.
    if _write_file(times_output_complete_path):
        with open(times_output_complete_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writeheader()
            writer.writerow(time_register)
    else:
        with open(times_output_complete_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=time_register.keys())
            writer.writerow(time_register)
    # return times_output_complete_path


def create_csv_header():
    return ["percentage"] + test1.create_csv_header()


def populate_csv_row(consolidated_statistics, percentage_number, execution_number, number_incomplete_classes):
    csv_row = [percentage_number] + test1.populate_csv_row(
        consolidated_statistics, execution_number, number_incomplete_classes)
    return csv_row


def create_statistics_csv_output_t2(ontology_dataclass_list, consolidated_statistics, test_results_folder,
                                    file_name, percentage_number, execution_number, initial_percentage):
    csv_header = create_csv_header()
    number_incomplete_classes = test1.calculate_incompleteness_values(ontology_dataclass_list)
    csv_row = populate_csv_row(consolidated_statistics, percentage_number, execution_number, number_incomplete_classes)
    statistics = os.path.join(test_results_folder,
                              f"statistics{file_name[:-4]}_ex{execution_number:03d}_pc{percentage_number:03d}.csv")
    test1.write_csv_row(statistics, csv_header, csv_row,
                        _write_file(statistics, percentage_number, initial_percentage, execution_number))
    # return statistics
