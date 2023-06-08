/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function dropdownSearch(dropdownTag) {
    document.getElementById(dropdownTag).classList.toggle("show"); // "myDropdown"
  }
  
function filterFunction(inputTag, dropdownTag, dropdownItemTag) {
  var input, filter, ul, li, a, i;
  input = document.getElementById(inputTag); // ""
  filter = input.value.toUpperCase();
  div = document.getElementById(dropdownTag); //"myDropdown"
  a = div.getElementsByClassName(dropdownItemTag); //""
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
} 

function changeValue(inputTag, dropdownTag, btnTag, val){
  document.getElementById(inputTag).value=val;
  document.getElementById(inputTag).placeholder=val;
  document.getElementById(dropdownTag).classList.toggle("show");
  document.getElementById(btnTag).innerHTML=val;
}