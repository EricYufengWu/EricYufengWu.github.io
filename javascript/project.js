var pageIndex = 1;
showPages(pageIndex);

function changePages(n) {
  showPages(pageIndex = n);
  //console.log(pageIndex);
}

function showPages(n) {
  //console.log("showing page " + n);
  var i;
  var pages = document.getElementsByClassName("projectSections");
  for (i = 0; i < pages.length; i++) {
      pages[i].style.display = "none";
  }
  pages[pageIndex-1].style.display = "block";
}

function goBack() {
  window.history.back();
}