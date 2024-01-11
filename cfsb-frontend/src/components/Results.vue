<template>
  <div class="results-container">
    <h2>Evaluation Results</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <!-- Table for displaying the results -->
      <table v-if="results.length > 0">
        <thead>
        <tr>
          <th>Fog Node</th>
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
    <div class="button-container">
      <button @click="goBackToWR">Add/Modify Weight Restrictions</button>
      <button @click="saveProjectResults">Save Project</button>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  data() {
    return {
      results: [],
      loading: true,
      deaScoresChart: null,
      ranksChart: null,
    };
  },
  mounted() {
    this.fetchResults();
  },
  methods: {
    goBackToWR() {
      // Make sure 'WR' matches the name of the route in your router configuration
      this.$router.push({ name: 'WR' });
    },
    saveProjectResults() {
      // For now, this method is a placeholder
      console.log('Save Project Results button clicked');
    },
    fetchResults() {
      fetch('http://127.0.0.1:5000/get-evaluation-results')
          .then(response => response.json())
          .then(data => {
            this.results = data;
            this.loading = false;
            this.createCharts();
          })
          .catch(error => {
            console.error('Error fetching results:', error);
            this.loading = false;
          });
    },
    createCharts() {
      const titles = this.results.map(result => result.Title);
      const deaScores = this.results.map(result => result['DEA Score']);
      const ranks = this.results.map(result => result.Rank);

      this.$nextTick(() => {
        this.createBarChart(titles, deaScores, 'deascoresChart', 'Fog Node Scores');
        this.createHorizontalBarChart(titles, ranks, 'ranksChart', 'Fog Node Ranking');
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
          indexAxis: 'y', // This will make the bar chart horizontal
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

</style>
