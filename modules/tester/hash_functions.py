""" Functions for registering hashes informations for all generated files. """
import csv
import hashlib
import os
import pathlib

from modules.tester.logger_config import initialize_logger

HASH_FILE_LOCATION = "\\catalog\\hash_sha256_register.csv"


def generate_sha256_hash(file_path):
    """ Receives the complete path of a file and returns its sha256 hash. """

    # The size of each read from the file. Prevents memory overload.
    BLOCK_SIZE = 65536

    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()


def create_hash_sha256_register_file_csv():
    """ If it doesn't exist, creates a new csv file for mapping sha256 hashes fo the original files to all
    generated files. """

    logger = initialize_logger()

    hash_register_file_path = str(pathlib.Path().resolve()) + HASH_FILE_LOCATION

    if not os.path.exists(hash_register_file_path):
        try:
            with open(hash_register_file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["file_name", "file_hash", "source_file_name", "source_file_hash"])
        except OSError:
            logger.error(f"Hash file could not be created in {hash_register_file_path}. Program aborted.")
            exit(1)
        else:
            logger.debug(f"New hash file successfully created in {hash_register_file_path}.")
    else:
        logger.debug(f"Hash file already exists in {hash_register_file_path}.")


def verify_hash_register_exist(generated_file_path):
    """ Checks if a generated file is already registered in the hash register and returns True or False.

    Hash file registers are structured in a csv with columns:
    ["file_name", "file_hash", "source_file_name", "source_file_hash"]
        - "file_path": path of the registered file
        - "file_hash": sha256 hash of the registered file
        - "file_path": path of the file from which the registered file was generated
        - "source_file_hash": sha256 hash of the file from which the registered file was generated.
    """

    hash_register_file_path = str(pathlib.Path().resolve()) + HASH_FILE_LOCATION
    file_hash = generate_sha256_hash(generated_file_path)

    with open(hash_register_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        registered_hashes_list = []
        for row in csv_reader:
            registered_hashes = row[1]
            registered_hashes_list.append(registered_hashes)

    if file_hash in registered_hashes_list:
        exists = True
    else:
        exists = False

    return exists


def write_sha256_hash_register(source_file_path, generated_file_path, hash_register_file_path):
    """ Creates a new entry in the hash register file. """

    logger = initialize_logger()

    generated_file_hash = generate_sha256_hash(generated_file_path)
    source_file_hash = generate_sha256_hash(source_file_path)
    entry = [generated_file_path, generated_file_hash, source_file_path, source_file_hash]

    try:
        with open(hash_register_file_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(entry)
    except OSError as e:
        logger.error(
            f"Hash file could not be created in {hash_register_file_path}. Program aborted.\nSystem error reported: {e}")
        exit(1)


def register_sha256_hash_information(generated_file_path, source_file_path):
    """ Register the hash of the generated file source for tracking purposes. """

    logger = initialize_logger()

    hash_register_file_path = str(pathlib.Path().resolve()) + HASH_FILE_LOCATION

    if verify_hash_register_exist(generated_file_path):
        logger.debug(f"File {source_file_path} already registered in hash register file.")
    else:
        write_sha256_hash_register(source_file_path, generated_file_path, hash_register_file_path)
        logger.debug(f"New hash entry successfully created in {hash_register_file_path}.")
