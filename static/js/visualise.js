// ==============================================
// Fitness & Food Dashboard Visualisation Script
// ==============================================

// Wait for DOM content to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log("Visualization initialized - " + new Date().toISOString());

  // ---------- DOM Element Initialisation ----------
  const startDateInput = document.getElementById('startDate');
  const endDateInput = document.getElementById('endDate');
  const applyButton = document.getElementById('applyFilter');
  const summaryCard = document.getElementById('summary-card');

  // Canvas elements for charts
  const ctxDuration = document.getElementById('durationChart')?.getContext('2d');
  const ctxIntensity = document.getElementById('intensityChart')?.getContext('2d');
  const ctxPerformance = document.getElementById('performanceRadarChart')?.getContext('2d');
  const ctxEmotion = document.getElementById('emotionChart')?.getContext('2d');
  const ctxGoal = document.getElementById('goalProgressChart')?.getContext('2d');
  const ctxCaloriesBurned = document.getElementById('caloriesBurnedChart')?.getContext('2d'); 
  const ctxCaloriesEfficiency = document.getElementById('caloriesEfficiencyChart')?.getContext('2d'); // New chart
  const ctxCalorieBalance = document.getElementById('calorieBalanceChart')?.getContext('2d');
  const ctxNutrition = document.getElementById('nutritionChart')?.getContext('2d');

  // Elements for Detailed Data Log
  const dataEntriesLogContainer = document.getElementById('dataEntriesLog');
  const dataEntriesPaginationContainer = document.getElementById('dataEntriesPagination');
  let currentPage = 1;
  const itemsPerPage = 10;
  let combinedData = [];

  // ---------- Chart Instances ----------
  let durationChart, intensityChart, performanceChart, emotionChart, goalChart, caloriesBurnedChart, caloriesEfficiencyChart, calorieBalanceChart, nutritionChart;

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
  // Check if data is available from the HTML
  if (!window.rawData) {
    console.error("Fitness data not available! Please check data loading in HTML.");
    window.rawData = []; // Fallback to empty array
  }
  
  if (!window.foodData) {
    console.error("Food data not available! Please check data loading in HTML.");
    window.foodData = []; // Fallback to empty array
  }
  
  // Debug data loading
  console.log("Raw fitness data:", window.rawData);
  console.log("Food data:", window.foodData);

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
      result[date] = (result[date] || 0) + (entry[key] || 0);
    });
    return result;
  }

  // ---------- Detailed Data Log Functions ----------
  function combineAndSortData(fitnessData, foodData) {
    const mappedFitnessData = fitnessData.map(entry => ({ ...entry, type: 'Fitness', icon: 'fa-person-running' }));
    const mappedFoodData = foodData.map(entry => ({ ...entry, type: 'Food', icon: 'fa-utensils' }));
    return [...mappedFitnessData, ...mappedFoodData].sort((a, b) => new Date(b.date) - new Date(a.date) || b.id - a.id);
  }

  function renderDataEntriesLog() {
    if (!dataEntriesLogContainer) return;

    dataEntriesLogContainer.innerHTML = ''; // Clear previous entries

    if (combinedData.length === 0) {
      dataEntriesLogContainer.innerHTML = '<p class="text-center text-sm text-neutral-500 dark:text-neutral-400 py-4">No data entries found for the selected period.</p>';
      renderPaginationControls(0);
      return;
    }

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedEntries = combinedData.slice(startIndex, endIndex);

    paginatedEntries.forEach(entry => {
      const card = document.createElement('div');
      card.className = 'bg-neutral-100 dark:bg-neutral-700/50 p-3 rounded-lg shadow-sm flex items-center space-x-3 transition-all duration-200 hover:shadow-md'; // Adjusted background and padding
      
      let entryDetails = '';
      const commonTextClass = 'text-xs text-neutral-600 dark:text-neutral-400'; // Slightly lighter text for labels
      const valueTextClass = 'font-medium text-neutral-800 dark:text-neutral-200'; // Values stand out more

      if (entry.type === 'Fitness') {
        entryDetails = `
          <div class="flex-1 min-w-0">
            <p class="${commonTextClass} truncate"><strong class="font-semibold">Activity:</strong> <span class="${valueTextClass}">${entry.activity_type || 'N/A'}</span></p>
            <div class="flex space-x-2.5 mt-0.5"> <!-- Reduced spacing -->
              <p class="${commonTextClass}"><strong class="font-semibold">Duration:</strong> <span class="${valueTextClass}">${entry.duration || 0}m</span></p>
              <p class="${commonTextClass}"><strong class="font-semibold">Calories:</strong> <span class="${valueTextClass}">${entry.calories_burned || 0}kcal</span></p>
            </div>
          </div>
        `;
      } else if (entry.type === 'Food') {
        entryDetails = `
          <div class="flex-1 min-w-0">
            <p class="${commonTextClass} truncate"><strong class="font-semibold">Item:</strong> <span class="${valueTextClass}">${entry.food_name || 'N/A'}</span> <span class="text-neutral-500 dark:text-neutral-400">(${entry.meal_type || 'N/A'})</span></p>
            <div class="flex space-x-2.5 mt-0.5"> <!-- Reduced spacing -->
              <p class="${commonTextClass}"><strong class="font-semibold">Qty:</strong> <span class="${valueTextClass}">${entry.quantity || 'N/A'}</span></p>
              <p class="${commonTextClass}"><strong class="font-semibold">Calories:</strong> <span class="${valueTextClass}">${entry.calories || 0}kcal</span></p>
            </div>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="flex-shrink-0">
          <i class="fas ${entry.icon} text-primary dark:text-primary-light text-lg w-5 text-center"></i> <!-- Slightly smaller icon -->
        </div>
        <div class="flex-grow min-w-0">
          <div class="flex justify-between items-center mb-0.5">
            <h4 class="text-xs font-semibold text-neutral-700 dark:text-neutral-100 truncate" title="${entry.type} Entry - ${new Date(entry.date).toLocaleDateString()}">${entry.type} - ${new Date(entry.date).toLocaleDateString('en-CA')}</h4>
          </div>
          ${entryDetails}
        </div>
        <button class="delete-entry-btn flex-shrink-0 text-neutral-400 hover:text-red-600 dark:text-neutral-500 dark:hover:text-red-400 transition-colors p-1.5 rounded-full focus:outline-none focus:ring-1 focus:ring-red-500 focus:ring-opacity-50" data-id="${entry.id}" data-type="${entry.type.toLowerCase()}" aria-label="Delete entry">
          <i class="fas fa-trash-alt text-xs"></i> <!-- Smaller delete icon -->
        </button>
      `;
      dataEntriesLogContainer.appendChild(card);
    });

    // Add event listeners to delete buttons
    document.querySelectorAll('.delete-entry-btn').forEach(button => {
      button.addEventListener('click', handleDeleteEntry);
    });
    
    renderPaginationControls(combinedData.length);
  }

  function renderPaginationControls(totalItems) {
    if (!dataEntriesPaginationContainer) return;
    dataEntriesPaginationContainer.innerHTML = ''; // Clear previous controls

    const totalPages = Math.ceil(totalItems / itemsPerPage);
    if (totalPages <= 1) return;

    // Previous Button
    const prevButton = document.createElement('button');
    prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevButton.className = 'px-3 py-1 rounded-md text-sm font-medium focus:outline-none transition-colors duration-200 ';
    prevButton.className += currentPage === 1 ? 'bg-neutral-200 dark:bg-neutral-600 text-neutral-400 dark:text-neutral-500 cursor-not-allowed' : 'bg-primary hover:bg-primary-dark text-white';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        renderDataEntriesLog();
      }
    });
    dataEntriesPaginationContainer.appendChild(prevButton);

    // Page Info
    const pageInfo = document.createElement('span');
    pageInfo.className = 'text-sm text-neutral-700 dark:text-neutral-300';
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    dataEntriesPaginationContainer.appendChild(pageInfo);
    
    // Next Button
    const nextButton = document.createElement('button');
    nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextButton.className = 'px-3 py-1 rounded-md text-sm font-medium focus:outline-none transition-colors duration-200 ';
    nextButton.className += currentPage === totalPages ? 'bg-neutral-200 dark:bg-neutral-600 text-neutral-400 dark:text-neutral-500 cursor-not-allowed' : 'bg-primary hover:bg-primary-dark text-white';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
      if (currentPage < totalPages) {
        currentPage++;
        renderDataEntriesLog();
      }
    });
    dataEntriesPaginationContainer.appendChild(nextButton);
  }

  async function handleDeleteEntry(event) {
    const button = event.currentTarget;
    const entryId = button.dataset.id;
    const entryType = button.dataset.type;

    if (!confirm(`Are you sure you want to delete this ${entryType} entry?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/delete_entry/${entryType}/${entryId}`, {
        method: 'DELETE',
        headers: {
          // Add any necessary headers, like CSRF token if applicable
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete entry');
      }

      // Remove entry from local data and re-render
      if (entryType === 'fitness') {
        window.rawData = window.rawData.filter(entry => entry.id !== parseInt(entryId));
      } else if (entryType === 'food') {
        window.foodData = window.foodData.filter(entry => entry.id !== parseInt(entryId));
      }
      
      // Re-filter and update everything
      updateDashboard(); 

      alert('Entry deleted successfully!');

    } catch (error) {
      console.error('Error deleting entry:', error);
      alert(`Error: ${error.message}`);
    }
  }

  // ---------- Main Dashboard Update Function ----------
  function updateDashboard() {
    const start = startDateInput.value || getNDaysAgo(6);
    const end = endDateInput.value || getToday();

    // Filter records within the selected date range
    const filteredFitness = window.rawData.filter(row => row.date >= start && row.date <= end);
    const filteredFood = window.foodData.filter(row => row.date >= start && row.date <= end);

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
      if (entry.activity_type) {
        typeCounts[entry.activity_type] = (typeCounts[entry.activity_type] || 0) + 1;
      }
    });

    // Summary totals
    const totalWorkouts = filteredFitness.length;
    const totalTime = durations.reduce((sum, d) => sum + d, 0);
    const totalCalories = calories.reduce((sum, c) => sum + c, 0);
    const totalIntake = intake.reduce((sum, c) => sum + c, 0);
    const calorieGap = totalIntake - totalCalories;

    // Update combined data for the log
    combinedData = combineAndSortData(filteredFitness, filteredFood);
    currentPage = 1; // Reset to first page on filter change
    renderDataEntriesLog();

    // ---------- Update Summary Card ----------
    const summaryContentDiv = document.getElementById('summary-content');
    if (summaryContentDiv) {
      summaryContentDiv.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <!-- Total Calories Burned Card -->
          <div class="flex flex-col items-center justify-center p-6 bg-sky-100 dark:bg-sky-700 rounded-xl shadow-lg transform hover:scale-105 transition-transform duration-300">
            <p class="text-sm font-medium text-sky-600 dark:text-sky-300 uppercase tracking-wider">Calories Burned</p>
            <p class="text-3xl font-bold text-sky-800 dark:text-sky-100 mt-1">${totalCalories.toLocaleString()} kcal</p>
          </div>

          <!-- Total Workout Time Card -->
          <div class="flex flex-col items-center justify-center p-6 bg-emerald-100 dark:bg-emerald-700 rounded-xl shadow-lg transform hover:scale-105 transition-transform duration-300">
            <p class="text-sm font-medium text-emerald-600 dark:text-emerald-300 uppercase tracking-wider">Workout Time</p>
            <p class="text-3xl font-bold text-emerald-800 dark:text-emerald-100 mt-1">${totalTime.toLocaleString()} mins</p>
          </div>

          <!-- Calorie Balance Card -->
          <div class="flex flex-col items-center justify-center p-6 ${calorieGap <= 0 ? 'bg-teal-100 dark:bg-teal-700' : 'bg-rose-100 dark:bg-rose-700'} rounded-xl shadow-lg transform hover:scale-105 transition-transform duration-300">
            <p class="text-sm font-medium ${calorieGap <= 0 ? 'text-teal-600 dark:text-teal-300' : 'text-rose-600 dark:text-rose-300'} uppercase tracking-wider">Calorie Balance</p>
            <p class="text-3xl font-bold ${calorieGap <= 0 ? 'text-teal-800 dark:text-teal-100' : 'text-rose-800 dark:text-rose-100'} mt-1">${calorieGap.toLocaleString()} kcal</p>
          </div>
        </div>
        <div class="mt-4 text-center">
          <p class="text-neutral-600 dark:text-neutral-300"><span class="font-semibold">Top Activities:</span> ${Object.keys(typeCounts).slice(0, 3).join(', ') || 'N/A'}</p>
        </div>
      `;
    }

    // ---------- Charts Section ----------

    // Destroy previous charts if they exist
    durationChart?.destroy();
    caloriesBurnedChart?.destroy(); 
    caloriesEfficiencyChart?.destroy(); // Destroy new chart instance
    intensityChart?.destroy();
    performanceChart?.destroy();
    emotionChart?.destroy();
    goalChart?.destroy();
    calorieBalanceChart?.destroy();
    nutritionChart?.destroy();

    // Line Chart: Duration
    if (ctxDuration) {
      durationChart = new Chart(ctxDuration, {
        type: 'line',
        data: {
          labels: allDates,
          datasets: [{ 
            label: 'Duration (min)', 
            data: durations, 
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Minutes'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    }

    // Line Chart: Calories Burned Trend
    if (ctxCaloriesBurned) {
      caloriesBurnedChart = new Chart(ctxCaloriesBurned, {
        type: 'line',
        data: {
          labels: allDates,
          datasets: [{
            label: 'Calories Burned',
            data: calories, // Use the 'calories' array
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Calories'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    }

    // Line Chart: Calorie Burn Efficiency (Calories per Minute)
    if (ctxCaloriesEfficiency) {
      const efficiencyData = allDates.map(date => {
        const duration = groupedDuration[date] || 0;
        const calories = groupedBurned[date] || 0;
        return duration > 0 ? calories / duration : 0; // Calculate calories per minute
      });

      caloriesEfficiencyChart = new Chart(ctxCaloriesEfficiency, {
        type: 'line',
        data: {
          labels: allDates,
          datasets: [{
            label: 'Calories Burned per Minute',
            data: efficiencyData,
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Calories/Minute'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    }

    // Intensity Chart (Activity Intensity Analysis)
    if (ctxIntensity) {
      // Calculate intensity (calories/minute) for each activity type
      const intensityData = [];
      const activityTypes = Object.keys(typeCounts);
      
      activityTypes.forEach(type => {
        const activities = filteredFitness.filter(entry => entry.activity_type === type);
        let totalCalories = 0;
        let totalDuration = 0;
        
        activities.forEach(activity => {
          totalCalories += (activity.calories_burned || 0);
          totalDuration += (activity.duration || 0);
        });
        
        // Calculate intensity (calories/minute)
        const intensity = totalDuration > 0 ? totalCalories / totalDuration : 0;
        
        intensityData.push({
          type: type,
          intensity: intensity,
          count: activities.length,
          totalCalories: totalCalories
        });
      });
      
      // Sort by intensity
      intensityData.sort((a, b) => b.intensity - a.intensity);

      // Slice to get top 10 records
      const top10IntensityData = intensityData.slice(0, 10);
      
      // Create chart data
      const labels = top10IntensityData.map(item => item.type);
      const data = top10IntensityData.map(item => item.intensity);
      const backgroundColors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
      ];
      
      // Create chart
      intensityChart = new Chart(ctxIntensity, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Intensity (calories/min)',
            data: data,
            backgroundColor: backgroundColors.slice(0, labels.length),
            borderColor: backgroundColors.slice(0, labels.length).map(color => color.replace('0.7', '1')),
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Calories per Minute'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const index = context.dataIndex;
                  const item = top10IntensityData[index]; // Use top10IntensityData here
                  return [
                    `Total Calories: ${item.totalCalories.toFixed(0)}`,
                    `Sessions: ${item.count}`
                  ];
                }
              }
            }
          }
        }
      });
    }
    
    // Performance Radar Chart
    if (ctxPerformance) {
      // Calculate performance metrics
      const metrics = {
        'Consistency': calculateConsistency(filteredFitness, allDates),
        'Duration': calculateAverageDuration(filteredFitness),
        'Intensity': calculateAverageIntensity(filteredFitness),
        'Frequency': Math.min(Object.keys(typeCounts).length, 10),
        'Diversity': calculateDiversityScore(filteredFitness)
      };
      
      // Normalize metrics (0-100)
      const maxValues = {
        'Consistency': 100,
        'Duration': 120, // 2-hour workout is considered excellent
        'Intensity': 15, // 15 calories per minute is high intensity
        'Frequency': 10, // 10 different activities is diverse
        'Diversity': 10  // 10 different activity types is very diverse
      };
      
      const normalizedMetrics = {};
      Object.keys(metrics).forEach(key => {
        normalizedMetrics[key] = Math.min(100, (metrics[key] / maxValues[key]) * 100);
      });
      
      // Create radar chart data
      const radarData = {
        labels: Object.keys(normalizedMetrics),
        datasets: [{
          label: 'Your Performance',
          data: Object.values(normalizedMetrics),
          fill: true,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgb(54, 162, 235)',
          pointBackgroundColor: 'rgb(54, 162, 235)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(54, 162, 235)'
        }]
      };
      
      // Create chart
      performanceChart = new Chart(ctxPerformance, {
        type: 'radar',
        data: radarData,
        options: {
          maintainAspectRatio: false, // Ensure chart fills container
          elements: {
            line: {
              borderWidth: 3
            }
          },
          scales: {
            r: {
              angleLines: {
                display: true
              },
              suggestedMin: 0,
              suggestedMax: 100,
              ticks: {
                display: false
              }
            }
          }
        }
      });
    }

    // Calorie Balance Chart
    if (ctxCalorieBalance) {
      calorieBalanceChart = new Chart(ctxCalorieBalance, {
        type: 'bar',
        data: {
          labels: allDates,
          datasets: [
            {
              label: 'Calories Consumed',
              data: allDates.map(date => groupedIntake[date] || 0),
              backgroundColor: 'rgba(255, 99, 132, 0.7)',
              borderColor: 'rgb(255, 99, 132)',
              borderWidth: 1
            },
            {
              label: 'Calories Burned',
              data: allDates.map(date => groupedBurned[date] || 0),
              backgroundColor: 'rgba(75, 192, 192, 0.7)',
              borderColor: 'rgb(75, 192, 192)',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false, // Added to respect container height
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Calories'
              }
            }
          }
        }
      });
    }

    // Nutrition Chart (if we have food data)
    if (ctxNutrition && filteredFood.length > 0) {
      // Group meals by type
      const mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
      const mealData = {};
      
      mealTypes.forEach(type => {
        mealData[type] = {
          count: 0,
          calories: 0
        };
      });
      
      filteredFood.forEach(entry => {
        const mealType = entry.meal_type || 'Snack';
        const type = mealTypes.includes(mealType) ? mealType : 'Snack';
        
        mealData[type].count += 1;
        mealData[type].calories += (entry.calories || 0);
      });
      
      nutritionChart = new Chart(ctxNutrition, {
        type: 'polarArea',
        data: {
          labels: mealTypes,
          datasets: [{
            data: mealTypes.map(type => mealData[type].calories),
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)',
              'rgba(54, 162, 235, 0.7)',
              'rgba(255, 206, 86, 0.7)',
              'rgba(75, 192, 192, 0.7)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false, // Added to respect container height
          plugins: {
            legend: {
              position: 'top'
            }
          }
        }
      });
    }

    // Emotion Chart (if we have emotion data)
    if (ctxEmotion) {
      const emotionCounts = {};
      filteredFitness.forEach(entry => {
        if (entry.emotion) {
          emotionCounts[entry.emotion] = (emotionCounts[entry.emotion] || 0) + 1;
        }
      });
      
      const emotionLabels = Object.keys(emotionCounts);
      const emotionData = Object.values(emotionCounts);
      
      if (emotionLabels.length > 0) {
        emotionChart = new Chart(ctxEmotion, {
          type: 'pie',
          data: {
            labels: emotionLabels,
            datasets: [{
              data: emotionData,
              backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)'
              ]
            }]
          },
          options: { 
            responsive: true,
            maintainAspectRatio: false, // Ensure chart fills container
            plugins: {
              legend: {
                position: 'top'
              }
            }
          }
        });
      }
    }

    // Goal Progress Chart
    if (ctxGoal) {
      initGoalProgressChart(filteredFitness);
    }
  }

  // ---------- Initial Render with Defaults ----------
  if (!startDateInput.value) startDateInput.value = getNDaysAgo(6);
  if (!endDateInput.value) endDateInput.value = getToday();

  // Apply button listener
  applyButton.addEventListener('click', updateDashboard);

  // First load
  updateDashboard();

  // Fetch and display fitness ranking data
  const rankingTableBody = document.getElementById('rankingTableBody');
  const rankingTimePeriodSelect = document.getElementById('rankingTimePeriod'); // Get time period select
  const rankingSortBySelect = document.getElementById('rankingSortBy'); // Get sort by select

  if (rankingTableBody) {
    // Function to handle changes in ranking filters
    function handleRankingFilterChange() {
      const timeRange = rankingTimePeriodSelect ? rankingTimePeriodSelect.value : 'week';
      const sortBy = rankingSortBySelect ? rankingSortBySelect.value : 'calories';
      fetchRankingData(timeRange, sortBy);
    }

    try {
      // Initial fetch using default or selected values from HTML
      handleRankingFilterChange(); 
    } catch (error) {
      console.error("Error fetching initial ranking data:", error);
    }

    // Add event listeners for ranking filter changes
    if (rankingTimePeriodSelect) {
      rankingTimePeriodSelect.addEventListener('change', handleRankingFilterChange);
    }
    if (rankingSortBySelect) {
      rankingSortBySelect.addEventListener('change', handleRankingFilterChange);
    }
  }

  // Function to fetch ranking data from API
  function fetchRankingData(timeRange = 'week', sortBy = 'calories') {
    if (!rankingTableBody) return;
    
    fetch(`/api/visualisation/ranking?time_range=${timeRange}&sort_by=${sortBy}`)
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log("Ranking data:", data);
        displayRankingData(data.ranking);
        // Store the data for export functionality
        window.currentRankingData = data;
      })
      .catch(error => {
        console.error("Error fetching ranking data:", error);
        if (rankingTableBody) {
          rankingTableBody.innerHTML = `
            <tr>
              <td colspan="5" class="px-6 py-4 text-center text-red-500">
                Failed to load ranking data. Please try again later.
              </td>
            </tr>
          `;
        }
      });
  }

  // Function to display ranking data in the table
  function displayRankingData(rankingData) {
    if (!rankingTableBody) return;

    const limitedData = rankingData.slice(0, 10); // Limit to top 10

    if (!limitedData || limitedData.length === 0) {
      rankingTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="px-6 py-4 text-center text-neutral-500 dark:text-neutral-400">
            No ranking data available for this time period
          </td>
        </tr>
      `;
      return;
    }

    // Clear existing rows
    rankingTableBody.innerHTML = '';

    // Add rows for each user in the ranking
    limitedData.forEach(entry => {
      const row = document.createElement('tr');
      
      // Highlight the current user
      if (entry.is_current_user) {
        row.classList.add('bg-primary-50', 'dark:bg-primary-900/30');
      }

      // Add row hover effect
      row.classList.add('hover:bg-neutral-100', 'dark:hover:bg-neutral-700/50', 'transition-colors');

      // Create table cells
      row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="flex items-center">
            <span class="text-sm font-medium ${entry.rank <= 3 ? 'text-primary dark:text-primary-light font-bold' : 'text-neutral-900 dark:text-neutral-100'}">
              ${entry.rank <= 3 ? getMedalEmoji(entry.rank) : ''} ${entry.rank}
            </span>
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="flex items-center">
            <span class="text-sm font-medium ${entry.is_current_user ? 'text-primary-dark dark:text-primary-light font-bold' : 'text-neutral-900 dark:text-neutral-100'}">
              ${entry.username} ${entry.is_current_user ? '(You)' : ''}
            </span>
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="text-sm text-neutral-900 dark:text-neutral-100">
            ${entry.total_calories_burned?.toLocaleString() || 0} kcal
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="text-sm text-neutral-900 dark:text-neutral-100">
            ${entry.total_duration?.toLocaleString() || 0} mins
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="text-sm text-neutral-900 dark:text-neutral-100">
            ${entry.activity_count?.toLocaleString() || 0}
          </span>
        </td>
      `;

      rankingTableBody.appendChild(row);
    });
  }

  // Helper function to get medal emoji for top 3 ranks
  function getMedalEmoji(rank) {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '';
    }
  }
  
  // Helper function: Calculate consistency (percentage of days with activity)
  function calculateConsistency(fitnessData, allDates) {
    if (fitnessData.length === 0 || allDates.length === 0) return 0;
    
    // Get dates with activity
    const activeDates = new Set(fitnessData.map(entry => entry.date));
    
    // Calculate consistency percentage
    return (activeDates.size / allDates.length) * 100;
  }
  
  // Helper function: Calculate average duration
  function calculateAverageDuration(fitnessData) {
    if (fitnessData.length === 0) return 0;
    
    const totalDuration = fitnessData.reduce((sum, entry) => sum + (entry.duration || 0), 0);
    return totalDuration / fitnessData.length;
  }
  
  // Helper function: Calculate average intensity
  function calculateAverageIntensity(fitnessData) {
    if (fitnessData.length === 0) return 0;
    
    let totalCalories = 0;
    let totalDuration = 0;
    
    fitnessData.forEach(entry => {
      totalCalories += (entry.calories_burned || 0);
      totalDuration += (entry.duration || 0);
    });
    
    return totalDuration > 0 ? (totalCalories / totalDuration) : 0;
  }
  
  // Helper function: Calculate diversity score
  function calculateDiversityScore(fitnessData) {
    if (fitnessData.length === 0) return 0;
    
    const uniqueActivities = new Set(fitnessData.map(entry => entry.activity_type).filter(Boolean));
    return uniqueActivities.size;
  }

  // Goal Progress Tracker functions
  function initGoalProgressChart(filteredFitness) {
    const ctxGoal = document.getElementById('goalProgressChart')?.getContext('2d');
    if (!ctxGoal) return;
    
    // Check if we have valid data
    if (!filteredFitness || !Array.isArray(filteredFitness) || filteredFitness.length === 0) {
      console.warn("No fitness data available for goal progress chart");
      return;
    }
    
    // Calculate weekly sessions
    function calculateWeeklySessions(fitnessData) {
      // Group entries by week
      const weekMap = {};
      fitnessData.forEach(entry => {
        const date = new Date(entry.date);
        const weekKey = `${date.getFullYear()}-${Math.floor(date.getTime() / (7 * 24 * 60 * 60 * 1000))}`;
        if (!weekMap[weekKey]) {
          weekMap[weekKey] = new Set();
        }
        weekMap[weekKey].add(entry.date);
      });
      
      // Calculate average sessions per week
      const weeks = Object.keys(weekMap);
      if (weeks.length === 0) return 0;
      
      const totalSessions = weeks.reduce((sum, week) => sum + weekMap[week].size, 0);
      return totalSessions / weeks.length;
    }
    
    // Calculate average daily movement
    function calculateAverageDailyMovement(fitnessData) {
      // Group entries by day
      const dayMap = {};
      fitnessData.forEach(entry => {
        if (!dayMap[entry.date]) {
          dayMap[entry.date] = 0;
        }
        dayMap[entry.date] += (entry.duration || 0);
      });
      
      // Calculate average minutes per day
      const days = Object.keys(dayMap);
      if (days.length === 0) return 0;
      
      const totalMinutes = days.reduce((sum, day) => sum + dayMap[day], 0);
      return totalMinutes / days.length;
    }

    // Define some typical fitness goals
    const goals = {
      'Weekly Activity': {
        target: 5, // 5 sessions per week
        current: calculateWeeklySessions(filteredFitness),
        unit: 'sessions'
      },
      'Daily Movement': {
        target: 30, // 30 minutes average per day
        current: calculateAverageDailyMovement(filteredFitness),
        unit: 'minutes'
      },
      'Calorie Burn': {
        target: 2000, // 2000 calories per week
        current: filteredFitness.reduce((sum, entry) => sum + (entry.calories_burned || 0), 0),
        unit: 'calories'
      },
      'Activity Diversity': {
        target: 3, // 3 different types of activities
        current: calculateDiversityScore(filteredFitness),
        unit: 'types'
      }
    };
    
    // Calculate percentage of goal achievement for each goal
    const goalPercentages = {};
    Object.keys(goals).forEach(goal => {
      const percentage = Math.min(100, ((goals[goal].current || 0) / goals[goal].target) * 100);
      goalPercentages[goal] = Math.round(percentage);
    });
    
    // Create datasets
    const datasets = [
      {
        label: 'Goal Achievement',
        data: Object.values(goalPercentages),
        backgroundColor: Object.values(goalPercentages).map(percentage => 
          percentage >= 100 ? 'rgba(75, 192, 92, 0.8)' :
          percentage >= 70 ? 'rgba(255, 206, 86, 0.8)' :
          'rgba(255, 99, 132, 0.8)'
        ),
        borderColor: 'white',
        borderWidth: 2,
        borderRadius: 5
      }
    ];

    // Destroy previous chart if exists
    goalChart?.destroy();
    
    // Create chart
    goalChart = new Chart(ctxGoal, {
      type: 'bar',
      data: {
        labels: Object.keys(goals),
        datasets: datasets
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 100,
            title: {
              display: true,
              text: 'Goal Achievement (%)'
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                const goalName = context.label;
                const percentage = context.raw;
                const goal = goals[goalName];
                return [
                  `Achievement: ${percentage}%`,
                  `Current: ${goal.current.toFixed(1)} ${goal.unit}`,
                  `Target: ${goal.target} ${goal.unit}`
                ];
              }
            }
          }
        }
      }
    });
  }
});
