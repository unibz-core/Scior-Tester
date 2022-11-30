""" Functions related to stereotypes. """

from rdflib import URIRef, RDF

from src.modules.build.build_taxonomy_files import clean_class_name
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely

VOCABULARY_CLASS_URI = URIRef("https://purl.org/ontouml-models/vocabulary/Class")
VOCABULARY_GENERALIZATION_URI = URIRef("https://purl.org/ontouml-models/vocabulary/Generalization")
VOCABULARY_GENERAL_URI = URIRef("https://purl.org/ontouml-models/vocabulary/general")
VOCABULARY_SPECIFIC_URI = URIRef("https://purl.org/ontouml-models/vocabulary/specific")
VOCABULARY_NAME_URI = URIRef("https://purl.org/ontouml-models/vocabulary/name")
VOCABULARY_STEREOTYPE_URI = URIRef("https://purl.org/ontouml-models/vocabulary/stereotype")


def get_gufo_stereotype(class_stereotype_original):
    """ Mapps OntoUML serialization in OWL stereotype for the gUFO types used in OntCatOWL """

    if class_stereotype_original == "category":
        mapped_stereotype = "category"
    elif (class_stereotype_original == "collective") or (class_stereotype_original == "kind") or (
            class_stereotype_original == "quality") or (class_stereotype_original == "quantity") or (
            class_stereotype_original == "mode") or (class_stereotype_original == "relator"):
        mapped_stereotype = "kind"
    elif class_stereotype_original == "mixin":
        mapped_stereotype = "mixin"
    elif class_stereotype_original == "phase":
        mapped_stereotype = "phase"
    elif class_stereotype_original == "phasemixin":
        mapped_stereotype = "phasemixin"
    elif class_stereotype_original == "role" or class_stereotype_original == "historicalrole":
        mapped_stereotype = "role"
    elif class_stereotype_original == "rolemixin" or class_stereotype_original == "historicalrolemixin":
        mapped_stereotype = "rolemixin"
    elif class_stereotype_original == "subkind":
        mapped_stereotype = "subkind"
    else:
        mapped_stereotype = "other"

    return mapped_stereotype


def collect_stereotypes_classes_information(catalog_path, dataset_classes_information, dataset, catalog_size, current):
    """ Read all classes information related to stereotypes and updates the catalog_information. """

    logger = initialize_logger()

    source_owl_file_path = catalog_path + "\\" + dataset + "\\" + "ontology.ttl"
    ontology_graph = load_graph_safely(source_owl_file_path)

    for owl_class in ontology_graph.subjects(RDF.type, VOCABULARY_CLASS_URI):

        # Getting classes' names
        class_name = ontology_graph.value(owl_class, VOCABULARY_NAME_URI)
        class_name = class_name.n3()[1:-(len(class_name.language) + 2)]
        class_name = clean_class_name(class_name)

        if class_name != "string" and class_name != "int" and class_name != "char":

            # Getting classes' stereotypes
            class_stereotype_original = ontology_graph.value(owl_class, VOCABULARY_STEREOTYPE_URI)

            if class_stereotype_original == None:
                class_stereotype_original_string = "none"
                class_stereotype_gufo = "other"
            else:
                class_stereotype_original_string = class_stereotype_original.n3()[44:-1]
                class_stereotype_original_string = class_stereotype_original_string.lower().strip()
                class_stereotype_gufo = get_gufo_stereotype(class_stereotype_original_string)

            for class_in_list in dataset_classes_information:
                if class_in_list.name == class_name:
                    class_in_list.stereotype_original = class_stereotype_original_string
                    class_in_list.stereotype_gufo = class_stereotype_gufo

    logger.info(f"Stereotypes information {current}/{catalog_size} collected from dataset {dataset}")
