import os
import get_data as file
import random
import json
from datetime import datetime
import math

# Boolean_Variables = ['Extend offered network capacity', 'Extend offered processing capacity', 'Extend offered memory capacity',
#                      'Fog resources addition', 'Edge resources addition', 'Solid State Drive']
# Boolean_Variables = [
#     "fd871ec6-d953-430d-a354-f13c66fa8bc9", "dcedb196-2c60-4c29-a66d-0e768cfd698a",
#     "0cf00a53-fd33-4887-bb38-e0bbb04e3f3e", "d95c1dae-1e22-4fb4-9cdc-743e96d0dddc",
#     "8cd09fe9-c119-4ccd-b651-0f18334dbbe4", "7147995c-8e68-4106-ab24-f0a7673eb5f5", "c1c5b3c9-6178-4d67-a7e3-0285c2bf98ef"]


#################  BLOCK FOR FRONTEND #################

# Used to extract_SAL_node_candidate_data from User Side for DataGrid
def extract_SAL_node_candidate_data_Front(json_data_all, app_specific, app_id):
    # Specify the file name
    file_name = "EDGE_EXAMPLE1.json"
    # # Write JSON data to the file
    with open(file_name, "w") as json_file:
        json.dump(json_data_all, json_file, indent=4)  # Use indent for readable formatting
    # print(f"JSON data has been saved to {file_name}")
    if isinstance(json_data_all, dict):  # Single node dictionary
        json_data_all = [json_data_all]  # Wrap it in a list

    # app_specific = 1
    # print(app_specific)
    # app_id = "123456789"

    # Filter the json_data_all based on app_specific
    if app_specific == "0" or not app_specific: # When all nodes chosen, we give only the nodes for all applications.
        print("ENTERED app_specific == 0")
        # Keep only nodes for all applications  # json_data = [node for node in json_data_all if is_for_all_applications(node)]
        # Keep only nodes for all applications and IAAS (CLOUDS) nodes
        json_data = [
            node for node in json_data_all
            if is_for_all_applications(node) or node.get("nodeCandidateType", "") == "IAAS"
        ]
    else:
        # Keep only nodes for specific applications that match application_id, and IAAS nodes
        json_data = [
            node for node in json_data_all if matches_application_id(node, app_id)
            # if matches_application_id(node, app_id) or node.get("nodeCandidateType", "") == "IAAS"
        ]
        print("USE ONLY app_specific NODES")
    # Print or use the filtered data
    # print(json_data)

    extracted_data = []
    node_ids = []
    node_names = []
    providers = []  # Store the distinct providers for defined criteria
    # This is how each attribute is named in SAL's JSON
    default_criteria_list = ["cores", "ram", "disk", "memoryPrice", "cpuFrequency"]

    for item in json_data: # Loop only in data of nodes that can be used based on app_specific
        hardware_info = item.get("hardware", {})
        # Extract default criteria values
        default_criteria_values = {criteria: hardware_info.get(criteria, 0.0) if criteria in hardware_info else item.get(criteria, 0.0) for criteria in default_criteria_list}
        node_type = item.get("nodeCandidateType", "")

        # Skip busy nodes
        if (item.get("jobIdForEdge") not in [None, "any", "", "all-applications"]) or (item.get("jobIdForByon") not in [None, "any", "", "all-applications"]):
            continue

        # This is needed because the provider is treated differently by SAL for EDGE and IAAS
        if node_type == "EDGE":
            provider_name = hardware_info.get("providerId")  # For EDGE type retrieve the provider_name from providerId in hardware
            if not provider_name:  # Check if provider_name is empty
                provider_name = "Unknown"
        elif node_type == "IAAS":  # Cloud
            cloud_info = item.get("cloud", {})
            # print("cloud_info:", cloud_info)
            api_info = cloud_info.get("api", {})
            provider_name = api_info.get("providerName")  # For CLOUD type retrieve from api in cloud
            if not provider_name:  # Check if provider_name is empty
                provider_name = "Unknown"
        else:
            provider_name = "Unknown"  # For rest types set provider_name as "Unknown Provider"

        providers = find_distinct_providers(providers, provider_name)
        # print("Providers:", providers)

        # each item is now a dictionary
        node_data = {
            # "nodeId": item.get("nodeId", ''),
            "id": item.get('id', ''),
            "nodeCandidateType": item.get("nodeCandidateType", ''),
            **default_criteria_values,  # Unpack default criteria values into node_data
            "price": item.get('price', ''),
            "hardware": hardware_info,
            "location": item.get("location", {}),  # Needed to create the names shown in datagrid
            "image": item.get("image", {}),  # Needed to create the names shown in datagrid
            "providerName": provider_name
        }
        # print("Extract Front:", node_data)
        extracted_data.append(node_data)
        node_ids.append(node_data["id"])
        # print("Before create_node_name")
        node_names.append(create_node_name(node_data))  # call create_node_name function
        # print("After create_node_name")

    return extracted_data, node_ids, node_names, providers

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

