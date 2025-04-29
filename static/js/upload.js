// static/js/upload.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const exerciseContainer = document.getElementById('exerciseContainer');
    const addExerciseBtn = document.getElementById('addExerciseBtn');
  
    // Dynamically generate a small sports form
    function createExerciseForm() {
      const div = document.createElement('div');
      div.className = "grid grid-cols-1 md:grid-cols-2 gap-4";

      div.innerHTML = `
        <select name="activity_type" class="block w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent" required>
          <option value="">Select Activity Type</option>
          <option value="Running">Running</option>
          <option value="Walking">Walking</option>
          <option value="Cycling">Cycling</option>
          <option value="Swimming">Swimming</option>
          <option value="Yoga">Yoga</option>
          <option value="Strength Training">Strength Training</option>
          <option value="HIIT">HIIT</option>
          <option value="Pilates">Pilates</option>
          <option value="Hiking">Hiking</option>
        </select>

        <input type="number" name="duration" placeholder="Duration (minutes)" class="block w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent" required>

        <input type="number" name="calories_burned" placeholder="Calories Burned" class="block w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent" required>

        <select name="emotion" class="block w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
          <option value="">Emotion during exercise</option>
          <option value="happy">Happy</option>
          <option value="tired">Tired</option>
          <option value="stressed">Stressed</option>
          <option value="relaxed">Relaxed</option>
        </select>
        `;
        return div;
    }

  // Add a sport by default when the page loads
    exerciseContainer.appendChild(createExerciseForm());

  // Click the button to add a new sport
    addExerciseBtn.addEventListener('click', () => {
        exerciseContainer.appendChild(createExerciseForm());
    });

    form.addEventListener('submit', async (event) => {
      event.preventDefault(); // Refuse default submit
  
      const formData = new FormData(form);
  
      const payload = {
        date: formData.get('date'),
        time: formData.get('time'),
        gender: formData.get('gender'),
        age: formData.get('age'),
        height: formData.get('height'),
        weight: formData.get('weight'),

        activity_type: formData.get('activity_type'),
        duration: formData.get('duration'),
        calories_burned: formData.get('calories_burned'),
        emotion: formData.get('emotion'),
        food_name: formData.get('food_name'),
        food_quantity: formData.get('food_quantity'),
        food_calories: formData.get('food_calories'),
        meal_type: formData.get('meal_type'),
        // 🏃‍♂️ Activities array
        activities: []
      };
      
      // Traverse all sports forms and fill in the activities list
      const exerciseForms = exerciseContainer.querySelectorAll('div');
      exerciseForms.forEach(div => {
          const selects = div.querySelectorAll('select');
          const inputs = div.querySelectorAll('input');

          payload.activities.push({
              activity_type: selects[0].value,
              duration: inputs[0].value,
              calories_burned: inputs[1].value,
              emotion: selects[1].value
          });
      });

      console.log("Prepare the payload to submit：", payload);

      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
  
      const result = await response.json();
      alert(result.message);
      if (result.success) {
        form.reset();  // Clear form
        exerciseContainer.innerHTML = ''; // Clear the old sports form
        exerciseContainer.appendChild(createExerciseForm()); // Add a new exercisse
      }
    });
  });
  