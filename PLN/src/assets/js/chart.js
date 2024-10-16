// Fetch and populate the first graph
function fetchSearchesPerDay() {
  fetch('/api/searches-per-day')
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById('lineChart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Searches Per Day',
            data: data.data,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            fill: false
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: { beginAtZero: true }
            }],
            xAxes: [{ display: true }]
          },
          legend: { display: false }
        }
      });
    });
}

// Fetch and populate the second graph
function fetchUsersLastTwoMonths() {
  fetch('/api/users-last-two-months')
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById('barChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'New Users',
            data: data.data,
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1,
            fill: false
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: { beginAtZero: true }
            }],
            xAxes: [{ display: true }]
          },
          legend: { display: false }
        }
      });
    });
}

// Call the functions to populate the graphs
fetchSearchesPerDay();
fetchUsersLastTwoMonths();
