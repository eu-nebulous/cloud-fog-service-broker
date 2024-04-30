import numpy as np
import json
from scipy.optimize import linprog
from scipy.stats import rankdata

def perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids):
    # print("Evaluation begun with perform_evaluation():")
    # print("Data Table:", data_table)
    # Identify the boolean criteria columns by checking if all values are either 0 or 1
    # boolean_criteria = [criterion for criterion in data_table if set(data_table[criterion]) <= {0, 1}]
    boolean_criteria = [criterion for criterion in data_table if 'boolean' in criterion.lower()]
    # print("Boolean Criteria:", boolean_criteria)

    # Check if any boolean variables exist
    if boolean_criteria:
        print("Boolean variables exist:", boolean_criteria)
        # Initialize a dictionary to store the categories for each fog node including a category for 0 true values
        # The first category is for the all False and the last for the all True values
        fog_node_categories = {i: [] for i in range(len(boolean_criteria) + 1)}

        # Iterate over the list of nodes to count the '1' (True) values and assign categories
        for i in range(len(node_ids)):
            true_count = sum(data_table[boolean][i] for boolean in boolean_criteria)
            fog_node_categories[true_count].append(node_ids[i])

        # Remove the boolean criteria from the data_table
        for boolean in boolean_criteria:
            del data_table[boolean]

        print(fog_node_categories)
        print(data_table)

        # Sort categories in descending order of true_count
        sorted_categories = sorted(fog_node_categories, reverse=True)
        # Create constraint matrices
        A_boolean = []  # This is the inequality constraint matrix
        b_boolean = []  # This is the inequality constraint vector

        # Create constraints for each category having higher scores than the next lower category
        for higher_cat in range(len(sorted_categories) - 1):
            for fog_node_high in fog_node_categories[sorted_categories[higher_cat]]:
                for fog_node_low in fog_node_categories[sorted_categories[higher_cat + 1]]:
                    # Create a constraint for each pair of fog nodes (high > low)
                    high_scores = [-data_table[criterion][node_ids.index(fog_node_high)] for criterion in data_table]
                    low_scores = [-data_table[criterion][node_ids.index(fog_node_low)] for criterion in data_table]
                    constraint = [h - l for h, l in zip(high_scores, low_scores)]
                    A_boolean.append(constraint)
                    b_boolean.append(0)  # The score difference must be greater than 0
        # print("A_boolean:", A_boolean)
        # print("b_boolean:", b_boolean)

    # Reserve a variable (column) for each criterion
    criteria_list = list(data_table.keys())
    criterion_index = {criterion: idx for idx, criterion in enumerate(criteria_list)}

    # Initialize A and b matrices for inequality constraints, and A_eq and b_eq for equality constraints
    A = []
    b = []
    A_eq = []
    b_eq = []

    # Create the Constraint of each unit
    for row_values in zip(*data_table.values()):
        A.append(list(row_values))
    b.extend([1] * len(A))

    # Add weight restriction constraints to A or A_eq based on the operator
    for constraint in relative_wr_data:
        lhs_index = criterion_index[constraint['LHSCriterion']]
        rhs_index = criterion_index[constraint['RHSCriterion']]
        intensity = constraint['Intense']

        constraint_row = [0] * len(criteria_list)
        if constraint['Operator'] == 1:  # >=
            constraint_row[lhs_index] = -1
            constraint_row[rhs_index] = intensity
            A.append(constraint_row)
            b.append(0)
        elif constraint['Operator'] == -1:  # <=
            constraint_row[lhs_index] = 1
            constraint_row[rhs_index] = -intensity
            A.append(constraint_row)
            b.append(0)
        elif constraint['Operator'] == 0:  # equality
            constraint_row[lhs_index] = -1
            constraint_row[rhs_index] = intensity
            A_eq.append(constraint_row)
            b_eq.append(0)

    # Add immediate constraints to A or A_eq based on the given operator
    for constraint in immediate_wr_data:
        criterion_idx = criterion_index[constraint['Criterion']]
        intensity = constraint['Value']

        constraint_row = [0] * len(criteria_list)
        if constraint['Operator'] == 1:
            constraint_row[criterion_idx] = -1
            A.append(constraint_row)
            b.append(-intensity)
        elif constraint['Operator'] == -1:
            constraint_row[criterion_idx] = 1
            A.append(constraint_row)
            b.append(intensity)
        elif constraint['Operator'] == 0:
            constraint_row[criterion_idx] = 1
            A_eq.append(constraint_row)
            b_eq.append(intensity)

    # Add constraints coming from the Boolean variables
    if boolean_criteria:
        A.extend(A_boolean)
        b.extend(b_boolean)

    # Convert lists to numpy arrays
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    A_eq = np.array(A_eq, dtype=float) if A_eq else None
    b_eq = np.array(b_eq, dtype=float) if b_eq else None
    # print(A)
    # print(b)
    # print(A_eq)
    # print(b_eq)

    num_of_dmus = len(next(iter(data_table.values())))
    Cols_No = len(criteria_list)
    DEA_Scores = []
    # epsilon = 0.000001  # Lower bound of the variables
    epsilon = 0
    # Iterating over each DMU to Perform DEA
    for dmu_index in range(num_of_dmus):
        # Gathering values for the current DMU
        dmu_values = [values[dmu_index] for values in data_table.values()]

        # Forming the objective function coefficients
        c = -np.array(dmu_values)

        # Bounds for each variable
        bounds = [(epsilon, None) for _ in range(Cols_No)]

        # Solve the problem https://pythonguides.com/python-scipy-linprog/
        res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        # res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='simplex', callback=None, options={'presolve': True, 'autoscale': True, 'bland': True})

        DEA_Scores.append(-res.fun if res.success else None)

    # Check if the optimization problem is infeasible
    if not res.success:
        # Return an appropriate JSON response indicating infeasibility
        infeasibility_response = {
            "LPstatus": "infeasible",
            "message": f"The optimization problem is infeasible with the given weight restrictions. Please review them."
            # In case no weight restrictions are used, then the infeasibility is caused due to the data of the criteria. Please make changes on the data.
        }
        return infeasibility_response
        # return {'LPstatus': 'infeasible', 'results': infeasibility_response}

    # Round the DEA scores to 2 decimal places
    DEA_Scores_Rounded = np.round(DEA_Scores, 2)
    #In case of Success then Rank the DEA scores using 'max' method for ties
    DEA_Scores_Ranked = len(DEA_Scores_Rounded) - rankdata(DEA_Scores_Rounded, method='max') + 1

    # Print the rounded scores and their corresponding ranks
    # print("Rounded DEA Scores:", DEA_Scores_Rounded)
    # print("Corresponding Ranks:", DEA_Scores_Ranked)

    # Create a JSON object with titles, DEA scores, and ranks
    results_json = [
        {
            "Title": node_names[i],
            "Id": node_ids[i],
            "DEA Score": DEA_Scores[i],
            "Rank": int(DEA_Scores_Ranked[i])
        }
        for i in range(len(node_ids))
    ]

    # Return successful results
    return {'LPstatus': 'feasible', 'results': results_json}
    # return results_json, DEA_Scores, DEA_Scores_Ranked