# Used to return true or false if criteria should be skipped in frontend Datagrid
def skip_criteria_front(selected_criteria):
    criteria_to_skip = ['9f5706e3-08bd-412d-8d59-04f464e867a8']
    for criterion in selected_criteria:
        if criterion in criteria_to_skip:
            selected_criteria.remove(criterion)
    return selected_criteria

# Used to save data for each application from Frontend
def save_app_data(json_data):
    # Extract app data and app_id
    app_data = json_data[0][0]  # Assuming the first element contains the app_id
    app_id = app_data['app_id']
    user_id = app_data['user_id']
    policy = app_data['policy']
    app_specific = app_data['app_specific'] # nodes mode
    print("app specific = " , app_specific)
    if app_specific == '0':
        app_specific = False
    else:
        app_specific = True
    print("app specific = " , app_specific)
    print(type(app_specific))

    # Directory setup
    app_dir = f"app_dirs/{app_id}"
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # New data structure with additional attributes
    structured_data = {
        "app_id": app_id,
        "appSpecific": app_specific, # THE VALUE WILL BE GIVEN FROM THE GUI BY THE USER in nodes mode
        "policy": policy, # the policy given by the user - 0 is min, 1 is max
        "providerCriteria": json_data[1],
        "nodeNames": json_data[2],
        "selectedCriteria": json_data[3],
        "gridData": json_data[4],
        "relativeWRData": json_data[5],
        "immediateWRData": json_data[6],
        "results": json_data[7]
    }

    # Save the newly structured data to a JSON file
    # with open(os.path.join(app_dir, "data.json"), 'w', encoding='utf-8') as f:
    #     json.dump(structured_data, f, ensure_ascii=False, indent=4)
    with open(os.path.join(app_dir,  f"{app_id}_data.json"), 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)
    return app_data


#################  BLOCK FOR GENERAL PURPOSE #################
# Used to map the criteria from SAL's response with the selected criteria (from frontend)
# If additions here, then add it in node_dict_map() also!!!
def create_criteria_mapping():
    field_mapping = {
        # "Cost": "price",
        "Operating cost": "price",
        "Memory Price": "memoryPrice",
        "Number of CPU Cores": "cores",
        "Memory Size": "ram",
        "Storage Capacity": "disk",
        "Proximity to Data Source": "distance",
        # Add GPU, FPGA, CPU Frequency
    }
    return field_mapping

# This function maps the default criteria with the flattened keys from the node data (e.g. ram inside hardware will become hardware_ram)
def node_dict_map():
    field_mapping = {
        "price": "price", # Operating cost
        "memoryPrice": "memoryPrice",
        "cores": "hardware_cores",
        "ram": "hardware_ram", # memory size
        "disk": "hardware_disk", # storage capacity
        "distance_lat": "location_geoLocation_latitude",
        "distance_long": "location_geoLocation_longitude",
    }
    return field_mapping

# Function to normalize a list of values by the maximum value
def normalize_with_max(values):
    max_value = max(values)
    return [value / max_value for value in values]


# USED TO BRING TO SAME LEVEL SAL DATA OF EACH NODE - Inner fields are prefixed with the parent
def extract_node_from_node_data(y, prefix=''):
    flat_dict = {}
    for key, value in y.items():
        new_key = f"{prefix}{key}" if prefix == '' else f"{prefix}_{key}"
        if isinstance(value, dict):
            flat_dict.update(extract_node_from_node_data(value, new_key))
        else:
            flat_dict[new_key] = value
    return flat_dict

