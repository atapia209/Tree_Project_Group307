function switchRightDisplay() {
  let rightSide = document.querySelector(".right");
  let children = rightSide.children;
  
  for(let i = 0; i < rightSide.childElementCount; i++) {
    if(children[i].classList.contains("no-display")) {
      children[i].classList.remove("no-display");
    } else {
      children[i].classList.add("no-display");
    }
  }
}


window.onload = function() {
  // console.log(document.querySelectorAll("div"));
  document.getElementById("create-new-project").addEventListener('click', switchRightDisplay, false);
}