// ---
// Status Indicator
window.addEventListener('load', function() {
  // Get all status indicator elements
  const statusIndicators = document.querySelectorAll('.status-indicator');

  // Loop through each status indicator element
  statusIndicators.forEach(function(indicator) {
    // Extract IP address and test type from the data attributes
    const ip_address = indicator.getAttribute('data-ip-address');
    const test_type = indicator.getAttribute('data-test-type');
    // Find the corresponding button element
    const buttonElement = indicator.closest('.card').querySelector('.status-power');
    updateStatus(ip_address, test_type, indicator, buttonElement);
  });
});

function updateStatus(ip_address, test_type, element, buttonElement) {
  // Make an HTTP GET request to the check_status endpoint
  fetch(`${check_status_url}?ip_address=${ip_address}&test_type=${test_type}`)
    .then(response => response.text())
    .then(status => {
      // Update the class of the element based on the returned status
      if (status === 'awake') {
        element.classList.remove('asleep');
        element.classList.add('awake');
        buttonElement.classList.remove('btn-success');
        buttonElement.classList.add('btn-danger');
        buttonElement.title = 'Sleep';
      } else {
        element.classList.remove('awake');
        element.classList.add('asleep');
        buttonElement.classList.remove('btn-danger');
        buttonElement.classList.add('btn-success');
        buttonElement.title = 'Wake';
      }
    });
}
