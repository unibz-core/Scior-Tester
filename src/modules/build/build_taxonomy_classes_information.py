""" Fills the statistics with taxonomy information. """
from src import NAMESPACE_TAXONOMY
from src.modules.build.build_information_classes import InformationStructure
from src.modules.tester.utils_graph import generates_nodes_lists
from src.modules.tester.logger_config import initialize_logger
from src.modules.tester.utils_rdf import load_graph_safely


def calculate_class_taxonomy_information(taxonomy_graph, taxonomy_nodes):
    """ Saving position of the classes in the taxonomy for statistics. """

    list_classes_statistics = []

    for dataset_class in taxonomy_nodes["all"]:
        dataset_class = dataset_class.removeprefix(NAMESPACE_TAXONOMY)

        class_taxonomy_information = InformationStructure(name=dataset_class)
        class_taxonomy_information.build_position(taxonomy_nodes)
        class_taxonomy_information.build_numbers(taxonomy_nodes, taxonomy_graph)

        list_classes_statistics.append(class_taxonomy_information)

    return list_classes_statistics


def collect_taxonomy_information(taxonomy_path, catalog_size, current):
    """ Populates the statistics list with taxonomy information. """

    logger = initialize_logger()

    taxonomy_graph = load_graph_safely(taxonomy_path)

    taxonomy_prefixed_nodes_list = generates_nodes_lists(taxonomy_graph)
    list_classes_information = calculate_class_taxonomy_information(taxonomy_graph, taxonomy_prefixed_nodes_list)

    dataset_name = taxonomy_path.split("\\")[-2]
    logger.info(f"Taxonomy information {current}/{catalog_size} collected from dataset {dataset_name}")

    return list_classes_information
