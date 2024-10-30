// Fetching and displaying recommendations
document.getElementById('symptom-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const symptomsInput = document.getElementById('symptoms').value;

    fetch('http://127.0.0.1:5000/get_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symptoms: symptomsInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data['LLM Response']) {
            document.getElementById('result').innerHTML = `<h3>Recommendation</h3><p>${data['LLM Response']}</p>`;
        } else {
            document.getElementById('result').innerHTML = `
                <h3>Disease: ${data.Disease}</h3>
                <p><strong>Description:</strong> ${data.Description}</p>
                <p><strong>Diet:</strong> ${data.Diet}</p>
                <p><strong>Medication:</strong> ${data.Medication}</p>
                <p><strong>Precautions:</strong> ${data.Precautions.join(', ')}</p>
                <p><strong>Workout:</strong> ${data.Workout}</p>`;
        }
    })
    .catch(error => console.error('Error:', error));
});

// About Us button event handler
document.getElementById('about-us').addEventListener('click', function() {
    alert("Developed by:\nNebin K Raj\nJoes Anto\nAnikha D Nair\nSanjana SS");
});