# Function to determine if a node is for all applications
def is_for_all_applications(node):
    name = node.get("hardware", {}).get("name", "")
    # print(f"Checking node name: {name}")  # Debugging
    if "|" not in name:
        return False
    parts = name.split("|")
    # print(f"Parts: {parts}")  # Debugging
    return len(parts) > 1 and parts[1] == "all-applications"

# Function to check if a node matches a specific application ID
def matches_application_id(node, application_id):
    """Check if the node matches the given application ID."""
    name = node.get("hardware", {}).get("name", "")
    if "|" not in name:
        return False  # If no "|" is present, it can't match an application ID
    parts = name.split("|")
    return len(parts) > 1 and parts[1] == application_id

# Used to convert RAM and # of Cores, i.e., 1/X
def convert_data_table(created_data_table):
    # Check if 'Number of CPU Cores' exists in the dictionary and convert its values
    if 'Number of CPU Cores' in created_data_table:
        created_data_table['Number of CPU Cores'] = [1/x for x in created_data_table['Number of CPU Cores']]
        created_data_table['Number of CPU Cores'] = normalize_with_max(created_data_table['Number of CPU Cores'])

    # Check if 'Memory Size' exists in the dictionary and convert its values
    if 'Memory Size' in created_data_table:
        created_data_table['Memory Size'] = [1/x for x in created_data_table['Memory Size']]
        created_data_table['Memory Size'] = normalize_with_max(created_data_table['Memory Size'])

    # Check if 'Proximity to Data Source' exists in the dictionary and convert its values
    if 'Proximity to Data Source' in created_data_table:
        created_data_table['Proximity to Data Source'] = [1/x for x in created_data_table['Proximity to Data Source']]
        created_data_table['Proximity to Data Source'] = normalize_with_max(created_data_table['Proximity to Data Source'])

    # Check if 'Operating cost' (Price) exists in the dictionary and convert its values
    if 'Operating cost' in created_data_table:
        created_data_table['Operating cost'] = [1/x for x in created_data_table['Operating cost']]
        created_data_table['Operating cost'] = normalize_with_max(created_data_table['Operating cost'])
    # Normalize the Data with column MAX
    # created_data_table = {key: normalize_with_max(values) for key, values in created_data_table.items()}

    return created_data_table

# Used to find distinct providers
def find_distinct_providers(providers, provider):
    if provider not in providers:
        providers.append(provider)
    return providers

