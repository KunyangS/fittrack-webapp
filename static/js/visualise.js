// ==============================================
// Fitness & Food Dashboard Visualisation Script
// ==============================================

// ---------- DOM Element Initialisation ----------
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const applyButton = document.getElementById('applyFilter');
const summaryCard = document.getElementById('summary-card');

// Canvas elements for charts
const ctxDuration = document.getElementById('durationChart').getContext('2d');
const ctxCalories = document.getElementById('caloriesChart').getContext('2d');
const ctxStacked = document.getElementById('stackedChart').getContext('2d');
const ctxPie = document.getElementById('activityPieChart').getContext('2d');
const ctxGap = document.getElementById('gapChart')?.getContext('2d');

// ---------- Chart Instances ----------
let durationChart, caloriesChart, stackedChart, pieChart, gapChart;

// ---------- Modal Setup (for Daily Breakdown) ----------
const modal = document.createElement('div');
modal.id = 'activityModal';
modal.style.cssText = `
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  display: none;
`;
modal.innerHTML = `
  <button id="closeModal" style="float: right;">✖</button>
  <div id="modalContent"></div>
`;
document.body.appendChild(modal);
modal.querySelector('#closeModal').onclick = () => {
  modal.style.display = 'none';
};

// ---------- Data from Flask via Template Context ----------
const rawData = window.rawData || [];
const foodData = window.foodData || [];

// ---------- Utility Functions ----------
function getToday() {
  return new Date().toISOString().slice(0, 10);
}

function getNDaysAgo(n) {
  const date = new Date();
  date.setDate(date.getDate() - n);
  return date.toISOString().slice(0, 10);
}

// Group data by date and sum the target key (e.g., calories or duration)
function groupData(data, key) {
  const result = {};
  data.forEach(entry => {
    const date = entry.date;
    result[date] = (result[date] || 0) + entry[key];
  });
  return result;
}

// ---------- Main Dashboard Update Function ----------
function updateDashboard() {
  const start = startDateInput.value || getNDaysAgo(6);
  const end = endDateInput.value || getToday();

  // Filter records within the selected date range
  const filteredFitness = rawData.filter(row => row.date >= start && row.date <= end);
  const filteredFood = foodData.filter(row => row.date >= start && row.date <= end);

  // Aggregate data
  const groupedDuration = groupData(filteredFitness, 'duration');
  const groupedBurned = groupData(filteredFitness, 'calories_burned');
  const groupedIntake = groupData(filteredFood, 'calories');

  // Merge and sort all dates
  const allDates = Array.from(new Set([
    ...Object.keys(groupedDuration),
    ...Object.keys(groupedBurned),
    ...Object.keys(groupedIntake)
  ])).sort();

  const durations = allDates.map(date => groupedDuration[date] || 0);
  const calories = allDates.map(date => groupedBurned[date] || 0);
  const intake = allDates.map(date => groupedIntake[date] || 0);
  const gaps = allDates.map((_, i) => intake[i] - calories[i]);

  // Count activity types
  const typeCounts = {};
  filteredFitness.forEach(entry => {
    typeCounts[entry.activity_type] = (typeCounts[entry.activity_type] || 0) + 1;
  });

  // Summary totals
  const totalWorkouts = filteredFitness.length;
  const totalTime = durations.reduce((sum, d) => sum + d, 0);
  const totalCalories = calories.reduce((sum, c) => sum + c, 0);
  const totalIntake = intake.reduce((sum, c) => sum + c, 0);
  const calorieGap = totalIntake - totalCalories;

  // ---------- Update Summary Card ----------
const summaryContentDiv = document.getElementById('summary-content');
if (summaryContentDiv) {
  summaryContentDiv.innerHTML = `
    <p>Workouts: <strong>${totalWorkouts}</strong></p>
    <p>Total Duration: <strong>${totalTime} min</strong></p>
    <p>Calories Burned: <strong>${totalCalories}</strong></p>
    <p>Calories Intake: <strong>${totalIntake}</strong></p>
    <p>Gap: <strong style="color:${calorieGap > 0 ? 'green' : 'red'}">${calorieGap}</strong></p>
  `;
}

  // ---------- Encouragement Popup ----------
  if (Math.abs(calorieGap) >= 500) {
    const message = calorieGap > 0 ? '💪 Keep pushing!' : '🔥 Great burn!';
    const popup = document.createElement('div');
    popup.textContent = message;
    popup.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #16a34a;
      color: white;
      padding: 12px;
      border-radius: 10px;
      font-size: 1rem;
      z-index: 9999;
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 3000);
  }

  // ---------- Charts Section ----------

  // Destroy previous charts if they exist
  durationChart?.destroy();
  caloriesChart?.destroy();
  stackedChart?.destroy();
  pieChart?.destroy();
  gapChart?.destroy();

  // Line Chart: Duration
  durationChart = new Chart(ctxDuration, {
    type: 'line',
    data: {
      labels: allDates,
      datasets: [{ label: 'Duration (min)', data: durations, borderColor: 'blue', tension: 0.3 }]
    },
    options: {
      responsive: true,
      onClick: (e, elements) => {
        if (elements.length) {
          const index = elements[0].index;
          const clickedDate = allDates[index];
          const activities = filteredFitness.filter(d => d.date === clickedDate);

          modal.querySelector('#modalContent').innerHTML = `
            <h3 style="font-size:1.2rem;margin-bottom:10px;">Activities on ${clickedDate}</h3>
            ${activities.map(act =>
              `<div style="margin-bottom:8px;"><strong>${act.activity_type}</strong> – ${act.duration} min, ${act.calories_burned} cal</div>`
            ).join('')}
          `;
          modal.style.display = 'block';
        }
      }
    }
  });

  // Line Chart: Calories
  caloriesChart = new Chart(ctxCalories, {
    type: 'line',
    data: {
      labels: allDates,
      datasets: [{ label: 'Calories Burned', data: calories, borderColor: 'red', tension: 0.3 }]
    },
    options: { responsive: true }
  });

  // Stacked Bar Chart: Activity types per day
  stackedChart = new Chart(ctxStacked, {
    type: 'bar',
    data: {
      labels: allDates,
      datasets: Object.keys(typeCounts).map(type => ({
        label: type,
        data: allDates.map(date =>
          filteredFitness.filter(d => d.date === date && d.activity_type === type).length
        ),
        stack: 'stack'
      }))
    },
    options: {
      responsive: true,
      scales: {
        x: { stacked: true },
        y: { stacked: true }
      }
    }
  });

  // Pie Chart: Overall activity distribution
  pieChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
      labels: Object.keys(typeCounts),
      datasets: [{
        data: Object.values(typeCounts),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
      }]
    },
    options: { responsive: true }
  });

  // Bar Chart: Calorie gap
  if (ctxGap) {
    gapChart = new Chart(ctxGap, {
      type: 'bar',
      data: {
        labels: allDates,
        datasets: [{
          label: 'Calorie Gap',
          data: gaps,
          backgroundColor: gaps.map(v => v >= 0 ? 'green' : 'red')
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            title: { display: true, text: 'Gap (Intake - Burned)' }
          }
        }
      }
    });
  }
}

// ---------- Initial Render with Defaults ----------
if (!startDateInput.value) startDateInput.value = getNDaysAgo(6);
if (!endDateInput.value) endDateInput.value = getToday();

// Apply button listener
applyButton.addEventListener('click', updateDashboard);

// First load
updateDashboard();
