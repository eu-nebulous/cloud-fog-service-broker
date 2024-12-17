# CFSB_Backend

Backend service providing criteria data

## Installation

Install requirements uning [pip](https://pip.pypa.io/en/stable/).

```bash
pip install -r requirements.txt
```

## Usage

```bash
flask --app app.py run
```
# Endpoints

#### returns the criteria in hierarchical list
/get_hierarchical_category_list

#### accepts and returns the selected cireteria
/process_selected_items
