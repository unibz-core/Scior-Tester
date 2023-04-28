""" Functions related to stereotypes. """
import os.path

from rdflib import RDF, URIRef

from src import NAMESPACE_GUFO
from src.modules.build import VOCABULARY_CLASS_URI, VOCABULARY_NAME_URI, VOCABULARY_STEREOTYPE_URI
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely


def clean_class_name(class_raw_name: str) -> str:
    """
    Clears class name from unnecessary chars
    :param class_raw_name: Class name as read from model
    :return: Class name after removing invalid characters
    """

    class_clean_name = class_raw_name.strip()
    class_clean_name = class_clean_name.replace(",", "_")
    class_clean_name = class_clean_name.replace("  ", " ")
    class_clean_name = class_clean_name.replace(" ", "_")
    class_clean_name = class_clean_name.replace("\n", "_")
    class_clean_name = class_clean_name.replace("\"\"", "_")
    class_clean_name = class_clean_name.replace("<", "_")
    class_clean_name = class_clean_name.replace(">", "_")

    return class_clean_name


def get_gufo_classification(class_stereotype_original):
    """ Maps OntoUML serialization in OWL stereotype for the gUFO types used in Scior """

    # Cleaning possible incorrect parameter string
    class_stereotype_original = class_stereotype_original.lower()
    class_stereotype_original = class_stereotype_original.strip()

    keeped_stereotypes = ("category", "mixin", "phase", "phasemixin", "kind", "subkind", "role", "rolemixin")
    if class_stereotype_original in keeped_stereotypes:
        return class_stereotype_original

    mapped_classification = {"collective": "kind", "quality": "kind", "quantity": "kind", "mode": "kind",
                             "relator": "kind", "historicalrole": "role", "historicalrolemixin": "rolemixin"}
    if class_stereotype_original in mapped_classification:
        return mapped_classification[class_stereotype_original]

    return "other"


def get_gufo_classification_supertypes(gufo_classification):
    """ Receives a gUFO classification and returns a list of all gUFO classifications (including itself)
    that are supertypes of it.  """

    gufo_supertypes_dict = {
        "antirigidtype": ["antirigidtype", "nonrigidtype"],
        "category": ["category", "rigidtype", "nonsortal"],
        "kind": ["kind", "rigidtype", "sortal"],
        "mixin": ["mixin", "semirigidtype", "nonrigidtype", "nonsortal"],
        "nonrigidtype": ["nonrigidtype"],
        "nonsortal": ["nonsortal"],
        "phase": ["phase", "antirigidtype", "nonrigidtype", "sortal"],
        "phasemixin": ["phasemixin", "antirigidtype", "nonrigidtype", "nonsortal"],
        "rigidtype": ["rigidtype"],
        "role": ["role", "antirigidtype", "nonrigidtype", "sortal"],
        "rolemixin": ["rolemixin", "antirigidtype", "nonrigidtype", "nonsortal"],
        "semirigidtype": ["semirigidtype", "nonrigidtype"],
        "sortal": ["sortal"],
        "subkind": ["subkind", "rigidtype", "sortal"]
    }

    return gufo_supertypes_dict[gufo_classification]


def return_gufo_classification_uri(simple_classification: str) -> URIRef:
    """ Receives a str with a lowercase gUFO classification and returns the corresponding gUFO classification URIRef"""

    logger = initialize_logger()

    classification_dictionary = {
        "antirigidtype": "AntiRigidType",
        "aspect": "Aspect",
        "category": "Category",
        "collection": "Collection",
        "endurant": "Endurant",
        "enduranttype": "EndurantType",
        "extrinsicaspect": "ExtrinsicAspect",
        "extrinsicmode": "ExtrinsicMode",
        "fixedcollection": "FixedCollection",
        "functionalcomplex": "FunctionalComplex",
        "intrinsicaspect": "IntrinsicAspect",
        "intrinsicmode": "IntrinsicMode",
        "kind": "Kind",
        "mixin": "Mixin",
        "nonrigidtype": "NonRigidType",
        "nonsortal": "NonSortal",
        "object": "Object",
        "phase": "Phase",
        "phasemixin": "PhaseMixin",
        "quality": "Quality",
        "quantity": "Quantity",
        "relator": "Relator",
        "rigidtype": "RigidType",
        "role": "Role",
        "rolemixin": "RoleMixin",
        "semirigidtype": "SemiRigidType",
        "sortal": "Sortal",
        "subkind": "SubKind",
        "variablecollection": "VariableCollection"
    }

    if simple_classification in classification_dictionary:
        return URIRef(NAMESPACE_GUFO + classification_dictionary[simple_classification])
    else:
        logger.error(f"Unexpected classification {simple_classification}. URIRef cannot be returned. Program aborted!")
        exit(1)


def collect_stereotypes_classes_information(source_owl_file_path, dataset_classes_information, catalog_size, current):
    """ Read all classes information related to stereotypes and updates the catalog_information
        :param source_owl_file_path: full path to *.ttl file
        :param dataset_classes_information:
        :param catalog_size: size of the whole catalog
        :param current: number of current dataset
    """

    logger = initialize_logger()

    ontology_graph = load_graph_safely(source_owl_file_path)

    class_inf = {}
    for owl_class in ontology_graph.subjects(RDF.type, VOCABULARY_CLASS_URI):

        # Getting classes' names
        class_name = ontology_graph.value(owl_class, VOCABULARY_NAME_URI)
        class_name = class_name.n3()[1:-(len(class_name.language) + 2)]
        class_name = clean_class_name(class_name)

        class_stereotype_original = None
        if class_name != "string" and class_name != "int" and class_name != "char":
            # Getting classes' stereotypes
            class_stereotype_original = ontology_graph.value(owl_class, VOCABULARY_STEREOTYPE_URI)

        class_stereotype_original_string = "none"
        class_stereotype_gufo = "other"
        if class_stereotype_original:
            class_stereotype_original_string = class_stereotype_original.n3().split("#")[-1][:-1]
            class_stereotype_original_string = class_stereotype_original_string.lower().strip()
            class_stereotype_gufo = get_gufo_classification(class_stereotype_original_string)

        class_inf[class_name] = (class_stereotype_original_string, class_stereotype_gufo)

    for sublist in dataset_classes_information:
        for class_in_list in sublist:
            if class_in_list.name in class_inf:
                class_in_list.stereotype_original = class_inf[class_in_list.name][0]
                class_in_list.stereotype_gufo = class_inf[class_in_list.name][1]

    dataset = source_owl_file_path.split(os.path.sep)[-2]
    logger.info(f"Stereotypes information {current}/{catalog_size} collected from dataset {dataset}")
