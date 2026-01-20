<template>
  <div v-show="hasDefinedCriteria">
    <DefinedCriteria :criteria="definedCriteria" :providers="serverProviders" @criteriaUpdated="updateDataGridWithSelection" />
    <div class="pt-4"></div>
    <div class="button-container">
    <button @click="goBackToCriteriaSelection" class="bg-color-primary">Back to Criteria Selection</button>
    <button @click="loadDataGrid" class="save-button">Set Values for Criteria</button>
<!--    <button @click="SaveDataforWR" class="save-button" v-bind:class="{'bg-color-primary': !hasNoData, 'disabled': hasNoData }" v-bind="{disabled: hasNoData}">Save and Add Weight Restrictions</button>-->
    <button @click="scrollToBottom" class="bg-color-primary">Scroll to Bottom</button>
    </div>
  </div>
  <div v-show="isLoading">
    <div class="alert alert-info">
      Loading Nodes. Please wait...
      <div class="spinner-border text-secondary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
  <div v-show="!isLoading">
    <div class="p-4">
      <h2>Nodes Data</h2>
    </div>
    <table v-if="gridData.length" class="grid-cell-class">
      <thead>
      <tr>
        <th>Node</th>
        <th v-for="(criterion, index) in gridData[0].criteria" :key="index">{{ criterion.title }}</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(entry, entryIndex) in gridData" :key="entry.name">
        <td>{{ entry.name }}</td>
        <td v-for="(criterion, criterionIndex) in entry.criteria" :key="`${entry.name}-${criterionIndex}`">
          <input v-if="criterion.data_type.type === 2" type="number" v-model="criterion.value" />
          <select v-else-if="criterion.data_type.type === 1" v-model="criterion.value">
            <option v-for="option in criterion.data_type.values" :value="option" :key="option">{{ option }}</option>
          </select>
          <select v-else-if="criterion.data_type.type === 5" v-model="criterion.value">
            <option v-for="option in ['True', 'False']" :value="option">{{ option }}</option>
          </select>
          <input v-else type="text" v-model="criterion.value" />
        </td>
      </tr>
      </tbody>
    </table>
    <div v-else>
      No data to display.
    </div>
    <div class="pt-4"></div>
    <div class="button-container">
    <button @click="goBackToCriteriaSelection" class="bg-color-primary">Back to Criteria Selection</button>
    <button @click="SaveDataforWR" class="save-button" v-bind:class="{ 'bg-color-primary': !hasNoData, 'disabled': hasNoData }" v-bind="{disabled: hasNoData}">Save and Add Weight Restrictions</button>
    <button @click="scrollToTop" class="bg-color-primary">Scroll to Top</button>
    </div>
  </div>


</template>

<script>
export const backendURL = import.meta.env.VITE_BACKEND_URL;
const apiURL = backendURL;
import DefinedCriteria from "@/components/DefinedCriteria.vue";
import { useNodeStore } from "@/stores/nodeStore.js";

