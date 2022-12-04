""" Functions for extracting taxonomy from OntoUML serialization in OWL. """
from copy import deepcopy, copy

from ontcatowl.modules.initialization_data_graph import initialize_nodes_lists
from ontcatowl.modules.utils_general import lists_subtraction
from rdflib import RDF, URIRef, Graph, RDFS, OWL

from modules.tester.hash_functions import register_sha256_hash_information
from modules.tester.logger_config import initialize_logger
from modules.tester.utils_graph import get_all_related_nodes_inc
from modules.tester.utils_rdf import load_graph_safely

VOCABULARY_CLASS_URI = URIRef("https://purl.org/ontouml-models/vocabulary/Class")
VOCABULARY_GENERALIZATION_URI = URIRef("https://purl.org/ontouml-models/vocabulary/Generalization")
VOCABULARY_GENERAL_URI = URIRef("https://purl.org/ontouml-models/vocabulary/general")
VOCABULARY_SPECIFIC_URI = URIRef("https://purl.org/ontouml-models/vocabulary/specific")
VOCABULARY_NAME_URI = URIRef("https://purl.org/ontouml-models/vocabulary/name")
VOCABULARY_STEREOTYPE_URI = URIRef("https://purl.org/ontouml-models/vocabulary/stereotype")


def clean_class_name(class_raw_name: str) -> str:
    """
    :param class_raw_name (string): Class name as read from model.
    :return class_clean_name (string): Class name after removing invalid characters .
    """

    class_clean_name = class_raw_name.strip()
    class_clean_name = class_clean_name.replace(",", "_")
    class_clean_name = class_clean_name.replace("  ", " ")
    class_clean_name = class_clean_name.replace(" ", "_")
    class_clean_name = class_clean_name.replace("\n", "_")
    class_clean_name = class_clean_name.replace("\"\"", "_")

    return class_clean_name


def create_full_taxonomy_graph(owl_file_path):
    """ Extract the dataset model's taxonomy into a new graph. """

    source_graph = load_graph_safely(owl_file_path)
    full_taxonomy_graph = Graph()

    taxonomy_namespace = "http://taxonomy.model/"

    # Isolated classes are ignored for the creation of the taxonomy.ttl file.
    for generalization in source_graph.subjects(RDF.type, VOCABULARY_GENERALIZATION_URI):
        # Getting uri of the general and specific participants in the generalization
        class_general = source_graph.value(generalization, VOCABULARY_GENERAL_URI)
        class_specific = source_graph.value(generalization, VOCABULARY_SPECIFIC_URI)

        # continue if general and specific are classes
        type_of_general = source_graph.value(class_general, RDF.type)
        type_of_specific = source_graph.value(class_specific, RDF.type)

        if (type_of_general != VOCABULARY_CLASS_URI) or (type_of_specific != VOCABULARY_CLASS_URI):
            continue

        # Getting classes names
        class_general_name = source_graph.value(class_general, VOCABULARY_NAME_URI)
        class_specific_name = source_graph.value(class_specific, VOCABULARY_NAME_URI)

        # Converting Literals to URIRef in the following format ("http://taxonomy.model/Class_Name")
        class_general_name_string = class_general_name.n3()[1:-(len(class_general_name.language) + 2)]
        class_specific_name_string = class_specific_name.n3()[1:-(len(class_specific_name.language) + 2)]

        class_general_name_string = clean_class_name(class_general_name_string)
        class_specific_name_string = clean_class_name(class_specific_name_string)

        class_general_full_name = taxonomy_namespace + class_general_name_string
        class_specific_full_name = taxonomy_namespace + class_specific_name_string
        uriref_general = URIRef(class_general_full_name)
        uriref_specific = URIRef(class_specific_full_name)

        # Including classes and generalization into the new graph
        full_taxonomy_graph.add((uriref_general, RDF.type, OWL.Class))
        full_taxonomy_graph.add((uriref_specific, RDF.type, OWL.Class))
        full_taxonomy_graph.add((uriref_specific, RDFS.subClassOf, uriref_general))

    return full_taxonomy_graph


def safe_save_taxonomy_graph(taxonomy_graph, complete_taxonomy_file_path,end=""):
    """ Safely save the taxonomy graph to a file. """

    logger = initialize_logger()

    try:
        taxonomy_graph.serialize(complete_taxonomy_file_path, encoding='utf-8')
        logger.info(f"Taxonomy file saved: {complete_taxonomy_file_path}{end}")
    except OSError as error:
        logger.error(f"Could not save {complete_taxonomy_file_path} file. Exiting program.\n"
                     f"System error reported: {error}")
        exit(1)


def remove_classes_from_graph(source_graph, classes_to_remove_list):
    """ Receives a graph and a list of classes that are part of this graph and that must be removed.
        Removes all classes in the list and returns a new graph without them.
    """

    reduced_graph = deepcopy(source_graph)

    for class_to_remove in classes_to_remove_list:
        uriref_to_remove = URIRef(class_to_remove)
        reduced_graph.remove((uriref_to_remove, None, None))
        reduced_graph.remove((None, None, uriref_to_remove))

    return reduced_graph


def generate_isolated_taxonomy_files(source_taxonomy_graph, saving_path, source_owl_file_path,
                                     current_taxonomy_number=0):
    """ Uses recursion for isolate all separated taxonomies inside a single taxonomical graph
    and saves each one of them as a separated file with the name taxonomy_X.ttl,
    where X is the number of the taxonomy."""

    taxonomy_file_path = saving_path + f"\\taxonomy_{current_taxonomy_number+1:02d}.ttl"

    source_taxonomy_nodes = initialize_nodes_lists(source_taxonomy_graph)
    source_taxonomy_roots = source_taxonomy_nodes["roots"]

    classes_related_to_root0 = get_all_related_nodes_inc(source_taxonomy_graph, source_taxonomy_nodes,
                                                         source_taxonomy_roots[0])
    classes_not_related_to_root0 = lists_subtraction(source_taxonomy_nodes["all"],classes_related_to_root0)

    # Single taxonomy (or end of recursion)
    if len(classes_not_related_to_root0) == 0:
        safe_save_taxonomy_graph(source_taxonomy_graph, taxonomy_file_path, "\n")
        register_sha256_hash_information(taxonomy_file_path, source_owl_file_path)
    # Isolating taxonomies from source graph
    else:
        # Save current
        reduced_graph = remove_classes_from_graph(source_taxonomy_graph, classes_not_related_to_root0)
        safe_save_taxonomy_graph(reduced_graph, taxonomy_file_path)
        register_sha256_hash_information(taxonomy_file_path, source_owl_file_path)

        # Proceeding to next
        current_taxonomy_number += 1
        new_source_graph = remove_classes_from_graph(source_taxonomy_graph, classes_related_to_root0)
        generate_isolated_taxonomy_files(new_source_graph, saving_path, source_owl_file_path, current_taxonomy_number)


def create_taxonomy_ttl_files(source_owl_file_path, dataset_folder_path, catalog_size, current):
    """ Generates and saves the file taxonomy.ttl - rdf-s graph with the model's taxonomy - for a dataset. """

    logger = initialize_logger()

    # Creating and saving taxonomy file
    full_taxonomy_graph = create_full_taxonomy_graph(source_owl_file_path)

    generate_isolated_taxonomy_files(full_taxonomy_graph, dataset_folder_path, source_owl_file_path)