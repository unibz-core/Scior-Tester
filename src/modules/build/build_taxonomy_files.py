import glob
import os.path
from copy import deepcopy

from rdflib import RDF, Graph, RDFS, OWL, URIRef

from src import NAMESPACE_TAXONOMY, NAMESPACE_GUFO
from src.modules.build import VOCABULARY_GENERALIZATION_URI, VOCABULARY_GENERAL_URI, VOCABULARY_SPECIFIC_URI, \
    VOCABULARY_CLASS_URI, VOCABULARY_NAME_URI, VOCABULARY_STEREOTYPE_URI, VOCABULARY_URI_STR
from src.modules.build.build_classes_stereotypes_information import get_gufo_classification, clean_class_name, \
    return_gufo_classification_uri, get_gufo_classification_supertypes
from src.modules.tester.hash_functions import register_sha256_hash_information
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_general import lists_subtraction
from src.modules.tester.utils_graph import generates_nodes_lists, get_all_related_nodes
from src.modules.tester.utils_rdf import load_graph_safely


def add_classification_to_graph(taxonomy_graph, class_uri, class_ontouml_stereotype):
    """ Adds to the graph the class's OntoUML stereotype mapped to gUFO. """

    # Getting classes OntoUML stereotypes (only stereotype string)
    class_ontouml_string = class_ontouml_stereotype.n3().replace(VOCABULARY_URI_STR, "")[1:-1]

    # Mapping OntoUML types to gUFO
    class_gufo_string = get_gufo_classification(class_ontouml_string)

    # Tagging out-of-scope classes for future removal
    if class_gufo_string == "other":
        taxonomy_graph.add((class_uri, RDFS.label, URIRef("OUT-OF-SCOPE")))
    # For all in-scope classes
    else:
        # Getting all types to be added to the class
        list_class_types = get_gufo_classification_supertypes(class_gufo_string)
        for class_type in list_class_types:
            class_general_gufo = return_gufo_classification_uri(class_type)
            # Adding gUFO categories to graph
            taxonomy_graph.add((class_uri, RDF.type, class_general_gufo))


def remove_out_of_scope_classes(taxonomical_graph):
    """ Removes all classes tagged as OUT-OF-SCOPE and all their subclasses. """

    identify_subclasses_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?subject
    WHERE {
    ?invalid rdfs:label <OUT-OF-SCOPE> . 
    ?subject rdfs:subClassOf* ?invalid
    }
    """

    query_answer = taxonomical_graph.query(identify_subclasses_query)
    for row in query_answer:
        taxonomical_graph.remove((row.subject, None, None))
        taxonomical_graph.remove((None, None, row.subject))


def create_full_taxonomy_graph(owl_file_path: str):
    """ Extract the dataset model's taxonomy into a new graph. This function:
    1. Loads ontology.ttl file into graph
    2. Copies to a new graph only classes and generalizations
    3. Converts OntoUML  stereotypes into gUFO classifications
    4. Removes classes that have out-of-scope classifications and their subclasses
    5. Returns the resulting graph
    """

    source_graph = load_graph_safely(owl_file_path)
    taxonomical_graph = Graph()

    taxonomical_graph.bind("", NAMESPACE_TAXONOMY)

    # Isolated classes are ignored for the creation of the taxonomy.ttl file.
    # Classes without stereotype are not added to the graph.
    for generalization in source_graph.subjects(RDF.type, VOCABULARY_GENERALIZATION_URI):
        # Getting uri of the general and specific participants in the generalization
        class_general = source_graph.value(generalization, VOCABULARY_GENERAL_URI)
        class_specific = source_graph.value(generalization, VOCABULARY_SPECIFIC_URI)

        # CONTINUE ONLY IF BOTH GENERAL AND SPECIFIC ARE CLASSES
        type_of_general = source_graph.value(class_general, RDF.type)
        type_of_specific = source_graph.value(class_specific, RDF.type)

        if (type_of_general != VOCABULARY_CLASS_URI) or (type_of_specific != VOCABULARY_CLASS_URI):
            continue

        # Getting OntoUML stereotypes of general and specific participants in the generalization (full URIRef)
        class_general_stereotype = source_graph.value(class_general, VOCABULARY_STEREOTYPE_URI)
        class_specific_stereotype = source_graph.value(class_specific, VOCABULARY_STEREOTYPE_URI)

        # CONTINUE ONLY IF BOTH GENERAL AND SPECIFIC HAVE STEREOTYPES
        if (class_general_stereotype == None) or (class_specific_stereotype == None):
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
        taxonomical_graph.add((uriref_general, RDF.type, OWL.Class))
        taxonomical_graph.add((uriref_specific, RDF.type, OWL.Class))
        taxonomical_graph.add((uriref_specific, RDFS.subClassOf, uriref_general))

        # Adding gUFO classifications
        taxonomical_graph.bind("gufo", NAMESPACE_GUFO)

        # Get related mapped gUFO classifications and adds to graph
        add_classification_to_graph(taxonomical_graph, uriref_general, class_general_stereotype)
        add_classification_to_graph(taxonomical_graph, uriref_specific, class_specific_stereotype)

    # Removing all classes tagged as out-of-scope and their subclasses
    remove_out_of_scope_classes(taxonomical_graph)

    return taxonomical_graph


def create_taxonomy_ttl_files(source_owl_file_path, dataset_folder_path, hash_register):
    """ Generates and saves files taxonomy.ttl - rdf-s graph with the model's taxonomy - for a dataset. """

    # Load ontology.ttl file into graph,
    # converting their OntoUML stereotypes to gUFO classifications and removing out-of-scope classes
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

    files = []
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
        files.append(taxonomy_file_path)
        idx += 1

    return files, hash_register


def remove_gufo_classifications():
    """ Removes all gUFO classifications from all generated taxonomies. """

    logger = initialize_logger()

    list_gufo_classifications = [
        "AntiRigidType",
        "Aspect",
        "Category",
        "Collection",
        "Endurant",
        "EndurantType",
        "ExtrinsicAspect",
        "ExtrinsicMode",
        "FixedCollection",
        "FunctionalComplex",
        "IntrinsicAspect",
        "IntrinsicMode",
        "Kind",
        "Mixin",
        "NonRigidType",
        "NonSortal",
        "Object",
        "Phase",
        "PhaseMixin",
        "Quality",
        "Quantity",
        "Relator",
        "RigidType",
        "Role",
        "RoleMixin",
        "SemiRigidType",
        "Sortal",
        "SubKind",
        "VariableCollection",
    ]

    # Iterate over all taxonomy files
    list_all_files = glob.glob("**/*.ttl", recursive=True)

    logger.info(f"### Removing gUFO classifications from {len(list_all_files)} taxonomies ###\n")

    for index, file in enumerate(list_all_files):

        current = index + 1

        # Loading file
        logger.info(f"Removing gUFO classifications of {current}/{len(list_all_files)}: {file}")
        taxonomy_graph = load_graph_safely(file)

        for gufo_classification in list_gufo_classifications:
            taxonomy_graph.remove((None, RDF.type, URIRef(NAMESPACE_GUFO + gufo_classification)))

        safe_save_taxonomy_graph(taxonomy_graph, file)
    logger.info(f"gUFO classifications successfully removed from {len(list_all_files)} taxonomies\n")
