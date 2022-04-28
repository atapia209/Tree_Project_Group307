// We'd fill cols/rows from the database
let rows, cols, container;

function setup(_rows = 5, _cols = 5) {
  rows = _rows;
  cols = _cols;
  container = document.getElementById("container");
  draw();
}

function draw() {
  container.textContent = "";
  for(let i = 0; i < rows; i++) {
    let newRow = document.createElement("div");
    newRow.classList.add("tree-row");
    for(let j = 0; j < cols; j++) {
      let newCol = document.createElement("div");
      newCol.classList.add("tree-wrapper");

      // fill the "tree" div with whatever information we want instead of just its position
      // probably write a constructor to do that instead of having it inline
      let newTree = document.createElement("div");
      newTree.classList.add("tree");
      newTree.innerHTML = "(" + j + ", " + i + ")";
      
      newCol.appendChild(newTree);
      newRow.appendChild(newCol);
    }
    container.appendChild(newRow);
  }
}
/*
document.getElementById("update").onclick = 
*/
function updateSize() {
  rows = document.getElementById("row-input").valueAsNumber;
  cols = document.getElementById("col-input").valueAsNumber;
  draw();
}

window.onload = function() {
  console.log("Loaded");
  setup();
}