# Used to parse Dummy JSON files for Review
def read_json_file_as_string(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


#################  BLOCK WHEN OPTIMIZER TRIGGERS CFSB #################
# Used to check if a JSON file for a given application ID exists
def check_json_file_exists(app_id):
    app_dir = f"app_dirs/{app_id}" # The directory where the JSON files are stored
    file_path = os.path.join(app_dir, f"{app_id}_data.json")

    return os.path.exists(file_path)

# Used to remove the additional fields in the request (sent by Optimizer) about the Locations
def remove_request_attribute(attribute_to_remove, data):
    print("try to remove " + attribute_to_remove)
    locations = []
    for dictionary in data:
        for key, value in dictionary.items():
            # print("key = " + str(key))
            # print("value = " + str(value))
            if key == "requirementAttribute":
                if value == attribute_to_remove:
                    locations = dictionary["value"]
                    data.remove(dictionary)
                    print("removed " + str(dictionary))
    return data, locations

# Used to read the saved application data CFSB when triggered by Optimizer
def read_application_data(app_id):
    relative_wr_data, immediate_wr_data, app_data = [], [], {}
    app_dir = os.path.join("app_dirs", app_id)
    file_path = os.path.join(app_dir, f"{app_id}_data.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        app_specific = data.get("appSpecific", False)
        policy = data.get("policy", 0) # read also app_specific and policy also
        app_data['policy'] = policy
        app_data['app_specific'] = app_specific # node mode
        # app_data['app_id'] = app_id

    # Get the saved Weight Restrictions
    relative_wr_data, immediate_wr_data = data.get('relativeWRData', []), data.get('immediateWRData', [])

    # Get all the criteria selected from the User
    selected_criteria = {criterion['title']: criterion for criterion in data.get('selectedCriteria', [])}
    print("selected criteria data in read_application_data:", selected_criteria)

    # Get the Info about Criteria given based on Provider, In the File, we store [providerData] { provider --> criterio --> value }
    provider_criteria = data.get("providerCriteria", {})
    # TO BE COMMENTED JUST USED FOR PRINTING
    if provider_criteria:
        print("provider_criteria:",provider_criteria)
        for provider, criteria in provider_criteria.items():
            print("Provider: " + provider)
            for criterion, value in criteria.items():
                print("Criterion: " + criterion + " is " + str(value))

    return app_data, selected_criteria, provider_criteria, relative_wr_data, immediate_wr_data

# USED TO EXTRACT SAL DATA WHEN TRIGGERED FROM OPTIMIZER
def extract_SAL_node_candidate_data_NEW(json_data_all, app_data, app_id, selected_criteria):
    """
    Extract node candidate data based on whether the node is specific to an app or usable by all apps.
    :param app_specific: 1 if filtering for app-specific nodes, 0 for all-app nodes.
    :param app_id: Application ID to match against when app_specific=True.
    """
    # Validate json_data_all
    if isinstance(json_data_all, str):
        try:
            json_data_all = json.loads(json_data_all)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}")

    if isinstance(json_data_all, dict):  # Single node dictionary
        json_data_all = [json_data_all]  # Wrap it in a list

    # application_id = "123456789"

    # Filter the json_data_all based on app_specific
    app_specific = app_data['app_specific']
    # app_specific = 1
    # print(app_specific)
    if app_specific == "0" or not app_specific: # All Applications
        print("ENTERED app_specific == 0")
        # Keep only nodes for all applications  # json_data = [node for node in json_data_all if is_for_all_applications(node)]
        # Keep only nodes for all applications and IAAS (CLOUDS) nodes
        json_data = [
            node for node in json_data_all
            if is_for_all_applications(node) or node.get("nodeCandidateType", "") == "IAAS"
        ]
    else:
        # Keep only nodes for specific applications that match application_id
        json_data = [
            # node for node in json_data_all if matches_application_id(node, app_id)
            # if matches_application_id(node, app_id) or node.get("nodeCandidateType", "") == "IAAS"
            node for node in json_data_all if isinstance(node, dict) and matches_application_id(node, app_id)
        ]
        print("USE ONLY app_specific NODES")

    # Print or use the filtered data
    # print("Data for eligible nodes in NEW:", json_data)

    extracted_data = []
    node_ids = []
    node_names = []
    providers = []  # Store the distinct providers for defined criteria

    # default_criteria_list : ["cores", "ram", "disk", "memoryPrice", "cpuFrequency"]
    default_criteria_list = create_criteria_mapping()

    for item in json_data:  # Loop only in data of nodes that can be used based on app_specific
        node_flat_dict = extract_node_from_node_data(item)
        # Skip busy nodes
        if (node_flat_dict["jobIdForEdge"] not in [None, "any", "", "all-applications"]) or (node_flat_dict["jobIdForByon"] not in [None, "any", "", "all-applications"]):
            continue
        if node_flat_dict["nodeCandidateType"] == "EDGE":
            node_flat_dict["nodeProviderId"] = node_flat_dict["hardware_providerId"]
        elif node_flat_dict["nodeCandidateType"] == "IAAS":
            node_flat_dict["nodeProviderId"] = node_flat_dict["cloud_api_providerName"]
        else:
            node_flat_dict["nodeProviderId"] = "Unknown"
        if node_flat_dict["nodeProviderId"] == "":
            node_flat_dict["nodeProviderId"] = "Unknown"
        # print("Node flat dict")
        # print(node_flat_dict)
        hardware_info = item.get("hardware", {})
        # Extract default criteria values else put ZERO value
        default_criteria_values = {criteria: hardware_info.get(criteria, 0.0) if criteria in hardware_info else item.get(criteria, 0.0) for criteria in default_criteria_list}

        node_type = item.get("nodeCandidateType", "")
        if node_type == "EDGE":
            provider_name = hardware_info.get("providerId")  # For EDGE type retrieve the provider_name from providerId in hardware
            if not provider_name:  # Check if provider_name is empty
                provider_name = "Unknown"
        elif node_type == "IAAS":  # Cloud
            cloud_info = item.get("cloud", {})
            # print("cloud_info:", cloud_info)
            api_info = cloud_info.get("api", {})
            provider_name = api_info.get("providerName")  # For CLOUD type retrieve from api in cloud
            if not provider_name:  # Check if provider_name is empty
                provider_name = "Unknown"
        else:
            provider_name = "Unknown"  # For rest types set provider_name as "Unknown Provider"

        # providers = find_distinct_providers(providers, provider_name)
        # print("Providers:", providers)

        # TODO:  We may THINK AGAIN WHAT WE SAVE INTO node_data POSSIBLE SAVING TWICE
        node_data = { # each item is now a dictionary
            # "nodeId": item.get("nodeId", ''),
            "id": item.get('id', ''),
            "nodeCandidateType": item.get("nodeCandidateType", ''),
            **default_criteria_values,  # Unpack default criteria values into node_data
            "price": item.get('price', ''),
            "hardware": hardware_info,
            "location": item.get("location", {}),
            # "image": item.get("image", {}),
            "providerName": provider_name
        }

        # extracted_data.append(node_data)
        extracted_data.append(node_flat_dict)
        node_ids.append(node_data["id"])
        # print("Before create_node_name")
        node_names.append(create_node_name(node_data))  # call create_node_name function

    # Extract node_ids and node_names
    # node_ids = [node['id'] for node in extracted_data]
    # node_names = [node.get('name', '') for node in json_data if isinstance(node, dict)]
    # print("Extracted from NEW:", extracted_data)
    return extracted_data, node_ids, node_names, providers

# Used to extract_SAL_node_candidate_data when Optimizer asks
def extract_SAL_node_candidate_data(json_string):
    # print("Entered in extract_SAL_node_candidate_data")
    json_data = json.loads(json_string)
    extracted_data = []

    for item in json_data:
        # Ensure each item is a dictionary before accessing it
        if isinstance(item, dict):
            # Skip busy nodes
            if (item.get("jobIdForEdge") not in [None, "any", "", "all-applications"]) or (item.get("jobIdForByon") not in [None, "any", "", "all-applications"]):
                continue
            node_data = {
                "nodeId": item.get("nodeId", ''),
                "id": item.get('id', ''),
                "nodeCandidateType": item.get("nodeCandidateType", ''),
                "price": item.get("price", ''),
                "pricePerInvocation": item.get("pricePerInvocation", ''),
                "memoryPrice": item.get("memoryPrice", ''),
                "hardware": item.get("hardware", {}),
                "location": item.get("location", {})
            }
            extracted_data.append(node_data)
        else:
            print(f"Unexpected item format: {item}")

    # number_of_nodes = len(extracted_data)
    node_ids = [node['id'] for node in extracted_data]
    node_names = [node['id'] for node in extracted_data]
    return extracted_data, node_ids, node_names

# Used to calculate the distance between Locations of Sources and Nodes
def calculate_distance(reference_point, raw_datasource_locations, default_reference_point=[0.0, 0.0]):
    # Earth's mean radius in kilometers
    EARTH_RADIUS_KM = 6371.0088

    # Validate and assign reference point
    if not (isinstance(reference_point, (list, tuple)) and len(reference_point) == 2 and
            -90 <= reference_point[0] <= 90 and -180 <= reference_point[1] <= 180):
        print(f"Invalid reference point: {reference_point}. Using default: {default_reference_point}")
        reference_point = default_reference_point

    # Parse the JSON string into a Python object
    try:
        datasource_locations = json.loads(raw_datasource_locations)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing datasource locations: {e}")

    # Filter and validate data source locations
    valid_locations = [
        [lat, lon] for lat, lon in datasource_locations
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
           -90 <= lat <= 90 and -180 <= lon <= 180
    ]

    if not valid_locations:
        raise ValueError("No valid data source locations provided.")

    # Haversine formula for distance calculation
    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])  # Convert to radians
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return EARTH_RADIUS_KM * c  # Distance in kilometers

    # Compute distances
    distances = [
        haversine(reference_point[0], reference_point[1], lat, lon)
        for lat, lon in valid_locations
    ]

    # Compute the average distance
    avg_distance = sum(distances) / len(distances) # in Kilometers
    distance = 1/avg_distance
    distance = distance * 10000
    return distance

