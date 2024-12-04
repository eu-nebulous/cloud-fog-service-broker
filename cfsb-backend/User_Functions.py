import os
import get_data as file
import random
import json
from datetime import datetime
import db.db_functions as db_functions

# Boolean_Variables = ['Extend offered network capacity', 'Extend offered processing capacity', 'Extend offered memory capacity',
#                      'Fog resources addition', 'Edge resources addition', 'Solid State Drive']
Boolean_Variables = [
    "fd871ec6-d953-430d-a354-f13c66fa8bc9", "dcedb196-2c60-4c29-a66d-0e768cfd698a",
    "0cf00a53-fd33-4887-bb38-e0bbb04e3f3e", "d95c1dae-1e22-4fb4-9cdc-743e96d0dddc",
    "8cd09fe9-c119-4ccd-b651-0f18334dbbe4", "7147995c-8e68-4106-ab24-f0a7673eb5f5", "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef"]

# Used to extract_SAL_node_candidate_data from Use Side for DataGrid
# def extract_SAL_node_candidate_data_Front(json_data):
#     default_criteria_list = ["cores", "ram", "disk", "memoryPrice", "price"]
#
#     if isinstance(json_data, dict):  # Single node dictionary
#         json_data = [json_data]  # Wrap it in a list
#
#     extracted_data = []
#     node_ids = []
#     node_names = []
#
#     for item in json_data:
#         hardware_info = item.get("hardware", {})
#         # Extract default criteria values
#         default_criteria_values = {criteria: hardware_info.get(criteria, 0.0) if criteria in hardware_info else item.get(criteria, 0.0) for criteria in default_criteria_list}
#
#         # Correctly extract the providerName from the cloud information
#         cloud_info = item.get("cloud", {})   # get the cloud info or default to an empty dict
#         api_info = cloud_info.get("api", {})
#         provider_name = api_info.get("providerName", "Unknown Provider")
#
#         # each item is now a dictionary
#         node_data = {
#             "nodeId": item.get("nodeId", ''),
#             "id": item.get('id', ''),
#             "nodeCandidateType": item.get("nodeCandidateType", ''),
#             **default_criteria_values,  # Unpack default criteria values into node_data
#             "hardware": hardware_info,
#             "location": item.get("location", {}),
#             "image": item.get("image", {}),
#             "providerName": provider_name
#         }
#         extracted_data.append(node_data)
#         node_ids.append(node_data["id"])
#
#         # print("Before create_node_name")
#         node_names.append(create_node_name(node_data))  # call create_node_name function
#         # print("After create_node_name")
#
#     return extracted_data, node_ids, node_names

def extract_SAL_node_candidate_data_Front(json_data):
    default_criteria_list = ["cores", "ram", "disk", "memoryPrice", "price"]

    if isinstance(json_data, dict):  # Single node dictionary
        json_data = [json_data]  # Wrap it in a list

    extracted_data = []
    node_ids = []
    node_names = []

    for item in json_data:
        hardware_info = item.get("hardware", {})
        # Extract default criteria values
        default_criteria_values = {criteria: hardware_info.get(criteria, 0.0) if criteria in hardware_info else item.get(criteria, 0.0) for criteria in default_criteria_list}

        cloud_info = item.get("cloud", {})   # get the cloud info or default to an empty dict
        node_type = item.get("nodeCandidateType", "")

        # extract the providerName from the cloud information
        if node_type == "EDGE":
            provider_name = "-"  # For "EDGE" type, set provider_name as "-"
        else:
            api_info = cloud_info.get("api", {})
            provider_name = api_info.get("providerName", "Unknown Provider")  # For other types, fetch from api_info

        # each item is now a dictionary
        node_data = {
            "nodeId": item.get("nodeId", ''),
            "id": item.get('id', ''),
            "nodeCandidateType": item.get("nodeCandidateType", ''),
            **default_criteria_values,  # Unpack default criteria values into node_data
            "hardware": hardware_info,
            "location": item.get("location", {}),
            "image": item.get("image", {}),
            "providerName": provider_name
        }
        extracted_data.append(node_data)
        node_ids.append(node_data["id"])

        # print("Before create_node_name")
        node_names.append(create_node_name(node_data))  # call create_node_name function
        # print("After create_node_name")

    return extracted_data, node_ids, node_names


