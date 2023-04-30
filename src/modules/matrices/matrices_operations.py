""" Defines functions that will be used to calculate the final resulting average matrices. """
import csv
import glob

from scior.modules.results.classifications_matrix import generate_empty_matrix

from src.modules.tester.logger_config import initialize_logger

LOGGER = initialize_logger()


def load_matrix_from_csv(file_path: str) -> list[list]:
    """ Receives a file path that contains a matrix in csv format, reads it and returns as a matrix. """

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        data_as_list = list(reader)

    return data_as_list


def normalize_matrix(matrix: list[list]) -> list[list]:
    """ Receives a matrix with raw values and returns percentages. """

    matrix_size_rows = len(matrix)
    matrix_size_columns = len(matrix[0])

    number_elements = 0
    row_position = 0

    # Counting number of elements
    while row_position < matrix_size_rows:
        column_position = 0
        while column_position < matrix_size_columns:
            number_elements += int(matrix[row_position][column_position])
            column_position += 1
        row_position += 1

    # Normalizing
    row_position = 0
    while row_position < matrix_size_rows:
        column_position = 0
        while column_position < matrix_size_columns:
            matrix[row_position][column_position] = int(matrix[row_position][column_position]) / number_elements
            column_position += 1
        row_position += 1

    return matrix


def adds_two_matrices(matrix_a: list[list], matrix_b: list[list]) -> list[list]:
    """ Receives two matrices and adds their elements, returning a single added matrix.
        The matrices must have the same size.
    """

    matrix_size_rows = len(matrix_a)
    matrix_size_columns = len(matrix_a[0])

    resulting_matrix = generate_empty_matrix(matrix_size_rows)

    row_position = 0
    while row_position < matrix_size_rows:
        column_position = 0
        while column_position < matrix_size_columns:
            resulting_matrix[row_position][column_position] = \
                matrix_a[row_position][column_position] + matrix_b[row_position][column_position]
            column_position += 1
        row_position += 1

    return resulting_matrix


def calculate_resulting_matrix(test_type: bool, matrix_type: str, test_number:str) -> list[list]:
    """ Receives information about the test and matrix type and calculate the final average matrix. """

    test_type_info = "CWA" if test_type else "OWA"
    test_type = "c" if test_type else "n"

    if matrix_type == "class":
        matrix_type_info = "Classifications"
    elif matrix_type == "leaves":
        matrix_type_info = "Leaves"
    else:
        LOGGER.error("Unknown matrix type. Program aborted.")
        exit(1)

    # get all matrix files for the received argument test
    list_all_matrix_files = glob.glob(f'./catalog/**/**/**/{matrix_type}_matrix_*_a{test_type}_{test_number}*.csv')

    LOGGER.info(f"Generating {matrix_type_info} for {test_type_info} using {len(list_all_matrix_files)} files.")

    list_normalized_matrices = []

    for matrix_file_path in list_all_matrix_files:
        loaded_matrix = load_matrix_from_csv(matrix_file_path)
        list_normalized_matrices.append(normalize_matrix(loaded_matrix))

    resulting_matrix = generate_empty_matrix(len(list_normalized_matrices[0]))

    for matrix in list_normalized_matrices:
        resulting_matrix = adds_two_matrices(resulting_matrix, matrix)

    final_matrix = normalize_matrix(resulting_matrix)

    return final_matrix
