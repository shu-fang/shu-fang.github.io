
// function displayAccount(event) {
//     event.preventDefault();

//     // update table whenever new account is added    
//     var form = event.target;
//     var data = new FormData(form);
//     fetch('/submit', {
//         method: 'POST',
//         body: data
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         var posttaxRadio = document.querySelector('input[name="tax_status"][value="post-tax"]');
//         var pretaxRadio = document.querySelector('input[name="tax_status"][value="pre-tax"]');
//         if (posttaxRadio && posttaxRadio.checked) {
//             tableid = "posttax-accounts"
//         } else {
//             tableid = "pretax-accounts"
//         }
//         var table = document.querySelector(`#${tableid}`);
//         var lastRow = table.rows[table.rows.length - 1];
//         var cell = lastRow.insertCell(-1);
//         cell.textContent = data.name;
//         form.reset();
//         let accountName = document.querySelector("#accountName");
//         accountName.value = "";
//     })
//     .catch(error => {
//         console.log("error:", error);
//     });
    
//     return false;
// }

function addAccount() {
    event.preventDefault();
    var form = event.target;
    var data = new FormData(form);
    fetch('/add_account', {
        method: 'POST',
        body: data
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    })
    .catch(error => {
        console.log("add database error:", error);
    })
}

function deleteAccount() {
    event.preventDefault();
    var form = event.target;
    var data = new FormData(form);
    fetch('/delete_account', {
        method: 'DELETE',
        body: data
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    })
    .catch(error => {
        console.log("delete database error:", error);
    })
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