# Used to create node names for DataGrid
def create_node_name(node_data):
    node_type = node_data.get("nodeCandidateType", "UNKNOWN_TYPE")

    # Initialize default values
    node_city = ""
    node_country = ""
    node_os_family = "Unknown OS"
    provider_name = node_data.get("providerName", "")

    # Safely access nested properties for city and country
    location = node_data.get("location")
    if location and "geoLocation" in location and location["geoLocation"]:
        geo_location = location["geoLocation"]
        node_city = geo_location.get("city", "")
        node_country = geo_location.get("country", "")

    image = node_data.get("image")
    if image and "operatingSystem" in image and image["operatingSystem"]:
        operating_system = image["operatingSystem"]
        node_os_family = operating_system.get("operatingSystemFamily", node_os_family)

    cores = node_data.get("cores", "")
    ram = node_data.get("ram", "")

    # Construct the node name with conditional inclusions
    node_name_parts = [node_type]
    if node_city and node_country:
        node_name_parts.append(f"{node_city}, {node_country}")

    if provider_name:
        node_name_parts.append(f"Provider: {provider_name}")

    node_name_parts.append(f"OS: {node_os_family}")

    if cores:
        node_name_parts.append(f"Cores: {cores} ")
    if ram:
        node_name_parts.append(f"RAM: {ram} ")

    node_name = " - ".join(part for part in node_name_parts if part)  # Only include non-empty parts
    return node_name

# Used to extract_SAL_node_candidate_data from App Side working with Optimizer
def extract_SAL_node_candidate_data(json_string):
    # print("Entered in extract_SAL_node_candidate_data")
    json_data = json.loads(json_string)
    # try:
    #     json_data = json.loads(json_string)  # json_data is a list of dictionaries
    # except json.JSONDecodeError as e:
    #     print(f"Error parsing JSON inside extract_SAL_node_candidate_data(): {e}")
    #     return [], 0, [], []

    extracted_data = []

    for item in json_data:
        # Ensure each item is a dictionary before accessing it
        if isinstance(item, dict):
            node_data = {
                "nodeId": item.get("nodeId", ''),
                "id": item.get('id', ''),
                "nodeCandidateType": item.get("nodeCandidateType", ''),
                "price": item.get("price", ''),
                "pricePerInvocation": item.get("pricePerInvocation", ''),
                "memoryPrice": item.get("memoryPrice", ''),
                "hardware": item.get("hardware", {})
            }
            extracted_data.append(node_data)
        else:
            print(f"Unexpected item format: {item}")

    number_of_nodes = len(extracted_data)
    node_ids = [node['id'] for node in extracted_data]
    node_names = [node['id'] for node in extracted_data]
    return extracted_data, node_ids, node_names


# Used to map the criteria from SAL's response with the selected criteria (from frontend)
def create_criteria_mapping():
    field_mapping = {
        # "Cost": "price",
        "Operating cost": "price",
        "Memory Price": "memoryPrice",
        "Number of CPU Cores": "cores",
        "Memory Size": "ram",
        "Storage Capacity": "disk"
    }
    return field_mapping


