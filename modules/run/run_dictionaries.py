""" Baseline dictionary definition. """
import csv
import pathlib


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
