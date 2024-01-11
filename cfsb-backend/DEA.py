import numpy as np
from scipy.optimize import linprog
from scipy.stats import rankdata

def perform_evaluation(data_table, wr_data,fog_nodes_titles):
    criteria_list = list(data_table.keys())
    criterion_index = {criterion: idx for idx, criterion in enumerate(criteria_list)}

    # Initialize A and b for inequality constraints, and A_eq and b_eq for equality constraints
    A = []
    b = []
    A_eq = []
    b_eq = []

    # Add data_table rows to A and b
    for row_values in zip(*data_table.values()):
        A.append(list(row_values))
    b.extend([1] * len(A))

    # Add weight restriction constraints to A or A_eq based on the operator
    for constraint in wr_data:
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
    epsilon = 0.0001  # Lower bound of the variables

    # Iterating over each DMU to Perform DEA
    for dmu_index in range(num_of_dmus):
        # Gathering values for the current DMU
        dmu_values = [values[dmu_index] for values in data_table.values()]

        # Forming the objective function coefficients
        c = -np.array(dmu_values)

        # Bounds for each variable
        bounds = [(epsilon, None) for _ in range(Cols_No)]

        # Solve the problem
        res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        DEA_Scores.append(-res.fun if res.success else None)

    # Rank the DEA scores using 'max' method for ties
    DEA_Scores_Ranked = len(DEA_Scores) - rankdata(DEA_Scores, method='max') + 1

    # Create a JSON object with titles, DEA scores, and ranks
    results_json = [
        {
            "Title": fog_nodes_titles[i],
            "DEA Score": DEA_Scores[i],
            "Rank": int(DEA_Scores_Ranked[i])
        }
        for i in range(len(fog_nodes_titles))
    ]

    return results_json
    # return DEA_Scores, DEA_Scores_Ranked

# # Provided data
# data_table = {
#     'Provider Track record': [44.3, 37.53, 51.91, 86.56, 28.43],
#     'Agility': [41.8, 53.69, 91.3, 84.72, 58.37],
#     'Reputation': [2, 1, 3, 1, 3],
#     'Brand Name': [71.39, 83.11, 20.72, 91.07, 89.49]
# }
#
# wr_data = [
#     {'LHSCriterion': 'Reputation', 'Operator': 1, 'Intense': 2.5, 'RHSCriterion': 'Brand Name'},
#     {'LHSCriterion': 'Brand Name', 'Operator': -1, 'Intense': 3, 'RHSCriterion': 'Agility'},
#     {'LHSCriterion': 'Brand Name', 'Operator': 0, 'Intense': 2, 'RHSCriterion': 'Provider Track record'}
# ]
#
# fog_nodes_titles = ['Fog Node 1', 'Fog Node 2', 'Fog Node 3', 'Fog Node 4', 'Fog Node 5']
#
# Evaluation_JSON = perform_evaluation(data_table, wr_data,fog_nodes_titles)
# print(Evaluation_JSON)
# # print("DEA Scores:", DEA_Scores)
# # print("Ranked DEA Scores:", DEA_Scores_Ranked)
