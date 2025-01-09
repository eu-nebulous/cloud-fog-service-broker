<template>
  <div class="wr-container">
    <!-- Relative constraints section -->
    <div class="relative-constraints">
      <h2>Relative Constraints</h2>
      <p class="description">
        Set relative constraints between the criteria. For example, "Weight of Criterion A >= 2* Weight of Criterion B".
      </p>
      <div v-for="(condition, index) in relativeConditions" :key="index" class="condition-row">
        <select v-model="condition.column1" @change="updateDropdowns(index)">
          <option value="" disabled>Select Criterion</option>
          <option v-for="col in availableColumns(index, 1)" :key="`1-${col}`" :value="col">{{ col }}</option>
        </select>

        <select v-model="condition.operator">
          <option value="" disabled>Select Operator</option>
          <option v-for="op in operators" :key="op" :value="op">{{ op }}</option>
        </select>

<!--        <select v-model="condition.operator">-->
<!--          <option value="" disabled>Select Operator</option>-->
<!--          <option v-for="(value, key) in operatorMapping" :key="key" :value="value">{{ key }}</option>-->
<!--        </select>-->

        <input type="number" v-model.number="condition.value" :min="0" step="0.5" placeholder="Value" />

        <select v-model="condition.column2" @change="updateDropdowns(index)">
          <option value="" disabled>Select Criterion</option>
          <option v-for="col in availableColumns(index, 2)" :key="`2-${col}`" :value="col">{{ col }}</option>
        </select>
        <button @click="removeCondition(index)">-</button>
      </div>
      <button @click="addCondition">+ Add Relative Constraint</button>
    </div>
    <!-- Separator Line -->
    <div class="separator-line"></div>
    <div class="immediate-constraints">
      <h2>Immediate Constraints</h2>
      <p class="description">
        Set immediate constraints on individual criteria. For example, "Weight of Criterion A >= 0.25".
      </p>
      <div v-for="(immediateCondition, index) in immediateConditions" :key="`immediate-${index}`" class="condition-row">
        <select v-model="immediateCondition.criterion">
          <option value="" disabled>Select Criterion</option>
          <option v-for="col in criteria_titles" :key="`immediate-${col}`" :value="col">{{ col }}</option>
        </select>

        <select v-model="immediateCondition.operator">
          <option value="" disabled>Select Operator</option>
          <option v-for="op in operators" :key="op" :value="op">{{ op }}</option>
        </select>

<!--        <select v-model="immediateCondition.operator">-->
<!--          <option value="" disabled>Select Operator</option>-->
<!--          <option v-for="(value, key) in operatorMapping" :key="key" :value="value">{{ key }}</option>-->
<!--        </select>-->

        <input type="number" v-model.number="immediateCondition.value" :min="0" step="0.1" placeholder="Value" />

        <button @click="removeImmediateCondition(index)">-</button>
      </div>

      <button @click="addImmediateCondition">+ Add Immediate Constraint</button>
    </div>
    <!-- Separator Line -->
    <div class="separator-line"></div>
    <div class="pt-4"> More information can be found <a href="https://github.com/eu-nebulous/nebulous/wiki/3.1.2-Resource-selection-and-preferences">here</a></div>
    <div class="button-container">
        <button @click="goBackToCriteriaSelection" class="bg-color-primary">Back to Criteria Selection</button>
        <button @click="sendWRData" class="bg-color-primary">Run Evaluation</button>
    </div>
    <div v-show="isLoading">
      <div class="alert alert-info">
        Running Optimization. Please wait
        <div class="spinner-border text-secondary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export const backendURL = import.meta.env.VITE_BACKEND_URL;
