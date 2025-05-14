// upload.js

document.addEventListener('DOMContentLoaded', () => {
  const exerciseContainer = document.getElementById('exerciseContainer');
  const addExerciseBtn = document.getElementById('addExerciseBtn');

  const foodContainer = document.getElementById('foodContainer');
  const addFoodBtn = document.getElementById('addFoodBtn');

  const todoList = document.getElementById('todoListNotebook');
  const addPlanBtn = document.getElementById('addPlanBtn');
  const saveTodoBtn = document.getElementById('saveTodoBtn');
  const uploadForm = document.getElementById('uploadForm');

  // Remove initial static list item for consistency
  todoList.innerHTML = '';

  // Load cached todos
  const savedTodos = JSON.parse(localStorage.getItem('todos') || '[]');
  savedTodos.forEach(text => addTodoItem(text));

  // Clone and append new exercise block
  addExerciseBtn.addEventListener('click', () => {
    const blocks = exerciseContainer.getElementsByClassName('exercise-block');
    const lastBlock = blocks[blocks.length - 1];
    const clone = lastBlock.cloneNode(true);

    [...clone.querySelectorAll('input, select')].forEach(input => {
      input.value = '';
    });

    exerciseContainer.appendChild(clone);
  });

  // Clone and append new food block
  addFoodBtn.addEventListener('click', () => {
    const lastBlock = foodContainer.lastElementChild;
    const clone = lastBlock.cloneNode(true);

    [...clone.querySelectorAll('input, select')].forEach(input => {
      input.value = '';
    });

    foodContainer.appendChild(clone);
  });

  // Add To-Do item (blank)
  addPlanBtn.addEventListener('click', () => {
    addTodoItem('');
  });

  // Save To-Do items to localStorage
  saveTodoBtn.addEventListener('click', () => {
    const inputs = todoList.querySelectorAll('input[type="text"]');
    const values = [...inputs].map(input => input.value.trim()).filter(text => text !== '');
    localStorage.setItem('todos', JSON.stringify(values));
    alert('✅ To-Do list saved locally!');
  });

  // Submit confirmation
  uploadForm.addEventListener('submit', (e) => {
    e.preventDefault();  
    alert('✅ Submit successfully!');
    setTimeout(() => {
      uploadForm.submit();  
    }, 200); 
  });
  

  function addTodoItem(text = '') {
    const li = document.createElement('li');
    const checkbox = document.createElement('input');
    const input = document.createElement('input');

    checkbox.type = 'checkbox';
    checkbox.className = 'mr-2';
    checkbox.addEventListener('change', () => {
      if (checkbox.checked) {
        li.remove();
        updateCache();
      }
    });

    input.type = 'text';
    input.placeholder = "Write your plan";
    input.value = text;
    input.className = 'bg-transparent border-b-2 border-dashed focus:outline-none w-full';
    input.addEventListener('input', updateCache);

    li.appendChild(checkbox);
    li.appendChild(input);
    li.className = 'flex items-center gap-2';
    todoList.appendChild(li);
  }

  function updateCache() {
    const inputs = todoList.querySelectorAll('input[type="text"]');
    const values = [...inputs].map(input => input.value.trim()).filter(text => text !== '');
    localStorage.setItem('todos', JSON.stringify(values));
  }
});