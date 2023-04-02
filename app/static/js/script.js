
function displayAccount(event) {
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
        var table = document.querySelector('#pretax-accounts');
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