# Used to create the required structure for the Evaluation in process_evaluation_data endpoint
def transform_grid_data_to_table(json_data):
    grid_data = json_data.get('gridData', [])
    relative_wr_data = json_data.get('relativeWRData', [])
    immediate_wr_data = json_data.get('immediateWRData', [])
    node_names = json_data.get('nodeNames', [])
    node_ids = []

    # Initialize temporary dictionaries to organize the data
    temp_data_table = {}
    criteria_titles = []
    # Mapping for ordinal values
    ordinal_value_mapping = {"High": 3, "Medium": 2, "Low": 1}
    boolean_value_mapping = {"True": 1, "False": 0}

    for node in grid_data:
        # node_name = node.get('name')
        node_ids.append(node.get('id'))
        node_id = node.get('id')

        criteria_data = {}
        for criterion in node.get('criteria', []):
            title = criterion.get('title')
            value = criterion.get('value')
            data_type = criterion.get('data_type')

            if data_type == 1:  # Ordinal data type
                numeric_value = ordinal_value_mapping.get(value, None)
                if numeric_value is not None:
                    criteria_data[title] = numeric_value
            elif data_type == 5:  # Boolean data type
                boolean_value = boolean_value_mapping.get(value, None)
                if boolean_value is not None:
                    criteria_data[title] = boolean_value
            else:  # Numeric and other types
                try:
                    criteria_data[title] = float(value)
                except ValueError:
                    # Handle or log the error for values that can't be converted to float
                    pass

        temp_data_table[node_id] = criteria_data

        # Collect all criteria titles
        criteria_titles.extend(criteria_data.keys())

    # Remove duplicates from criteria titles
    criteria_titles = list(set(criteria_titles))

    # Initialize the final data table
    data_table = {title: [] for title in criteria_titles}

    # Populate the final data table
    for node_id, criteria_data in temp_data_table.items():
        for title, value in criteria_data.items():
            data_table[title].append(value)

    # Format relative weight restriction data
    formatted_relative_wr_data = []
    for relative_wr in relative_wr_data:
        formatted_relative_wr = {
            'LHSCriterion': relative_wr.get('LHSCriterion'),
            'Operator': relative_wr.get('Operator'),
            'Intense': relative_wr.get('Intense'),
            'RHSCriterion': relative_wr.get('RHSCriterion')
        }
        formatted_relative_wr_data.append(formatted_relative_wr)

    # Format immediate weight restriction data
    formatted_immediate_wr_data = []
    for immediate_wr in immediate_wr_data:
        formatted_immediate_wr = {
            'Criterion': immediate_wr.get('Criterion'),
            'Operator': immediate_wr.get('Operator'),
            'Value': immediate_wr.get('Value')
        }
        formatted_immediate_wr_data.append(formatted_immediate_wr)

    return data_table, formatted_relative_wr_data, formatted_immediate_wr_data, node_names, node_ids


# Used to save data for each application from Frontend
def save_app_data(json_data):
    # Extract app data and app_id
    app_data = json_data[0][0]  # Assuming the first element contains the app_id
    app_id = app_data['app_id']
    user_id = app_data['user_id']

    # Directory setup
    user_dir = f"app_dirs/{user_id}"
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    app_dir = f"app_dirs/{user_id}/{app_id}"
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # New data structure with additional attributes
    structured_data = {
        "app_id": app_id,
        "nodeNames": json_data[1],
        "selectedCriteria": json_data[2],
        "gridData": json_data[3],
        "relativeWRData": json_data[4],
        "immediateWRData": json_data[5],
        "results": json_data[6]
    }

    # Save the newly structured data to a JSON file
    # with open(os.path.join(app_dir, "data.json"), 'w', encoding='utf-8') as f:
    #     json.dump(structured_data, f, ensure_ascii=False, indent=4)
    with open(os.path.join(app_dir,  f"{app_id}_data.json"), 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)
    return app_data


# Used to check if a JSON file for a given application ID exists
def check_json_file_exists(app_id):
    app_dir = f"app_dirs/{app_id}" # The directory where the JSON files are stored
    file_path = os.path.join(app_dir, f"{app_id}_data.json")

    return os.path.exists(file_path)

