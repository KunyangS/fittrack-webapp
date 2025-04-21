// static/js/upload.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
  
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
      };
  
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
      }
    });
  });
  