""" General auxiliary functions. """
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


"""
---------------------------------------------------
The rest of the functions are not used anywhere
---------------------------------------------------
"""


def has_duplicates(input_list) -> bool:
    """ Check if given list contains any duplicated element """
    return len(input_list) != len(set(input_list))


def lists_intersection(list1, list2):
    """ Returns the intersection of two lists. """
    temp = set(list2)
    list3 = [value for value in list1 if value in temp]
    return list3
