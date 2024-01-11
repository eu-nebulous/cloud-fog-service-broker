from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
# import read_file
import get_data as file
import random
import json
import data_types as attr_data_types
from DEA import perform_evaluation
from data_types import get_attr_data_type

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# Store evaluation results globally
evaluation_results_global = {}
criteria_titles = []

# Global variable for the number of rows
NUMBER_OF_FOG_NODES = 7
def create_fog_node_titles(NUMBER_OF_FOG_NODES):
    return [f"Fog Node {i+1}" for i in range(NUMBER_OF_FOG_NODES)]

FOG_NODES_TITLES = create_fog_node_titles(NUMBER_OF_FOG_NODES)


# List of items with Ordinal Data
Ordinal_Variables = ['attr-reputation', 'attr-assurance']
NoData_Variables = ['attr-security', 'attr-performance-capacity', 'attr-performance-suitability']
Cont_Variables = ['attr-performance', 'attr-financial', 'attr-performance-capacity-memory',
                  'attr-performance-capacity-memory-speed']

# TODO boolean vars random choice generate
#Bool_Variables = []

@app.route('/get_hierarchical_category_list')
def get_hierarchical_category_list():
    data = file.get_level_1_items()
    # TODO order by something
    return jsonify(data)


# Receives the Selected Criteria and Generates data
@app.route('/process_selected_items', methods=['POST'])
def process_selected_items():
    try:
        data = request.json
        selected_items = data.get('selectedItems', [])
        global criteria_titles
        criteria_titles = [file.get_subject_data(file.SMI_prefix + item)["title"] for item in selected_items]

        # Generate random values for each selected item
        grid_data = {}

        for item in selected_items:
            item_data = {}
            item_data["data_type"] = get_attr_data_type(item)
            if item in Ordinal_Variables:
                # grid_data[item] = [random.choice(["High", "Medium", "Low"]) for _ in range(NUMBER_OF_FOG_NODES)]
                item_data["data_values"] = [random.choice(["High", "Medium", "Low"]) for _ in
                                            range(NUMBER_OF_FOG_NODES)]
                item_data_dict = file.get_subject_data(file.SMI_prefix + item)
                item_data["title"] = item_data_dict["title"]
            elif item in NoData_Variables:
                # Leave blank for this items
                item_data["data_values"] = ['' for _ in range(NUMBER_OF_FOG_NODES)]
                item_data_dict = file.get_subject_data(file.SMI_prefix + item)
                item_data["title"] = item_data_dict["title"]
            elif item in Cont_Variables:
                # grid_data[item] = [round(random.uniform(50.5, 312.3), 2) for _ in range(NUMBER_OF_FOG_NODES)]
                item_data["data_values"] = [round(random.uniform(50.5, 312.3), 2) for _ in range(NUMBER_OF_FOG_NODES)]
                item_data_dict = file.get_subject_data(file.SMI_prefix + item)
                item_data["title"] = item_data_dict["title"]
            else:
                # Default data generation for other items
                # grid_data[item] = [round(random.uniform(1, 100), 2) for _ in range(NUMBER_OF_FOG_NODES)]
                item_data["data_values"] = [round(random.uniform(1, 100), 2) for _ in range(NUMBER_OF_FOG_NODES)]
                item_data_dict = file.get_subject_data(file.SMI_prefix + item)
                item_data["title"] = item_data_dict["title"]
            grid_data[item] = item_data

        return jsonify({'success': True, 'gridData': grid_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/show_selected_items/<items>')
@cross_origin()
def show_selected_items(items):
    return render_template('selected_items.html', items=items.split(','))


@app.route('/get-criteria-titles', methods=['GET'])
def get_criteria_titles():
    return jsonify(criteria_titles)


@app.route('/get-fog-nodes-titles', methods=['GET'])
def get_fog_nodes_titles():
    return jsonify(FOG_NODES_TITLES)


# # Process the Grid Data and the WR Data
# @app.route('/process-evaluation-data', methods=['POST'])
# def process_evaluation_data():
#     global evaluation_results_global
#     try:
#         data = request.get_json()
#         data_table, wr_data = transform_grid_data_to_table(data)
#         print(data_table)
#         print(wr_data)
#         evaluation_results_global = perform_evaluation(data_table, wr_data,FOG_NODES_TITLES)
#         return jsonify({'status': 'success', 'message': 'Evaluation completed successfully'})
#     except Exception as e:
#         app.logger.error(f"Error processing evaluation data: {str(e)}")
#         return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/process-evaluation-data', methods=['POST'])
def process_evaluation_data():
    global evaluation_results_global
    try:
        # Log the incoming request data
        request_data = request.get_data(as_text=True)
        app.logger.info(f"Received data: {request_data}")

        data = request.get_json()
        if data is None:
            raise ValueError("Received data is not in JSON format or 'Content-Type' header is not set to 'application/json'")

        app.logger.info(f"Parsed JSON data: {data}")

        data_table, wr_data = transform_grid_data_to_table(data)
        app.logger.info(f"Data table: {data_table}, WR data: {wr_data}")

        evaluation_results_global = perform_evaluation(data_table, wr_data, FOG_NODES_TITLES)
        return jsonify({'status': 'success', 'message': 'Evaluation completed successfully'})
    except Exception as e:
        error_message = str(e)
        app.logger.error(f"Error processing evaluation data: {error_message}")
        return jsonify({'status': 'error', 'message': error_message}), 500


def transform_grid_data_to_table(json_data):
    grid_data = json_data.get('gridData', {}).get('gridData', {})
    wr_data = json_data.get('wrData', [])

    # if not wr_data:
    #     # return a default value
    #     wr_data = default_wr_data()

    data_table = {}
    row_count = None

    # Mapping for ordinal values
    ordinal_value_mapping = {"High": 3, "Medium": 2, "Low": 1}
    boolean_value_mapping = {"True": 2, "False": 1}

    for key, value in grid_data.items():
        title = value.get('title')
        data_values = value.get('data_values', [])

        # Replace ordinal values with their numeric counterparts
        numeric_data_values = [ordinal_value_mapping.get(val, val) for val in data_values]

        # Initialize row_count if not set
        if row_count is None:
            row_count = len(numeric_data_values)

        if len(numeric_data_values) != row_count:
            raise ValueError(f"Inconsistent row count for {title}")

        data_table[title] = numeric_data_values

    return data_table, wr_data


# Endpoint to transfer the results to Results.vue
@app.route('/get-evaluation-results', methods=['GET'])
def get_evaluation_results():
    return jsonify(evaluation_results_global)

if __name__ == '__main__':
    app.run(debug=True)
