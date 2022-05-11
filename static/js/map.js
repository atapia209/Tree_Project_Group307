// API Calls to display from database
const request = new XMLHttpRequest();
// const url = 'http://localhost:5000/trees';
const url = "http://127.0.0.1:5000/trees"

function data_get() {
  request.open('GET', url);
  request.send();

  request.onload = () => {
    let requested_data = JSON.parse(request.responseText);
    makeTable(requested_data);
    makeMap(requested_data);
  }
}

function makeTable(jsonInput) {
  let table = document.querySelector(".dashboard-table");
  let count = 1;
  jsonInput.forEach(element => {
    let tr = document.createElement("tr");
    tr.classList.add("dashboard-table-row");

    let countElement = document.createElement("td");
    countElement.classList.add("dashboard-table-elem");
    countElement.innerText = count;
    count++;

    let row = document.createElement("td");
    row.classList.add("dashboard-table-elem");
    row.innerText = element.row;

    let column = document.createElement("td");
    column.classList.add("dashboard-table-elem");
    column.innerText = element.column;

    let confidence = document.createElement("td");
    confidence.classList.add("dashboard-table-elem");
    confidence.innerText = element.confidence.toFixed(3) + "%";


    tr.appendChild(countElement);
    tr.appendChild(row);
    tr.appendChild(column);
    tr.appendChild(confidence);

    table.appendChild(tr);
  });

}

function makeTree(tree) {
  let newTree = document.createElement("div");
  newTree.classList.add("tree");
  let treeText = document.createElement("div");
  treeText.classList.add("tree-text");
  // newTree.innerText = tree.id + ": (" + tree.column + ", " + tree.row + ")\n" + tree.confidence;
  treeText.innerText = `(${tree.row},${tree.column})`
  
  newTree.appendChild(treeText);
  return newTree;
}

function makeMap(jsonInput) {
  let container = document.getElementById("container");
  // deep copies it so we can sort without altering original array at all
  let trees = jsonInput.slice();
  // sort so elements in same row are consecutive, rows are grouped in ascending order, and within the row columns are ascending as well
  trees.sort((a, b) => {
    if(a.row == b.row) {
      return a.column - b.column;
    } else {
      return a.row - b.row;
    }
  });
  // clear the inside of container just in case, ensures we don't stack multiple maps
  container.textContent = "";
  // start currentRow empty and with lastRow set to same as first tree
  let currentRow = document.createElement("div");
  currentRow.classList.add("tree-row");
  let lastRow = trees[0].row;

  trees.forEach(tree => {
    // if it's a new row
    if(tree.row != lastRow) {
      // append the current row
      container.appendChild(currentRow);
      // make a new row
      currentRow = document.createElement("div");
      currentRow.classList.add("tree-row");
      lastRow = tree.row;
    }
    let newCol = document.createElement("div");
    newCol.classList.add("tree-wrapper");

    let newTree = makeTree(tree);
    
    newCol.appendChild(newTree);
    currentRow.appendChild(newCol);
  });
  // once we're done, there's a hanging currentRow, append that to container as well
  container.appendChild(currentRow);
}

// wait till window is loaded to run this function, that way when things need to use elements on the page we can be sure
// they're already loaded
window.onload = function() {
  data_get();
}