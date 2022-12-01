""" Auxiliary functions for extending and complementing RDFLib's graph functions """
from rdflib import RDFS, URIRef, RDF, OWL

from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import remove_duplicates, lists_subtraction


def get_superclasses(graph, all_classes, element: str):
    """ Returns a list of all direct superclasses of the given element of a graph.
        Analogous to function get_subclasses.
    """

    elem = URIRef(element)
    superclasses = []

    for obj in graph.objects(elem, RDFS.subClassOf):
        ins = obj.n3()[1:-1]
        if ins in all_classes:
            superclasses.append(ins)

    return superclasses


def get_subclasses(graph, all_classes, element: str):
    """ Returns a list of all direct subclasses of the given element of a graph.
        Analogous to function get_superclasses.
    """

    elem = URIRef(element)
    subclasses = []

    for subj in graph.subjects(RDFS.subClassOf, elem):
        ins = subj.n3()[1:-1]
        if ins in all_classes:
            subclasses.append(ins)

    return subclasses


def get_list_root_classes(graph, all_classes):
    """ Returns a list without repetitions with the URI of all root classes in a graph.
        Root classes are:  (1) classes that (2) have no SUPERclasses besides owl:Thing.
        Isolated classes are both root and leaf at the same time.
    """

    # List of all entities that have a rdfs:subclass property with other entity (participating as source)
    cond2 = [subj.n3()[1:-1] for subj, _, _ in graph.triples((None, RDFS.subClassOf, None))]

    list_root_classes = lists_subtraction(all_classes, cond2)

    return list_root_classes


def get_list_leaf_classes(graph, all_classes):
    """ Returns a list without repetitions with the URI of all leaf classes in a graph.
        Leaf classes are:  (1) classes that (2) have no SUBclasses.
        Isolated classes are both root and leaf nodes at the same time.
    """

    # List of all entities that have a rdfs:subclass property with other entity (participating as target)
    cond2 = [obj.n3()[1:-1] for _, _, obj in graph.triples((None, RDFS.subClassOf, None))]

    list_leaf_nodes = lists_subtraction(all_classes, cond2)

    return list_leaf_nodes


def get_list_of_all_classes(ontology_graph, exceptions_list: list = []):
    """ Returns a list of all classes as URI strings without repetitions available in a Graph.
        Classes that have namespaces included in the exception_list parameter are not included in the returned list. """

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
    no_rep_classes_list = remove_duplicates(classes_list)

    # Removing classes that have namespace in the exceptions_list
    classes_list = [x for x in no_rep_classes_list if not any(x.startswith(y) for y in exceptions_list)]
    return classes_list


def get_all_superclasses(graph, nodes_list, element):
    """ Return list of all nodes of the given graph that are direct or indirect superclasses of the given element.
        The return list DOES NOT include the own element.
        Analogous to function get_all_subclasses.
    """

    all_superclasses = []
    superclasses = get_superclasses(graph, nodes_list["all"], element)

    for sc in superclasses:
        all_superclasses.append(sc)
        if sc not in nodes_list["roots"]:
            temp = get_all_superclasses(graph, nodes_list, sc)
            all_superclasses.extend(temp)

    return remove_duplicates(all_superclasses)


def get_all_subclasses(graph, nodes_list, element):
    """ Return list of all nodes of the given graph that are direct or indirect subclasses of the given element.
        The return list DOES NOT include the own element.
        Analogous to function get_all_superclasses.
    """

    all_subclasses = []
    subclasses = get_subclasses(graph, nodes_list["all"], element)

    for sc in subclasses:
        all_subclasses.append(sc)
        if subclasses not in nodes_list["leaves"]:
            temp = get_all_subclasses(graph, nodes_list, sc)
            all_subclasses.extend(temp)

    return remove_duplicates(all_subclasses)


def _get_all_related_nodes(graph, nodes_list, node, visited):
    """ Implements the BFS algorithm to return the list of all nodes of the given graph that are directly or indirectly
        related to the given element. I.e., return all nodes that are reachable from the ontology's node (element).
        The return list DOES INCLUDE the own element.
    """
    if not visited:
        visited = []

    neighbours = get_subclasses(graph, nodes_list["all"], node) + get_superclasses(graph, nodes_list["all"], node)
    visited.append(node)

    while neighbours:
        neighbour = neighbours.pop(0)
        if neighbour not in visited:
            neighbours.extend(_get_all_related_nodes(graph, nodes_list, neighbour, visited))

    return visited


def get_all_related_nodes(graph, nodes_list, node):
    """ Return the list of all nodes of the given graph that are directly or indirectly
        related to the given element. I.e., return all nodes that are reachable from the ontology's node (element).

        The return list DOES NOT INCLUDE the element itself.
    """

    return _get_all_related_nodes(graph, nodes_list, node, None)[1:]


def generates_nodes_lists(graph) -> dict:
    """ Return lists of different types of classes (string with the class URI) for the ontologies ontology to be used
        in other functions. This lists of classes must be initializated and, after that, not be edited anymore.
    """
    logger = initialize_logger()
    logger.debug("Initializing list of Taxonomy nodes...")

    prefixed_node_list = {"all": get_list_of_all_classes(graph), "roots": [], "leaves": []}
    prefixed_node_list["roots"] = get_list_root_classes(graph, prefixed_node_list["all"])
    prefixed_node_list["leaves"] = get_list_leaf_classes(graph, prefixed_node_list["all"])

    logger.debug("List of Taxonomy nodes successfully initialized.")

    return prefixed_node_list


"""
---------------------------------------------------
The rest of the functions are not used anywhere
---------------------------------------------------
"""


def get_related(graph, nodes_list, element, _type: str):
    related = []
    scs = get_superclasses(graph, nodes_list["all"], element) if _type == "roots" else \
          get_subclasses(graph, nodes_list["all"], element)

    for sc in scs:
        if sc in nodes_list[_type]:
            related.append(sc)
        else:
            temp = get_related(graph, nodes_list, sc, _type)
            related.extend(temp)

    related = remove_duplicates(related)
    return related


def get_related_roots(graph, nodes_list, element):
    """ Return list of all roots of the given graph that are (in)directly related to the given element."""
    return get_related(graph, nodes_list, element, "roots")


def get_related_leaves(graph, nodes_list, element):
    """ Return list of all leaves of the given graph that are (in)directly related to the given element."""
    return get_related(graph, nodes_list, element, "leaves")
