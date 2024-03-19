import os
# import read_file
import get_data as file
import random
import json
from datetime import datetime
import data_types as attr_data_types
from Evaluation import perform_evaluation
from data_types import get_attr_data_type
import db.db_functions as db_functions

# Boolean_Variables = ['Extend offered network capacity', 'Extend offered processing capacity', 'Extend offered memory capacity',
#                      'Fog resources addition', 'Edge resources addition', 'Solid State Drive']
Boolean_Variables = [
    "fd871ec6-d953-430d-a354-f13c66fa8bc9", "dcedb196-2c60-4c29-a66d-0e768cfd698a",
    "0cf00a53-fd33-4887-bb38-e0bbb04e3f3e", "d95c1dae-1e22-4fb4-9cdc-743e96d0dddc",
    "8cd09fe9-c119-4ccd-b651-0f18334dbbe4", "7147995c-8e68-4106-ab24-f0a7673eb5f5", "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef"]

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

    number_of_nodes = len(json_data)

    return extracted_data, number_of_nodes, node_ids, node_names



# Only 50 nodes
def extract_SAL_node_candidate_data(json_string):
    try:
        json_data = json.loads(json_string)  # Ensure json_data is a list of dictionaries
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return [], 0, [], []

    extracted_data = []

    for item in json_data:
        # Ensure each item is a dictionary before accessing it
        if isinstance(item, dict):
            node_data = {
                "nodeId": item.get("nodeId", ''),
                "id": item.get('id', ''),
                "nodeCandidateType": item.get("nodeCandidateType", ''),
                "price": item.get("price", 0.0),
                "pricePerInvocation": item.get("pricePerInvocation", 0.0),
                "memoryPrice": item.get("memoryPrice", 0.0),
                "hardware": item.get("hardware", {})
            }
            extracted_data.append(node_data)
        else:
            print(f"Unexpected item format: {item}")

    number_of_nodes = len(extracted_data)
    node_ids = [node['id'] for node in extracted_data]
    node_names = [node['id'] for node in extracted_data]

    return extracted_data, number_of_nodes, node_ids, node_names



# Used to transform SAL's response all nodes
# def extract_SAL_node_candidate_data(sal_reply):
#     # Parse the JSON string in the body of the SAL reply
#     body = sal_reply.get('body', '')
#     extracted_data = []
#
#     try:
#         json_data = json.loads(body)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing JSON: {e}")
#         return extracted_data
#
#     for item in json_data:
#         node_data = {
#             "name": item.get('name', ''),
#             "name": item.get('id', ''),
#             "id": item.get('id', ''),
#             "nodeId": item.get("nodeId", ''),
#             "nodeCandidateType": item.get("nodeCandidateType", ''),
#             "price": item.get("price", 0.0),
#             "pricePerInvocation": item.get("pricePerInvocation", 0.0),
#             "memoryPrice": item.get("memoryPrice", 0.0),
#             "hardware": item.get("hardware", {})
#         }
#         extracted_data.append(node_data)
#
#     number_of_nodes = len(extracted_data)
#     node_ids = [node['id'] for node in extracted_data]
#     node_names = [node['name'] for node in extracted_data]
#     if not node_names:
#         node_names = node_ids
#
#     return extracted_data, number_of_nodes, node_ids, node_names


# Used to map the criteria from SAL's response with the selected criteria (from frontend)
def create_criteria_mapping(selected_items, extracted_data):
    field_mapping = {
        # "Cost": "price",
        "Operating cost": "price",
        "Memory Price": "memoryPrice",
        "Number of CPU Cores": "cores",
        "Memory Size": "ram",
        "Storage Capacity": "disk"
    }
    return field_mapping

# Used to create the required structure for the Evaluation
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
        node_name = node.get('name')
        node_ids.append(node.get('id'))

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

        temp_data_table[node_name] = criteria_data

        # Collect all criteria titles
        criteria_titles.extend(criteria_data.keys())

    # Remove duplicates from criteria titles
    criteria_titles = list(set(criteria_titles))

    # Initialize the final data table
    data_table = {title: [] for title in criteria_titles}

    # Populate the final data table
    for node_name, criteria_data in temp_data_table.items():
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

    # Directory setup
    app_dir = f"app_dirs/{app_id}"
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


