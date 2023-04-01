const accountsTable = document.querySelector("#accounts-table");
accounts.forEach((account) => {
  const newRow = accountsTable.insertRow();
  const accountNameCell = newRow.insertCell(0);
  accountNameCell.innerHTML = account;
});