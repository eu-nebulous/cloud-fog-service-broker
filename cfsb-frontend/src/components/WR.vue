<template>
  <div class="wr-container">
    <div v-for="(condition, index) in conditions" :key="index" class="condition-row">
      <select v-model="condition.column1" @change="updateDropdowns(index)">
        <option value="" disabled>Select Criterion</option>
        <option v-for="col in availableColumns(index, 1)" :key="`1-${col}`" :value="col">{{ col }}</option>
      </select>

      <select v-model="condition.operator">
        <option value="" disabled>Select Operator</option>
        <option v-for="op in operators" :key="op" :value="op">{{ op }}</option>
      </select>

      <input type="number" v-model.number="condition.value" :min="0" placeholder="Value" />

      <select v-model="condition.column2" @change="updateDropdowns(index)">
        <option value="" disabled>Select Criterion</option>
        <option v-for="col in availableColumns(index, 2)" :key="`2-${col}`" :value="col">{{ col }}</option>
      </select>

      <button @click="removeCondition(index)">-</button>
    </div>

    <button @click="addCondition">+</button>
    <!-- <button @click.prevent="sendWRData">Run Evaluation</button> -->
    <button @click="sendWRData">Run Evaluation</button>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
export default {
  data() {
    return {
      receivedGridData: null,
      conditions: [{ column1: '', operator: '', value: 0, column2: '' }],
      criteria_titles: [], // This is populated with the column titles
      operators: ['>=', '=', '<='],
    };
  },
  mounted() {
    if (this.$route.params.data) {
      // Parse the JSON string back into an object
      this.receivedGridData = JSON.parse(this.$route.params.data);
    }
    console.log('WR.vue Received gridData:', this.receivedGridData);
    this.fetchCriteriaTitles();
  },
  methods: {
    fetchCriteriaTitles() {
      fetch('http://127.0.0.1:5000/get-criteria-titles')
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
      this.conditions.push({column1: '', column2: '', operator: '', value: 0});
    },
    removeCondition(index) {
      this.conditions.splice(index, 1);
    },
    validateForm() {
      for (const condition of this.conditions) {
        if (!condition.operator) {
          alert('Please select an operator for each condition.');
          return false;
        }
        if (condition.value === null || condition.value === '') {
          alert('Please enter a numeric value for each.');
          return false;
        }
        if (condition.value < 0) {
          alert('Values cannot be less than zero.');
          return false;
        }

        const uniquePairs = new Set(
            this.conditions.map(c => [c.column1, c.column2].sort().join('-'))
        );

        if (uniquePairs.size !== this.conditions.length) {
          alert('Each pair of criteria can only be used once in a restriction!');
          return false;
        }
      }
      return true;
    },
    updateDropdowns(index) {
      // May be used to update dropdown availability
    },
    availableColumns(index, dropdownNumber) {
      if (dropdownNumber === 1) {
        // For the first dropdown, filter out the column selected in the second dropdown
        return this.criteria_titles.filter(col => col !== this.conditions[index].column2);
      } else {
        // For the second dropdown, filter out the column selected in the first dropdown
        return this.criteria_titles.filter(col => col !== this.conditions[index].column1);
      }
    },
    validateNonInvertedConditions() {
      let isValid = true;
      let conditionPairs = this.conditions.map(c => [c.column1, c.column2].sort().join('-'));

      // Create a Set for unique pairs
      const uniquePairs = new Set(conditionPairs);

      if (uniquePairs.size !== conditionPairs.length) {
        // There are duplicates
        isValid = false;
      }

      return isValid;
    },
    async sendWRData() {
      // Check if any condition is set
      const isAnyConditionSet = this.conditions.some(condition => condition.column1 && condition.column2 && condition.operator);

      // If no conditions are set, prompt the user
      if (!isAnyConditionSet) {
        const proceedWithoutWR = confirm("Would you like to proceed without imposing Weight Restrictions?");
        if (!proceedWithoutWR) {
          // User chose 'No', do nothing to stay on the current page
          return;
        }
        // User chose 'Yes', proceed with sending data
      } else {
        // Validate the form only if there are conditions set
        if (!this.validateForm() || !this.validateNonInvertedConditions()) {
          alert('Invalid Weight Restrictions, each pair of criteria can be used only once!');
          return; // Stop if validation fails
        }
      }

      const operatorMapping = {
        '<=': -1,
        '=': 0,
        '>=': 1
      };

      const processedWRData = this.conditions.map(condition => {
        return {
          LHSCriterion: condition.column1,
          Operator: operatorMapping[condition.operator],
          Intense: condition.value,
          RHSCriterion: condition.column2
        };
      });

      const payload = {
        gridData: this.receivedGridData, // Data received from DataGrid.vue
        wrData: processedWRData
      };

      try {
        const response = await fetch('http://127.0.0.1:5000/process-evaluation-data', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log('Response from backend:', data);

        // Check if the response was successful
        if (response.ok && data.status === 'success') {
          // Redirect to Results.vue
          this.$router.push({ name: 'Results' });
         } /*else {
          // Handle error
          console.error('Error in response:', data.message);
          alert('Failed to process data: ' + data.message);
        } */
      } catch (error) {
        console.error('Error sending data to backend:', error);
        alert('Failed to send data to backend.');
      }
    },
    sendDataToBackend(payload) {
      console.log('Sending payload to backend:', payload);
      fetch('http://127.0.0.1:5000/process-evaluation-data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      })
          .then(response => {
            console.log('Raw response:', response);
            return response.json();
          })
          .then(data => {
            console.log('Response from backend:', data);
            // Handle the response from the backend
          })
          .catch(error => {
            console.error('Error sending data to backend:', error);
          });
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
  border:2px;
  border-color:var(--main-color);
}
</style>