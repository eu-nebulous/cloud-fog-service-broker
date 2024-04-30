<template>
  <div class="results-container">
    <h2>Evaluation Results</h2>
    <p class="description">
      The scores have been rounded to the nearest two decimal places.
    </p>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <!-- Table for displaying the results -->
      <table v-if="results.length > 0">
        <thead>
        <tr>
          <th>Node</th>
          <th>Score (%)</th>
          <th>Ranking</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(result, index) in results" :key="index">
          <td>{{ result.Title }}</td>
          <td>{{ formatPercentage(result['DEA Score']) }}</td>
          <td>{{ result.Rank }}</td>
        </tr>
        </tbody>
      </table>
      <!-- Separator Line -->
      <div class="separator-line"></div>
      <!-- Chart Container -->
      <div class="charts-container">
        <div class="chart-wrapper">
          <canvas id="deascoresChart"></canvas>
        </div>
        <div class="chart-wrapper">
          <canvas id="ranksChart"></canvas>
        </div>
      </div>
      </div>
      <!-- Separator Line -->
      <div class="separator-line"></div>
      <div class="button-container">
        <button @click="goBackToWR">Add/Modify Weight Restrictions</button>
        <button @click="saveProjectResults">Save Project</button>
      </div>
    </div>
  </template>

  <script>
  export const backendURL = import.meta.env.VITE_BACKEND_URL;
  const apiURL = backendURL;
  import Chart from 'chart.js/auto';

  export default {
    data() {
      return {
        results: [],
        loading: true,
        deaScoresChart: null,
        ranksChart: null,
        gridData: null,
        relativeWRData: null,
        immediateWRData: null
      };
    },
    mounted() {
      const resultsString = localStorage.getItem('evaluationResults');

      try {
        const data = JSON.parse(resultsString);
        if (data && data.results) {
          this.results = data.results;
          this.createCharts();
          this.loading = false;
        } else {
          console.error('Error fetching results: Data is not in the expected format.');
          this.loading = false;
          // Handle the error by navigating to a different page or displaying an error message
        }
      } catch (error) {
        console.error('Error parsing JSON:', error);
        // Handle parsing error by navigating to a different page or displaying an error message
        this.loading = false;
      }
    },
    methods: {
      goBackToWR() {
        // Make sure 'WR' matches the name of the route in your router configuration
        this.$router.push({ name: 'WR' });
      },
      async saveProjectResults() {
        if (confirm("Save Project?")) {
          console.log('Save Project Results button clicked');
          let array_data = []
          // Application Id
          let app_id = localStorage.getItem('fog_broker_app_id');
          let appData = [
            {app_id: app_id}
          ];
          array_data.push(appData);

          // Node Names
          let NodeNamesFromStorage = localStorage.getItem('NodeNames');
          let NodeNames = JSON.parse(NodeNamesFromStorage);
          array_data.push(NodeNames);

          // Selected  Criteria
          let selectedCriteriaFromStorage = localStorage.getItem('selectedCriteria');
          let selectedCriteria = JSON.parse(selectedCriteriaFromStorage);
          array_data.push(selectedCriteria);

          // DataGrid Data
          let gridDataFromStorage = localStorage.getItem('gridData');
          let GridData = JSON.parse(gridDataFromStorage);
          array_data.push(GridData);
          // relativeWRData
          let relativeWRDataFromStorage = localStorage.getItem('relativeWRData');
          let relativeWRData = JSON.parse(relativeWRDataFromStorage);
          array_data.push(relativeWRData);
          //immediateWRData
          let immediateWRDataFromStorage = localStorage.getItem('immediateWRData');
          let immediateWRData = JSON.parse(immediateWRDataFromStorage);
          array_data.push(immediateWRData);
          // evaluation Results
          let evaluationResultsFromStorage = localStorage.getItem('evaluationResults');
          let evaluationResults = JSON.parse(evaluationResultsFromStorage);
          array_data.push(evaluationResults.results);  // Save only th results not the LPStatus

          let result = await this.saveProjectData(array_data);
          console.log(result);

          // Clear local storage
          localStorage.removeItem('evaluationResults');
          localStorage.removeItem('selectedCriteria');
          localStorage.removeItem('NodeNames');
          localStorage.removeItem('gridData');
          localStorage.removeItem('relativeWRData');
          localStorage.removeItem('immediateWRData');
          // localStorage.removeItem('fog_broker_user_uuid'); May keep them so the user can evaluate again
          // localStorage.removeItem('fog_broker_app_id');

          // Redirect to the Home page
          this.$router.push({ name: 'HomePage' });
        }
        else {
          console.log('Project not saved.');
        }
      },
      async saveProjectData(data) {
        try {
          const response = await fetch(apiURL+'/app/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
          });
          console.log("response" + response);
          let response_data = await response.json();
          console.log(response_data);
        } catch (error) {
          console.error('Error saving project:', error);
        }
      },
      createCharts() {
        if (!this.results || this.results.length === 0) {
          console.error('No results data available to create charts.');
          return;
        }
        console.log(this.results);

        const titles = this.results.map(result => result.Title);
        const deaScores = this.results.map(result => result['DEA Score']);
        const ranks = this.results.map(result => result.Rank);

        this.$nextTick(() => {
          this.createBarChart(titles, deaScores, 'deascoresChart', 'Scores');
          this.createHorizontalBarChart(titles, ranks, 'ranksChart', 'Ranking');
        });
      },
      createBarChart(labels, data, chartId, label) {
        const ctx = document.getElementById(chartId).getContext('2d');
        if (this.deaScoresChart) {
          this.deaScoresChart.destroy();
        }
        this.deaScoresChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label,
              data,
              backgroundColor: 'rgba(181,141,243,0.56)',
              borderColor: 'rgb(102,16,242)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            //maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 1, // Set the maximum value of the y-axis to 1
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(tooltipItem) {
                    let score = tooltipItem.raw * 100;
                    return `Score: ${score.toFixed(2)}%`;
                  }
                },
                bodyFontSize: 16, // Adjust font size as needed
                titleFontSize: 16
              }
            }
          }
        });
      },
      createHorizontalBarChart(labels, data, chartId, label) {
        const ctx = document.getElementById(chartId).getContext('2d');
        if (this.ranksChart) {
          this.ranksChart.destroy();
        }
        // Assuming higher scores should have longer bars, so we invert the scores
        // as higher rank should have lower numerical value
        const invertedData = data.map(score => Math.max(...data) - score + Math.min(...data));
        this.ranksChart = new Chart(ctx, {
          type: 'bar', // In Chart.js 3.x, you specify horizontal bars using indexAxis
          data: {
            labels,
            datasets: [{
              label,
              data: invertedData,
              backgroundColor: 'rgba(110,108,229,0.55)',
              borderColor: 'rgb(60,54,235)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            //maintainAspectRatio: false, // Set to false to allow full width and controlled height
            indexAxis: 'y', // This makes the bar chart horizontal
            scales: {
              x: {
                beginAtZero: true
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    // Since we inverted the data, we need to correct the value displayed in the tooltip
                    const rankValue = Math.max(...data) - context.parsed.x + Math.min(...data);
                    return `Rank: ${rankValue}`;
                  }
                },
                bodyFontSize: 16, // Adjust font size as needed
                titleFontSize: 16
              }
            }
          }
        });
      },
      formatPercentage(value) {
        const percentage = (value * 100).toFixed(2);
        return percentage === '100.00' ? '100%' : `${percentage}%`;
      }
    }
  };
  </script>

  <style>
  .results-container {
    padding: 20px;
  }

  .loading {
    text-align: center;
  }

  .charts-container {
    display: flex;
    flex-direction: row; /* Align charts horizontally */
    justify-content: space-around;
    padding: 0 20px; /* Add padding if needed */
  }

  .chart-wrapper {
    flex: 1; /* Each chart will take equal space */
    /* Remove max-width or set it to a higher value if you want a specific limit */
    margin: auto;
  }

  td {
    text-align: center;
  }

  .separator-line {
    height: 4px; /* Thickness of the line */
    background-color: #172135; /* Deep purple color */
    margin: 10px 0; /* Spacing above and below the line */
  }

  </style>
