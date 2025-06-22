from flask import Blueprint, request, jsonify, render_template, session
from node_functions import *
import data_types as attr_data_types
from node_evaluation import perform_evaluation
from data_types import get_attr_data_type
import db.db_functions as db_functions
import os
import time
import get_data as file
import message_handler
import traceback

main_routes = Blueprint('main', __name__)

# List of items with Ordinal Data
# Ordinal_Variables = ['attr-reputation', 'attr-assurance']
# NoData_Variables = ['attr-security', 'attr-performance-capacity', 'attr-performance-suitability']
# Cont_Variables = ['attr-performance', 'attr-financial', 'attr-performance-capacity-memory',
#                   'attr-performance-capacity-memory-speed']


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
        # skip criteria if any
        selected_criteria = skip_criteria_front(selected_criteria)
        print("-------------------------------------------------")

        # Get app_id and user_id already obtained in the Frontend from URL
        application_id = data.get('app_id')
        user_id = data.get('user_id')
        print("user_id:", user_id)
        print("application_id:", application_id)
        evaluation_settings = data.get('settings') # in evaluation_settings we pass data like policy and nodes mode
        policy = evaluation_settings[0]
        app_specific = evaluation_settings[1] # nodes_mode
        print("policy: ", policy + ", app_specific: ", app_specific) # nodes_mode

        # check for user defined criteria
        defined_criteria = []
        defined_criteria = file.get_defined_criteria(data.get('selectedItemsWithTypes', []))
        if defined_criteria:
            print("User defined criteria are found")
        else:
            print("No user defined criteria")

        # Prepare message to be sent to SAL
        message_for_SAL = [
            {
                "type": "NodeTypeRequirement",
                "nodeTypes": ["IAAS", "PAAS", "FAAS", "BYON", "EDGE", "SIMULATION"],
                # "nodeTypes": ["EDGE"],
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
        formatted_json = json.dumps(nodes_data, indent=4)
        with open('NodeCandidates.json', 'w') as file1:
            file1.write(formatted_json)
        print("Request from front-end (Printed from Routes)")

        # Check if there is any error in SAL's reply body
        if 'key' in nodes_data and any(keyword in nodes_data['key'].lower() for keyword in ['error', 'exception']):
            messageToDataGrid = "Error in SAL's reply" + nodes_data['message']
            print("Error found in SAL's message body:", messageToDataGrid)
            node_names = []
            grid_data_with_names = []
            providers = []
        else:  # No error found in SAL's reply body
            ###-------- Extract data from SAL's response --------###
            print("Use of SAL's response")
            extracted_data, node_ids, node_names, providers = extract_SAL_node_candidate_data_Front(nodes_data,app_specific,application_id)
            # print("SAL's extracted_data: ", extracted_data)
            ###-------- Extract data from SAL's response --------###

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
                        if criterion_title == 'Operating cost':
                            value = node_data.get('price', 0) or 100 # If 'price' is not present, it defaults to 100 (a large cost)
                        else:
                            value = hardware_info.get(SAL_criterion_name, "N/A") # For the rest criteria the values are in hardware
                    else:
                        # Handle other criteria
                        # value = "N/A"  # Placeholder for the logic to determine non-default criteria values
                        if criterion_key in file.get_defined_criteria_list():
                            # for defined criteria do not generate values
                            value = "N/A"
                        else:
                            # Generate low or default values for rest criteria
                            type_value = criterion_data_type['type']
                            # print("type_value:", type_value)

                            if type_value == 1:
                                # value = random.choice(["High", "Medium", "Low"])
                                value = "Low"
                            elif type_value == 5:
                                # value = random.choice(["True", "False"])
                                value = "False"
                            else:
                                # value = round(random.uniform(1, 100), 2)
                                value = 0.001

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
            'NodeNames': node_names,
            'definedCriteria': defined_criteria,
            'providers': providers
        })

    except Exception as e:
        print(f"Error processing selected items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



# Used for Evaluating the node candidates
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
        # if policy min then do the convert. else no
        evaluation_settings = data.get('evaluation_settings')  # in evaluation_settings we pass data like policy and nodes mode
        policy = evaluation_settings[0]
        # app_specific = evaluation_settings[1] #nodes_mode
        if policy == '0':
            print("Policy was min - Conversion was made")
            data_table = convert_data_table(data_table)  # Convert RAM and # of Cores, e.g. 1/X
            print("Converted Data Table", data_table)
        else:
            print("Policy was max - No Conversion was made")
        # Run Optimization - Perform evaluation
        results = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)
        # print("Results: ", results)
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


# Checks if app exists or insert it in db
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
    body = json.dumps(body)
    print(type(body))
    application_id = data['application_id']
    correlation_id = data['correlation_id']
    key = data['key']
    sender = activemq.call_otp_publisher(data)
    return data
