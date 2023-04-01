
function displayAccount() {
    // add to accounts page
    let accountName = document.querySelector("#accountName");
    let pretax_accounts = document.querySelector("#pretax-accounts");
    let newRow = pretax_accounts.insertRow();
    let newCell = newRow.insertCell();
    newCell.textContent = accountName.value();
    
    accountName.value = "";

    // save to storage
    let accounts = JSON.parse(localStorage.getItem("accounts")) || [];
    accounts.push(newCell.textContent);
    localStorage.setItem("accounts", JSON.stringify(accounts));

    // add to inputs page
    const accountsTable = document.querySelector("#accounts-table");
    accounts.forEach((account) => {
        const newRow = accountsTable.insertRow();
        const accountNameCell = newRow.insertCell(0);
        accountNameCell.innerHTML = account;
    });
}