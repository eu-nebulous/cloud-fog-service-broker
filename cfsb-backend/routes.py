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
logging.disable(logging.CRITICAL)

main_routes = Blueprint('main', __name__)

# List of items with Ordinal Data
Ordinal_Variables = ['attr-reputation', 'attr-assurance']
NoData_Variables = ['attr-security', 'attr-performance-capacity', 'attr-performance-suitability']
Cont_Variables = ['attr-performance', 'attr-financial', 'attr-performance-capacity-memory',
                  'attr-performance-capacity-memory-speed']


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
        # Get selected criteria app_id and user_id sent from Frontend
        data = request.json
        selected_criteria = data.get('selectedItems', [])
        print("-------------------------------------------------")

        # Get app_id and user_id already obtained in the Frontend from URL
        application_id = data.get('app_id')
        user_id = data.get('user_id')
        print("user_id:", user_id)
        print("application_id:", application_id)

        # Prepare message to be sent to SAL
        message_for_SAL = [
            {
                "type": "NodeTypeRequirement",
                "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"],
                #"nodeTypes": ["EDGE"],
                "jobIdForEDGE": ""
                #"jobIdForEDGE": "FCRnewLight0"
            }
        ]

        # message_for_SAL =[{"type":"AttributeRequirement","requirementClass":"image","requirementAttribute":"operatingSystem.family","requirementOperator":"IN","value":"UBUNTU"},{"type":"AttributeRequirement","requirementClass":"image","requirementAttribute":"name","requirementOperator":"INC","value":"22"},{"type":"AttributeRequirement","requirementClass":"location","requirementAttribute":"name","requirementOperator":"EQ","value":"bgo"},{"type":"AttributeRequirement","requirementClass":"hardware","requirementAttribute":"ram","requirementOperator":"GEQ","value":"8192"},
        #  {"type":"AttributeRequirement","requirementClass":"hardware","requirementAttribute":"cores","requirementOperator":"GEQ","value":"4"}]

        body_json_string_for_SAL = json.dumps(message_for_SAL)

        RequestToSal = {
            "metaData": {"user": "admin"},
            "body": body_json_string_for_SAL
        }
        print("Request to Sal:", RequestToSal)

        sal_reply = activemq.call_publisher(RequestToSal)
        # Parse the JSON string to a Python object
        nodes_data = json.loads(sal_reply) if isinstance(sal_reply, str) else sal_reply
        # print("nodes_data", nodes_data)
        print("Request from front-end")

        # Check if there is any error in SAL's reply body
        if 'key' in nodes_data and any(keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
            messageToDataGrid = "Error in SAL's reply" + nodes_data['message']
            print("Error found in SAL's message body:", messageToDataGrid)
            node_names = []
            grid_data_with_names = []
        else:  # No error found in SAL's reply body

            ###--- For Review, use ONLY ONE block, SAL's response or JSON file ----------------------###

            ###-------- Extract data from SAL's response --------###
            print("Use of SAL's response")
            extracted_data, node_ids, node_names = extract_SAL_node_candidate_data_Front(nodes_data)
            # print("SAL's extracted_data: ", extracted_data)
            ###-------- Extract data from SAL's response --------###

            ###-------- Extract data from dummy JSON file --------###
            # print("Use of dummy JSON file")
            # json_file_path = 'dummySALresponse.json'
            # jsondata = read_json_file_as_string(json_file_path)
            # nodes_data = json.loads(jsondata)
            # if nodes_data:
            #     extracted_data, node_ids, node_names = extract_SAL_node_candidate_data_Front(nodes_data)
            ###-------- Extract data from dummy JSON file --------###

            ###--- For Review, use ONLY ONE block, SAL's response or JSON file ----------------------###


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
            messageToDataGrid = "True"

        return jsonify({
            'success': messageToDataGrid,
            'gridData': grid_data_with_names,
            'NodeNames': node_names
        })

    except Exception as e:
        print(f"Error processing selected items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



# Used for Evating the node candidates
@main_routes.route('/process-evaluation-data', methods=['POST'])
def process_evaluation_data():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Received data is not in JSON format or 'Content-Type' header is not set to 'application/json'")

        # print("JSON in process_evaluation_data:", data)
        # Transform grid data to table and get node names directly from the function
        data_table, relative_wr_data, immediate_wr_data, node_names, node_ids = transform_grid_data_to_table(data)

        print("data_table Frontend:", data_table)
        # print("relative_wr_data:", relative_wr_data)
        # print("immediate_wr_data:", immediate_wr_data)
        # print("# node_names:", len(node_names))
        # print("# node_ids:", len(node_ids))

        # Convert RAM and Cores
        data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
        # Run Optimization - Perform evaluation
        results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
        print("Results: ", results)
        print("-------------------------------------------------")
        # Return the results
        return jsonify({'status': 'success', 'results': results})

    except Exception as e:
        error_message = str(e)
        return jsonify({'status': 'error', 'message': error_message}), 500


# Creates a new user
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
    sender = activemq.call_otp_publisher(data)
    return data
