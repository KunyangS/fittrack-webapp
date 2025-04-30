document.addEventListener('DOMContentLoaded', () => {
  const startDateInput = document.getElementById('startDate');
  const endDateInput = document.getElementById('endDate');
  const periodSelect = document.getElementById('timePeriod');
  const applyButton = document.getElementById('applyFilter');
  const summaryCard = document.getElementById('summary-card');
  const ctxDuration = document.getElementById('durationChart').getContext('2d');
  const ctxCalories = document.getElementById('caloriesChart').getContext('2d');
  const ctxStacked = document.getElementById('stackedChart').getContext('2d');
  const ctxPie = document.getElementById('activityPieChart').getContext('2d');
  const ctxGap = document.getElementById('gapChart')?.getContext('2d');

  let durationChart, caloriesChart, stackedChart, pieChart, gapChart;

  const modal = document.createElement('div');
  modal.id = 'activityModal';
  modal.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.2);z-index:1000;display:none;';
  modal.innerHTML = '<button id="closeModal" style="float:right;">X</button><div id="modalContent"></div>';
  document.body.appendChild(modal);
  modal.querySelector('#closeModal').onclick = () => modal.style.display = 'none';

  const rawData = [
    { date: '2025-04-01', activity_type: 'Running', duration: 30, calories_burned: 280 },
    { date: '2025-04-01', activity_type: 'Yoga', duration: 40, calories_burned: 150 },
    { date: '2025-04-02', activity_type: 'Cycling', duration: 50, calories_burned: 300 },
    { date: '2025-04-02', activity_type: 'Swimming', duration: 45, calories_burned: 350 },
    { date: '2025-04-03', activity_type: 'Walking', duration: 60, calories_burned: 200 },
    { date: '2025-04-03', activity_type: 'Gym', duration: 30, calories_burned: 280 },
    { date: '2025-04-04', activity_type: 'Running', duration: 35, calories_burned: 290 },
    { date: '2025-04-04', activity_type: 'Yoga', duration: 45, calories_burned: 160 },
    { date: '2025-04-05', activity_type: 'Swimming', duration: 60, calories_burned: 400 },
    { date: '2025-04-05', activity_type: 'Cycling', duration: 30, calories_burned: 220 },
    { date: '2025-04-06', activity_type: 'Gym', duration: 50, calories_burned: 430 },
    { date: '2025-04-06', activity_type: 'Walking', duration: 40, calories_burned: 150 },
    { date: '2025-04-07', activity_type: 'Running', duration: 45, calories_burned: 330 },
    { date: '2025-04-07', activity_type: 'Yoga', duration: 30, calories_burned: 110 },
    { date: '2025-04-08', activity_type: 'Cycling', duration: 60, calories_burned: 360 },
    { date: '2025-04-08', activity_type: 'Swimming', duration: 40, calories_burned: 300 },
    { date: '2025-04-09', activity_type: 'Walking', duration: 55, calories_burned: 180 },
    { date: '2025-04-09', activity_type: 'Gym', duration: 45, calories_burned: 400 },
    { date: '2025-04-10', activity_type: 'Running', duration: 30, calories_burned: 280 },
    { date: '2025-04-10', activity_type: 'Yoga', duration: 35, calories_burned: 130 },
    { date: '2025-04-11', activity_type: 'Swimming', duration: 60, calories_burned: 390 },
    { date: '2025-04-11', activity_type: 'Cycling', duration: 40, calories_burned: 270 },
    { date: '2025-04-12', activity_type: 'Gym', duration: 50, calories_burned: 450 },
    { date: '2025-04-12', activity_type: 'Walking', duration: 45, calories_burned: 160 },
    { date: '2025-04-13', activity_type: 'Running', duration: 40, calories_burned: 300 },
    { date: '2025-04-13', activity_type: 'Yoga', duration: 50, calories_burned: 180 },
    { date: '2025-04-14', activity_type: 'Cycling', duration: 55, calories_burned: 340 },
    { date: '2025-04-14', activity_type: 'Swimming', duration: 35, calories_burned: 260 },
    { date: '2025-04-15', activity_type: 'Walking', duration: 60, calories_burned: 200 },
    { date: '2025-04-15', activity_type: 'Gym', duration: 40, calories_burned: 390 },
    { date: '2025-04-16', activity_type: 'Running', duration: 35, calories_burned: 280 },
    { date: '2025-04-16', activity_type: 'Yoga', duration: 45, calories_burned: 160 },
    { date: '2025-04-17', activity_type: 'Swimming', duration: 50, calories_burned: 370 },
    { date: '2025-04-17', activity_type: 'Cycling', duration: 60, calories_burned: 390 },
    { date: '2025-04-18', activity_type: 'Gym', duration: 55, calories_burned: 460 },
    { date: '2025-04-18', activity_type: 'Walking', duration: 50, calories_burned: 180 },
    { date: '2025-04-19', activity_type: 'Running', duration: 40, calories_burned: 310 },
    { date: '2025-04-19', activity_type: 'Yoga', duration: 30, calories_burned: 120 },
    { date: '2025-04-20', activity_type: 'Cycling', duration: 45, calories_burned: 300 },
    { date: '2025-04-20', activity_type: 'Swimming', duration: 40, calories_burned: 290 },
    { date: '2025-04-21', activity_type: 'Gym', duration: 60, calories_burned: 470 },
    { date: '2025-04-21', activity_type: 'Walking', duration: 35, calories_burned: 140 },
    { date: '2025-04-22', activity_type: 'Running', duration: 30, calories_burned: 260 },
    { date: '2025-04-22', activity_type: 'Yoga', duration: 50, calories_burned: 190 },
    { date: '2025-04-23', activity_type: 'Swimming', duration: 55, calories_burned: 360 },
    { date: '2025-04-23', activity_type: 'Cycling', duration: 40, calories_burned: 280 },
    { date: '2025-04-24', activity_type: 'Gym', duration: 45, calories_burned: 420 },
    { date: '2025-04-24', activity_type: 'Walking', duration: 50, calories_burned: 180 },
    { date: '2025-04-25', activity_type: 'Running', duration: 35, calories_burned: 290 },
    { date: '2025-04-25', activity_type: 'Yoga', duration: 40, calories_burned: 150 },
    { date: '2025-04-26', activity_type: 'Swimming', duration: 60, calories_burned: 400 },
    { date: '2025-04-26', activity_type: 'Cycling', duration: 35, calories_burned: 250 },
    { date: '2025-04-27', activity_type: 'Gym', duration: 60, calories_burned: 480 },
    { date: '2025-04-27', activity_type: 'Walking', duration: 45, calories_burned: 170 },
    { date: '2025-04-28', activity_type: 'Running', duration: 40, calories_burned: 310 },
    { date: '2025-04-28', activity_type: 'Yoga', duration: 35, calories_burned: 130 },
    { date: '2025-04-29', activity_type: 'Cycling', duration: 60, calories_burned: 370 },
    { date: '2025-04-29', activity_type: 'Swimming', duration: 50, calories_burned: 360 },
    { date: '2025-04-30', activity_type: 'Gym', duration: 55, calories_burned: 460 },
    { date: '2025-04-30', activity_type: 'Walking', duration: 40, calories_burned: 150 }
  ];

  const foodData = [
    { date: '2025-04-01', food_name: 'Sandwich', calories: 300 },
    { date: '2025-04-01', food_name: 'Apple', calories: 100 },
    { date: '2025-04-02', food_name: 'Chicken Rice', calories: 550 },
    { date: '2025-04-03', food_name: 'Oatmeal', calories: 250 },
    { date: '2025-04-03', food_name: 'Salad', calories: 150 },
    { date: '2025-04-04', food_name: 'Burger', calories: 600 },
    { date: '2025-04-05', food_name: 'Pizza', calories: 500 },
    { date: '2025-04-06', food_name: 'Pasta', calories: 550 },
    { date: '2025-04-06', food_name: 'Orange Juice', calories: 120 },
    { date: '2025-04-07', food_name: 'Yogurt', calories: 180 },
    { date: '2025-04-08', food_name: 'Curry Rice', calories: 650 },
    { date: '2025-04-09', food_name: 'Bento Box', calories: 550 },
    { date: '2025-04-10', food_name: 'Toast', calories: 250 },
    { date: '2025-04-10', food_name: 'Milk', calories: 120 },
    { date: '2025-04-11', food_name: 'Fried Rice', calories: 600 },
    { date: '2025-04-12', food_name: 'Beef Bowl', calories: 700 },
    { date: '2025-04-13', food_name: 'Fruit Salad', calories: 300 },
    { date: '2025-04-14', food_name: 'Grilled Chicken', calories: 600 },
    { date: '2025-04-15', food_name: 'Wrap', calories: 400 },
    { date: '2025-04-16', food_name: 'Sushi', calories: 480 },
    { date: '2025-04-17', food_name: 'Smoothie', calories: 220 },
    { date: '2025-04-18', food_name: 'Cereal', calories: 300 },
    { date: '2025-04-19', food_name: 'Tuna Sandwich', calories: 350 },
    { date: '2025-04-20', food_name: 'Rice + Veggies', calories: 500 },
    { date: '2025-04-21', food_name: 'Avocado Toast', calories: 280 },
    { date: '2025-04-21', food_name: 'Green Tea', calories: 30 },
    { date: '2025-04-22', food_name: 'Chicken Salad', calories: 450 },
    { date: '2025-04-23', food_name: 'Ramen', calories: 600 },
    { date: '2025-04-24', food_name: 'Fruit Bowl', calories: 200 },
    { date: '2025-04-25', food_name: 'Steak', calories: 650 },
    { date: '2025-04-26', food_name: 'Ice Cream', calories: 250 },
    { date: '2025-04-27', food_name: 'Panini', calories: 400 },
    { date: '2025-04-28', food_name: 'Porridge', calories: 300 },
    { date: '2025-04-29', food_name: 'Hot Dog', calories: 350 },
    { date: '2025-04-30', food_name: 'Rice Bowl', calories: 600 },
    { date: '2025-04-30', food_name: 'Banana', calories: 100 }
  ];

  function getToday() {
    return new Date().toISOString().slice(0, 10);
  }

  function getNDaysAgo(n) {
    const d = new Date();
    d.setDate(d.getDate() - n);
    return d.toISOString().slice(0, 10);
  }

  function groupData(data, key = 'duration') {
    const result = {};
    data.forEach(e => {
      if (!result[e.date]) result[e.date] = 0;
      result[e.date] += e[key];
    });
    return result;
  }

  function updateDashboard() {
    const start = startDateInput.value || getNDaysAgo(6);
    const end = endDateInput.value || getToday();
    const filtered = rawData.filter(d => d.date >= start && d.date <= end);
    const foods = foodData.filter(d => d.date >= start && d.date <= end);

    const groupDur = groupData(filtered, 'duration');
    const groupCal = groupData(filtered, 'calories_burned');
    const groupIntake = groupData(foods, 'calories');

    const dates = Array.from(new Set([...Object.keys(groupDur), ...Object.keys(groupCal), ...Object.keys(groupIntake)])).sort();
    const durations = dates.map(d => groupDur[d] || 0);
    const calories = dates.map(d => groupCal[d] || 0);
    const intake = dates.map(d => groupIntake[d] || 0);
    const gap = dates.map((_, i) => intake[i] - calories[i]);

    const types = {};
    filtered.forEach(f => {
      if (!types[f.activity_type]) types[f.activity_type] = 0;
      types[f.activity_type]++;
    });

    const totalWorkouts = filtered.length;
    const totalTime = durations.reduce((a, b) => a + b, 0);
    const totalCal = calories.reduce((a, b) => a + b, 0);
    const totalIntake = intake.reduce((a, b) => a + b, 0);

    summaryCard.innerHTML = `
      <h3 class="text-xl font-semibold mb-4">Summary (Fixed)</h3>
      <p>Workouts: <strong>${totalWorkouts}</strong></p>
      <p>Total Duration: <strong>${totalTime} min</strong></p>
      <p>Calories Burned: <strong>${totalCal}</strong></p>
      <p>Calories Intake: <strong>${totalIntake}</strong></p>
      <p>Gap: <strong style="color:${totalIntake - totalCal > 0 ? 'green' : 'red'}">${totalIntake - totalCal}</strong></p>
    `;

    if (Math.abs(totalIntake - totalCal) >= 500) {
      const emoji = totalIntake - totalCal > 0 ? '💪 Keep pushing!' : '🔥 Great burn!';
      const popup = document.createElement('div');
      popup.textContent = emoji;
      popup.style.cssText = 'position:fixed;top:20px;right:20px;background:#16a34a;color:white;padding:12px;border-radius:10px;font-size:1rem;z-index:9999;';
      document.body.appendChild(popup);
      setTimeout(() => popup.remove(), 3000);
    }

    if (typeof durationChart?.destroy === 'function') durationChart.destroy();
    if (durationChart) durationChart.destroy();
    durationChart = new Chart(ctxDuration, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'Duration (min)',
          data: durations,
          borderColor: 'blue',
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        onClick: function (event, elements) {
          if (elements.length > 0) {
            const index = elements[0].index;
            const selectedDate = dates[index];
            const dayActivities = rawData.filter(e => e.date === selectedDate);
    
            const modalContent = modal.querySelector('#modalContent');
            modalContent.innerHTML = `
              <h3 style="font-size:1.2rem;margin-bottom:10px;">Activities on ${selectedDate}</h3>
              ${dayActivities.map(act => `
                <div style="margin-bottom:8px;">
                  <strong>${act.activity_type}</strong> – ${act.duration} min, ${act.calories_burned} cal
                </div>
              `).join('')}
            `;
            modal.style.display = 'block';
          }
        }
      }
    });
    

    if (typeof caloriesChart?.destroy === 'function') caloriesChart.destroy();
    caloriesChart = new Chart(ctxCalories, {
      type: 'line',
      data: { labels: dates, datasets: [{ label: 'Calories Burned', data: calories, borderColor: 'red', tension: 0.3 }] },
      options: { responsive: true }
    });

    if (typeof stackedChart?.destroy === 'function') stackedChart.destroy();
    stackedChart = new Chart(ctxStacked, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: Object.keys(types).map(type => ({
          label: type,
          data: dates.map(date => rawData.filter(e => e.date === date && e.activity_type === type).length),
          stack: 'stack'
        }))
      },
      options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true } } }
    });

    if (typeof pieChart?.destroy === 'function') pieChart.destroy();
    pieChart = new Chart(ctxPie, {
      type: 'pie',
      data: {
        labels: Object.keys(types),
        datasets: [{ data: Object.values(types), backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF','#FF9F40'] }]
      },
      options: { responsive: true }
    });

    if (ctxGap && typeof gapChart?.destroy === 'function') gapChart.destroy();
    if (ctxGap) {
      gapChart = new Chart(ctxGap, {
        type: 'bar',
        data: {
          labels: dates,
          datasets: [{
            label: 'Calorie Gap',
            data: gap,
            backgroundColor: gap.map(v => v >= 0 ? 'green' : 'red')
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: { title: { display: true, text: 'Gap (Intake - Burned)' } }
          }
        }
      });
    }
  }

  if (!startDateInput.value) startDateInput.value = getNDaysAgo(6);
  if (!endDateInput.value) endDateInput.value = getToday();

  applyButton.addEventListener('click', updateDashboard);
  updateDashboard();
});
