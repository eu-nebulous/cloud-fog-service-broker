import numpy as np
import json
from scipy.optimize import linprog
from scipy.stats import rankdata

def perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids):
    print("--------------  Evaluation Process -------------------")
    # print("Evaluation begun with perform_evaluation():")
    # print("Data Table:", data_table)

    Boolean_Variables = ['Extend offered network capacity', 'Extend offered processing capacity', 'Extend offered memory capacity',
                         'Cloud resources addition', 'Fog resources addition', 'Edge resources addition', 'Solid State Drive',
                         'Attribute based Access Control supported(ABAC)', 'Role based Access Control (RBAC)', 'Audit Trailing',
                         'Firewall (UTM-unified threat management)', 'Process Transparency', 'Free Support',
                         'Encrypted Storage', 'Transport Layer Security', 'Desired Move Support']

    # # Normalize keys to handle potential mismatches (case sensitivity, whitespace)
    normalized_data_table_keys = [key.strip().lower() for key in data_table.keys()]
    normalized_boolean_variables = [var.strip().lower() for var in Boolean_Variables]
    # print("Normalized Data Table Keys:", normalized_data_table_keys)
    # print("Normalized Boolean Variables:", normalized_boolean_variables)

    # Identify boolean criteria
    boolean_criteria = [
        key for key, normalized_key in zip(data_table.keys(), normalized_data_table_keys)
        if normalized_key in normalized_boolean_variables
    ]
    print("Boolean Criteria:", boolean_criteria)
    # boolean_criteria =[]

    # boolean_criteria = [criterion for criterion in data_table if 'boolean' in criterion.lower()]
    # lower() Converts each column name to lowercase, and Checks if the substring 'boolean' exists in the lowercase version of the name
    num_of_dmus = len(next(iter(data_table.values())))  # Number of Nodes

    # Check if any boolean variables exist
    A_boolean= [] # Initialize the LHS Boolean Constraints
    if boolean_criteria:
        print("Boolean Criteria were chosen:", boolean_criteria)
        # Initialize a dictionary to store the categories for each node including a category for 0 true values
        # The first category has the nodes that have in all Boolean criteria False and the last the ones that hava in all Boolean criteria True values
        node_categories = {i: [] for i in range(len(boolean_criteria) + 1)}

        # Iterate over the list of nodes to count the '1' (True) values and assign node to categories
        for i in range(len(node_ids)):
            true_values_count = sum(data_table[boolean][i] for boolean in boolean_criteria)
            # print(true_count)
            node_categories[true_values_count].append(node_ids[i])

        # Remove the boolean criteria from the data_table
        for boolean in boolean_criteria:
            del data_table[boolean]

        # print("node_categories:", node_categories)
        # print(data_table)

        # Sort categories in descending order of true_count
        sorted_categories = sorted(node_categories, reverse=True)
        # Create constraint matrices
        A_boolean = []  # This is the inequality constraint matrix
        b_boolean = []  # This is the inequality constraint vector

        gamma = 0 # 1e-3 # Lower bound of the difference between the scores of nodes belonging to different category
        # Create constraints for each node in higher category imposing higher scores than the next lower category
        for higher_cat in range(len(sorted_categories) - 1):
            for node_high in node_categories[sorted_categories[higher_cat]]:
                for node_low in node_categories[sorted_categories[higher_cat + 1]]:
                    # Create a constraint for each pair of nodes (high > low)
                    high_scores = [-data_table[criterion][node_ids.index(node_high)] for criterion in data_table]
                    low_scores = [-data_table[criterion][node_ids.index(node_low)] for criterion in data_table]
                    # constraint = [h - l for h, l in zip(high_scores, low_scores)]
                    constraint = [h - l for h, l in zip(high_scores, low_scores)] + [0] * num_of_dmus
                    # print("high_scores:", high_scores)
                    # print("low_scores:", low_scores)
                    # print("constraint:", constraint)
                    A_boolean.append(constraint)
                    b_boolean.append(-gamma) # difference between the scores of nodes belonging to different category must be greater than gamma
        # print("A_boolean:", A_boolean)
        # print("b_boolean:", b_boolean)
        # print("node_categories:", node_categories)
        # print("sorted_categories:", sorted_categories)


    criteria_list = list(data_table.keys())  # print(criteria_list)
    criterion_index = {criterion: idx for idx, criterion in enumerate(criteria_list)}  # print(criterion_index)
    num_of_criteria = len(criteria_list) # Number of Criteria
    # Cols_No = num_of_criteria+num_of_dmus # Number of Criteria + No of Nodes (for deviations vars)

    # Initialize A and b matrices for inequality constraints, and A_eq and b_eq for equality constraints
    A = []
    b = []
    A_eq = []
    b_eq = []

    # Create the diagonal submatrix for deviation variables
    diagonal_submatrix = [[1 if i == j else 0 for j in range(num_of_dmus)] for i in range(num_of_dmus)]

    # Create the Constraints for each Node Score, combine data table values and the diagonal submatrix
    for i, row_values in enumerate(zip(*data_table.values())):
        # Combine the data table values and each row of diagonal submatrix
        combined_row = list(row_values) + diagonal_submatrix[i]
        A_eq.append(combined_row)  # Create the Constraint for the Score of each Node
    # Create b_eq as a list of ones
    b_eq = [1] * len(A_eq)  # Ones for RHS of the constraints, Number of ones equals the number of rows in A_eq

    # Add Relative Constraints to A or A_eq based on the given operator
    for constraint in relative_wr_data:
        lhs_index = criterion_index[constraint['LHSCriterion']] # Criterion at the left
        rhs_index = criterion_index[constraint['RHSCriterion']] # Criterion at the right
        intensity = constraint['Intense'] # value

        constraint_row = [0] * (num_of_criteria + num_of_dmus) # Initialize all positions with zeros
        if constraint['Operator'] == 1:  # case >=
            constraint_row[lhs_index] = -1   # Because the Default Constraint Type of Solver is <=
            constraint_row[rhs_index] = intensity # value
            A.append(constraint_row)
            b.append(0)
            print("constraint_row", constraint_row)
        elif constraint['Operator'] == -1:  # case <=
            constraint_row[lhs_index] = 1
            constraint_row[rhs_index] = -intensity # value
            A.append(constraint_row)
            b.append(0)
            print("constraint_row", constraint_row)
        elif constraint['Operator'] == 0:  # case equality
            constraint_row[lhs_index] = -1
            constraint_row[rhs_index] = intensity # value
            A_eq.append(constraint_row)
            b_eq.append(0)
            print("constraint_row", constraint_row)

    # Add Immediate Constraints to A or A_eq based on the given operator
    for constraint in immediate_wr_data:
        criterion_idx = criterion_index[constraint['Criterion']]
        intensity = constraint['Value']

        constraint_row = [0] * (num_of_criteria + num_of_dmus) # Initialize all positions with zeros
        if constraint['Operator'] == 1:  # case >=
            constraint_row[criterion_idx] = -1
            A.append(constraint_row)
            b.append(-intensity)
            print("Immediate Constraint >= :", constraint_row)
        elif constraint['Operator'] == -1:  # case <=
            constraint_row[criterion_idx] = 1
            A.append(constraint_row)
            b.append(intensity)
            print("Immediate onstraint <= :", constraint_row)
        elif constraint['Operator'] == 0:  # case =
            constraint_row[criterion_idx] = 1
            A_eq.append(constraint_row)
            b_eq.append(intensity)
            print("Immediate Constraint = :", constraint_row)

    # Add constraints derived from the Boolean Criteria if Boolean constrains were formed
    if A_boolean:
        print("Boolean Constraints are Found")
        A.extend(A_boolean)
        b.extend(b_boolean)

    # Convert lists to numpy arrays
    A = np.array(A, dtype=float) if A else None
    b = np.array(b, dtype=float) if b else None
    A_eq = np.array(A_eq, dtype=float) if A_eq else None
    b_eq = np.array(b_eq, dtype=float) if b_eq else None

    # print("A:", A)
    # print("b:", b)
    # print("A_eq:", A_eq)
    # print("b_eq:", b_eq)
    # print("---------------------------")

    # num_of_dmus = len(next(iter(data_table.values())))
    # Cols_No = len(criteria_list)
    epsilon = 1e-3  # Lower bound of the variables
    min_epsilon = 1e-5  # Minimum epsilon threshold

    # Objective Function, first num_of_criteria variables have coefficients 0, then num_of_dmus variables have -1
    c = np.array([0] * num_of_criteria + [1] * num_of_dmus, dtype=float)
    # Iteratively solve the LP problem
    while epsilon >= min_epsilon:
        # Update the bounds with the current epsilon
        bounds = [(epsilon, None) for _ in range(num_of_criteria)] + [(0, None) for _ in range(num_of_dmus)]

        # Solve the LP problem
        res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        # Check if the optimization was successful
        if res.success:
            print("-------------------------------------------------------")
            print(f"Optimization successful with epsilon = {epsilon}")
            break  # Exit the loop if a solution is found
        else:
            print(res.message)
            print(f"Infeasible with epsilon = {epsilon}, reducing epsilon...")
            print("-------------------------------------------------------")
            # Reduce epsilon
            epsilon /= 10

    MOP_Scores = []
    # Check if the optimization was successful after the loop
    if res.success:
        optimal_solution = res.x[:num_of_criteria] # Extract the first num_of_criteria variables from the optimal solution
        # print("Optimal Solution:", optimal_solution)
        # print(res.message)
        # print("---------------------------")

        # Calculate the Score for each node
        for dmu_index in range(num_of_dmus):
            # Gather the values for the current DMU
            dmu_values = [values[dmu_index] for values in data_table.values()]
            # print(f"Node {dmu_index} Values:", [values[dmu_index] for values in data_table.values()])
            # Calculate the score for the current DMU
            score = sum(optimal_solution[j] * dmu_values[j] for j in range(num_of_criteria))
            # Append the adjusted score to Scores
            MOP_Scores.append(score)
        # print("MOP_Scores: ", MOP_Scores)
        # Round the Scores to 2 decimal places
        MOP_Scores_Rounded = np.round(MOP_Scores, 4)
        # In case of Success then Rank the Scores using 'max' method for ties
        MOP_Scores_Ranked = len(MOP_Scores_Rounded) - rankdata(MOP_Scores_Rounded, method='max') + 1

        # Print the rounded scores and their corresponding ranks
        # print("Rounded Node Scores:", MOP_Scores_Rounded)
        # print("Corresponding Ranks:", Scores_Ranked)

        # Create a JSON object with title, id, Scores, and ranks
        results_json = [
            {
                "Title": node_names[i],
                "Id": node_ids[i],
                "Score": float(MOP_Scores_Rounded[i]), # Provide the Scores to be depicted in the Graph
                "Rank": int(MOP_Scores_Ranked[i])
            }
            for i in range(len(node_ids))
        ]
        # print(results_json)
        # Return successful results
        return {'LPstatus': 'feasible', 'results': results_json}

    else: # If no solution is found after all attempts, report failure
        print("The problem remains infeasible even with epsilon: ", epsilon)
        print(res.message)
        if A_boolean and (relative_wr_data or immediate_wr_data): # Rel. and/or Immed., and Boolean Constraints
            infeasibility_message = ("The optimization problem is infeasible with the given constraints.\n"
            "Please review the Relative and/or Immediate constraints.\n"
            "Otherwise, this should be attributed to the extra contraints derived from the Boolean criteria.\n"
            "In such a case, please make changes on the selected criteria or on their data.")
        elif not A_boolean and (relative_wr_data or immediate_wr_data): # Not Boolean, Rel. and/or Immed.
            infeasibility_message = ("The optimization problem is infeasible with the given constraints.\n"
            "Please review the Relative and/or Immediate constraints.")
        elif not relative_wr_data and not immediate_wr_data and A_boolean: # No Rel. and Immed., only Boolean Constraints
            infeasibility_message = ("The optimization problem is infeasible.\n"
                                    "This is caused by the extra contraints derived from the Boolean criteria.\n"
                                    "Please make changes on the selected criteria or on their data.")
        else: # For any other case of Infeasibility
            infeasibility_message = "The optimization problem is infeasible with the given constraints and data."

        # Return an appropriate JSON response indicating infeasibility
        infeasibility_response = {
            "message": infeasibility_message
        }
        print(infeasibility_response)
        return {'LPstatus': 'infeasible', 'results': infeasibility_response}



