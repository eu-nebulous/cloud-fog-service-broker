from flask import Blueprint, request, jsonify, render_template, session
from User_Functions import *
import data_types as attr_data_types
from Evaluation import perform_evaluation
from data_types import get_attr_data_type
import db.db_functions as db_functions
import os
import time
import get_data as file
import activemq
import traceback
import logging
# logging.disable(logging.CRITICAL)

main_routes = Blueprint('main', __name__)

# List of items with Ordinal Data
Ordinal_Variables = ['attr-reputation', 'attr-assurance']
NoData_Variables = ['attr-security', 'attr-performance-capacity', 'attr-performance-suitability']
Cont_Variables = ['attr-performance', 'attr-financial', 'attr-performance-capacity-memory',
                  'attr-performance-capacity-memory-speed']

dummy_node_data = {
    "id": "8a7481d98e702b64018e702cbe070000",
    "nodeCandidateType": "EDGE",
    "jobIdForByon": "",
    "jobIdForEdge": "FCRnewLight0",
    "price": 0.0,
    "cloud": {
        "id": "edge",
        "endpoint": "",
        "cloudType": "EDGE",
        "api": "",
        "credential": "",
        "cloudConfiguration": {
            "nodeGroup": "",
            "properties": {}
        },
        "owner": "EDGE",
        "state": "",
        "diagnostic": ""
    },
    "location": {
        "id": "edge-location-KmVf4xDJKL7acBGc",
        "name": "",
        "providerId": "",
        "locationScope": "",
        "isAssignable": "",
        "geoLocation": {
            "city": "Warsaw",
            "country": "Poland",
            "latitude": 52.237049,
            "longitude": 21.017532
        },
        "parent": "",
        "state": "",
        "owner": ""
    },
    "image": {
        "id": "edge-image-KmVf4xDJKL7acBGc",
        "name": "edge-image-name-UBUNTU-UNKNOWN",
        "providerId": "",
        "operatingSystem": {
            "operatingSystemFamily": "UBUNTU",
            "operatingSystemArchitecture": "UNKNOWN",
            "operatingSystemVersion": 1804.00
        },
        "location": "",
        "state": "",
        "owner": ""
    },
    "hardware": {
        "id": "edge-hardware-KmVf4xDJKL7acBGc",
        "name": "",
        "providerId": "",
        "cores": 1,
        "ram": 1,
        "disk": 1.0,
        "fpga": 0,
        "location": "",
        "state": "",
        "owner": ""
    },
    "pricePerInvocation": 0.0,
    "memoryPrice": 0.0,
    "nodeId": "",
    "environment": ""
}


#Used in HomePage.vue to save app_id and user_id
# @main_routes.route('/save_ids', methods=['POST'])
# def save_ids():
#     data = request.json
#     app_id = data.get('app_id')
#     user_id = data.get('user_id')
#     print("user_id:", user_id)
#     # Respond back with a success message
#     return jsonify({"message": "IDs received successfully.", "app_id": app_id, "user_id": user_id})



#Used in CriteriaSelection.vue
@main_routes.route('/get_hierarchical_category_list')
def get_hierarchical_category_list():
    items_list = file.get_level_1_items()  # Assume this function returns the list correctly
    if items_list is not None:
        # Return the list as a JSON response
        return jsonify(items_list)
    else:
        # Return an empty list or an error message if items_list is None
        return jsonify([]), 404  # or return jsonify({"error": "No items found"}), 404

