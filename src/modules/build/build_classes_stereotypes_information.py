""" Functions related to stereotypes. """

from rdflib import RDF

from src.modules.build import *
from src.modules.build.build_taxonomy_files import clean_class_name
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely


def get_gufo_stereotype(class_stereotype_original):
    """ Mapps OntoUML serialization in OWL stereotype for the gUFO types used in OntCatOWL """

    keeped_stereotypes = ("category", "mixin", "phase", "phasemixin", "kind", "subkind", "role", "rolemixin")
    if class_stereotype_original in keeped_stereotypes:
        return class_stereotype_original

    mapped_stereotypes = {"collective": "kind", "quality": "kind", "quantity": "kind", "mode": "kind",
                          "relator": "kind", "historicalrole": "role", "historicalrolemixin": "rolemixin"}
    if class_stereotype_original in mapped_stereotypes:
        return mapped_stereotypes[class_stereotype_original]

    return "other"


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

        if class_name != "string" and class_name != "int" and class_name != "char":
            # Getting classes' stereotypes
            class_stereotype_original = ontology_graph.value(owl_class, VOCABULARY_STEREOTYPE_URI)

            if not class_stereotype_original:
                class_stereotype_original_string = "none"
                class_stereotype_gufo = "other"
            else:
                class_stereotype_original_string = class_stereotype_original.n3()[44:-1]
                class_stereotype_original_string = class_stereotype_original_string.lower().strip()
                class_stereotype_gufo = get_gufo_stereotype(class_stereotype_original_string)

            class_inf[class_name] = (class_stereotype_original_string, class_stereotype_gufo)

    for sublist in dataset_classes_information:
        for class_in_list in sublist:
            if class_in_list.name in class_inf:
                class_in_list.stereotype_original = class_inf[class_in_list.name][0]
                class_in_list.stereotype_gufo = class_inf[class_in_list.name][1]

    dataset = source_owl_file_path.split("\\")[-2]
    logger.info(f"Stereotypes information {current}/{catalog_size} collected from dataset {dataset}")
