""" Auxiliary functions for extending and complementing RDFLib's RDF treatment functions """
import time

from owlrl import DeductiveClosure, RDFS_Semantics
from rdflib import RDF, OWL, Graph

from src.modules.tester.logger_config import initialize_logger


def load_graph_safely(ontology_file):
    """ Safely load graph from file to working memory. """

    logger = initialize_logger()

    ontology_graph = Graph()
    try:
        ontology_graph.parse(ontology_file, encoding='utf-8')
    except OSError as error:
        logger.error(f"Could not load {ontology_file} file. Exiting program.\n"
                     f"Reported system error: {error}")
        exit(1)

    logger.debug(f"Ontology file {ontology_file} successfully loaded to working memory.")

    return ontology_graph


"""
---------------------------------------------------
The rest of the functions are not used anywhere
---------------------------------------------------
"""


def has_prefix(ontology_graph, prefix) -> bool:
    """ Return boolean indicating if the argument prefix exists in the graph"""

    for pre, nam in ontology_graph.namespaces():
        if prefix == pre:
            return True

    return False


def has_namespace(ontology_graph, namespace) -> bool:
    """ Return boolean indicating if the argument namespace exists in the graph.
        The argument namespace must be provided without the surrounding <>"""

    for pre, nam in ontology_graph.namespaces():
        if namespace == nam.n3()[1:-1]:
            return True

    return False


def list_prefixes(ontology_graph):
    """ Return a list of all prefixes in the graph"""

    return [pre for pre, _ in ontology_graph.namespaces()]


def list_namespaces(ontology_graph):
    """ Return a list of all namespaces in the graph without the surrounding <>"""

    return [nam.n3()[1:-1] for _, nam in ontology_graph.namespaces()]


def get_ontology_uri(ontology_graph):
    """ Return the URI of the ontology graph. """

    return ontology_graph.value(predicate=RDF.type, object=OWL.Ontology)


def perform_reasoning(ontology_graph):
    """Perform reasoner and consequently expands the ontology graph. """

    logger = initialize_logger()

    logger.info("Initializing RDFS reasoning. This may take a while...")

    st = time.perf_counter()
    DeductiveClosure(RDFS_Semantics).expand(ontology_graph)
    et = time.perf_counter()
    elapsed_time = round((et - st), 4)

    logger.info(f"Reasoning process completed in {elapsed_time} seconds.")
