
function displayAccount(event) {
    event.preventDefault();
    var frm = $('#accountForm')
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (data) {
            console.log('Submission was successful.');
            console.log(data);
        },
        error: function (data) {
            console.log('An error occurred.');
            console.log(data);
        },
    });
    // save to storage
    let accountName = document.querySelector("#accountName").value;

    // add to accounts page
    let pretax_accounts = document.querySelector("#pretax-accounts");
    let newRow = pretax_accounts.insertRow();
    let newCell = newRow.insertCell();
    newCell.textContent = accountName;

    // send AJAX request to Flask server
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/submit");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onload = function() {
        if (xhr.status === 201) {
            // add new account to accounts page
            let account = JSON.parse(xhr.responseText).account;
            let pretaxAccounts = document.querySelector("#pretax-accounts");
            let newRow = pretaxAccounts.insertRow();
            let newCell = newRow.insertCell();
            newCell.textContent = account.name;

            accountName.value = "";
        }
    };
    xhr.send(JSON.stringify({accountName: accountName.value}));

    accountName = "";
    return false;
}

const form = document.querySelector('form');
form.addEventListener('subnmit', displayAccount);