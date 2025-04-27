<<<<<<< HEAD
// Here is the first comment of the file
=======
document.addEventListener('DOMContentLoaded', () => {
    fetch("/api/visualisation/fitness")
      .then(res => res.json())
      .then(data => {
        console.log("Data interface：", data);
  
        const container = document.getElementById('vis-container');
        container.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
      })
      .catch(error => console.error("Error：", error));
  });
  
>>>>>>> f2da4b8b2c2df4e40d82bcb78b2b6c407ba5a92e
