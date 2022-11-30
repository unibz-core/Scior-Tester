""" Functions for extracting taxonomy from OntoUML serialization in OWL. """

from rdflib import RDF, URIRef, Graph, RDFS, OWL

from modules.tester.hash_functions import register_sha256_hash_information
from modules.tester.logger_config import initialize_logger
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


def create_taxonomy_graph(owl_file_path):
    """ Extract the dataset model's taxonomy into a new graph. """

    source_graph = load_graph_safely(owl_file_path)
    taxonomy_graph = Graph()

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
        taxonomy_graph.add((uriref_general, RDF.type, OWL.Class))
        taxonomy_graph.add((uriref_specific, RDF.type, OWL.Class))
        taxonomy_graph.add((uriref_specific, RDFS.subClassOf, uriref_general))

    return taxonomy_graph


def create_taxonomy_ttl_file(source_owl_file_path, dataset_folder_path, catalog_size, current):
    """ Generates and saves the file taxonomy.ttl - rdf-s graph with the model's taxonomy - for a dataset. """

    logger = initialize_logger()

    # Creating and saving taxonomy file
    taxonomy_graph = create_taxonomy_graph(source_owl_file_path)
    taxonomy_file_path = dataset_folder_path + "\\" + "taxonomy.ttl"

    try:
        taxonomy_graph.serialize(taxonomy_file_path, encoding='utf-8')
        logger.info(f"Taxonomy file {current}/{catalog_size} saved: {taxonomy_file_path}")
    except OSError as error:
        logger.error(f"Could not save {taxonomy_file_path} file. Exiting program.\n"
                     f"System error reported: {error}")
        exit(1)

    register_sha256_hash_information(taxonomy_file_path, source_owl_file_path)