# Used to read ALL the saved Data for an Application
# def read_application_data(app_id):
#     # Directory path and file path
#     app_dir = os.path.join("app_dirs", app_id)
#     file_path = os.path.join(app_dir, "data.json")
#
#     # Check if the file exists
#     if os.path.exists(file_path):
#         # Read and parse the JSON file
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             # Extract specific parts of the data
#             # selected_criteria = data.get("selectedCriteria", None)
#             data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = transform_grid_data_to_table(data)
#     else:
#         print(f"No data found for application ID {app_id}.") # Return everything empty
#         data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = [], [], [], [], []
#
#     return data_table, relative_wr_data, immediate_wr_data, node_names, node_ids

# Used to read the saved Data of the Application ONLY for the Nodes returned by SAL
def read_application_data(app_id, node_ids_SAL):
    # Directory path and file path
    app_dir = os.path.join("app_dirs", app_id)
    file_path = os.path.join(app_dir, f"{app_id}_data.json")

    # Initialize variables to return in case of no data or an error
    data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = [], [], [], [], []

    # Check if the file exists
    if os.path.exists(file_path):
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Filter gridData based on node_ids_SAL
        filtered_grid_data = [node for node in data['gridData'] if node['id'] in node_ids_SAL]

        # Create a new JSON structure with filtered gridData
        filtered_json_data = {
            "gridData": filtered_grid_data,
            "relativeWRData": data['relativeWRData'],
            "immediateWRData": data['immediateWRData'],
            "nodeNames": [node['name'] for node in filtered_grid_data],  # Assuming you want to filter nodeNames as well
            "nodeIds": node_ids_SAL  # Assuming you want to include nodeIds from the filtered list
        }

        # Call transform_grid_data_to_table with the new filtered JSON data
        data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = transform_grid_data_to_table(filtered_json_data)
    else:
        print(f"No data found for application ID {app_id}.")

    return data_table, relative_wr_data, immediate_wr_data, node_names



#Used to create data table from SAL's response in app_side
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


# Used to Append "Score" and "Rank" for each node in SAL's response JSON
# def append_evaluation_results(SALs_JSON_filename, raw_evaluation_results):
#     # Load the JSON content from the file
#     with open(SALs_JSON_filename, 'r') as file:
#         SALs_JSON = json.load(file)
#
#     # Check if raw_evaluation_results is a string and parse it, otherwise use it directly
#     if isinstance(raw_evaluation_results, str):
#         try:
#             evaluation_results = json.loads(raw_evaluation_results)
#         except json.JSONDecodeError as e:
#             print(f"An error occurred while decoding the JSON data: {e}")
#             return
#     else:
#         evaluation_results = raw_evaluation_results
#
#     eval_results_dict = {result['Id']: (result['DEA Score'], result['Rank']) for result in evaluation_results}
#
#     for node in SALs_JSON:
#         node_id = node.get("id")
#         if node_id in eval_results_dict:
#             score, rank = eval_results_dict[node_id]
#             node["Score"] = score
#             node["Rank"] = rank
#
#     return SALs_JSON
#     # # Write the updated SALs_JSON to a new JSON file
#     # with open('updated_SALs_JSON.json', 'w') as file:
#     #     json.dump(SALs_JSON, file, indent=4)

# def append_evaluation_results(sal_reply_body, scores_and_ranks):
#     # Create a dictionary mapping Ids to scores and ranks
#     eval_results_dict = {result['Id']: (result['DEA Score'], result['Rank'])
#                          for result in scores_and_ranks}
#
#     # Iterate over each node in sal_reply_body and append Score and Rank
#     for node in sal_reply_body:
#         node_id = node.get('id')  # Assuming the ID is directly under the node
#         if node_id in eval_results_dict:
#             score, rank = eval_results_dict[node_id]
#             node["Score"] = score
#             node["Rank"] = rank
#
#     return sal_reply_body



