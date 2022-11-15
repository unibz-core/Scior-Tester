""" Functions for extracting taxonomy from OntoUML serialization in OWL. """

from rdflib import RDF, URIRef

from modules.logger_config import initialize_logger
from modules.utils_rdf import load_graph_safely


class class_stereotype_data(object):
    """ Stereotype information related a specific class in the dataset's model. """

    def __init__(self, name, stereotype_original, stereotype_gufo):
        self.name = name
        self.stereotype_original = stereotype_original
        self.stereotype_gufo = stereotype_gufo


class class_taxonomy_data(object):
    """ Taxonomy information related a specific class in the dataset's model. """

    # Validating parameter node_type
    def __init__(self, name, node_type):
        self.name = name
        self.node_type = node_type

        valid_node_type = ["root", "leaf", "isolated", "intermediate"]
        if node_type not in valid_node_type:
            logger = initialize_logger()
            logger.error(f"Invalid note_type ({node_type}) for class_stereotype_data {name}. Program aborted.")
            exit(1)

class dataset_data(object):
    """ Class with statistics from the classes in a dataset. """

    def __init__(self, number_classes):
        self.number_classes = number_classes


def get_gufo_stereotype(class_stereotype_original):
    """ Mapps OntoUML serialization in OWL stereotype for the gUFO types used in OntCatOWL """

    if class_stereotype_original == "category":
        mapped_stereotype = "category"
    elif (class_stereotype_original == "collective") or (class_stereotype_original == "kind") or \
            (class_stereotype_original == "quality") or (class_stereotype_original == "quantity") or \
            (class_stereotype_original == "mode") or (class_stereotype_original == "relator"):
        mapped_stereotype = "kind"
    elif class_stereotype_original == "mixin":
        mapped_stereotype = "mixin"
    elif class_stereotype_original == "phase":
        mapped_stereotype = "phase"
    elif class_stereotype_original == "phasemixin":
        mapped_stereotype = "phasemixin"
    elif class_stereotype_original == "role" or \
            class_stereotype_original == "historicalrole":
        mapped_stereotype = "role"
    elif class_stereotype_original == "rolemixin" or \
            class_stereotype_original == "historicalrolemixin":
        mapped_stereotype = "rolemixin"
    elif class_stereotype_original == "subkind":
        mapped_stereotype = "subkind"
    else:
        mapped_stereotype = "other"

    return mapped_stereotype


def generate_dataset_classes_data(owl_file_path):
    """
    1) Populates the class list for the dataset with the following information:
        - class_name, stereotype_original, stereotype_gufo.

    2) Populates the dataset statistics with the following information:
        - number_classes, number of each gUFO stereotype

    Restrictions and limitations:
     - Removes the language tag from the class name and also the build-in types string, int, and char.
     - Classes without stereotype are set to the stereotype "none".
    """

    source_graph = load_graph_safely(owl_file_path)

    vocabulary_class_uri = URIRef("https://purl.org/ontouml-models/vocabulary/Class")
    vocabulary_name_property_uri = URIRef("https://purl.org/ontouml-models/vocabulary/name")
    vocabulary_stereotype_property_uri = URIRef("https://purl.org/ontouml-models/vocabulary/stereotype")

    list_classes_data = []

    for owl_class in source_graph.subjects(RDF.type, vocabulary_class_uri):
        # Getting classes' names
        class_name = source_graph.value(owl_class, vocabulary_name_property_uri)
        class_name = class_name.n3()[1:-(len(class_name.language) + 2)]

        if class_name != "string" and class_name != "int" and class_name != "char":
            # Getting classes' stereotypes
            class_stereotype_original = source_graph.value(owl_class, vocabulary_stereotype_property_uri)
            if class_stereotype_original == None:
                class_stereotype_original_string = "none"
                class_stereotype_gufo = "none"
            else:
                class_stereotype_original_string = class_stereotype_original.n3()[44:-1]
                class_stereotype_original_string = class_stereotype_original_string.lower().strip()
                class_stereotype_gufo = get_gufo_stereotype(class_stereotype_original_string)

            current_class_data = class_stereotype_data(class_name, class_stereotype_original_string,
                                                       class_stereotype_gufo)
            list_classes_data.append(current_class_data)

    return list_classes_data


def generate_dataset_csv_classes_taxonomy(dataset, owl_file_path):
    """ Generates a csv file with the dataset model taxonomy in the following format:
    class_name, type (root, leaf, isolated, intermediate).

    Restrictions and limitations:
     - Removes the language tag from the class name and also the build-in types string, int, and char.
     - Classes without stereotype are ignored.
    """
    pass


def generate_dataset_taxonomy(dataset, owl_file_path):
    """ Generates a ttl file with the dataset model taxonomy. """
    pass


def generate_dataset_taxonomy(dataset, owl_file_path):
    """ Generates all files related to the dataset model's taxonomy. """
    # generate_dataset_csv_classes_taxonomy()
    # generate_dataset_rdf_taxonomy()

    # TODO (@pedropaulofb): Save basic statistics for each dataset.
    #  Statistics CSV with: (stereotype data) .
    pass


# def saves_dataset_csv_classes_data():

# csv_header = ["class_name", "stereotype_original", "stereotype_gufo"]
# csv_list_rows = []
#
# tester_path = str(pathlib.Path().resolve())
# dataset_path = tester_path + chr(92) + "catalog" + chr(92) + dataset_name + chr(92)
# csv_file_full_path = dataset_path + "classes_stereotypes.csv"
# print(csv_file_full_path)
#
# with open(csv_file_full_path, 'w', encoding='UTF8', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(csv_header)
#
#     for csv_row in csv_list_rows:
#         writer.writerow(csv_row)

#     pass
#
# def saves_dataset_csv_classes_statistics():
#     pass

def generate_catalog_data_files(catalog_path, list_datasets):
    """ Generates and saves in files data to be evaluated for each dataset in the catalog.

    The following files are saved in each dataset folder:
        - classes_data.csv: contains information about each class in the dataset's model.
        - statistics.csv:   number_classes, number of each gUFO stereotype,
                            number_roots, number_leafs, number_isolated, number_intermediates
        - taxonomy.ttl: rdf-s graph with the model's taxonomy.
    """

    for dataset in list_datasets:

        owl_file_path = catalog_path + "\\" + dataset + "\\" + "ontology.ttl"

        dataset_classes_data = generate_dataset_classes_data(owl_file_path)
        # dataset_classes_statistics = dataset_data()

        for class_data in dataset_classes_data:
            print(f"class_data.name = {class_data.name}")
            print(f"class_data.stereotype_original = {class_data.stereotype_original}")

        # generate_dataset_taxonomy(dataset, owl_file_path)

        # get stereotype information
        # get taxonomy
        # saves graph
        # saves classes_data csv file
        # saves dataset_data csv file
