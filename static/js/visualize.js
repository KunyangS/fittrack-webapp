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