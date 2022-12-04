""" Main module  for OntCatOWL """

from rdflib import RDFS, RDF

from modules.ontcatowl.modules.dataclass_verifications import verify_all_ontology_dataclasses_consistency
from modules.ontcatowl.modules.initialization_data_graph import initialize_nodes_lists
from modules.ontcatowl.modules.initialization_data_gufo_dictionary import initialize_gufo_dictionary
from modules.ontcatowl.modules.initialization_data_ontology_dataclass import initialize_ontology_dataclasses, \
    load_known_gufo_information
from modules.ontcatowl.modules.logger_config import initialize_logger
from modules.ontcatowl.modules.results_calculation import generates_partial_statistics_list, calculate_final_statistics
from modules.ontcatowl.modules.rules_types_run import execute_rules_types
from modules.ontcatowl.modules.utils_rdf import load_graph_safely_considering_restrictions

SOFTWARE_ACRONYM = "OntCatOWL - tester ready version"
SOFTWARE_NAME = "Identification of Ontological Categories for OWL Ontologies - tester ready version"
SOFTWARE_VERSION = "0.22.11.21"
SOFTWARE_URL = "https://github.com/unibz-core/OntCatOWL/"
VERSION_RESTRICTION = "TYPES_ONLY"
LIST_GRAPH_RESTRICTIONS = [RDF.type, RDFS.subClassOf]


def run_ontcatowl(global_configurations, working_graph):
    """ Main function. """

    # DATA LOADINGS AND INITIALIZATIONS
    logger = initialize_logger()
    gufo_graph = load_graph_safely_considering_restrictions("modules/ontcatowl/resources/gufoEndurantsOnly.ttl",
                                                            LIST_GRAPH_RESTRICTIONS)
    gufo_dictionary = initialize_gufo_dictionary()
    ontology_dataclass_list = initialize_ontology_dataclasses(working_graph, gufo_dictionary)
    verify_all_ontology_dataclasses_consistency(ontology_dataclass_list)
    ontology_nodes = initialize_nodes_lists(working_graph)
    load_known_gufo_information(working_graph, gufo_graph, ontology_dataclass_list)
    before_statistics = generates_partial_statistics_list(ontology_dataclass_list)

    # EXECUTION
    time_register = execute_rules_types(ontology_dataclass_list, working_graph, ontology_nodes, global_configurations)

    # STATISTICS
    after_statistics = generates_partial_statistics_list(ontology_dataclass_list)
    consolidated_statistics = calculate_final_statistics(before_statistics, after_statistics)

    return ontology_dataclass_list, time_register, consolidated_statistics
