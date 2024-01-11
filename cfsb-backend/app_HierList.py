from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
import json
app = Flask(__name__, template_folder='templates')
#app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/get_hierarchical_category_list": {"origins": "http://localhost:8080"}})


hierarchy_data = hierarchical_list = [
    {
        "name": "Level 1 - Item 1",
        "children": [
            {
                "name": "Level 2 - Item 1.1",
                "children": [
                    {"name": "Level 3 - Item 1.1.1"},
                    {"name": "Level 3 - Item 1.1.2"},
                ],
            },
            {
                "name": "Level 2 - Item 1.2",
                "children": [
                    {"name": "Level 3 - Item 1.2.1"},
                    {"name": "Level 3 - Item 1.2.2"},
                ],
            },
        ],
    },
    {
        "name": "Level 1 - Item 2",
        "children": [
            {
                "name": "Level 2 - Item 2.1",
                "children": [
                    {"name": "Level 3 - Item 2.1.1"},
                    {"name": "Level 3 - Item 2.1.2"},
                ],
            },
            {
                "name": "Level 2 - Item 2.2",
                "children": [
                    {"name": "Level 3 - Item 2.2.1"},
                    {"name": "Level 3 - Item 2.2.2"},
                ],
            },
        ],
    },
    # Add more items as needed
]

# print(json.dumps(hierarchical_list, indent=2))
'''
def traverse_hierarchy(node, selected_items, required_count):
    if node['name'] in selected_items:
        required_count -= 1
    for child in node.get('children', []):
        required_count = traverse_hierarchy(child, selected_items, required_count)
    return required_count
'''
@app.route('/get_hierarchical_category_list')
def get_hierarchical_category_list():
    return jsonify(hierarchy_data)

@app.route('/process_selected_items', methods=['POST'])
def process_selected_items():
    try:
        data = request.get_json()
        selected_items = data.get('selectedItems', [])

        # Print selected items for debugging
        print("Selected Items:", selected_items)

        # Continue processing the selected items
        # For example, you can print or process the selected items here

        # Redirect to the show_selected_items route
        return redirect(url_for('show_selected_items', items=','.join(selected_items)))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/show_selected_items/<items>')
@cross_origin()
def show_selected_items(items):
    return render_template('selected_items.html', items=items.split(','))

if __name__ == '__main__':
    app.run(debug=True)