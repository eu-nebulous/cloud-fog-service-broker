from rdflib import Graph, URIRef
# from rdflib.namespace import RDF, RDFS, DC, DCTERMS, SKOS

# Create a new RDF graph
g = Graph()

# Load TTL data into the graph
file_path = 'assets/Preferences_Model.ttl'
g.parse(file_path, format='turtle')
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

subjects = g.subjects()
predicates = g.predicates()
objects = g.objects()

# for subject in subjects:
#     print(subject)
#     print(g.objects(subject=subject))
#
# for predicate in predicates:
#     print(predicate)
#
# for object in objects:
#     print("object start")
#     print(object)
#     print(g.subject_predicates(object))

# print(g.serialize(format='turtle'))

# file_data = g.serialize(format='turtle')

level_1_items = []
level_1_subjects_dict = {}
level_2_items = []
level_2_subjects_dict = {}
level_3_items = []
level_3_subjects_dict = {}


def scan_level_1_items():
    for subject, predicate, object in g:
        print("\nloop data for level 1")
        # print(f"Subject: {subject}, Predicate: {predicate}, Object: {object}")
        if "broader" in predicate and "attr-root" in object:
            attribute = str(subject)
            attribute = attribute.replace(SMI_prefix, '')
            print("\nRoot from predicate type: " + attribute)
            level_1_items.append(attribute)
            level_1_subjects_dict[attribute] = subject
    return level_1_subjects_dict


def scan_level_2_items():
    for subject, predicate, object in g:
        print("\nloop data for level 2")
        # print(f"Subject: {subject}, Predicate: {predicate}, Object: {object}")
        if "broader" in predicate:
            object_str = str(object)
            object_str = object_str.replace(SMI_prefix, '')
            if object_str in level_1_items:
                # parent found in level 1
                level_2_attribute = str(subject)
                level_2_attribute = level_2_attribute.replace(SMI_prefix, '')
                print("\nLevel 2 attr: " + level_2_attribute)
                level_2_items.append(level_2_attribute)
                level_2_subjects_dict[level_2_attribute] = subject
                print("for dict 2 key = " + level_2_attribute + " - Value = " + subject)
    return level_2_subjects_dict


def scan_level_3_items():
    for subject, predicate, object in g:
        print("\nloop data for level 3")
        print(f"Subject: {subject}, Predicate: {predicate}, Object: {object}")
        if "broader" in predicate:
            object_str = str(object)
            object_str = object_str.replace(SMI_prefix, '')
            if object_str in level_2_items:
                level_3_attribute = str(subject)
                level_3_attribute = level_3_attribute.replace(SMI_prefix, '')
                print("\nLevel 3 attr: " + level_3_attribute)
                level_3_items.append(level_3_attribute)
                level_3_subjects_dict[level_3_attribute] = subject
    return level_3_subjects_dict


print(level_1_items)
print(level_1_subjects_dict)
print("count level 1: " + str(len(level_1_items)))
print(level_2_items)
print(level_2_subjects_dict)
print("count level 2: " + str(len(level_2_items)))
print(level_3_items)
print(level_3_subjects_dict)
print("count level 3: " + str(len(level_3_items)))

print("\n------------\n")

attr_dict = {}


def create_level_1_attr_dict(item, item_subject):
        print("item: " + item)
        attr_data = {}
        for subject, predicate, object in g:
            if subject == item_subject:
                attr_data["level"] = 1
                attr_data["subject"] = subject
                if str(predicate) == terms_description:
                    # print("\nDescription found for " + item + " - description: " + str(object))
                    attr_data["description"] = str(object)
                if str(predicate) == terms_title:
                    # print("\nTitle found for " + item + " - title: " + str(object))
                    attr_data["title"] = str(object)
                if str(predicate) == skos_broader:
                    # print("\nskos found for " + item + " - Parent: " + str(object))
                    attr_data["parent"] = str(object)

                attr_dict[item] = attr_data
        print(attr_data)


def create_attr_dict(item, item_subject):
    attr_data_dict = {}
    for subject, predicate, object in g:
        if subject == item_subject:
            attr_data_dict["subject"] = subject
            if str(predicate) == terms_description:
                print("\nDescription found for " + item + " - description: " + str(object))
                attr_data_dict["description"] = str(object)
            if str(predicate) == terms_title:
                print("\nTitle found for " + item + " - title: " + str(object))
                attr_data_dict["title"] = str(object)
            if str(predicate) == skos_broader:
                print("\nskos found for " + item + " - Parent: " + str(object))
                attr_data_dict["parent"] = str(object)
                if object in level_1_subjects_dict.values():
                    print("found level 2 item")
                    attr_data_dict["level"] = 2
                elif object in level_2_subjects_dict.values():
                    print("found level 3 item")
                    attr_data_dict["level"] = 3
            attr_dict[item] = attr_data_dict


for item, item_subject in level_1_subjects_dict.items():
    create_level_1_attr_dict(item, item_subject)

for item, item_subject in level_2_subjects_dict.items():
    create_attr_dict(item, item_subject)

for item, item_subject in level_3_subjects_dict.items():
    create_attr_dict(item, item_subject)

print(attr_dict)


def get_data():
    print("in get data")
    scan_level_1_items()
    scan_level_2_items()
    scan_level_3_items()

    for item, item_subject in level_1_subjects_dict.items():
        create_level_1_attr_dict(item, item_subject)

    for item, item_subject in level_2_subjects_dict.items():
        create_attr_dict(item, item_subject)

    for item, item_subject in level_3_subjects_dict.items():
        create_attr_dict(item, item_subject)

    return attr_dict
