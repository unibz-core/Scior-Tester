import os.path

from rdflib import RDF, Graph, RDFS, OWL
from copy import deepcopy

from src import NAMESPACE_TAXONOMY
from src.modules.build import *
from src.modules.run.test1 import write_csv_row
from src.modules.tester.hash_functions import register_sha256_hash_information
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely
from src.modules.tester.utils_graph import generates_nodes_lists, get_all_related_nodes
from src.modules.tester.utils_general import lists_subtraction


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

    return class_clean_name


def create_full_taxonomy_graph(owl_file_path):
    """ Extract the dataset model's taxonomy into a new graph. """

    source_graph = load_graph_safely(owl_file_path)
    taxonomy_graph = Graph()

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

        class_general_full_name = NAMESPACE_TAXONOMY + class_general_name_string
        class_specific_full_name = NAMESPACE_TAXONOMY + class_specific_name_string
        uriref_general = URIRef(class_general_full_name)
        uriref_specific = URIRef(class_specific_full_name)

        # Including classes and generalization into the new graph
        taxonomy_graph.add((uriref_general, RDF.type, OWL.Class))
        taxonomy_graph.add((uriref_specific, RDF.type, OWL.Class))
        taxonomy_graph.add((uriref_specific, RDFS.subClassOf, uriref_general))

    return taxonomy_graph


def create_taxonomy_ttl_files(source_owl_file_path, dataset_folder_path, hash_register):
    """ Generates and saves files taxonomy.ttl - rdf-s graph with the model's taxonomy - for a dataset. """

    # get the full graph
    full_taxonomy_graph = create_full_taxonomy_graph(source_owl_file_path)
    # generate isolated files
    taxonomy_files, hash_register = generate_isolated_taxonomy_files(
        full_taxonomy_graph, dataset_folder_path, source_owl_file_path, hash_register)

    return taxonomy_files, hash_register


def safe_save_taxonomy_graph(taxonomy_graph, complete_taxonomy_file_path):
    """ Safely save the taxonomy graph to a file. """

    logger = initialize_logger()

    try:
        taxonomy_graph.serialize(complete_taxonomy_file_path, encoding='utf-8')
        logger.info(f"Taxonomy file saved: {complete_taxonomy_file_path}")
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


def generate_isolated_taxonomy_files(source_taxonomy_graph, saving_path, source_owl_file_path, hash_register):
    """ Uses recursion for isolate all separated taxonomies inside a single graph
        and saves each one of them as a separated file with the name taxonomy_X.ttl,
        where X is the number of the taxonomy.
    """

    source_taxonomy_nodes = generates_nodes_lists(source_taxonomy_graph)
    source_taxonomy_roots = source_taxonomy_nodes["roots"]
    source_taxonomy_roots.sort()
    dataset_name = saving_path.split(os.path.sep)[-1]

    files = {}
    idx = 0
    while len(source_taxonomy_roots) > 0:
        related_classes = get_all_related_nodes(source_taxonomy_graph, source_taxonomy_nodes,
                                                source_taxonomy_roots[0], remove_itself=False)
        not_related_classes = lists_subtraction(source_taxonomy_nodes["all"], related_classes)
        reduced_graph = remove_classes_from_graph(source_taxonomy_graph, not_related_classes)
        source_taxonomy_roots = lists_subtraction(source_taxonomy_roots, related_classes)

        taxonomy_file_path = os.path.join(saving_path, f"{dataset_name}_tx{idx + 1:03d}.ttl")
        safe_save_taxonomy_graph(reduced_graph, taxonomy_file_path)
        hash_register = register_sha256_hash_information(hash_register, taxonomy_file_path, source_owl_file_path)
        files[taxonomy_file_path] = len(related_classes)
        idx += 1

    full_file_name = os.path.join(saving_path.rsplit(os.path.sep, 1)[0], f"taxonomies.csv")
    csv_header = ["taxonomy_name", "dataset_name", "num_classes"]
    for full_taxonomy_name, num_classes in files.items():
        csv_row = [full_taxonomy_name.split(os.path.sep)[-1], dataset_name, num_classes]
        write_csv_row(full_file_name, csv_header, csv_row)

    return list(files.keys()), hash_register
