
function displayAccount(event, tableid) {
    event.preventDefault();

    // update table whenever new account is added
    var form = event.target;
    var data = new FormData(form);
    fetch('/submit', {
        method: 'POST',
        body: data
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        var table = document.querySelector(`#${tableid}`);
        var row = table.insertRow(-1);
        var cell = row.insertCell(0);
        cell.textContent = data.name;
        form.reset();
        let accountName = document.querySelector("#accountName");
        accountName.value = "";
    })
    .catch(error => {
        console.log("error:", error);
    });
    
    return false;
}

function clearDatabase() {
    event.preventDefault();
    fetch('/clear', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    })
    .catch(error => {
        console.log("clear database error:", error);
    })
}

function createChart(){
    fetch('/data')
    .then(response => response.json())
    .then(data => {
        data.sort((a, b) => (a[0] > b[0]) ? 1 : -1);
        console.log("sorted data:", data)
        // Extract the dates and balances from the data
        const dates = data.map(entry => entry[0]);
        const pretaxBalances = data.map(entry => entry[1]);
        const posttaxBalances = data.map(entry => entry[2])
        // Create a new Chart.js chart using the retrieved data
        const ctx = document.getElementById('balance-chart').getContext('2d');
        const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Pretax Account Balance',
                    data: pretaxBalances,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Aftertax Account Balance',
                    data: posttaxBalances,
                    fill: false,
                    borderColor: 'rgb(192, 75, 192)',
                    tension: 0.1
                }
            ]
        }, options: {
            scales: {
                yAxes: [{
                    type: 'linear',
                    position: 'left'
                }]
            }
        }
        });
    });
}