# Used in DataGrid.vue
@main_routes.route('/process_selected_criteria', methods=['POST'])
def process_selected_criteria():
    try:
        data = request.json
        selected_criteria = data.get('selectedItems', [])

        # application_id = data.get('app_id')
        # user_id = data.get('user_id')
        # print("user_id:", user_id)
        # print("application_id:", application_id)

        message_for_SAL = [{
            "type": "NodeTypeRequirement",
            "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"]}
            # ,{
            #     "type": "AttributeRequirement",
            #     "requirementClass": "hardware",
            #     "requirementAttribute": "cores",
            #     "requirementOperator": "GEQ",
            #     "value": "64"
            # },
            # {
            #     "type": "AttributeRequirement",
            #     "requirementClass": "hardware",
            #     "requirementAttribute": "ram",
            #     "requirementOperator": "GEQ",
            #     "value": "33000"
            # }
        ]
        body_json_string_for_SAL = json.dumps(message_for_SAL)

        RequestToSal = {
            "metaData": {"user": "admin"},
            "body": body_json_string_for_SAL
        }
        # print("RequestToSal:", RequestToSal)

        sal_reply = activemq.call_publisher(RequestToSal)
        nodes_data = json.loads(sal_reply) if isinstance(sal_reply, str) else sal_reply
        # print("nodes_data", nodes_data)

        extracted_data, node_ids, node_names = extract_SAL_node_candidate_data_Front(nodes_data)
        # print("extracted_data:", extracted_data)
        field_mapping = create_criteria_mapping()
        # print("field_mapping", field_mapping)

        default_list_criteria_mapping = {
                    # "Cost": "price",
                    "Operating cost": "price",
                    "Memory Price": "memoryPrice",
                    "Number of CPU Cores": "cores",
                    "Memory Size": "ram",
                    "Storage Capacity": "disk"
                }

        grid_data = {}

        for node_data in extracted_data:
            node_id = node_data.get('id')
            # print("Before create_node_name")
            node_name = create_node_name(node_data) if node_data else "Unknown"
            # print("After create_node_name")

            if node_id and node_id not in grid_data:
                grid_data[node_id] = {"name": node_name, "criteria": []}

            hardware_info = node_data.get('hardware', {}) # contains the values for criteria coming from SAL

            for criterion_key in selected_criteria:
                # print("criterion_key:", criterion_key)
                criterion_info = file.get_subject_data(file.SMI_prefix + criterion_key)   # It contains the titles of the criteria
                # print("criterion_info:", criterion_info)

                # Resolve title and then map title to field name
                criterion_data_type = get_attr_data_type(criterion_key)  # criterion_data_type: {'type': 1, 'values': ['Low', 'Medium', 'High']}
                # print("criterion_data_type:", criterion_data_type)
                criterion_title = criterion_info["title"]

                # Fetch the values of the selected default criteria
                if criterion_title in default_list_criteria_mapping:
                    SAL_criterion_name = field_mapping.get(criterion_title)  # Map the criterion title with the criterion name in SAL's reply
                    value = hardware_info.get(SAL_criterion_name, "N/A")     # Get the criterion values
                else:
                    # Handle other criteria (this part may need adjustment based on your actual data structure)
                    # value = "N/A"  # Placeholder for the logic to determine non-default criteria values
                    # Generate random or default values for rest criteria
                    type_value = criterion_data_type['type']
                    # print("type_value:", type_value)

                    if type_value == 1:
                        value = random.choice(["High", "Medium", "Low"])
                    elif type_value == 5:
                        value = random.choice(["True", "False"])
                    else:
                        value = round(random.uniform(1, 100), 2)

                criterion_data = {
                    "title": criterion_title,
                    "value": value,
                    "data_type": criterion_data_type  # criterion_data_type: {'type': 1, 'values': ['Low', 'Medium', 'High']}
                }
                grid_data[node_id]["criteria"].append(criterion_data)

        grid_data_with_names = [{
            'name': data["name"],
            'id': node_id,
            'criteria': data["criteria"]
        } for node_id, data in grid_data.items()]
        # print("grid_data_with_names:", grid_data_with_names)

        return jsonify({
            'success': True,
            'gridData': grid_data_with_names,
            'NodeNames': node_names
        })

    except Exception as e:
        print(f"Error processing selected items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Works by reading a JSON file with dummy data
# def process_selected_criteria():
#     try:
#         data = request.json
#         # Selected Criteria by the User from the List
#         selected_criteria = data.get('selectedItems', [])
#         # Extract app_id, user_id
#         application_id = data.get('app_id')  # Take it from local storage from frontend
#         # application_id = 'd535cf554ea66fbebfc415ac837a5828' #dummy application_id_optimizer
#         user_id = data.get('user_id') # Take it from local storage from frontend
#         print("user_id:", user_id)
#         print("application_id:", application_id)
#
#         ## Process SAL's Reply
#         # extracted_data, number_of_nodes, node_names = extract_node_candidate_data('dummy_data_node_candidates.json')
#         extracted_data, node_ids, node_names = extract_node_candidate_data('SAL_Response_11EdgeDevs.json')
#         print("extracted_data:", extracted_data)
#
#         # Use the create_criteria_mapping() to get the criteria mappings
#         field_mapping = create_criteria_mapping(selected_criteria, extracted_data)
#         grid_data = {name: [] for name in node_names}
#
#         # Prepare the data to be sent to DataGrid.vue
#         for node_data in extracted_data:
#             node_name = node_data.get('name')  # Using name to match
#             node_id = node_data.get('id')  # Extract the node ID
#             grid_data[node_name] = {"id": node_id, "criteria": []}
#
#             if node_name in grid_data:  # Check if node_name exists in grid_data keys
#                 for item in selected_criteria:
#                     criterion_data = {}
#                     criterion_data["data_type"] = get_attr_data_type(item)
#                     item_data_dict = file.get_subject_data(file.SMI_prefix + item)
#                     criterion_data["title"] = item_data_dict["title"]
#                     field_name = field_mapping.get(criterion_data["title"], item)
#
#                     # Check if the field_name is a direct key or nested inside 'hardware'
#                     if field_name in node_data:
#                         value = node_data[field_name]
#                     elif 'hardware' in node_data and field_name in node_data['hardware']:
#                         value = node_data['hardware'][field_name]
#                     else:
#                         # Generate random or default values for unmapped criteria or missing data
#                         item_data_type_value = criterion_data["data_type"].get('type')
#                         if item_data_type_value == 1:
#                             value = random.choice(["High", "Medium", "Low"])
#                         elif item_data_type_value == 5:
#                             value = random.choice(["True", "False"])
#                         else:
#                             value = round(random.uniform(1, 100), 2)
#
#                     criterion_data["value"] = value if value != 0 else 0.00001
#                     # grid_data[node_id].append(criterion_data)
#                     grid_data[node_name]["criteria"].append(criterion_data)
#
#         # Conversion to list format remains unchanged
#         # grid_data_with_names = [{'name': name, 'criteria': data} for name, data in grid_data.items()]
#         grid_data_with_names = [{'name': name, 'id': data["id"], 'criteria': data["criteria"]} for name, data in grid_data.items()]
#         print("grid_data_with_names:", grid_data_with_names)
#
#         # Send the comprehensive grid_data_with_names to the frontend
#         return jsonify({
#             'success': True,
#             'gridData': grid_data_with_names,
#             'NodeNames': node_names
#         })
#     except Exception as e:
#         print(f"Error processing selected items: {e}")
#         traceback.print_exc()
#         return jsonify({'success': False, 'error': str(e)}), 500



@main_routes.route('/process-evaluation-data', methods=['POST'])
def process_evaluation_data():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Received data is not in JSON format or 'Content-Type' header is not set to 'application/json'")

        # print("JSON in process_evaluation_data:", data)
        # Transform grid data to table and get node names directly from the function
        data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = transform_grid_data_to_table(data)

        # print("data_table FRONT:", data_table)
        # print("relative_wr_data:", relative_wr_data)
        # print("immediate_wr_data:", immediate_wr_data)
        # print("# node_names:", len(node_names))
        # print("# node_ids:", len(node_ids))

        # Convert RAM and Cores
        data_table = convert_data_table(data_table)
        # Run Optimization - Perform evaluation
        results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
        # print(results)
        # Return the results
        return jsonify({'status': 'success', 'results': results})

    except Exception as e:
        error_message = str(e)
        return jsonify({'status': 'error', 'message': error_message}), 500


#Creates a new user
@main_routes.route('/user', methods=['POST'])
def create_user():
    data = request.json
    result = db_functions.insert_user(data)
    return jsonify(result)


# Used in front end to authenticate the user
@main_routes.route('/login', methods=['POST'])
def select_user():
    data = request.json
    result = db_functions.get_user(data)
    return jsonify(result)


# Returns the user's apps
@main_routes.route('/apps', methods=['POST'])
def select_user_apps():
    data = request.json
    result = db_functions.get_user_apps(data)
    return jsonify(result)


# Creates a new app in db
@main_routes.route('/app/create', methods=['POST'])
def create_app():
    data = request.json
    result = db_functions.insert_app(data)
    return jsonify(result)


# Checks if app exists or inserts it in db
@main_routes.route('/app', methods=['POST'])
def check_for_app():
    data = request.json
    result = db_functions.get_app(data)
    if not result:
        data['title'] = "Demo App"
        data['description'] = "Demo App description"
        result = db_functions.insert_app(data)
    return jsonify(result)


# Get app from db
@main_routes.route('/app/get', methods=['POST'])
def get_app():
    data = request.json
    result = db_functions.get_app(data)
    return jsonify(result)


# Called by save project in .VUE
@main_routes.route('/app/save', methods=['POST'])
def save_app():
    data = request.get_json()
    result = save_app_data(data)
    return result


# Emulate ActMQ functionality
@main_routes.route('/test_sender', methods=['POST'])
def send():
    data = request.get_json()
    body = data['body']
    application_id = data['application_id']
    correlation_id = data['correlation_id']
    key = data['key']
    sender = activemq.test_send(data)
    return data
