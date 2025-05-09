document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('uploadForm');
  const exerciseContainer = document.getElementById('exerciseContainer');
  const addExerciseBtn = document.getElementById('addExerciseBtn');

  // Generate a sport block
  function createExerciseForm() {
    const div = document.createElement('div');
    div.className = "exercise-block grid grid-cols-1 md:grid-cols-2 gap-4 mb-4";

    div.innerHTML = `
      <select name="activity_type" class="input" required>
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

      <input type="number" name="duration" placeholder="Duration (minutes)" class="input" required>
      <input type="number" name="calories_burned" placeholder="Calories Burned" class="input" required>

      <select name="emotion" class="input">
        <option value="">Emotion during exercise</option>
        <option value="happy">Happy</option>
        <option value="tired">Tired</option>
        <option value="stressed">Stressed</option>
        <option value="relaxed">Relaxed</option>
      </select>
    `;
    return div;
  }

  // Add the first sport
  if (exerciseContainer.children.length === 0) {
    exerciseContainer.appendChild(createExerciseForm());
  }

  //Click to add a sport
  addExerciseBtn.addEventListener('click', () => {
    exerciseContainer.appendChild(createExerciseForm());
  });

  // form submission
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);

    const activities = [];
    const blocks = exerciseContainer.querySelectorAll('.exercise-block');
    blocks.forEach(block => {
      activities.push({
        activity_type: block.querySelector('[name="activity_type"]').value,
        duration: block.querySelector('[name="duration"]').value,
        calories_burned: block.querySelector('[name="calories_burned"]').value,
        emotion: block.querySelector('[name="emotion"]').value
      });
    });

    const payload = {
      date: formData.get('date'),
      time: formData.get('time'),
      gender: formData.get('gender'),
      age: formData.get('age'),
      height: formData.get('height'),
      weight: formData.get('weight'),
      food_name: formData.get('food_name'),
      food_quantity: formData.get('food_quantity'),
      food_calories: formData.get('food_calories'),
      meal_type: formData.get('meal_type'),
      activities: activities
    };

    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    alert(result.message);
    if (result.success) {
      form.reset();
      exerciseContainer.innerHTML = '';
      exerciseContainer.appendChild(createExerciseForm());
    }
  });
});
