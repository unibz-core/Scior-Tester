from rdflib import RDF, Graph, RDFS, OWL

from src import NAMESPACE_TAXONOMY
from src.modules.build import *
from src.modules.tester.hash_functions import register_sha256_hash_information
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

    return class_clean_name


def create_taxonomy_graph(owl_file_path):
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


def create_taxonomy_ttl_file(source_owl_file_path, dataset_folder_path, catalog_size, current, hash_register) -> str:
    """
    Generates and saves the file taxonomy.ttl - rdf-s graph with the model's taxonomy - for a dataset.
    :return: name of the created file
    """

    logger = initialize_logger()

    # Creating and saving taxonomy file
    taxonomy_graph = create_taxonomy_graph(source_owl_file_path)
    taxonomy_file_name = dataset_folder_path + "\\taxonomy.ttl"

    try:
        taxonomy_graph.serialize(taxonomy_file_name, encoding='utf-8')
        logger.info(f"Taxonomy file {current}/{catalog_size} saved: {taxonomy_file_name}")
    except OSError as error:
        logger.error(f"Could not save {taxonomy_file_name} file. Exiting program.\n"
                     f"System error reported: {error}")
        exit(1)

    hash_register = register_sha256_hash_information(hash_register, taxonomy_file_name, source_owl_file_path)

    return taxonomy_file_name, hash_register
