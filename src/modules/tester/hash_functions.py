""" Functions for registering hashes information for all generated files. """
import csv
import hashlib
import os
import pandas as pd

from src import BLOCK_SIZE
from src.modules.tester.logger_config import initialize_logger


def generate_sha256_hash(file_path):
    """ Receives the complete path of a file and returns its sha256 hash. """

    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()


def write_sha256_hash_register(hash_register, hash_register_file_path):
    """ Writes into hash register file. """

    logger = initialize_logger()

    try:
        hash_register.to_csv(hash_register_file_path, mode="a", index=False)
    except OSError as e:
        logger.error(f"Hash file could not be created in {hash_register_file_path}. Program aborted.\n"
                     f"System error reported: {e}")
        exit(1)


def register_sha256_hash_information(hash_register, generated_file_path, source_file_path):
    """ Register the hash of the generated file source for tracking purposes. """

    logger = initialize_logger()

    generated_file_hash = generate_sha256_hash(generated_file_path)

    if generated_file_hash in hash_register["file_hash"].values:
        logger.debug(f"File {source_file_path} already registered in hash register file.")
    else:
        source_file_hash = generate_sha256_hash(source_file_path)
        entry = {'file_name': [generated_file_path],
                 'file_hash': [generated_file_hash],
                 'source_file_name': [source_file_path],
                 'source_file_hash': [source_file_hash]}
        hash_register = pd.concat([hash_register, pd.DataFrame.from_dict(entry)])

    logger.debug(f"New hash entry for {generated_file_hash} successfully created.")
    return hash_register