## Provided data
# data_table = {
#     'Provider Track record': [44.3, 37.53, 51.91, 86.56, 28.43],
#     'Agility': [41.8, 53.69, 91.3, 84.72, 58.37],
#     'Reputation': [2, 1, 3, 1, 3],
#     'Brand Name': [71.39, 83.11, 20.72, 91.07, 89.49],
#     'Free Support': [1, 0, 0, 1, 0],
#     # 'Boolean2': [0, 1, 0, 1, 0]
# }
#
# relative_wr_data = [
#     {'LHSCriterion': 'Reputation', 'Operator': 1, 'Intense': 1.5, 'RHSCriterion': 'Brand Name'},
#     {'LHSCriterion': 'Brand Name', 'Operator': -1, 'Intense': 1, 'RHSCriterion': 'Agility'},
#     {'LHSCriterion': 'Agility', 'Operator': 0, 'Intense': 0.5, 'RHSCriterion': 'Provider Track record'}
# ]
# immediate_wr_data = [
#     {'Criterion': 'Brand Name', 'Operator': 1, 'Value': 1e-3}
# ]
#
# # immediate_wr_data = [
# #     {'Criterion': 'Reputation', 'Operator': 1, 'Value': 0.2},
# #     {'Criterion': 'Reputation', 'Operator': -1, 'Value': 0.5},
# #     {'Criterion': 'Agility', 'Operator': -1, 'Value': 0.75},
# #     {'Criterion': 'Brand Name', 'Operator': 0, 'Value': 0.3}
# # ]
# #
# # # "immediate_wr_data":[{"Criterion":"Accountability","Operator":1,"Value":0.2}]}
# # # w1>=0.2 and w1<=0.5
#
# node_ids = ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5']
# node_names = ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5']
# Evaluation_JSON = perform_evaluation(data_table, relative_wr_data, immediate_wr_data, node_names, node_ids)

# Evaluation_JSON = perform_evaluation(data_table, [], [], node_names, node_ids)
# print("Evaluation_JSON:", Evaluation_JSON)


# data_table = {'A': [3, 1], 'B': [2, 1], 'C': [3, 1], 'D': [3, 2]}
# relative_wr_data: [{'LHSCriterion': 'Accountability', 'Operator': 1, 'Intense': 2, 'RHSCriterion': 'Compliance'}]
# immediate_wr_data: [{'Criterion': 'Compliance', 'Operator': 1, 'Value': 0.5}]
#
# node_ids = ['A', 'B', 'C', 'D']

# Evaluation_JSON = perform_evaluation(data_table, [], [], node_ids)
# pretty_json = json.dumps(Evaluation_JSON)
# print(pretty_json)
# print("Evaluation_JSON:", Evaluation_JSON)
# # print("Scores:", Scores)
# # print("Ranked Scores:", Scores_Ranked)