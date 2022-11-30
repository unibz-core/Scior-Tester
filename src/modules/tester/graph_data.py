""" Initialization of node lists """
from rdflib import RDFS, RDF, OWL

from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_graph import get_list_root_classes, get_list_leaf_classes , get_list_of_all_classes






def lists_subtraction(list1, list2):
    """ Returns the subtraction between two lists. """

    list3 = list(set(list1) - set(list2))

    return list3


def generates_nodes_lists(ontology_graph):
    """ Return lists of different types of classes (string with the class URI) for the ontologies ontology to be used
        in other functions. This lists of classes must be initializated and, after that, not be edited anymore.
    """
    logger = initialize_logger()
    logger.debug("Initializing list of Taxonomy nodes...")

    prefixed_node_list = {"all": [], "roots": [], "leaves": []}

    prefixed_node_list["all"] = get_list_of_all_classes(ontology_graph)
    prefixed_node_list["roots"] = get_list_root_classes(ontology_graph, prefixed_node_list["all"])
    prefixed_node_list["leaves"] = get_list_leaf_classes(ontology_graph, prefixed_node_list["all"])

    logger.debug("List of Taxonomy nodes successfully initialized.")

    return prefixed_node_list
