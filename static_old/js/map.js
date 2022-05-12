// We'd fill cols/rows from the database
let rows, cols, container;

function setup(jsonInput) {
  rows = 5;
  cols = 5;
  jsonInput.sort(function(a, b) {
    if(a.Geometry.BoundingBox.Top == b.Geometry.BoundingBox.Top) {
      return a.Geometry.BoundingBox.Left - b.Geometry.BoundingBox.Left;
    } else {
      return a.Geometry.BoundingBox.Top - b.Geometry.BoundingBox.Top;
    }
  });
  container = document.getElementById("container");
  draw();
  makeTable(jsonInput);
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
    row.innerText = Math.floor(count / cols); // TODO make this read the individual row lenghts instead of the total # of columns

    let column = document.createElement("td");
    column.classList.add("dashboard-table-elem");
    column.innerText = count % cols;

    let confidence = document.createElement("td");
    confidence.classList.add("dashboard-table-elem");
    confidence.innerText = element.Confidence.toFixed(3) + "%";


    tr.appendChild(countElement);
    tr.appendChild(row);
    tr.appendChild(column);
    tr.appendChild(confidence);

    table.appendChild(tr);
  });

}

function makeTree(i, j) {
  let newTree = document.createElement("div");
  newTree.classList.add("tree");
  newTree.innerHTML = "(" + j + ", " + i + ")";
  
  return newTree;
}

function draw() {
  container.textContent = "";
  for(let i = 0; i < rows; i++) {
    let newRow = document.createElement("div");
    newRow.classList.add("tree-row");
    for(let j = 0; j < cols; j++) {
      let newCol = document.createElement("div");
      newCol.classList.add("tree-wrapper");

      let newTree = makeTree(i, j);
      
      newCol.appendChild(newTree);
      newRow.appendChild(newCol);
    }
    container.appendChild(newRow);
  }
}


function updateSize() {
  rows = document.getElementById("row-input").valueAsNumber;
  cols = document.getElementById("col-input").valueAsNumber;
  draw();
}

window.onload = function() {
  let testInput = [
    {"Geometry": {
        "BoundingBox": {
          "Left": 0,
          "Top": 0,
          "Width": 10,
          "Height": 8
        }
      }, "Confidence": 87.82499694824219
    }, {
      "Geometry": {
        "BoundingBox": {
          "Left": 10,
          "Top": 15,
          "Width": 5,
          "Height": 9
        }
      }, "Confidence": 86.03299713134766
    }, {
      "Geometry": {
        "BoundingBox": {
          "Left": 20,
          "Top": 3,
          "Width": 4,
          "Height": 16
        }
      }, "Confidence": 82.15799713134766
    }, {
      "Geometry": {
        "BoundingBox": {
          "Left": 2,
          "Top": 20,
          "Width": 10,
          "Height": 10
        }
      }, "Confidence": 82.6259994506836
    }];
 

    
  console.log("Loaded");
  console.log(testInput);
  setup(testInput);
}