export default {
  components: {DefinedCriteria},
  data() {
    return {
      NodeNames: [],
      gridData: [], // Updated to be an array to match the structure provided by the backend
      isLoading: null,
      hasNoData: false,
      hasDefinedCriteria: false,
      serverProviders: [],
      definedCriteria: [],
      selectedCriteria: {},
    };
  },
  mounted() {
    let selectedItemsWithTypes = this.getSelectedItemsFromStorage();
    if (!selectedItemsWithTypes.length) {
      selectedItemsWithTypes = this.$route.params.selectedItems || [];
    }
    if (selectedItemsWithTypes.length > 0) {
      this.fetchGridData(selectedItemsWithTypes.map(item => item.name), selectedItemsWithTypes);
    }
  },
  methods: {
    scrollToTop() {
      document.documentElement.scrollTop = 0; // For most browsers
      document.body.scrollTop = 0; // For Safari and older browsers
    },
    scrollToBottom() {
      window.scrollTo({
        top: document.body.scrollHeight || document.documentElement.scrollHeight,
        behavior: "smooth", // Smooth scrolling effect
      });
    },
    getSelectedItemsFromStorage() {
      const storedItems = localStorage.getItem('selectedCriteria');
      return storedItems ? JSON.parse(storedItems) : [];
    },
    async fetchGridData(selectedItems, selectedItemsWithTypes) {
      this.isLoading = true;
      try {
        // Retrieve app_id and user_id from local storage directly within this method
        const app_id = localStorage.getItem('fog_broker_app_id');
        const user_id = localStorage.getItem('fog_broker_user_uuid');
        const settings = [localStorage.getItem('policyChoice'), localStorage.getItem('nodesModeChoice'), localStorage.getItem('nodesLocation')];
        const response = await fetch(apiURL+'/process_selected_criteria', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          // body: JSON.stringify({selectedItems}),
          body: JSON.stringify({
            selectedItems,
            selectedItemsWithTypes,
            app_id,  // Include app_id from local storage
            user_id,  // Include user_id from local storage
            settings
          })
        });

        if (response.ok) {
          this.isLoading = false;
          const { gridData, NodeNames, definedCriteria, providers = [] } = await response.json();
          if (definedCriteria.length > 0) {
            // defined criteria
            console.log("has defined criteria");
            console.log(definedCriteria);
            this.definedCriteria = definedCriteria;
            this.hasDefinedCriteria = true;
            this.serverProviders = providers;
            // this.serverProviders.push('a', 'b', '1', '2', 'aws-europe-1');
            this.serverProviders.reverse();
            console.log("providers "+providers);
          }
          // Initialize data_values for each entry in gridData
          this.gridData = gridData.map(entry => ({
            ...entry,
            data_values: entry.criteria.map(criterion => ({
              value: criterion.value,
              data_type: criterion.data_type
            }))
          }));
          this.NodeNames = NodeNames || [];
          if (Object.keys(gridData).length === 0){
            this.hasNoData = true;
          }
        } else {
          throw new Error('Failed to fetch grid data');
        }
      } catch (error) {
        console.error('Error fetching grid data:', error);
      }
    },
    validateNumeric(entry, criterionIndex) {
      // Directly modify and validate numeric value within the entry's criteria
      const numericValue = parseFloat(entry.criteria[criterionIndex].value);
      if (isNaN(numericValue) || numericValue <= 0) {
        alert('Please enter a number greater than zero.');
        entry.criteria[criterionIndex].value = ''; // Reset invalid value
        return false; // Halt further processing
      } else {
        entry.criteria[criterionIndex].value = numericValue; // Update with valid numeric value
      }
    },
    validateGridData() {
      for (const entry of this.gridData) {
        for (const criterion of entry.criteria) {
          // Convert value to string to handle trimming and empty checks
          const valueAsString = String(criterion.value).trim();

          switch (criterion.data_type.type) {
            case 2: // Numeric
              const numericValue = parseFloat(valueAsString);
              if (isNaN(numericValue) || numericValue <= 0) {
                alert('Please enter a valid number for all numeric fields.');
                return false; // Prevent further processing
              }
              break;

            case 1: // Ordinal
              if (!criterion.data_type.values.includes(criterion.value)) {
                alert(`Please select a valid option for ${criterion.title}.`);
                return false; // Prevent further processing
              }
              break;

            case 5: // Boolean
              if (!["True", "False"].includes(valueAsString)) {
                alert(`Please select a valid boolean value for ${criterion.title}.`);
                return false; // Prevent further processing
              }
              break;

            default:
              // Check for empty values for any other data types
              if (valueAsString === '') {
                alert(`Please ensure all fields are filled for ${criterion.title}.`);
                return false; // Prevent further processing
              }
          }
        }
      }
      return true; // All validations passed
    },
    goBackToCriteriaSelection() {
      this.$router.push({ name: 'CriteriaSelection' });
    },
    async SaveDataforWR() {
      if (!this.validateGridData()) {
        return;
      }
      // Log the current state of gridData
      console.log("Before saving, gridData is:", JSON.parse(JSON.stringify(this.gridData)));

      try {
        const formattedGridData = this.gridData.map(node => ({
          name: node.name,
          id: node.id,
          criteria: node.criteria.map(criterion => ({
            title: criterion.title,
            value: criterion.value,
            data_type: criterion.data_type.type
          }))
        }));

        const nodeStore = useNodeStore();

        const DataforWR = JSON.stringify(formattedGridData);
        // localStorage.setItem('gridData', DataforWR); // Save gridData to localStorage
        // console.log("Save DataforWR DataGrid.VUE to localstorage:", JSON.stringify(JSON.parse(DataforWR), null, 2));
        // new code to use store --  commented the setItem line: setItem('gridData', DataforWR).
        nodeStore.setGridData(DataforWR);

        // Save the NodeNames to localStorage
        const NodeNames = JSON.stringify(this.NodeNames);
        // localStorage.setItem('NodeNames', NodeNames);
        // New code. Try to store them in state -- commented above line
        nodeStore.setNodeNames(NodeNames);

        // Navigate to WR component with prepared data and NodeNames
        this.$router.push({
          name: 'WR',
          params: {
            data: DataforWR,
            NodeNames: NodeNames // Include NodeNames in the route parameters
          }
        });
      } catch (error) {
        console.error('Error:', error);
      }
    },
    updateDataGridWithSelection(selections) {
      this.selectedCriteria = selections; // Store selections from DefinedCriteria
      // let provider_selections = JSON.stringify(selections);
      // localStorage.setItem('provider_selections', provider_selections); // store the selections per provider
    },
    loadDataGrid() {
      // Apply stored selections to gridData when the "Set" button is clicked
      // Loop over each node entry in gridData
      this.gridData.forEach((entry) => {
        // Check if entry name contains any provider from the list
        Object.keys(this.selectedCriteria).forEach((provider) => {
          // Extract the provider name using a regular expression
          let match = entry.name.match(/Provider:\s*([\w-]+)/);
          let extractedProvider = match ? match[1] : null;
          console.log(provider);
          console.log(entry.name);
          if (extractedProvider === provider) {
            // Update each criterion in entry based on the selected criteria
            entry.criteria.forEach((criterion) => {
              console.log(criterion);
              console.log(this.selectedCriteria[provider]);
              const criterionTitle = criterion.title;
              const selectedValue = this.selectedCriteria[provider][criterionTitle];
              if (selectedValue) {
                criterion.value = selectedValue;
              }
            });
          }
        });
      });
      console.log("Updated gridData:", this.gridData);
    },

  }
};
</script>