# # Provided data
# data_table = {'2ad4bd97-d932-42a5-860e-e607a50f161d': [3, 1], 'e917581d-1a62-496b-9d2e-05972fe309e9': [2, 1], '78aca9a8-8c14-4c7d-af34-72cef0da992d': [3, 1], 'd2bddce9-4118-41a9-b528-3bac32b13312': [3, 2]}
# relative_wr_data: [{'LHSCriterion': 'Accountability', 'Operator': 1, 'Intense': 2, 'RHSCriterion': 'Compliance'}]
# immediate_wr_data: [{'Criterion': 'Compliance', 'Operator': 1, 'Value': 0.5}]
#
# node_ids = ['2ad4bd97-d932-42a5-860e-e607a50f161d', 'e917581d-1a62-496b-9d2e-05972fe309e9', '78aca9a8-8c14-4c7d-af34-72cef0da992d', 'd2bddce9-4118-41a9-b528-3bac32b13312']
#
# Evaluation_JSON = perform_evaluation(data_table, [], [], node_ids)
# pretty_json = json.dumps(Evaluation_JSON)


#
# data_table = {
#     'Provider Track record': [44.3, 37.53, 51.91, 86.56, 28.43],
#     'Agility': [41.8, 53.69, 91.3, 84.72, 58.37],
#     'Reputation': [2, 1, 3, 1, 3],
#     'Brand Name': [71.39, 83.11, 20.72, 91.07, 89.49],
#     'Boolean1': [1, 0, 1, 1, 0],
#     'Boolean2': [0, 1, 0, 1, 0]
# }
#
# relative_wr_data = [
#     {'LHSCriterion': 'Reputation', 'Operator': 1, 'Intense': 1.5, 'RHSCriterion': 'Brand Name'},
#     {'LHSCriterion': 'Brand Name', 'Operator': -1, 'Intense': 1, 'RHSCriterion': 'Agility'},
#     # {'LHSCriterion': 'Brand Name', 'Operator': 0, 'Intense': 0.5, 'RHSCriterion': 'Provider Track record'}
# ]
# immediate_wr_data = [
#     {'Criterion': 'Brand Name', 'Operator': 1, 'Value': 0.000000001}
#     ]
# # immediate_wr_data = [
# #     {'Criterion': 'Reputation', 'Operator': 1, 'Value': 0.2},
# #     {'Criterion': 'Reputation', 'Operator': -1, 'Value': 0.5},
# #     {'Criterion': 'Agility', 'Operator': -1, 'Value': 0.75},
# #     {'Criterion': 'Brand Name', 'Operator': 0, 'Value': 0.3}
# # ]
# #
# # # "immediate_wr_data":[{"Criterion":"Accountability","Operator":1,"Value":0.2}]}
# # # w1>=0.2 and w1<=0.5
# #
# node_ids = ['Fog Node 1', 'Fog Node 2', 'Fog Node 3', 'Fog Node 4', 'Fog Node 5']
#
# Evaluation_JSON = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_ids)
# print("Evaluation_JSON:", Evaluation_JSON)


# Evaluation_JSON = perform_evaluation(data_table, [], [], node_ids)
# pretty_json = json.dumps(Evaluation_JSON)
# print(pretty_json)
# print("Evaluation_JSON:", Evaluation_JSON)
# # print("DEA Scores:", DEA_Scores)
# # print("Ranked DEA Scores:", DEA_Scores_Ranked)