def create_data_table(selected_criteria, extracted_data, field_mapping):
    # Initialize the data table with lists for each criterion
    data_table = {criterion: [] for criterion in selected_criteria}

    # Loop over each node in the extracted data
    for node in extracted_data:
        # For each selected criterion, retrieve the corresponding value from the node's data
        for criterion in selected_criteria:
            # Determine the field name using the mapping, defaulting to the criterion name itself
            field_name = field_mapping.get(criterion, criterion)
            value = None  # Default value if field is not found

            # Special case for hardware attributes
            if 'hardware' in node and field_name in node['hardware']:
                value = node['hardware'][field_name]
            elif field_name in node:
                value = node[field_name]

            # Replace zero value with 0.00001
            if value == 0:
                # value = 0.00001
                value = 10

            data_table[criterion].append(value)

    return data_table


# Used to convert RAM and # of Cores
def convert_data_table(created_data_table):
    # Check if 'Number of CPU Cores' exists in the dictionary and convert its values
    if 'Number of CPU Cores' in created_data_table:
        created_data_table['Number of CPU Cores'] = [1/x for x in created_data_table['Number of CPU Cores']]

    # Check if 'Memory Size' exists in the dictionary and convert its values
    if 'Memory Size' in created_data_table:
        created_data_table['Memory Size'] = [1/x for x in created_data_table['Memory Size']]

    return created_data_table

# Used to Append "Score" and "Rank" for each node in SAL's response JSON
def append_evaluation_results(sal_reply_body, scores_and_ranks):
    # Check if sal_reply_body is a string and convert it to a Python object
    if isinstance(sal_reply_body, str):
        sal_reply_body = json.loads(sal_reply_body)

    # Check if there is only one node and scores_and_ranks are empty
    if len(sal_reply_body) == 1 and not scores_and_ranks:
        # Directly assign score and rank to the single node
        sal_reply_body[0]["score"] = 1
        sal_reply_body[0]["rank"] = 1
        return sal_reply_body

    # Proceed if there are multiple nodes or scores_and_ranks is not empty
    # Create a dictionary mapping Ids to scores and ranks
    eval_results_dict = {result['Id']: (result['DEA Score'], result['Rank'])
                         for result in scores_and_ranks if scores_and_ranks}

    # Iterate over each node in sal_reply_body and append Score and Rank
    for node in sal_reply_body:
        node_id = node.get('id')  # Assuming the ID is directly under the node
        if node_id in eval_results_dict:
            score, rank = eval_results_dict[node_id]
            node["score"] = score
            node["rank"] = rank

    return sal_reply_body


def convert_value(value, criterion_info, is_matched):
    if criterion_info['type'] == 5:  # Boolean type
        return 1 if value else 0
    elif criterion_info['type'] == 1:  # Ordinal type
        if is_matched:  # For matched nodes, use the mapping
            ordinal_value_mapping = {"High": 3, "Medium": 2, "Low": 1}
            return ordinal_value_mapping.get(value, value)  # Use the value from mapping, or keep it as is if not found
        else:  # For unmatched nodes, assign default value
            return 1
    return value


