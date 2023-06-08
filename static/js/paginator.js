// initial configuration
let totalPages = 100;  // set total number of pages
let currentPage = 1;  // set default/initial page

// function to update the pagination buttons
function updatePagination() {
  let paginationDiv = document.querySelector('.pagination');
  paginationDiv.innerHTML = '';  // clear the existing buttons
  
  // add the 'First' button
  let firstButton = document.createElement('button');
  firstButton.href = "#";
  firstButton.innerHTML = "First";
  firstButton.onclick = function (event) {
    event.preventDefault();
    currentPage = 1;
    updatePagination();
    sendPostRequest(currentPage);
  };
  paginationDiv.appendChild(firstButton);

  // add the 'Previous' button
  let prevButton = document.createElement('button');
  prevButton.href = "#";
  prevButton.innerHTML = "&laquo;";
  prevButton.onclick = function (event) {
    event.preventDefault();
    if (currentPage > 1) {
      currentPage--;
      updatePagination();
      sendPostRequest(currentPage);
    }
  };
  paginationDiv.appendChild(prevButton);
  
  // calculate start and end page
  let startPage = Math.max(currentPage - 2, 1);
  let endPage = Math.min(startPage + 4, totalPages);

  // adjust if we're too close to the start
  if (currentPage <= 3) {
    endPage = 5;
  }

  // adjust if we're too close to the end
  if (currentPage >= totalPages - 2) {
    startPage = totalPages - 4;
  }

  // add page number buttons
  for (let i = startPage; i <= endPage; i++) {
    let pageButton = document.createElement('button');
    pageButton.href = "#";
    pageButton.innerHTML = i;
    
    // if this is the current page, add the 'active' class
    if (i == currentPage) {
      pageButton.className = "active";
    }
    
    pageButton.onclick = function (event) {
      event.preventDefault();
      currentPage = i;
      updatePagination();
      sendPostRequest(i);
    };
    
    paginationDiv.appendChild(pageButton);
  }
  
  // add the 'Next' button
  let nextButton = document.createElement('button');
  nextButton.href = "#";
  nextButton.innerHTML = "&raquo;";
  nextButton.onclick = function (event) {
    event.preventDefault();
    if (currentPage < totalPages) {
      currentPage++;
      updatePagination();
      sendPostRequest(currentPage);
    }
  };
  paginationDiv.appendChild(nextButton);

  // add the 'Last' button
  let lastButton = document.createElement('button');
  lastButton.href = "#";
  lastButton.innerHTML = "Last";
  lastButton.onclick = function (event) {
    event.preventDefault();
    currentPage = totalPages;
    updatePagination();
    sendPostRequest(currentPage);
  };
  paginationDiv.appendChild(lastButton);
}

// function to send the POST request
function sendPostRequest(pageNum) {
    var params = new URLSearchParams();
    let asinCleaned = asin.replaceAll('&#x27;', "");
    asinCleaned = asinCleaned.replaceAll('[', "");
    asinCleaned = asinCleaned.replaceAll(']', "");
    params.append('page-num', pageNum);
    params.append('retrieve-asin-data-1', asinCleaned);

    fetch(paginator_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken
        },
        body: params,
      })
      .then(response => response.text()) // .text() instead of .json()
      .then(data => {
        // Here you manipulate the DOM to update the page with the server response
        let reviewCards = document.getElementById('review-cards')
        var tempDOM = new DOMParser().parseFromString(data, 'text/html');
        let newReviewCards = tempDOM.getElementById('review-cards');
        reviewCards.innerHTML = newReviewCards.innerHTML;
      })
    //   .then(data => console.log(data))
      .catch((error) => {
        console.error('Error:', error);
      });
      
    updatePagination();
}

// initial call to update the pagination buttons
updatePagination();