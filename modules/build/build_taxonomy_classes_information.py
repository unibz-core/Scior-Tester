""" Fills the statistics with taxonomy information. """
import pathlib

from modules.build.build_information_classes import class_information_structure
from modules.tester.graph_data import generates_nodes_lists
from modules.tester.logger_config import initialize_logger
from modules.tester.utils_graph import get_all_superclasses, get_all_subclasses, get_all_related_nodes
from modules.tester.utils_rdf import load_graph_safely


def get_taxonomy_position_information(class_taxonomy_information, taxonomy_nodes):
    """ Collect information about the position of a class in a taxonomy and save in a class. """

    if class_taxonomy_information.prefixed_name in taxonomy_nodes["roots"]:
        class_taxonomy_information.is_root = True
    else:
        class_taxonomy_information.is_root = False

    if class_taxonomy_information.prefixed_name in taxonomy_nodes["leaves"]:
        class_taxonomy_information.is_leaf = True
    else:
        class_taxonomy_information.is_leaf = False

    if class_taxonomy_information.prefixed_name not in taxonomy_nodes["roots"] \
            and class_taxonomy_information.prefixed_name not in taxonomy_nodes["leaves"]:
        class_taxonomy_information.is_intermediate = True
    else:
        class_taxonomy_information.is_intermediate = False


def get_taxonomy_relations_information(class_taxonomy_information, taxonomy_nodes, taxonomy_graph):
    """ Get number of subclasses, superclasses and reachable nodes. """

    list_superclasses = get_all_superclasses(taxonomy_graph, taxonomy_nodes, class_taxonomy_information.prefixed_name)
    list_subclasses = get_all_subclasses(taxonomy_graph, taxonomy_nodes, class_taxonomy_information.prefixed_name)
    list_reachable = get_all_related_nodes(taxonomy_graph, taxonomy_nodes, class_taxonomy_information.prefixed_name)

    number_superclasses = len(list_superclasses)
    number_subclasses = len(list_subclasses)
    number_reachable = len(list_reachable)

    class_taxonomy_information.number_superclasses = number_superclasses
    class_taxonomy_information.number_subclasses = number_subclasses
    class_taxonomy_information.number_reachable_classes = number_reachable


def calculate_class_taxonomy_information(taxonomy_graph, taxonomy_nodes):
    """ Saving position of the classes in the taxonomy for statistics. """

    list_classes_statistics = []
    taxonomy_namespace = "http://taxonomy.model/"

    for dataset_class in taxonomy_nodes["all"]:
        dataset_class = dataset_class.removeprefix(taxonomy_namespace)
        class_taxonomy_information = class_information_structure(name=dataset_class)

        get_taxonomy_position_information(class_taxonomy_information, taxonomy_nodes)
        get_taxonomy_relations_information(class_taxonomy_information, taxonomy_nodes, taxonomy_graph)

        list_classes_statistics.append(class_taxonomy_information)

    return list_classes_statistics


def collect_taxonomy_information(dataset, catalog_size, current):
    """ Populates the statistics list with taxonomy information. """

    logger = initialize_logger()

    dataset_folder_path = str(pathlib.Path().resolve()) + "\\" + "catalog" + "\\" + dataset
    taxonomy_path = dataset_folder_path + "/taxonomy.ttl"

    taxonomy_graph = load_graph_safely(taxonomy_path)

    taxonomy_prefixed_nodes_list = generates_nodes_lists(taxonomy_graph)
    list_classes_information = calculate_class_taxonomy_information(taxonomy_graph, taxonomy_prefixed_nodes_list)

    logger.info(f"Taxonomy information {current}/{catalog_size} collected from dataset {dataset}")

    return list_classes_information