# Used to read the saved application data CFSB when triggered by Optimizer
def read_application_data(app_id, sal_reply_body):
    app_dir = os.path.join("app_dirs", app_id)
    file_path = os.path.join(app_dir, f"{app_id}_data.json")

    data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = {}, [], [], [], []

    if isinstance(sal_reply_body, str):
        sal_reply_body = json.loads(sal_reply_body)

    if os.path.exists(file_path):
        print(f"JSON file found for application ID {app_id}.")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            selected_criteria = {criterion['title']: criterion for criterion in data.get('selectedCriteria', [])}

            # Define the default list criteria mapping
            default_list_criteria_mapping = {
                "Operating cost": "price",
                "Memory Price": "memoryPrice",
                "Number of CPU Cores": "cores",
                "Memory Size": "ram",
                "Storage Capacity": "disk"
            }

            for criterion in selected_criteria:
                data_table[criterion] = []

            matched_node_ids = [node['id'] for node in data.get('gridData', []) if node['id'] in [n['id'] for n in sal_reply_body]]
            unmatched_node_ids = [n['id'] for n in sal_reply_body if n['id'] not in matched_node_ids]

            # Process MATCHED nodes
            for node in data.get('gridData', []):
                if node['id'] in matched_node_ids:
                    node_ids.append(node['id'])
                    # node_names.append(node.get('name', 'Unknown'))
                    for crit, criterion_info in selected_criteria.items():
                        value = next((criterion['value'] for criterion in node['criteria'] if criterion['title'] == crit), None)
                        converted_value = convert_value(value, criterion_info, is_matched=True)
                        data_table[crit].append(converted_value)

            # Process UNMATCHED nodes
            for node_id in unmatched_node_ids:
                node_data = next((node for node in sal_reply_body if node['id'] == node_id), {})
                node_ids.append(node_id)
                for criterion, crit_info in selected_criteria.items():
                    mapped_field = default_list_criteria_mapping.get(criterion, '')
                    value = node_data.get(mapped_field, 0.001 if crit_info['type'] == 2 else False)
                    converted_value = convert_value(value, crit_info, is_matched=False)
                    data_table[criterion].append(converted_value)

            node_names = node_ids
            relative_wr_data, immediate_wr_data = data.get('relativeWRData', []), data.get('immediateWRData', [])

    else:  # There is not any node id match - Proceed only with the nodes from SAL's reply
        print(f"No JSON file found for application ID {app_id}. Proceed only with data from SAL.")
        extracted_data_SAL, node_ids_SAL, node_names_SAL = extract_SAL_node_candidate_data(sal_reply_body)
        selected_criteria = ["Number of CPU Cores", "Memory Size"]
        field_mapping = create_criteria_mapping()
        data_table = create_data_table(selected_criteria, extracted_data_SAL, field_mapping)
        # Assign relativeWRData and immediateWRData regardless of node ID matches
        relative_wr_data = []
        immediate_wr_data = []
        node_ids = node_ids_SAL
        node_names = node_ids

    return data_table, relative_wr_data, immediate_wr_data, node_names, node_ids


# Used to generate random values for DataGrid
def random_value_based_on_type(data_type, criterion_info=None):
    if data_type == 1:  # Ordinal
        # Assuming 'values' are part of criterion_info for ordinal types
        return random.choice(criterion_info.get('values', ["High", "Medium", "Low"]))
    elif data_type == 5:  # Boolean
        return random.choice([True, False])
    else:  # Numeric
        # Default case for numeric types
        return round(random.uniform(1, 100), 2)


# Used to parse Dummy JSON files for Review
def read_json_file_as_string(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


# Used to transform SAL's response before sending to DataGrid
# This version is designed to read the structure of SAL's response obtained from POSTMAN
def extract_node_candidate_data(json_file_path):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    extracted_data = []
    node_ids = []
    node_names = []

    for item in json_data:
        hardware_info = item.get("nodeCandidate", {}).get("hardware", {})
        node_data = {
            "name": item['name'],
            "id": item['id'],
            "nodeId": item.get("nodeCandidate", {}).get("nodeId"),
            "nodeCandidateType": item.get("nodeCandidate", {}).get("nodeCandidateType"),
            "price": item.get("nodeCandidate", {}).get("price", 0.0),
            "pricePerInvocation": item.get("nodeCandidate", {}).get("pricePerInvocation", 0.0),
            "memoryPrice": item.get("nodeCandidate", {}).get("memoryPrice", 0.0),
            "hardware": {
                "id": hardware_info.get("id"),
                "name": hardware_info.get("name"),
                "providerId": hardware_info.get("providerId"),
                "cores": hardware_info.get("cores"),
                "ram": hardware_info.get("ram") * 1024 if hardware_info.get("ram") else None,  # Assuming RAM needs conversion from GB to MB
                "disk": hardware_info.get("disk"),
                "fpga": hardware_info.get("fpga")
            }
        }
        extracted_data.append(node_data)
        node_ids.append(item['id'])
        node_names.append(item.get('name', ''))

    return extracted_data, node_ids, node_names

