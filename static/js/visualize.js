document.addEventListener('DOMContentLoaded', () => {
  // Debug data loading
  console.log("DOM Content Loaded");
  console.log("Raw data available:", window.rawData);
  console.log("Food data available:", window.foodData);
  
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
    // Check if data is available
    if (!data || !data.fitness_entries || !data.food_entries) {
      console.error("No data available for visualization");
      return;
    }
    
    console.log("Initializing charts with data:", data);
    
    // Initialize charts if they exist
    initDurationChart(data.fitness_entries);
    initIntensityChart(data.fitness_entries);
    initPerformanceRadarChart(data.fitness_entries);
    initActivityPieChart(data.fitness_entries);
    initGoalProgressChart(data.fitness_entries, data.summary);
    initCaloriesDashboard(data.fitness_entries, data.food_entries, data.summary);
    
    // If emotion data is available, initialize emotion chart
    if (data.fitness_entries.some(entry => entry.emotion)) {
      initEmotionChart(data.fitness_entries);
    }
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
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return `Duration: ${context.parsed.y} mins`;
              }
            }
          }
        }
      }
    });
  }
  
  // Initialize Intensity Chart (replacing Calories Chart)
  function initIntensityChart(fitnessData) {
    const canvas = document.getElementById('intensityChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.intensityChartInstance) {
      window.intensityChartInstance.destroy();
    }
    
    // Check if we have valid data
    if (!fitnessData || !Array.isArray(fitnessData) || fitnessData.length === 0) {
      console.warn("No fitness data available for intensity chart");
      // Display a message on the canvas
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No fitness data available for intensity analysis', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Process data for chart - calculate calories burned per minute as intensity
    const activityTypes = [...new Set(fitnessData.map(entry => entry.activity_type).filter(Boolean))];
    
    // If no activity types with valid data, show a message
    if (activityTypes.length === 0) {
      console.warn("No activity types found in fitness data");
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No activity type data available', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    const intensityData = {};
    activityTypes.forEach(type => {
      const activities = fitnessData.filter(entry => entry.activity_type === type);
      let totalCalories = 0;
      let totalDuration = 0;
      
      activities.forEach(activity => {
        totalCalories += (activity.calories_burned || 0);
        totalDuration += (activity.duration || 0);
      });
      
      // Calculate average calories burned per minute (intensity)
      const intensity = totalDuration > 0 ? (totalCalories / totalDuration).toFixed(2) : 0;
      intensityData[type] = {
        intensity: parseFloat(intensity),
        count: activities.length,
        totalCalories: totalCalories
      };
    });
    
    // Sort activities by intensity
    const sortedActivities = Object.keys(intensityData).sort((a, b) => 
      intensityData[b].intensity - intensityData[a].intensity);
    
    // Select top activities for better visualization
    const topActivities = sortedActivities.slice(0, Math.min(7, sortedActivities.length));
    
    // If no activities to show, display a message
    if (topActivities.length === 0) {
      console.warn("No activities with intensity data");
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No activity intensity data available', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Colors array
    const colorScale = [
      'rgba(255, 99, 132, 0.8)',   // High intensity - red
      'rgba(255, 159, 64, 0.8)',   // Orange
      'rgba(255, 205, 86, 0.8)',   // Yellow
      'rgba(75, 192, 192, 0.8)',   // Green
      'rgba(54, 162, 235, 0.8)',   // Blue
      'rgba(153, 102, 255, 0.8)',  // Purple
      'rgba(201, 203, 207, 0.8)'   // Low intensity - gray
    ];
    
    // Create dataset with bubble size representing activity count
    const dataset = {
      label: 'Activity Intensity',
      data: topActivities.map((activity, index) => ({
        x: intensityData[activity].intensity,
        y: intensityData[activity].totalCalories,
        r: Math.max(5, Math.min(20, intensityData[activity].count * 3))
      })),
      backgroundColor: topActivities.map((_, i) => colorScale[i % colorScale.length])
    };
    
    // Create chart
    window.intensityChartInstance = new Chart(canvas, {
      type: 'bubble',
      data: {
        datasets: [dataset]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const activityName = topActivities[context.dataIndex];
                const intensity = intensityData[activityName].intensity;
                const totalCals = intensityData[activityName].totalCalories;
                const count = intensityData[activityName].count;
                return [
                  `Activity: ${activityName}`,
                  `Intensity: ${intensity} cal/min`,
                  `Total Calories: ${totalCals}`,
                  `Sessions: ${count}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Calories Burned Per Minute (Intensity)'
            },
            suggestedMin: 0
          },
          y: {
            title: {
              display: true,
              text: 'Total Calories Burned'
            },
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Initialize Performance Radar Chart (new visualization)
  function initPerformanceRadarChart(fitnessData) {
    const canvas = document.getElementById('performanceRadarChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.performanceRadarChartInstance) {
      window.performanceRadarChartInstance.destroy();
    }
    
    // Check if we have valid data
    if (!fitnessData || !Array.isArray(fitnessData) || fitnessData.length === 0) {
      console.warn("No fitness data available for performance radar chart");
      // Display a message on the canvas
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No fitness data available for performance analysis', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Extract activity types and compute metrics for each
    const activityTypes = [...new Set(fitnessData.map(entry => entry.activity_type).filter(Boolean))];
    
    // Take only top 5 activities by frequency for radar
    const activityCounts = {};
    fitnessData.forEach(entry => {
      if (entry.activity_type) {
        activityCounts[entry.activity_type] = (activityCounts[entry.activity_type] || 0) + 1;
      }
    });
    
    // Calculate performance metrics
    const metrics = {
      'Consistency': calculateConsistency(fitnessData),
      'Duration': calculateAverageDuration(fitnessData),
      'Intensity': calculateAverageIntensity(fitnessData),
      'Frequency': Math.min(activityTypes.length, 10), // Cap at 10
      'Diversity': calculateDiversityScore(fitnessData)
    };
    
    // Normalize metrics to 0-100 scale
    const normalizedMetrics = normalizeMetrics(metrics);
    
    // Create chart data
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
    window.performanceRadarChartInstance = new Chart(canvas, {
      type: 'radar',
      data: radarData,
      options: {
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
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                const metricName = context.label;
                const score = context.raw;
                const originalValue = metrics[metricName];
                let unit = '';
                
                switch(metricName) {
                  case 'Duration':
                    unit = ' mins';
                    break;
                  case 'Intensity':
                    unit = ' cal/min';
                    break;
                  case 'Frequency':
                  case 'Diversity':
                    unit = ' types';
                    break;
                  default:
                    unit = '';
                }
                
                return [`Score: ${score.toFixed(0)}/100`, `Value: ${originalValue.toFixed(1)}${unit}`];
              }
            }
          }
        }
      }
    });
  }
  
  // Helper function to calculate consistency (% of days with activity)
  function calculateConsistency(fitnessData) {
    if (fitnessData.length === 0) return 0;
    
    // Get unique dates
    const uniqueDates = new Set(fitnessData.map(entry => entry.date));
    
    // Get date range
    const dates = [...uniqueDates].sort();
    if (dates.length <= 1) return 100; // Only one day of data
    
    const firstDate = new Date(dates[0]);
    const lastDate = new Date(dates[dates.length - 1]);
    const daysDiff = Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24)) + 1;
    
    // Calculate consistency as percentage of days with activity
    return (uniqueDates.size / daysDiff) * 100;
  }
  
  // Helper function to calculate average duration
  function calculateAverageDuration(fitnessData) {
    if (fitnessData.length === 0) return 0;
    const totalDuration = fitnessData.reduce((sum, entry) => sum + (entry.duration || 0), 0);
    return totalDuration / fitnessData.length;
  }
  
  // Helper function to calculate average intensity
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
  
  // Helper function to calculate diversity score
  function calculateDiversityScore(fitnessData) {
    const uniqueActivities = new Set(fitnessData.map(entry => entry.activity_type).filter(Boolean));
    return uniqueActivities.size;
  }
  
  // Helper function to normalize metrics to 0-100 scale
  function normalizeMetrics(metrics) {
    const normalizedMetrics = {};
    const maxValues = {
      'Consistency': 100,
      'Duration': 120, // A 2-hour workout is considered excellent
      'Intensity': 15, // 15 calories per minute is high intensity
      'Frequency': 10, // 10 different activities is diverse
      'Diversity': 10  // 10 different activity types is very diverse
    };
    
    Object.keys(metrics).forEach(key => {
      normalizedMetrics[key] = Math.min(100, (metrics[key] / maxValues[key]) * 100);
    });
    
    return normalizedMetrics;
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
    
    // Sort activities by count
    const sortedActivities = Object.entries(activityCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6); // Top 6 activities
    
    const activities = sortedActivities.map(entry => entry[0]);
    const counts = sortedActivities.map(entry => entry[1]);
    
    // Generate dynamic colors
    const colorPalette = [
      'rgba(255, 99, 132, 0.8)',
      'rgba(54, 162, 235, 0.8)',
      'rgba(255, 206, 86, 0.8)',
      'rgba(75, 192, 192, 0.8)',
      'rgba(153, 102, 255, 0.8)',
      'rgba(255, 159, 64, 0.8)'
    ];
    
    // Create chart
    window.activityPieChartInstance = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: activities,
        datasets: [{
          data: counts,
          backgroundColor: colorPalette.slice(0, activities.length),
          borderColor: 'white',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'right',
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.raw;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = Math.round((value / total) * 100);
                return `${label}: ${value} sessions (${percentage}%)`;
              }
            }
          }
        },
        cutout: '60%'
      }
    });
  }
  
  // Initialize Goal Progress Chart (new visualization)
  function initGoalProgressChart(fitnessData, summaryData) {
    const canvas = document.getElementById('goalProgressChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.goalProgressChartInstance) {
      window.goalProgressChartInstance.destroy();
    }
    
    // Check if we have valid data
    if (!fitnessData || !Array.isArray(fitnessData) || fitnessData.length === 0) {
      console.warn("No fitness data available for goal progress chart");
      // Display a message on the canvas
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No fitness data available to track goals', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Ensure summary data exists
    const summary = summaryData || {
      total_calories_burned: 0,
      total_workout_minutes: 0
    };
    
    // Define some typical fitness goals
    const goals = {
      'Weekly Activity': {
        target: 5, // 5 sessions per week
        current: calculateWeeklySessions(fitnessData),
        unit: 'sessions'
      },
      'Daily Movement': {
        target: 30, // 30 minutes average per day
        current: calculateAverageDailyMovement(fitnessData),
        unit: 'minutes'
      },
      'Calorie Burn': {
        target: 2000, // 2000 calories per week
        current: summary.total_calories_burned || 0,
        unit: 'calories'
      },
      'Activity Diversity': {
        target: 3, // 3 different types of activities
        current: calculateDiversityScore(fitnessData),
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
    
    // Create chart
    window.goalProgressChartInstance = new Chart(canvas, {
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
  
  // Helper function to calculate weekly sessions
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
  
  // Helper function to calculate average daily movement
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
    return Math.round(totalMinutes / days.length);
  }
  
  // Initialize Calories Dashboard (combines previous charts)
  function initCaloriesDashboard(fitnessData, foodData, summaryData) {
    initCalorieBalanceChart(fitnessData, foodData);
    initNutritionChart(foodData);
  }
  
  // Initialize Calorie Balance Chart
  function initCalorieBalanceChart(fitnessData, foodData) {
    const canvas = document.getElementById('calorieBalanceChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.calorieBalanceChartInstance) {
      window.calorieBalanceChartInstance.destroy();
    }
    
    // Process data for chart
    const dates = [...new Set([...fitnessData.map(entry => entry.date), ...foodData.map(entry => entry.date)])].sort();
    
    // Only use the last 7 days for clarity
    const recentDates = dates.slice(-7);
    
    const caloriesBurnedByDate = {};
    const caloriesConsumedByDate = {};
    
    recentDates.forEach(date => {
      caloriesBurnedByDate[date] = fitnessData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.calories_burned || 0), 0);
        
      caloriesConsumedByDate[date] = foodData
        .filter(entry => entry.date === date)
        .reduce((sum, entry) => sum + (entry.calories || 0), 0);
    });
    
    // Create chart
    window.calorieBalanceChartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: recentDates,
        datasets: [
          {
            label: 'Calories Consumed',
            data: recentDates.map(date => caloriesConsumedByDate[date] || 0),
            backgroundColor: 'rgba(255, 99, 132, 0.7)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 1
          },
          {
            label: 'Calories Burned',
            data: recentDates.map(date => caloriesBurnedByDate[date] || 0),
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgb(75, 192, 192)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Calorie Balance'
          },
          tooltip: {
            callbacks: {
              afterBody: function(tooltipItems) {
                const index = tooltipItems[0].dataIndex;
                const date = recentDates[index];
                const consumed = caloriesConsumedByDate[date] || 0;
                const burned = caloriesBurnedByDate[date] || 0;
                const balance = consumed - burned;
                return `Net Balance: ${balance.toFixed(0)} cal`;
              }
            }
          }
        },
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
  
  // Initialize Nutrition Chart
  function initNutritionChart(foodData) {
    const canvas = document.getElementById('nutritionChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.nutritionChartInstance) {
      window.nutritionChartInstance.destroy();
    }
    
    // Check if we have valid food data
    if (!foodData || !Array.isArray(foodData) || foodData.length === 0) {
      console.warn("No food data available for nutrition chart");
      // Display a message on the canvas
      const ctx = canvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.fillStyle = '#666';
      ctx.textAlign = 'center';
      ctx.fillText('No nutrition data available', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Group meals by type with default handling
    const mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
    const mealData = {};
    
    // Initialize all meal types with zero values
    mealTypes.forEach(type => {
      mealData[type] = {
        count: 0,
        calories: 0
      };
    });
    
    // Process food data
    foodData.forEach(entry => {
      // Handle missing meal_type with a default value
      const mealType = entry.meal_type || 'Snack';
      
      // If this meal type is not in our predefined types, add it to Snack
      const type = mealTypes.includes(mealType) ? mealType : 'Snack';
      
      if (!mealData[type]) {
        mealData[type] = { count: 0, calories: 0 };
      }
      
      mealData[type].count += 1;
      mealData[type].calories += (entry.calories || 0);
    });
    
    // Calculate total calories for percentage
    const totalCalories = Object.values(mealData).reduce((sum, data) => sum + data.calories, 0);
    
    // Create chart
    window.nutritionChartInstance = new Chart(canvas, {
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
        plugins: {
          title: {
            display: true,
            text: 'Calorie Distribution by Meal'
          },
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const mealType = context.label;
                const calories = context.raw;
                const percentage = totalCalories > 0 ? Math.round((calories / totalCalories) * 100) : 0;
                return `${mealType}: ${calories} cal (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }
  
  // New function to visualize emotions if available
  function initEmotionChart(fitnessData) {
    const canvas = document.getElementById('emotionChart');
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (window.emotionChartInstance) {
      window.emotionChartInstance.destroy();
    }
    
    // Filter entries with emotion data
    const entriesWithEmotion = fitnessData.filter(entry => entry.emotion);
    
    if (entriesWithEmotion.length === 0) {
      console.warn("No emotion data available for chart");
      return;
    }
    
    // Count emotions
    const emotionCounts = {};
    entriesWithEmotion.forEach(entry => {
      emotionCounts[entry.emotion] = (emotionCounts[entry.emotion] || 0) + 1;
    });
    
    // Prepare data for chart
    const labels = Object.keys(emotionCounts);
    const data = Object.values(emotionCounts);
    
    // Create emotion chart
    window.emotionChartInstance = new Chart(canvas, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(201, 203, 207, 0.7)'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Workout Emotions'
          },
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const emotion = context.label;
                const count = context.raw;
                const percentage = Math.round((count / entriesWithEmotion.length) * 100);
                return `${emotion}: ${count} workouts (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }
});