document.addEventListener('DOMContentLoaded', async () => {
  const periodSelect = document.getElementById('timePeriod');
  const summaryCard = document.getElementById('summary-card');
  const ctxDuration = document.getElementById('durationChart').getContext('2d');
  const ctxActivity = document.getElementById('activityPieChart').getContext('2d');

  let rawData = [];
  let durationChart, activityPieChart;

  async function fetchData() {
    const response = await fetch('/api/data');
    const fullData = await response.json();
    rawData = fullData.fitness_entries; 
    updateDashboard();
  }

  function groupData(period) {
    const now = new Date();
    const groups = {};

    rawData.forEach(item => {
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

  function getWeek(date) {
    const firstJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((((date - firstJan) / 86400000) + firstJan.getDay() + 1) / 7);
  }

  function updateDashboard() {
    const period = periodSelect.value;
    const grouped = groupData(period);

    const labels = Object.keys(grouped).sort();
    const durations = labels.map(k => grouped[k].duration);
    const typesCount = {};

    labels.forEach(k => {
      const types = grouped[k].types;
      for (let type in types) {
        typesCount[type] = (typesCount[type] || 0) + types[type];
      }
    });

    // update Summary
    const totalWorkouts = labels.reduce((sum, k) => sum + grouped[k].count, 0);
    const totalTime = durations.reduce((sum, d) => sum + d, 0);
    const totalCalories = labels.reduce((sum, k) => sum + grouped[k].calories, 0);

    summaryCard.innerHTML = `
      <h3 class="text-xl font-semibold mb-4">Activity Summary (${capitalize(period)})</h3>
      <p>Workouts: <strong>${totalWorkouts}</strong></p>
      <p>Total Duration: <strong>${Math.round(totalTime)} min</strong></p>
      <p>Calories Burned: <strong>${Math.round(totalCalories)}</strong></p>
    `;

    // update Duration 
    if (durationChart) durationChart.destroy();
    durationChart = new Chart(ctxDuration, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Workout Duration (min)',
          data: durations,
          fill: false,
          borderColor: 'blue',
          backgroundColor: 'blue',
          tension: 0.2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
        },
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: 'Date'
            }
          },
          y: {
            display: true,
            title: {
              display: true,
              text: 'Duration (minutes)'
            }
          }
        }
      }
    });

    // update Activity 
    if (activityPieChart) activityPieChart.destroy();
    activityPieChart = new Chart(ctxActivity, {
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

  periodSelect.addEventListener('change', updateDashboard);

  fetchData();
});

