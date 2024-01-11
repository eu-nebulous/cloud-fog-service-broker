<template>
  <div>
    <div class="p-4">
      <h2>Edge / Fog Nodes Data</h2>
    </div>

    <table v-if="Object.keys(gridData).length" class="grid-cell-class">
      <thead>
      <tr>
        <th>Edge / Fog Nodes</th>
        <th v-for="(values, column) in gridData" :key="column">{{ values.title }}</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="index in rowCount" :key="index">
        <!-- (-1) Because there is a different indexing in the gridData and the fog node titles that starts from 0 -->
        <td>{{ fogNodesTitles[index-1] }}</td>
        <td v-for="(values, column) in gridData" :key="`${column}-${index}`">
          <select v-if="Ordinal_Variables.includes(column)" v-model="values.data_values[index - 1]">
            <option v-for="option in dropdownOptions" :value="option" :key="option">{{ option }}</option>
          </select>
          <input v-else type="text" v-model="values.data_values[index - 1]" />
        </td>
      </tr>
      </tbody>
    </table>
    <div v-else>
      No data to display.
    </div>
    <div class="pt-4"></div>
    <!-- <button @click="SaveDataforEvaluation" class="bg-color-primary">Save and Run Evaluation</button> -->
    <button @click="SaveDataforWR" class="bg-color-primary">Save and Add Weight Restrictions</button>
  </div>

</template>

<script>
import { useRouter } from 'vue-router';

export default {
  data() {
    return {
      fogNodesTitles: [],
      gridData: [], // Data for the grid
      selectedItemsFromBack: [],
      Ordinal_Variables: ['attr-reputation', 'attr-assurance', 'attr-security'],
      dropdownOptions: ['High', 'Medium', 'Low'], // Options for the dropdown
    };
  },
  setup() {
    const router = useRouter();
    return {
      router
    };
  },
  mounted() {
    const selectedItems = this.$route.params.selectedItems || [];
    if (selectedItems.length > 0) {
      this.fetchGridData(selectedItems);
    }
    this.fetchFogNodesTitles();
  },
  computed: {
    rowCount() {
      // Check if gridData has any keys and use the first key to find the row count
      const firstKey = Object.keys(this.gridData)[0];
      return firstKey ? this.gridData[firstKey].data_values.length : 0;
    }
  },
  methods: {
    // Receives the Grid  Data 1st time
    async fetchGridData(selectedItems) {
      try {
        const response = await fetch('http://127.0.0.1:5000/process_selected_items', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({selectedItems}),
        });
        if (response.ok) {
          const criteria_data = await response.json();
          this.gridData = criteria_data.gridData; // Assigning the gridData from the response
          console.log('DataGrid.vue received the criteria data from the Backend:', this.gridData); // Log the received grid data
        } else {
          throw new Error('Failed to fetch grid data');
        }
      } catch (error) {
        console.error('Error fetching grid data:', error);
      }
    },
    fetchFogNodesTitles() { // Receives the names of fog nodes (grid's 1st column)
      fetch('http://127.0.0.1:5000/get-fog-nodes-titles')
          .then(response => response.json())
          .then(data => {
            // 'data' is an array like ['Fog Node 1', 'Fog Node 2', ...]
            this.fogNodesTitles = data;
          })
          .catch(error => console.error('Error fetching fog nodes titles:', error));
    },
    validateGridData() {
      for (const key in this.gridData) {
        if (this.gridData.hasOwnProperty(key)) {
          const dataValues = this.gridData[key].data_values;
          for (const value of dataValues) {
            if (value === 0 || value === null || value === '') {
              return false; // Invalid data found
            }
          }
        }
      }
      return true; // All data is valid
    },
     async SaveDataforWR() {
       if (!this.validateGridData()) {
         alert('Invalid input: Zero or null values are not accepted.');
         return; // Stop submission if validation fails
       }
       else{
         try {
           const DataforWR = JSON.stringify({
             gridData: this.gridData
           });
             // Navigate to WR component with data
           this.router.push({ name: 'WR', params: { data: DataforWR } });
         } catch (error) {
           console.error('Error:', error);
         }
       }
    },
    async SaveDataforEvaluation() {
    }
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
background-color: #813F8F; /* Primary color */
color: #FFFFFF; /* White text */
padding: 10px;
text-align: center;
}

/* Row styling */
td {
background-color: #E7E7E7; /* Light grey */
color: #374591; /* Secondary color */
padding: 8px;
}

/* Alternate row colors for better readability */
tr:nth-child(even) {
background-color: #E4DCD5; /* Light tan */
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
  background-color: var(--secondary-color); /* Lighter shade of purple on hover */
  color: var(--main-color);
  border:2px;
  border-color:var(--main-color);
}

select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
}

.grid-cell-class {
  text-align: center;
}
</style>
