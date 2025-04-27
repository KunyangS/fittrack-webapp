// static/js/visualise.js

document.addEventListener('DOMContentLoaded', async () => {
  const startDateInput = document.getElementById('startDate');
  const endDateInput = document.getElementById('endDate');
  const periodSelect = document.getElementById('timePeriod');
  const applyButton = document.getElementById('applyFilter');

  const summaryCard = document.getElementById('summary-card');
  const ctxDuration = document.getElementById('durationChart').getContext('2d');
  const ctxCalories = document.getElementById('caloriesChart').getContext('2d');
  const ctxStacked = document.getElementById('stackedChart').getContext('2d');
  const ctxPie = document.getElementById('activityPieChart').getContext('2d');

  let rawData = [];
  let durationChart, caloriesChart, stackedChart, pieChart;

  // Fetch data from backend
  async function fetchData() {
    const response = await fetch('/api/data');
    const fullData = await response.json();
    rawData = fullData.fitness_entries;
    updateDashboard();
  }

  // Get today's date string (yyyy-mm-dd)
  function getToday() {
    return new Date().toISOString().slice(0, 10);
  }

  // Get date 6 days ago
  function getSevenDaysAgo() {
    const today = new Date();
    today.setDate(today.getDate() - 6);
    return today.toISOString().slice(0, 10);
  }

  // Format date into yyyy-mm-dd
  function formatDate(date) {
    return new Date(date).toISOString().slice(0, 10);
  }

  // Group data based on period
  function groupData(data, period) {
    const groups = {};
    data.forEach(item => {
      const itemDate = new Date(item.date);
      const key = (period === 'day') ? itemDate.toISOString().slice(0, 10)
        : (period === 'week') ? `${itemDate.getFullYear()}-W${getWeek(itemDate)}`
        : `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}`;

      if (!groups[key]) {
        groups[key] = { duration: 0, calories: 0, count: 0, types: {} };
      }

      groups[key].duration += item.duration;
      groups[key].calories += item.calories_burned;
      groups[key].count += 1;
      groups[key].types[item.activity_type] = (groups[key].types[item.activity_type] || 0) + 1;
    });
    return groups;
  }

  // Calculate week number
  function getWeek(date) {
    const firstJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((((date - firstJan) / 86400000) + firstJan.getDay() + 1) / 7);
  }

  // Update dashboard UI and charts
  function updateDashboard() {
    const start = startDateInput.value || getSevenDaysAgo();
    const end = endDateInput.value || getToday();
    const period = periodSelect.value;

    const filtered = rawData.filter(item => {
      return item.date >= start && item.date <= end;
    });

    const grouped = groupData(filtered, period);
    const labels = Object.keys(grouped).sort();

    const durations = labels.map(k => grouped[k].duration);
    const calories = labels.map(k => grouped[k].calories);

    const typesCount = {};
    labels.forEach(k => {
      const types = grouped[k].types;
      for (let type in types) {
        typesCount[type] = (typesCount[type] || 0) + types[type];
      }
    });

    // Update summary card
    const totalWorkouts = labels.reduce((sum, k) => sum + grouped[k].count, 0);
    const totalTime = durations.reduce((sum, d) => sum + d, 0);
    const totalCalories = calories.reduce((sum, c) => sum + c, 0);

    summaryCard.innerHTML = `
      <h3 class="text-xl font-semibold mb-4">Summary (${capitalize(period)})</h3>
      <p>Workouts: <strong>${totalWorkouts}</strong></p>
      <p>Total Duration: <strong>${Math.round(totalTime)} min</strong></p>
      <p>Calories Burned: <strong>${Math.round(totalCalories)}</strong></p>
    `;

    // Destroy existing charts if any
    if (durationChart) durationChart.destroy();
    if (caloriesChart) caloriesChart.destroy();
    if (stackedChart) stackedChart.destroy();
    if (pieChart) pieChart.destroy();

    // Draw Duration Trend chart
    durationChart = new Chart(ctxDuration, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Workout Duration (minutes)',
          data: durations,
          fill: false,
          borderColor: 'blue',
          backgroundColor: 'blue',
          tension: 0.3
        }]
      },
      options: commonOptions('Duration')
    });

    // Draw Calories Burned chart
    caloriesChart = new Chart(ctxCalories, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Calories Burned',
          data: calories,
          fill: false,
          borderColor: 'red',
          backgroundColor: 'red',
          tension: 0.3
        }]
      },
      options: commonOptions('Calories')
    });

    // Draw Stacked Chart for workout types
    const stackedDatasets = Object.keys(typesCount).map(type => {
      return {
        label: type,
        data: labels.map(k => grouped[k].types[type] || 0),
        stack: 'workout',
      };
    });

    stackedChart = new Chart(ctxStacked, {
      type: 'bar',
      data: {
        labels,
        datasets: stackedDatasets
      },
      options: {
        responsive: true,
        scales: {
          x: { stacked: true },
          y: { stacked: true }
        },
        animation: { duration: 1000 }
      }
    });

    // Draw Pie Chart for activity types
    pieChart = new Chart(ctxPie, {
      type: 'pie',
      data: {
        labels: Object.keys(typesCount),
        datasets: [{
          data: Object.values(typesCount),
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
          ]
        }]
      },
      options: {
        responsive: true,
        animation: {
          animateRotate: true,
          duration: 1500
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.raw || 0;
                return `${label}: ${value} times`;
              }
            }
          }
        }
      }
    });
  }

  function capitalize(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
  }

  function commonOptions(yLabel) {
    return {
      responsive: true,
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: { display: true },
        y: {
          display: true,
          title: {
            display: true,
            text: yLabel
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    };
  }

  applyButton.addEventListener('click', updateDashboard);

  fetchData();
});
