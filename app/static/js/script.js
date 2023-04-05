
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
        console.log("add database error:", error.message);
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
        console.log("sorted data:", data)
        // Extract the dates and balances from the data
        const dates = data.map(entry => entry[0]);
        const posttaxBalance = data.map(entry => entry[1]);
        // Create a new Chart.js chart using the retrieved data
        const ctx = document.getElementById('balance-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Posttaax Account Balance',
                        data: posttaxBalance,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }
                ]
            }, options: {
                scales: {
                    yAxes: [{
                        type: 'linear',
                        position: 'left',
                        ticks: {
                            fontColor: 'white' // set the font color of the y-axis ticks to white
                        },
                        gridLines: {
                            color: 'rgba(255,255,255,0.1)' // set the color of the y-axis grid lines to white with 10% opacity
                        }
                    }],
                    xAxes: [{
                        ticks: {
                            fontColor: 'white' // set the font color of the x-axis ticks to white
                        },
                        gridLines: {
                            color: 'rgba(255,255,255,0.1)' // set the color of the x-axis grid lines to white with 10% opacity
                        }
                    }]
                }
            },
            elements: {
                point: {
                    backgroundColor: 'white', // set the color of the data points to white
                    borderColor: 'white' // set the color of the data point borders to white
                },
                line: {
                    borderColor: 'white' // set the color of the lines to white
                }
            }
        });
    });
}