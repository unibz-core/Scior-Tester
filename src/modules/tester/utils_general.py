""" General auxiliary functions. """
import os
import csv

from datetime import datetime


def remove_duplicates(input_list):
    """ Remove duplicated elements from a list. """

    return [*set(input_list)]


def lists_subtraction(list1, list2):
    """ Returns the subtraction between two lists. """

    return list(set(list1) - set(list2))


def get_date_time():
    """ Return a string in a specified format with date and time.
    Format example: 2022.10.23-14.43
    """

    now = datetime.now()
    return now.strftime("%Y.%m.%d-%H.%M.%S")


def write_csv_row(file_name, header_row, row):
    if os.path.exists(file_name):
        with open(file_name, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    else:
        with open(file_name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)
            writer.writerow(row)


def write_dictionary(file_name, keys, register):
    if os.path.exists(file_name):
        with open(file_name, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writerow(register)
    else:
        with open(file_name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerow(register)