def create_data_table(extracted_data, selected_criteria, provider_criteria, locations):
    field_mapping = create_criteria_mapping()  # Get the default criteria using the function
    node_dict_mapping = node_dict_map()
    # Initialize the data table with lists for each criterion
    data_table = {criterion: [] for criterion in selected_criteria}
    # 3 Types of criteria (Default and Distance), Providers, and Rest

    # Loop over each node in the extracted data
    for node in extracted_data:
        # print("Node Data:", node)
        # print("END Printing Node Data")
        # For each selected criterion, retrieve the corresponding value from the node's data
        for criterion, criterion_info in selected_criteria.items():
            # print("Criterion data")
            # print("Name = " +criterion_info["name"] + " and type = " + str(criterion_info["type"]))
            # Determine the field name using the mapping, defaulting to the criterion name itself
            field_name = field_mapping.get(criterion, criterion)
            # print("field_name = " + field_name)

            # value = 100  # Default value if field will not be found
            if criterion in field_mapping: # if criterion belong to the default ones
                # print(criterion + " exists in field mapping")
                if field_name in node_dict_mapping: # take its value from the node data
                    # print(field_name + " exists in node dict mapping and value = " + str(node[node_dict_mapping[field_name]]))
                    value = node[node_dict_mapping[field_name]]
                elif field_name == "distance": # calculate values for location
                    if locations: # if locations asked by optimizer
                        print("Check for locations")
                        if (node[node_dict_mapping["distance_lat"]] not in [None, ""]) and (
                                node[node_dict_mapping["distance_long"]] not in [None, ""]):
                            latitude = node[node_dict_mapping["distance_lat"]]
                            longitude = node[node_dict_mapping["distance_long"]]
                            reference_point = [latitude, longitude]
                            value = calculate_distance(reference_point, locations,
                                                                 default_reference_point=[0.0, 0.0])
                        else: # when node does not provide location data
                            value = 0.3 # Any antipodal distance on earth is approximately 20,037 kilometers, thus we considered 30k, that is 1/30 due to the conversion
                else:
                    print("Error in node dict mapping. create_criteria_mapping() and node_dict_map do not match")
            elif provider_criteria and (node["nodeProviderId"] in provider_criteria):
                # first check if this provider is in the providerCriteria in file
                node_provider = node["nodeProviderId"]
                print("Check for provider's "+ node_provider +" criteria")
                if criterion_info["name"] in provider_criteria[node_provider]:
                    # then check if for this provider, this criterio exists in the criteria matched with providers (e.g. reputation)
                    print(criterion_info["name"] + " exists for " + node_provider)
                    # get the criterion's value
                    stored_criteria_value = provider_criteria[node_provider][criterion_info["name"]]
                    print(stored_criteria_value)
                    value = stored_criteria_value
                else:
                    # Criterion does not exist in matched provider's criteria
                    print("Error else in provider criteria" + criterion_info["name"] + " does not exist for " + node_provider)
            else: # rest criteria that we do not HAVE DATA
                value = None

            # call convert_value
            converted_value = convert_value(value, criterion_info)
            data_table[criterion].append(converted_value)

    return data_table