const apiURL = backendURL;
export default {
  data() {
    return {
      receivedGridData: null,
      relativeConditions: [{ column1: '', operator: '', value: 0, column2: '' }],
      criteria_titles: [], // This is populated with the column titles
      operators: ['>=', '=', '<='],
      immediateConditions: [{ criterion: '', operator: '', value: 0 }],
      operatorMapping: {
        '>=': 1,
        '=': 0,
        '<=': -1
      },
      errorMessage: '', // Add this line
      isLoading: null
    };
  },
  mounted() {
    // Prioritize data from route parameters
    if (this.$route.params.data) {
      // Parse the JSON string back into an object
      this.receivedGridData = JSON.parse(this.$route.params.data);
    } else {
      // Fallback to localStorage if route params are not available
      const gridDataFromStorage = localStorage.getItem('gridData');
      if (gridDataFromStorage) {
        this.receivedGridData = JSON.parse(gridDataFromStorage);
      }
    }

    // Continue with other localStorage checks
    const wrDataFromStorage = localStorage.getItem('wrData');
    const immediateWRDataFromStorage = localStorage.getItem('immediateWRData');

    if (wrDataFromStorage) {
      this.wrData = JSON.parse(wrDataFromStorage);
    }

    if (immediateWRDataFromStorage) {
      this.immediateConditions = JSON.parse(immediateWRDataFromStorage);
    } else {
      this.immediateConditions = [{ criterion: '', operator: '', value: 0 }];
    }

    // Retrieve selectedCriteria from local storage
    const selectedCriteriaJson = localStorage.getItem('selectedCriteria');
    if (selectedCriteriaJson) {
      try {
        const selectedCriteria = JSON.parse(selectedCriteriaJson);
        // Use selectedCriteria to populate criteria_titles and filter out boolean criteria (type 5)
        this.criteria_titles = selectedCriteria
            .filter(info => info.type !== 5)
            .map(info => info.title);
      } catch (e) {
        console.error('Error parsing selected criteria information:', e);
        this.$router.push({ name: 'CriteriaSelection' });
      }
    } else {
      console.error('Error: Selected criteria information not found in local storage.');
      this.$router.push({ name: 'CriteriaSelection' });
    }
  },
  methods: {
    addCondition() {
      this.relativeConditions.push({column1: '', column2: '', operator: '', value: 0});
    },
    removeCondition(index) {
      this.relativeConditions.splice(index, 1);
    },
    validateForm() {
      for (const condition of this.relativeConditions) {
        if (!condition.column1 || !condition.column2) {
          alert('Please select criteria for each relative constraint.');
          return false;
        }
        if (!condition.operator) {
          alert('Please select an operator for each relative constraint.');
          return false;
        }
        if (condition.value === null || condition.value === '') {
          alert('Please enter a numeric value for each relative constraint.');
          return false;
        }
        if (condition.value <= 0) {
          alert('The priority in each relative constraint must be greater than zero.');
          return false;
        }
      }

      const uniquePairs = new Set(
          this.relativeConditions.map(c => [c.column1, c.column2].sort().join('-'))
      );

      if (uniquePairs.size !== this.relativeConditions.length) {
        alert('Each pair of criteria can only be used once in a restriction!');
        return false;
      }

      return true;
    },
    updateDropdowns(index) {
      // May be used to update dropdown availability
    },
    availableColumns(index, dropdownNumber) {
      if (dropdownNumber === 1) {
        // For the first dropdown, filter out the column selected in the second dropdown
        return this.criteria_titles.filter(col => col !== this.relativeConditions[index].column2);
      } else {
        // For the second dropdown, filter out the column selected in the first dropdown
        return this.criteria_titles.filter(col => col !== this.relativeConditions[index].column1);
      }
    },
    // Add a method to validate the Immediate Constraints
    validateImmediateConstraints() {
      let criterionConstraints = {};

      // Iterate over immediate conditions and organize them by criterion
      for (const condition of this.immediateConditions) {
        if (!condition.criterion || !condition.operator) {
          continue; // Skip empty conditions
        }

        // Ensure value is greater than 0
        if (condition.value === null || condition.value === '' || condition.value <= 0) {
          alert(`The importance of criterion "${condition.criterion}" should be greater than 0.`);
          return false;
        }

        // Initialize the constraints list for the criterion if not already done
        if (!criterionConstraints[condition.criterion]) {
          criterionConstraints[condition.criterion] = {};
        }

        // Check for duplicate operators
        if (criterionConstraints[condition.criterion][condition.operator]) {
          alert(`You cannot use the same operator more than once for the criterion "${condition.criterion}".`);
          return false;
        }

        // Add the condition to the list for the criterion
        criterionConstraints[condition.criterion][condition.operator] = condition.value;
      }

      // Iterate over the constraints for each criterion and apply validation rules
      for (const [criterion, operators] of Object.entries(criterionConstraints)) {
        // Only one constraint allowed when using '=' operator
        if (operators['='] !== undefined && Object.keys(operators).length > 1) {
          alert(`Only one constraint allowed for '${criterion}' when using '=' operator.`);
          return false;
        }

        // Validate logical consistency between '>=' and '<=' values
        if (operators['>='] !== undefined && operators['<='] !== undefined) {
          const greaterThanOrEqualValue = parseFloat(operators['>=']);
          const lessThanOrEqualValue = parseFloat(operators['<=']);

          if (isNaN(greaterThanOrEqualValue) || isNaN(lessThanOrEqualValue)) {
            alert(`Invalid numeric values for the criterion "${criterion}".`);
            return false;
          }

          if (greaterThanOrEqualValue > lessThanOrEqualValue) {
            alert(`For the criterion "${criterion}", the value for '>=' must be less than or equal to the value for '<='.`);
            return false;
          }
        }
      }

      return true;
    },
    validateNonInvertedConditions() {
      let isValid = true;
      let conditionPairs = this.relativeConditions.map(c => [c.column1, c.column2].sort().join('-'));

      // Create a Set for unique pairs
      const uniquePairs = new Set(conditionPairs);

      if (uniquePairs.size !== conditionPairs.length) {
        // There are duplicates
        isValid = false;
      }

      return isValid;
    },
    addImmediateCondition() {
      this.immediateConditions.push({ criterion: '', operator: '', value: 0 });
    },
    removeImmediateCondition(index) {
      this.immediateConditions.splice(index, 1);
    },
    async sendWRData() {
      // Check if any relative or immediate condition is set
      const isAnyRelativeConditionSet = this.relativeConditions.some(condition => condition.column1 && condition.column2 && condition.operator);
      const isAnyImmediateConditionSet = this.immediateConditions.some(condition => condition.criterion && condition.operator);

      // Filter out incomplete or empty relative constraints
      const validRelativeConditions = this.relativeConditions.filter(condition => condition.column1 && condition.column2 && condition.operator);
      // Filter out incomplete or empty immediate constraints
      const validImmediateConditions = this.immediateConditions.filter(condition => condition.criterion && condition.operator);

      // Prompt the user if no conditions are set
      if (!isAnyRelativeConditionSet && !isAnyImmediateConditionSet) {
        const proceedWithoutWR = confirm("Would you like to proceed without imposing Weight Restrictions?");
        if (!proceedWithoutWR) {
          return; // User chose 'No', do nothing
        }
        // Clear data if user chose 'Yes'
        this.relativeConditions = [];
        this.immediateConditions = [];
      } else {
        // Validate conditions
        if ((isAnyRelativeConditionSet && (!this.validateForm() || !this.validateNonInvertedConditions())) ||
            (isAnyImmediateConditionSet && (!this.validateImmediateConstraints()))) {
          return; // Stop if validation fails
        }
      }

      // Process Relative constraints
      const relativeWRData = validRelativeConditions.map(condition => ({
        LHSCriterion: condition.column1,
        Operator: this.operatorMapping[condition.operator],
        Intense: condition.value,
        RHSCriterion: condition.column2
      }));

      // Process Immediate constraints
      const immediateWRData = validImmediateConditions.map(condition => ({
        Criterion: condition.criterion,
        Operator: this.operatorMapping[condition.operator],
        Value: condition.value
      }));

      // Retrieve node names from local storage
      let nodeNamesArray = [];
      const NodeNamesString = localStorage.getItem('NodeNames');
      if (NodeNamesString) {
        nodeNamesArray = JSON.parse(NodeNamesString);
      }

      // Prepare payload with filtered conditions
      const payload = {
        gridData: this.receivedGridData,
        relativeWRData: relativeWRData,
        immediateWRData: immediateWRData,
        nodeNames: nodeNamesArray,
        evaluation_settings: [localStorage.getItem('policyChoice'), localStorage.getItem('nodesModeChoice')]
      };
      console.log('Payload being sent to backend from WR.vue:', payload);
      this.isLoading = true;

      // Ask the backend to perform evaluation
      try {
        const response = await fetch(apiURL+'/process-evaluation-data', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          // If the HTTP response is not OK, throw an error
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Response from backend process-evaluation-data():', data);
        console.log('Response data.results.LPstatus:', data.results.LPstatus);

        //Loading message should stop here
        this.isLoading = false;

        // First, check the general status of the response to confirm the request was processed successfully
        // Check the LP problem's feasibility status
        if (data.status === 'success') {
          if (data.results.LPstatus === 'feasible') {
            localStorage.setItem('evaluationResults', JSON.stringify(data.results));
            localStorage.setItem('relativeWRData', JSON.stringify(relativeWRData));
            localStorage.setItem('immediateWRData', JSON.stringify(immediateWRData));

            // Navigate to Results.vue
            this.$router.push({ name: 'Results', params: { evaluationResults: data.results.results } });
          } else if (data.results.LPstatus === 'infeasible') {
            // Set the error message for infeasible LP solution
            this.errorMessage = data.results.message; // Accessing the message directly
            alert(this.errorMessage); // Show the message to the user via alert
          }
        } else {
          // Handle other unexpected 'status'
          this.errorMessage = 'An unexpected error occurred.';
        }
      } catch (error) {
        console.error('Error:', error);
        this.errorMessage = error.message || 'Failed to send data to backend.';
      }

    },
    goBackToCriteriaSelection() {
      this.$router.push({ name: 'CriteriaSelection' });
    }
  }
};
</script>

<style scoped>
input{height: 40px;}

.wr-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  //background-color: #e7e7e7;
}

select {
  background-color: #f5f3f3;
}

.condition-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

button {
  background-color: var(--main-color); /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: 2px solid;
  border-color:  #1B253BFF;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}


button:hover {
  background-color: #e9ebed;
  color: var(--main-color);
  border: 2px solid;
  border-color: var(--main-color);
}
</style>