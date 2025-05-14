document.addEventListener('DOMContentLoaded', () => {
  // Fetch and display fitness ranking data
  fetchRankingData();

  // Add event listener for ranking time period change
  const rankingTimePeriodSelect = document.getElementById('rankingTimePeriod');
  if (rankingTimePeriodSelect) {
    rankingTimePeriodSelect.addEventListener('change', () => {
      fetchRankingData(rankingTimePeriodSelect.value);
    });
  }
  
  // Add event listener for ranking sort option change
  const rankingSortBySelect = document.getElementById('rankingSortBy');
  if (rankingSortBySelect) {
    rankingSortBySelect.addEventListener('change', () => {
      fetchRankingData(rankingTimePeriodSelect.value, rankingSortBySelect.value);
    });
  }
  
  // Add event listener for export button
  const exportRankingButton = document.getElementById('exportRanking');
  if (exportRankingButton) {
    exportRankingButton.addEventListener('click', () => {
      exportRankingData();
    });
  }

  // Function to fetch ranking data from API
  function fetchRankingData(timeRange = 'week', sortBy = 'calories') {
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
        document.getElementById('rankingTableBody').innerHTML = `
          <tr>
            <td colspan="5" class="px-6 py-4 text-center text-red-500">
              Failed to load ranking data. Please try again later.
            </td>
          </tr>
        `;
      });
  }

  // Function to display ranking data in the table
  function displayRankingData(rankingData) {
    const tableBody = document.getElementById('rankingTableBody');
    
    if (!tableBody) {
      console.error('Ranking table body element not found');
      return;
    }

    if (!rankingData || rankingData.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="px-6 py-4 text-center text-neutral-500 dark:text-neutral-400">
            No ranking data available for this time period
          </td>
        </tr>
      `;
      return;
    }

    // Clear existing rows
    tableBody.innerHTML = '';

    // Add rows for each user in the ranking
    rankingData.forEach(entry => {
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
            ${entry.total_calories_burned.toLocaleString()} kcal
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="text-sm text-neutral-900 dark:text-neutral-100">
            ${entry.total_duration.toLocaleString()} mins
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="text-sm text-neutral-900 dark:text-neutral-100">
            ${entry.activity_count.toLocaleString()}
          </span>
        </td>
      `;

      tableBody.appendChild(row);
    });
  }
  
  // Function to export ranking data as CSV
  function exportRankingData() {
    if (!window.currentRankingData || !window.currentRankingData.ranking) {
      alert('No ranking data available to export');
      return;
    }
    
    const rankingData = window.currentRankingData.ranking;
    const timeRange = window.currentRankingData.time_range;
    const sortBy = window.currentRankingData.sort_by;
    
    // Create CSV content
    let csvContent = 'Rank,Username,Calories Burned,Duration (mins),Activity Count\n';
    
    rankingData.forEach(entry => {
      csvContent += `${entry.rank},"${entry.username}",${entry.total_calories_burned},${entry.total_duration},${entry.activity_count}\n`;
    });
    
    // Create a download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `fitness_ranking_${timeRange}_${sortBy}_${new Date().toISOString().slice(0,10)}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

  // Fetch visualization data with adjustment for last active week
  fetchFitnessDataForLastActiveWeek();
  
  // Function to fetch fitness data focusing on the last active week
  function fetchFitnessDataForLastActiveWeek() {
    // First get all fitness data to find the last active date
    fetch("/api/visualisation/fitness?days=90")  // Get last 90 days of data to find last activity
      .then(res => res.json())
      .then(data => {
        // Find the last date with activity
        let lastActiveDate = findLastActiveDate(data.fitness_entries);
        if (!lastActiveDate) {
          // If no activity found, use current date
          console.log("No recent activity found, using current date");
          return fetch("/api/visualisation/fitness?days=7");
        } else {
          console.log("Last active date found:", lastActiveDate);
          // Now fetch one week of data ending on the last active date
          const endDate = new Date(lastActiveDate);
          const startDate = new Date(endDate);
          startDate.setDate(startDate.getDate() - 6); // 7 days including the last active day
          
          // Format dates for API
          const formattedEndDate = formatDateForAPI(endDate);
          const formattedStartDate = formatDateForAPI(startDate);
          
          // Update date inputs in the UI
          updateDateInputs(formattedStartDate, formattedEndDate);
          
          return fetch(`/api/visualisation/fitness?days=7&start_date=${formattedStartDate}&end_date=${formattedEndDate}`);
        }
      })
      .then(res => res.json())
      .then(data => {
        console.log("Fitness data for last active week:", data);
        
        // Update summary content
        updateSummary(data.summary);
        
        // Initialize charts with the data
        initializeCharts(data);
      })
      .catch(error => {
        console.error("Error fetching fitness data:", error);
        // Fallback to regular data fetch
        fetch("/api/visualisation/fitness")
          .then(res => res.json())
          .then(data => {
            updateSummary(data.summary);
            initializeCharts(data);
          });
      });
  }
  
  // Function to find the last date with activity data
  function findLastActiveDate(fitnessEntries) {
    if (!fitnessEntries || fitnessEntries.length === 0) {
      return null;
    }
    
    // Sort entries by date in descending order
    const sortedEntries = [...fitnessEntries].sort((a, b) => {
      return new Date(b.date) - new Date(a.date);
    });
    
    // Return the most recent date
    return sortedEntries[0].date;
  }
  
  // Function to format date for API
  function formatDateForAPI(date) {
    return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
  }
  
  // Function to update date inputs in the UI
  function updateDateInputs(startDate, endDate) {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput) {
      startDateInput.value = startDate;
    }
    
    if (endDateInput) {
      endDateInput.value = endDate;
    }
  }
  
  // Add event listener for date filter button
  const applyFilterButton = document.getElementById('applyFilter');
  if (applyFilterButton) {
    applyFilterButton.addEventListener('click', () => {
      applyDateFilter();
    });
  }
  
  // Function to apply date filters and fetch new data
  function applyDateFilter() {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const timePeriodSelect = document.getElementById('timePeriod');
    
    let queryParams = '';
    
    if (startDateInput && startDateInput.value) {
      const startDate = new Date(startDateInput.value);
      const endDate = endDateInput && endDateInput.value ? new Date(endDateInput.value) : new Date();
      
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        alert('Please enter valid dates');
        return;
      }
      
      if (startDate > endDate) {
        alert('Start date cannot be after end date');
        return;
      }
      
      // Calculate days between dates
      const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
      queryParams = `?days=${daysDiff}&start_date=${startDateInput.value}`;
      
      if (endDateInput && endDateInput.value) {
        queryParams += `&end_date=${endDateInput.value}`;
      }
    } else if (timePeriodSelect && timePeriodSelect.value) {
      // If no date range selected, use time period dropdown
      const daysMap = {
        'day': 1,
        'week': 7,
        'month': 30
      };
      queryParams = `?days=${daysMap[timePeriodSelect.value] || 30}`;
    }
    
    // Fetch data with the new filters
    fetch(`/api/visualisation/fitness${queryParams}`)
      .then(res => res.json())
      .then(data => {
        console.log("Filtered fitness data:", data);
        
        // Update summary content
        updateSummary(data.summary);
        
        // Initialize charts with the new data
        initializeCharts(data);
      })
      .catch(error => console.error("Error fetching filtered fitness data:", error));
  }
    
  // Function to update the summary section with data
  function updateSummary(summaryData) {
    if (!summaryData) return;
    
    const summaryContent = document.getElementById('summary-content');
    if (!summaryContent) return;
    
    summaryContent.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 bg-primary-50 dark:bg-primary-900/30 rounded-lg">
          <p class="text-lg font-semibold text-primary-dark dark:text-primary-light">Total Calories Burned</p>
          <p class="text-2xl font-bold mt-2">${summaryData.total_calories_burned.toLocaleString()} kcal</p>
        </div>
        <div class="p-4 bg-neutral-100 dark:bg-neutral-800/50 rounded-lg">
          <p class="text-lg font-semibold">Total Workout Time</p>
          <p class="text-2xl font-bold mt-2">${summaryData.total_workout_minutes.toLocaleString()} mins</p>
        </div>
        <div class="p-4 bg-neutral-100 dark:bg-neutral-800/50 rounded-lg">
          <p class="text-lg font-semibold">Calorie Balance</p>
          <p class="text-2xl font-bold mt-2 ${summaryData.calorie_balance <= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">${summaryData.calorie_balance.toLocaleString()} kcal</p>
        </div>
      </div>
      <div class="mt-4">
        <p class="text-neutral-700 dark:text-neutral-300">Top Activities: ${summaryData.top_activities.map(a => a.type).join(', ')}</p>
      </div>
    `;
  }
  
  // Function to initialize charts
  function initializeCharts(data) {
    // Initialize charts if they exist
    initDurationChart(data.fitness_entries);
    initCaloriesChart(data.fitness_entries);
    initActivityPieChart(data.fitness_entries);
    initStackedChart(data.fitness_entries);
    initGapChart(data.fitness_entries, data.food_entries);
  }
  
  // Initialize Duration Chart
  function initDurationChart(fitnessData) {
    const canvas = document.getElementById('durationChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.durationChartInstance) {
      window.durationChartInstance.destroy();
    }
    
    // Process data for chart
    const dates = [...new Set(fitnessData.map(entry => entry.date))].sort();
    const durationByDate = {};
    
    dates.forEach(date => {
      durationByDate[date] = fitnessData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.duration || 0), 0);
    });
    
    // Create chart
    window.durationChartInstance = new Chart(canvas, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'Duration (mins)',
          data: dates.map(date => durationByDate[date]),
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
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Initialize Calories Chart
  function initCaloriesChart(fitnessData) {
    const canvas = document.getElementById('caloriesChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.caloriesChartInstance) {
      window.caloriesChartInstance.destroy();
    }
    
    // Process data for chart
    const dates = [...new Set(fitnessData.map(entry => entry.date))].sort();
    const caloriesByDate = {};
    
    dates.forEach(date => {
      caloriesByDate[date] = fitnessData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.calories_burned || 0), 0);
    });
    
    // Create chart
    window.caloriesChartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: [{
          label: 'Calories Burned',
          data: dates.map(date => caloriesByDate[date]),
          backgroundColor: 'rgba(255, 99, 132, 0.7)',
          borderColor: 'rgb(255, 99, 132)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Initialize Activity Pie Chart
  function initActivityPieChart(fitnessData) {
    const canvas = document.getElementById('activityPieChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.activityPieChartInstance) {
      window.activityPieChartInstance.destroy();
    }
    
    // Process data for chart
    const activityCounts = {};
    fitnessData.forEach(entry => {
      if (entry.activity_type) {
        activityCounts[entry.activity_type] = (activityCounts[entry.activity_type] || 0) + 1;
      }
    });
    
    const activities = Object.keys(activityCounts);
    
    // Create chart
    window.activityPieChartInstance = new Chart(canvas, {
      type: 'pie',
      data: {
        labels: activities,
        datasets: [{
          data: activities.map(activity => activityCounts[activity]),
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
        responsive: true
      }
    });
  }
  
  // Initialize Stacked Chart
  function initStackedChart(fitnessData) {
    const canvas = document.getElementById('stackedChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.stackedChartInstance) {
      window.stackedChartInstance.destroy();
    }
    
    // Process data for chart
    const dates = [...new Set(fitnessData.map(entry => entry.date))].sort();
    const activityTypes = [...new Set(fitnessData.map(entry => entry.activity_type).filter(Boolean))];
    
    const datasets = activityTypes.map((activity, index) => {
      const data = dates.map(date => {
        return fitnessData
          .filter(entry => entry.date === date && entry.activity_type === activity)
          .reduce((sum, entry) => sum + (entry.duration || 0), 0);
      });
      
      const colors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
      ];
      
      return {
        label: activity,
        data: data,
        backgroundColor: colors[index % colors.length]
      };
    });
    
    // Create chart
    window.stackedChartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: datasets
      },
      options: {
        responsive: true,
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true,
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Initialize Calorie Gap Chart
  function initGapChart(fitnessData, foodData) {
    const canvas = document.getElementById('gapChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.gapChartInstance) {
      window.gapChartInstance.destroy();
    }
    
    // Process data for chart
    const dates = [...new Set([...fitnessData.map(entry => entry.date), ...foodData.map(entry => entry.date)])].sort();
    
    const caloriesBurnedByDate = {};
    const caloriesConsumedByDate = {};
    
    dates.forEach(date => {
      caloriesBurnedByDate[date] = fitnessData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.calories_burned || 0), 0);
        
      caloriesConsumedByDate[date] = foodData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.calories || 0), 0);
    });
    
    const calorieGap = dates.map(date => caloriesConsumedByDate[date] - caloriesBurnedByDate[date]);
    
    // Create chart
    window.gapChartInstance = new Chart(canvas, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'Calorie Gap (+ means surplus)',
          data: calorieGap,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: true,
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: false
          }
        },
        elements: {
          point: {
            backgroundColor: (context) => {
              const value = context.dataset.data[context.dataIndex];
              return value > 0 ? 'rgba(255, 99, 132, 1)' : 'rgba(75, 192, 192, 1)';
            },
            radius: 4,
            hoverRadius: 6
          }
        }
      }
    });
  }
});