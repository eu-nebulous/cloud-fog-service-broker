from rdflib import Graph, URIRef
from data_types import get_attr_data_type

# Create a new RDF graph
g = Graph()

# Load TTL data into the graph
file_path = 'assets/Preferences_Model.ttl'
g.parse(file_path, format='turtle')

# Create variables for predicate names
SMI_prefix = "https://www.nebulouscloud.eu/smi/SMI-OBJECT#"
a = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
type = "http://purl.org/dc/elements/1.1/type"
terms_URI = "http://purl.org/dc/terms/URI"
terms_created = "http://purl.org/dc/terms/created"
terms_description = "http://purl.org/dc/terms/description"
terms_identifier = "http://purl.org/dc/terms/identifier"
terms_modified = "http://purl.org/dc/terms/modified"
terms_title = "http://purl.org/dc/terms/title"
skos_broader = "http://www.w3.org/2004/02/skos/core#broader"


def get_level_1_items():
    items_list = []
    level_1_items_list = []
    for subject, predicate, object in g:
        if "broader" in predicate and "attr-root" in object:
            item_dict = {}
            # keep only the attribute part - attr-performance
            attribute = str(subject)
            attribute = attribute.replace(SMI_prefix, '')
            # add it in level_1_items_list for easy search in level 2 items loop
            level_1_items_list.append(attribute)
            item_data_dict = get_subject_data(str(subject))
            item_dict["title"] = item_data_dict["title"]
            item_dict["description"] = item_data_dict["description"]
            item_dict["name"] = attribute
            item_dict["children"] = []
            criterion_type_values = get_attr_data_type(item_dict["name"])
            item_dict["type"] = criterion_type_values['type']
            # item_dict["values"] = criterion_type_values['values'] # they do not have all criteria
            items_list.append(item_dict)
    items_2_list = get_level_2_items(level_1_items_list, items_list)
    return items_2_list


def get_level_2_items(level_1_items_list, level_1_items_dict_list):
    items_list = []
    level_2_items_list = []
    for subject, predicate, object in g:
        if "broader" in predicate:
            object_str = str(object)
            object_str = object_str.replace(SMI_prefix, '')
            if object_str in level_1_items_list:
                item_dict = {}
                level_2_attribute = str(subject)
                level_2_attribute = level_2_attribute.replace(SMI_prefix, '')
                level_2_items_list.append(level_2_attribute)
                item_data_dict = get_subject_data(str(subject))
                item_dict["title"] = item_data_dict["title"]
                item_dict["description"] = item_data_dict["description"]
                item_dict["parent"] = object_str
                item_dict["name"] = level_2_attribute
                item_dict["children"] = []
                criterion_type_values = get_attr_data_type(item_dict["name"])
                item_dict["type"] = criterion_type_values['type']
                items_list.append(item_dict)
    items_3_list = get_level_3_items(level_2_items_list, items_list, level_1_items_dict_list)
    return items_3_list


def get_level_3_items(level_2_items_list, level_2_items_dict_list, level_1_items_dict_list):
    items_list = []
    level_3_items_list = []
    for subject, predicate, object in g:
        if "broader" in predicate:
            object_str = str(object)
            object_str = object_str.replace(SMI_prefix, '')
            if object_str in level_2_items_list:
                item_dict = {}
                level_3_attribute = str(subject)
                level_3_attribute = level_3_attribute.replace(SMI_prefix, '')
                level_3_items_list.append(level_3_attribute)
                item_data_dict = get_subject_data(str(subject))
                item_dict["title"] = item_data_dict["title"]
                item_dict["description"] = item_data_dict["description"]
                item_dict["parent"] = object_str
                item_dict["name"] = level_3_attribute
                item_dict["children"] = []
                criterion_type_values = get_attr_data_type(item_dict["name"])
                item_dict["type"] = criterion_type_values['type']
                items_list.append(item_dict)
    level_2_children_list = insert_level_2_children(level_1_items_dict_list, level_2_items_dict_list, items_list)
    return level_2_children_list


def insert_level_2_children(level_1_items_dict_list, level_2_items_dict_list, level_3_items_dict_list):
    for level_2_item in level_2_items_dict_list:
        level_2_children_list = []
        # print("level_2_item = " + level_2_item["name"])
        for level_3_item in level_3_items_dict_list:
            # print("level_3_item = " + level_3_item["name"])
            if level_3_item["parent"] == level_2_item["name"]:
                # print("Children of " + level_2_item["name"] + " is " + level_3_item["name"])
                item_dict = {"name": level_3_item["name"]}
                # level_2_children_list.append(item_dict)
                level_2_children_list.append(level_3_item)
        # here to append the list at the correct position of level_2_items_dict_list
        # Sort the children by their title
        level_2_item["children"] = sorted(level_2_children_list, key=lambda x: x['title'])
        items_dict_list = insert_level_1_children(level_1_items_dict_list, level_2_items_dict_list)
    # return level_2_items_dict_list
    return items_dict_list


