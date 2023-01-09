from decouple import config
from typing import Final

SOFTWARE_ACRONYM = "Scior Tester"
SOFTWARE_NAME = "Tester for the Identification of Ontological Categories for OWL Ontologies"
SOFTWARE_VERSION = "0.22.11.25"
SOFTWARE_URL = "https://github.com/unibz-core/Scior-Tester"

NAMESPACE_GUFO = "http://purl.org/nemo/gufo#"
NAMESPACE_TAXONOMY = "http://taxonomy.model/"

CLASSES_DATA_FILE_NAME = "data"
HASH_FILE_NAME = "hash_sha256_register.csv"
BLOCK_SIZE = 65536

EXCEPTIONS_LIST = [
    "ahmad2018aviation",
    "chartered-service",
    "cmpo2017",
    "debbech2019gosmo",
    "debbech2020dysfunction-analysis",
    "dpo2017",
    "duarte2018osdef",
    "duarte2018reqon",
    "duarte2021ross",
    "experiment2013",
    "gailly2016value",
    "guizzardi2014nfr",
    "lindeberg2022simple-ontorights",
    "mello2022monotheism",
    "pereira2020ontotrans",
    "quality-assurance-process-ontology2017",
    "richetti2019tdecision",
    "rodrigues2019ontocrime",
    "saleme2019mulseonto",
    "spmo2017",
    "spo2017",
    "swo2016",
    "van-ee2021modular",
    "zhou2017hazard",
    "zhou2017hazard-ontology-robotic-strolling",
    "zhou2017hazard-ontology-train-control"
]

CATALOG_FOLDER: Final[str] = config("CATALOG_FOLDER")

"""
------------------------------------------------------------
TEST_1 constants
------------------------------------------------------------
"""
TEST1_AUTOMATIC: Final[bool] = bool(config("TEST1_AUTOMATIC"))
TEST1_COMPLETE: Final[bool] = bool(config("TEST1_COMPLETE"))

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
