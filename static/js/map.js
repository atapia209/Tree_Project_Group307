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

  // first make sure there's only one element in the table, the header row
  while(table.childElementCount > 1) {
    table.removeChild(table.lastChild);
  }


  let count = 1;
  let longestColumn = 0;
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

function fillRow(row, longestRow) {
  let rowLength = row.childElementCount;
  console.log(rowLength, longestRow);
  while(rowLength < longestRow) {
    let tree = makeTree({"column":0,"row":0});
    tree.classList.add("hide");
    row.appendChild(tree);
    rowLength++;
  }
}

function makeTree(tree) {
  let wrapper = document.createElement("div");
  wrapper.classList.add("tree-wrapper");

  let newTree = document.createElement("div");
  newTree.classList.add("tree");
  let treeText = document.createElement("div");
  treeText.classList.add("tree-text");
  // newTree.innerText = tree.id + ": (" + tree.column + ", " + tree.row + ")\n" + tree.confidence;
  treeText.innerText = `(${tree.column}, ${tree.row})`
  
  newTree.appendChild(treeText);
  wrapper.appendChild(newTree);
  return wrapper;
}

function makeMap(jsonInput) {
  let container = document.getElementById("container");

  // deep copies it so we can sort without altering original array at all
  let trees = jsonInput.slice();

  // Find longest row, useful for sorting and for making the display
  let longestRow = 0;
  trees.forEach(tree => {
    if(tree.column > longestRow)
      longestRow = tree.column
    }
  );
  console.log(longestRow);
  // sort so elements in same row are consecutive, rows are grouped in ascending order, and within the row columns are ascending as well
  trees.sort((a, b) => {
    return (a.row * longestRow + a.column) - (b.row * longestRow + b.column);
  });
  console.log(trees);
  // clear the inside of container just in case, ensures we don't stack multiple maps
  container.textContent = "";
  // start currentRow empty and with lastRow set to same as first tree
  let currentRow = document.createElement("div");
  currentRow.classList.add("tree-row");
  let lastRowNumber = trees[0].row;

  trees.forEach(tree => {
    // if it's a new row
    if(tree.row != lastRowNumber) {
      fillRow(currentRow, longestRow);
      // append the current row
      container.appendChild(currentRow);
      // make a new row
      currentRow = document.createElement("div");
      currentRow.classList.add("tree-row");
      lastRowNumber = tree.row;
    }
    
    let newTree = makeTree(tree);

    currentRow.appendChild(newTree);
  });
  // once we're done, there's a hanging currentRow, append that to container as well
  fillRow(currentRow, longestRow);
  container.appendChild(currentRow);
}

// wait till window is loaded to run this function, that way when things need to use elements on the page we can be sure
// they're already loaded
window.onload = function() {
  data_get();
}