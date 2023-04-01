
function displayAccount() {
    // save to storage
    let accounts = JSON.parse(localStorage.getItem("accounts")) || [];
    let accountName = document.querySelector("#accountName");
    accounts.push(accountName.value);
    localStorage.setItem("accounts", JSON.stringify(accounts));
    
    // add to accounts page
    let pretax_accounts = document.querySelector("#pretax-accounts");
    let newRow = pretax_accounts.insertRow();
    let newCell = newRow.insertCell();
    newCell.textContent = accountName.value();
    
    accountName.value = "";

    // add to inputs page
    const accountsTable = document.querySelector("#accounts-table");
    accounts.forEach((account) => {
        const newRow = accountsTable.insertRow();
        const accountNameCell = newRow.insertCell(0);
        accountNameCell.innerHTML = account;
    });
}