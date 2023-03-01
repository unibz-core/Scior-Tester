from typing import Final

from decouple import config

SOFTWARE_ACRONYM = "Scior Tester"
SOFTWARE_NAME = "Tester for the Identification of Ontological Categories for OWL Ontologies"
SOFTWARE_VERSION = "0.22.11.25"
SOFTWARE_URL = "https://github.com/unibz-core/Scior-Tester"

NAMESPACE_GUFO = "http://purl.org/nemo/gufo#"
NAMESPACE_TAXONOMY = "http://taxonomy.model/"

CLASSES_DATA_FILE_NAME = "data"
HASH_FILE_NAME = "hash_sha256_register.csv"
BLOCK_SIZE = 65536

EXCEPTIONS_LIST = ["van-ee2021modular"]

"""
------------------------------------------------------------
Constants
------------------------------------------------------------
"""
CATALOG_FOLDER: Final[str] = config("CATALOG_FOLDER")
AUTOMATIC: Final[bool] = bool(config("AUTOMATIC"))
COMPLETE: Final[bool] = bool(config("COMPLETE"))

"""
------------------------------------------------------------
TEST_2 constants
------------------------------------------------------------
"""

MINIMUM_ALLOWED_NUMBER_CLASSES: Final[int] = int(config("MINIMUM_ALLOWED_NUMBER_CLASSES"))
PERCENTAGE_INITIAL: Final[int] = int(config("PERCENTAGE_INITIAL"))
PERCENTAGE_FINAL: Final[int] = int(config("PERCENTAGE_FINAL"))
PERCENTAGE_RATE: Final[int] = int(config("PERCENTAGE_RATE"))
NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE: Final[int] = \
    int(config("NUMBER_OF_EXECUTIONS_PER_DATASET_PER_PERCENTAGE"))
