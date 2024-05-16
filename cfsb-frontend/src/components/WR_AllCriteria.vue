<template>
  <div class="wr-container">
    <!-- Relative constraints section -->
    <div class="relative-constraints">
      <h3>Relative Constraints</h3>
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

        <input type="number" v-model.number="condition.value" :min="0" step="0.5" placeholder="Value" />

        <select v-model="condition.column2" @change="updateDropdowns(index)">
          <option value="" disabled>Select Criterion</option>
          <option v-for="col in availableColumns(index, 2)" :key="`2-${col}`" :value="col">{{ col }}</option>
        </select>
        <button @click="removeCondition(index)">-</button>
      </div>
      <button @click="addCondition">+ Add Relative Constraint</button>
    </div>
    <div class="immediate-constraints">
      <h3>Immediate Constraints</h3>
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

        <input type="number" v-model.number="immediateCondition.value" :min="0" step="0.1" placeholder="Value" />

        <button @click="removeImmediateCondition(index)">-</button>
      </div>

      <button @click="addImmediateCondition">+ Add Immediate Constraint</button>
    </div>
    <button @click="sendWRData">Run Evaluation</button>
  </div>
</template>

<script>
export const backendURL = process.env.VITE_BACKEND_URL;
const apiURL = backendURL;
import {useRouter} from 'vue-router';

export default {
  data() {
    return {
      receivedGridData: null,
      relativeConditions: [{column1: '', operator: '', value: 0, column2: ''}],
      criteria_titles: [], // This is populated with the column titles
      operators: ['>=', '=', '<='],
      immediateConditions: [{criterion: '', operator: '', value: 0}],
      operatorMapping: {
        '<=': -1,
        '=': 0,
        '>=': 1
      },
    };
  },
  mounted() {
    if (this.$route.params.data) {
      // Parse the JSON string back into an object
      this.receivedGridData = JSON.parse(this.$route.params.data);
    }

    const gridDataFromStorage = localStorage.getItem('gridData');
    const wrDataFromStorage = localStorage.getItem('wrData');
    const immediateWRDataFromStorage = localStorage.getItem('immediateWRData');

    if (gridDataFromStorage) {
      this.receivedGridData = JSON.parse(gridDataFromStorage);
    }

    if (wrDataFromStorage) {
      this.wrData = JSON.parse(wrDataFromStorage);
    }

    if (immediateWRDataFromStorage) {
      this.immediateConditions = JSON.parse(immediateWRDataFromStorage);
    } else {
      // Reset immediateConditions if there is no stored data
      this.immediateConditions = [{criterion: '', operator: '', value: 0}];
    }

    this.fetchCriteriaTitles();

  },
  methods: {
    fetchCriteriaTitles() {
      fetch(apiURL+'/get-criteria-titles')
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            this.criteria_titles = data;
          })
          .catch(error => {
            console.error('Error fetching criteria titles:', error);
          });
    },
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
      this.immediateConditions.push({criterion: '', operator: '', value: 0});
    },
    removeImmediateCondition(index) {
      this.immediateConditions.splice(index, 1);
    },
    async sendWRData() {
      const operatorMapping = {'<=': -1, '=': 0, '>=': 1};
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
      const RelativeWRData = validRelativeConditions.map(condition => ({
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

      // Prepare payload with filtered conditions
      const payload = {
        gridData: this.receivedGridData,
        wrData: RelativeWRData,
        immediateWRData: immediateWRData
      };


      try {
        const response = await fetch(apiURL+'/process-evaluation-data', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log('Response from backend:', data);

        // Check if the response was successful
        if (response.ok && data.status === 'success') {
          localStorage.setItem('gridData', JSON.stringify(this.receivedGridData));
          localStorage.setItem('wrData', JSON.stringify(RelativeWRData));

          this.$router.push({name: 'Results'});
        } else {
          console.error('Error in response:', data.message);
          alert('Failed to process data: ' + data.message);
        }
      } catch (error) {
        console.error('Error sending data to backend:', error);
        alert('Failed to send data to backend.');
      }
    }
  }
};
</script>

<style scoped>
.wr-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.condition-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

button {
  background-color: var(--main-color); /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: var(--secondary-color); /* Lighter shade of purple on hover */
  color: var(--main-color);
  border: 2px;
  border-color: var(--main-color);
}
</style>