# Used to Give Numerical values to Ordinal and Boolean for Evaluation
def convert_value(value: None, criterion_info):
    if criterion_info['type'] == 5:  # Boolean type
        return 1 if value else 0
    elif criterion_info['type'] == 1:  # Ordinal type
        if value:  # If value found
            ordinal_value_mapping = {"High": 3, "Medium": 2, "Low": 1}
            return ordinal_value_mapping.get(value) or 1  # Use the value from mapping, or assign default value
    elif criterion_info['type'] == 2:  # Numeric
        return value if value else 100 # A big value because then will be converted
    return value


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



#################  BLOCK NOT USED  #################
# Used to RETRIEVE THE PROVIDER NAME OF EACH NODE
def extract_node_provider(node):
    hardware_info = node.get("hardware", {})
    node_type = node.get("nodeCandidateType", "")
    if node_type == "EDGE":
        provider_name = hardware_info.get(
            "providerId")  # For EDGE type retrieve the provider_name from providerId in hardware
        if not provider_name:  # Check if provider_name is empty
            provider_name = "Unknown"
    elif node_type == "IAAS":  # Cloud
        cloud_info = node.get("cloud", {})
        # print("cloud_info:", cloud_info)
        api_info = cloud_info.get("api", {})
        provider_name = api_info.get("providerName")  # For CLOUD type retrieve from api in cloud
        if not provider_name:  # Check if provider_name is empty
            provider_name = "Unknown"
    else:
        provider_name = "Unknown"
    return provider_name

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