<style>
/* Basic table styling */
table {
  width: 100%;
  border-collapse: collapse;
}

/* Header styling */
th {
  background-color: #232d45; /* Primary color */
  color: #FFFFFF; /* White text */
  padding: 10px;
  text-align: center;
}

/* Row styling */
td {
  background-color: #E7E7E7; /* Light grey */
  color: #172135; /* Secondary color */
  padding: 8px;
  font-weight: bold;
}

/* Alternate row colors for better readability */
tr:nth-child(even) {
  background-color: #155e75; /* Light tan */
}

/* Hover effect on rows */
tr:hover {
  background-color: #6FBFFF; /* Light blue */
}

/* Additional styles for editable input fields in the table */
table input[type="text"] {
  border: none;
  background-color: transparent;
  width: 100%;
  padding: 8px;
  text-align: center;
}

table input[type="text"]:focus {
  outline: none;
  background-color: #fff; /* Change color on focus for visibility */
}

/* Style for the submit button */
button {
  background-color: var(--main-color); /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-right: 30px;
}

button:hover {
  background-color: #e9ebed;
  color: var(--main-color);
  border: 2px solid;
  border-color: var(--main-color);
}

button.disabled {
  background-color: #6c757d; /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-right: 30px;
}

.button-container {
  display: flex;
  justify-content: space-between; /* Spread buttons across the container */
  align-items: center; /* Align buttons vertically */
  margin-top: 20px;
}

.save-button {
  margin-left: auto; /* Push this button to the far right */
}

select {
  width: 100%;
  padding: 8px;
  border: 1px solid #1b253b;
  background-color: white;
}

.grid-cell-class {
  text-align: center;
}

/*CSS for spinner*/
/* HTML: <div class="loader"></div> */
.loader {
  width: 108px;
  height: 60px;
  color: #269af2;
  --c: radial-gradient(farthest-side,currentColor 96%,#0000);
  background:
      var(--c) 100% 100% /30% 60%,
      var(--c) 70%  0    /50% 100%,
      var(--c) 0    100% /36% 68%,
      var(--c) 27%  18%  /26% 40%,
      linear-gradient(to bottom, currentColor 0%, transparent 100%) bottom/67% 58%;
  background-repeat: no-repeat;
  position: relative;
}
.loader:after {
  content: "";
  position: absolute;
  inset: 0;
  background: inherit;
  opacity: 0.4;
  animation: l7 1s infinite;
}
@keyframes l7 {
  to {transform:scale(1.8);opacity:0}
}


</style>