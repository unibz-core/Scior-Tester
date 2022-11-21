""" Initialization of node lists """
from rdflib import RDFS, RDF, OWL

from modules.logger_config import initialize_logger
from modules.utils_graph import get_list_root_classes, get_list_leaf_classes


def get_list_root_classes(graph, all_classes):
    """ Returns a list without repetitions with the URI of all root classes in a graph.
        Root classes are:  (1) classes that (2) have no SUPERclasses besides owl:Thing.
        Isolated classes are both root and leaf at the same time.
    """

    # List of all entities that have a rdfs:subClassOf property with other entity (participating as source)
    cond2 = []
    for subj, pred, obj in graph.triples((None, RDFS.subClassOf, None)):
        cond2.append(subj.n3()[1:-1])

    list_root_classes = lists_subtraction(all_classes, cond2)

    return list_root_classes


def get_list_leaf_classes(graph, all_classes):
    """ Returns a list without repetitions with the URI of all leaf classes in a graph.
        Leaf classes are:  (1) classes that (2) have no SUBclasses.
        Isolated classes are both root and leaf nodes at the same time.
    """

    # List of all entities that have a rdfs:subClassOf property with other entity (participating as target)
    cond2 = []
    for subj, pred, obj in graph.triples((None, RDFS.subClassOf, None)):
        cond2.append(obj.n3()[1:-1])

    list_leaf_nodes = lists_subtraction(all_classes, cond2)

    return list_leaf_nodes


def lists_subtraction(list1, list2):
    """ Returns the subtraction between two lists. """

    list3 = list(set(list1) - set(list2))

    return list3


def get_list_all_classes(ontology_graph, exceptions_list=None):
    """ Returns a list of all classes as URI strings without repetitions available in a Graph.
        Classes that have namespaces included in the exception_list parameter are not included in the returned list.
    """

    if exceptions_list == None:
        exceptions_list = []

    classes_list = []

    for sub, pred, obj in ontology_graph:
        if (sub, RDF.type, OWL.Class) in ontology_graph:
            # Eliminating BNodes
            if type(sub).__name__ != "BNode":
                # N3 necessary for returning string and [1:-1] necessary for removing <>
                classes_list.append(sub.n3()[1:-1])
        if (obj, RDF.type, OWL.Class) in ontology_graph:
            # Eliminating BNodes
            if type(obj).__name__ != "BNode":
                # N3 necessary for returning string and [1:-1] necessary for removing <>
                classes_list.append(obj.n3()[1:-1])

    # Removing repetitions
    no_rep_classes_list = [*set(classes_list)]

    # Removing classes that have namespace in the exceptions_list
    classes_list = no_rep_classes_list.copy()
    for class_uri in no_rep_classes_list:
        for exception_item in exceptions_list:
            if class_uri.startswith(exception_item):
                classes_list.remove(class_uri)
                break

    return classes_list


def generates_nodes_lists(ontology_graph):
    """ Return lists of different types of classes (string with the class URI) for the ontologies ontology to be used
        in other functions. This lists of classes must be initializated and, after that, not be edited anymore.
    """
    logger = initialize_logger()
    logger.debug("Initializing list of Taxonomy nodes...")

    prefixed_node_list = {"all": [], "roots": [], "leaves": []}

    prefixed_node_list["all"] = get_list_all_classes(ontology_graph)
    prefixed_node_list["roots"] = get_list_root_classes(ontology_graph, prefixed_node_list["all"])
    prefixed_node_list["leaves"] = get_list_leaf_classes(ontology_graph, prefixed_node_list["all"])

    logger.debug("List of Taxonomy nodes successfully initialized.")

    return prefixed_node_list
