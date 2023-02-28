""" Functions related to Test 2 """
import os

import yaml

import src.modules.run.test1 as test1


def create_inconsistency_csv_output_t2(inconsistencies_file_name, file_name, percentage_number, execution_number):
    """ Creates and updates a CSV file with a list of percentages and executions that reported inconsistencies. """
    csv_header = ["taxonomy_name", "percentage", "execution_number"]
    csv_row = [file_name[1:-18] + file_name[-9:-4] + ".ttl", percentage_number, execution_number]
    test1.write_csv_row(inconsistencies_file_name, csv_header, csv_row)


def create_classes_yaml_output_t2(input_class_list, ontology_dataclass_list, test_results_folder, file_name):
    """ Receives an ontology_dataclass_list and saves its information in yaml format. """

    yaml_folder = os.path.join(test_results_folder, "results")
    test1.create_folder(yaml_folder, "Results directory created")
    classes_output_complete_path = os.path.join(yaml_folder, file_name)

    ontology_dictionary_list = test1.convert_ontology_dataclass_list_to_dictionary_list(
        input_class_list, ontology_dataclass_list)

    with open(classes_output_complete_path, 'w', encoding='utf-8') as file:
        yaml.dump_all(ontology_dictionary_list, file, sort_keys=True)


def create_times_csv_output_t2(time_register, test_results_folder, file_name, percentage_number, execution_number):
    times_output_complete_path = os.path.join(test_results_folder,
                                              f"times{file_name[:-4]}_ex{execution_number:03d}_pc{percentage_number:03d}.csv")
    time_keys = list(time_register.keys())
    time_keys.sort()
    time_keys = ["percentage", "execution"] + time_keys
    time_register["percentage"] = percentage_number
    time_register["execution"] = execution_number
    test1.write_dictionary(times_output_complete_path, time_keys, time_register)


def create_csv_header():
    return ["percentage"] + test1.create_csv_header()


def populate_csv_row(consolidated_statistics, percentage_number, execution_number, number_incomplete_classes):
    csv_row = [percentage_number] + test1.populate_csv_row(
        consolidated_statistics, execution_number, number_incomplete_classes)
    return csv_row


def create_statistics_csv_output_t2(ontology_dataclass_list, consolidated_statistics, test_results_folder,
                                    file_name, percentage_number, execution_number):
    csv_header = create_csv_header()
    number_incomplete_classes = test1.calculate_incompleteness_values(ontology_dataclass_list)
    csv_row = populate_csv_row(consolidated_statistics, percentage_number, execution_number, number_incomplete_classes)
    statistics = os.path.join(test_results_folder,
                              f"statistics{file_name[:-4]}_ex{execution_number:03d}_pc{percentage_number:03d}.csv")
    test1.write_csv_row(statistics, csv_header, csv_row)