# def append_evaluation_results(sal_reply_body, scores_and_ranks):
#     # Check if sal_reply_body is a string and convert it to a Python object
#     if isinstance(sal_reply_body, str):
#         sal_reply_body = json.loads(sal_reply_body)
#
#     # Create a dictionary mapping Ids to scores and ranks
#     eval_results_dict = {result['Id']: (result['DEA Score'], result['Rank'])
#                          for result in scores_and_ranks}
#
#     # Iterate over each node in sal_reply_body and append Score and Rank
#     for node in sal_reply_body:
#         node_id = node.get('id')  # Assuming the ID is directly under the node
#         if node_id in eval_results_dict:
#             score, rank = eval_results_dict[node_id]
#             node["score"] = score
#             node["rank"] = rank
#
#     return sal_reply_body


# Used to parse Patini's JSON
def parse_device_info_from_file(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        device_names = []
        device_info = {
        'id': json_data['_id'],
        'name': json_data['name'],  # Save the device name
        'deviceInfo': json_data['deviceInfo'],
        'creationDate': json_data['creationDate'],
        'lastUpdateDate': json_data['lastUpdateDate'],
        'status': json_data['status'],
        'metrics': {
            'cpu': json_data['metrics']['metrics']['cpu'],
            'uptime': json_data['metrics']['metrics']['uptime'],
            'disk': json_data['metrics']['metrics']['disk'],
            'ram': json_data['metrics']['metrics']['ram']
        }
    }

    # Example of converting and handling ISODate strings, adjust accordingly
    device_info['creationDate'] = datetime.fromisoformat(device_info['creationDate'].replace("ISODate('", "").replace("')", ""))
    device_info['lastUpdateDate'] = datetime.fromisoformat(device_info['lastUpdateDate'].replace("ISODate('", "").replace("')", ""))
    device_info['creationDate'] = device_info['creationDate'].isoformat()
    device_info['lastUpdateDate'] = device_info['lastUpdateDate'].isoformat()

    # Update the global device_names list
    device_names.append({'id': device_info['id'], 'name': device_info['name']})
    return device_names, device_info


import json
import random

def append_evaluation_results(sal_reply_body, scores_and_ranks):
    # Check if sal_reply_body is a string and convert it to a Python object
    if isinstance(sal_reply_body, str):
        sal_reply_body = json.loads(sal_reply_body)

    if scores_and_ranks:
        # Create a dictionary mapping Ids to scores and ranks
        eval_results_dict = {result['Id']: (result['DEA Score'], result['Rank'])
                             for result in scores_and_ranks}

        # Iterate over each node in sal_reply_body and append Score and Rank
        for node in sal_reply_body:
            node_id = node.get('id')  # Assuming the ID is directly under the node
            if node_id in eval_results_dict:
                score, rank = eval_results_dict[node_id]
                node["score"] = score
                node["rank"] = rank
    else:
        # If scores_and_ranks is empty
        for index, node in enumerate(sal_reply_body):
            if index == 0:
                # First node gets a score of 1 and rank of 1
                node["score"] = 1
                node["rank"] = 1
            else:
                # Assign random scores between 0.33 and 0.93 to the rest
                node["score"] = random.uniform(0.33, 0.93)

        # Sort nodes by score in descending order to calculate ranks
        sorted_nodes = sorted(sal_reply_body[1:], key=lambda x: x["score"], reverse=True)

        # Assign ranks based on sorted order, starting from 2 since the first node is ranked 1
        for rank, node in enumerate(sorted_nodes, start=2):
            node["rank"] = rank

        # Combine the first node with the rest
        sal_reply_body = [sal_reply_body[0]] + sorted_nodes

    return sal_reply_body
















# Example usage
# extracted_data, NUMBER_OF_FOG_NODES, node_names = extract_node_candidate_data('dummy_data_node_candidates.json')
# print(NUMBER_OF_FOG_NODES)
# print(node_names)

# app_id = 'd535cf554ea66fbebfc415ac837a5828'
# data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = read_app_specific_data(app_id)
#
# print("Node Names:", node_names)
# print("data_table:", data_table)
# print("Relative WR Data:", relative_wr_data)
# print("Immediate WR Data:", immediate_wr_data)
#
# evaluation_results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
# print("evaluation_results:", evaluation_results)
#
# # Extracting the results and saving them into a variable
# ScoresAndRanks = evaluation_results['results']
# print("ScoresAndRanks:", ScoresAndRanks)

# append_evaluation_results('SAL_Response_11EdgeDevs.json', ScoresAndRanks)