# def insert_level_1_children(level_1_items_dict_list, level_2_items_dict_list):
#     for level_1_item in level_1_items_dict_list:
#         level_1_children_list = []
#         # print("level_1_item = " + level_1_item["name"])
#         for level_2_item in level_2_items_dict_list:
#             # print("level_2_item = " + level_2_item["name"])
#             if level_2_item["parent"] == level_1_item["name"]:
#                 # print("Children of " + level_1_item["name"] + " is " + level_2_item["name"])
#                 level_1_children_list.append(level_2_item)
#         # here to append the list at the correct position of level_1_items_dict_list
#         level_1_item["children"] = level_1_children_list
#     return level_1_items_dict_list

def insert_level_1_children(level_1_items_dict_list, level_2_items_dict_list):
    for level_1_item in level_1_items_dict_list:
        level_1_children_list = []
        for level_2_item in level_2_items_dict_list:
            if level_2_item["parent"] == level_1_item["name"]:
                level_1_children_list.append(level_2_item)

        # Sort the children by their title
        level_1_item["children"] = sorted(level_1_children_list, key=lambda x: x['title'])

    # Now sort the level 1 items themselves
    sorted_level_1_items_dict_list = sorted(level_1_items_dict_list, key=lambda x: x['title'])
    return sorted_level_1_items_dict_list


def get_subject_data(item_subject):
    subject_data = {
        "title": "",
        "description": ""
    }
    for subject, predicate, object in g:
        if str(subject) == item_subject:
            # print("checking data for " + item_subject + " and subject is " + subject)
            if str(predicate) == terms_description and not str(object) == " ":
                subject_data["description"] = str(object)
            elif str(predicate) == terms_description:
                subject_data["description"] = "No description available"
            if str(predicate) == terms_title and not str(object) == " ":
                subject_data["title"] = str(object)
            elif str(predicate) == terms_title:
                attr_subject = str(item_subject)
                attr_subject = attr_subject.replace(SMI_prefix, '')
                subject_data["title"] = attr_subject
    return subject_data


def get_defined_criteria_list():
    defined_criteria = ["attr-accountability", "attr-reputation", "attr-agility"]  # List of criteria given by the user based on Provider
    return defined_criteria


# This function is used to set the criteria for which the user gives values per provider
def get_defined_criteria(selected_criteria):
    defined_criteria = get_defined_criteria_list()
    criteria_to_define = []
    for criteria in selected_criteria:
        if criteria['name'] in defined_criteria:
            # print(criteria['name'])
            criteria_to_define.append(criteria)
    return criteria_to_define

# This functions stores a list with the criteria used in the CFSB criteria selection
def get_active_criteria_list():
    active_citeria = [
        "attr-reputation",
        "attr-agility",
        # "attr-performance",
        # "attr-performance-capacity",
        "attr-performance-capacity-num-of-cores",
        "attr-performance-capacity-memory",
    ]
    return active_citeria

# This function goes to children only if the parent is active. If parent inactive, then all children are inactive
def get_active_criteria_parent(items_list):
    active_items_list = []
    active_criteria = get_active_criteria_list()
    for item in items_list:
        # print(item)
        if item["name"] in active_criteria:
            print("active criterion parent")
            active_items_list.append(item)
            if item["children"] is not None:
                children1 = []
                for child in item["children"]:
                    if child["name"] in active_criteria:
                        # print("active criterion child 1")
                        children1.append(child)
                        if child["children"] is not None:
                            children2 = []
                            for child2 in child["children"]:
                                if child2["name"] in active_criteria:
                                    # print("active criterion child 2")
                                    children2.append(child2)
                            child["children"] = children2
                item["children"] = children1
    return active_items_list

# This function handles active criteria individually. If a parent has active children it is considered active to keep the usual hierarchy
def get_active_criteria_specific(items_list):
    active_items_list = []
    active_criteria = get_active_criteria_list()
    for item in items_list:
        # if item["name"] in active_criteria:
        #     active_items_list.append(item) # if level 1 in active we put it in active_items_list
        if item["children"] is not None:
            children1 = []
            for child in item["children"]:
                # if child["name"] in active_criteria:
                #     children1.append(child) # if level 2 in active we put it in active_items_list
                if child["children"] is not None:
                    children2 = []
                    for child2 in child["children"]:
                        if child2["name"] in active_criteria:
                            children2.append(child2) # In children2 we put the active level 3 items
                    child["children"] = children2 # In item from level 2 we put its active children --> level 3

                    if child["name"] in active_criteria: # if child in active
                        children1.append(child)  # In children1 we put the active level 2 items
                    elif children2: # else if this child has active children
                        children1.append(child) # in Children1 we put the child because it has at least one active child(from level 3)

            item["children"] = children1 # in item from level 1 we put its active children --> level 2

            if item["name"] in active_criteria:
                active_items_list.append(item)  # if level 1 in active we put it in active_items_list
            elif children1: # else if this parent has children(directly active or with active children) we put it in active items list
                active_items_list.append(item)

    return active_items_list