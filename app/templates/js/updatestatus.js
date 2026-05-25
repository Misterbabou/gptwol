// ---
// Status Indicator
window.addEventListener('load', function() {
  updateAllStatuses();
});

function updateAllStatuses() {
  const checked = new Set();

  document.querySelectorAll('.status-indicator').forEach(function(indicator) {
    const ip_address = indicator.getAttribute('data-ip-address');
    const test_type = indicator.getAttribute('data-test-type');
    const key = `${ip_address}|${test_type}`;

    if (checked.has(key)) {
      return;
    }

    checked.add(key);
    updateStatus(ip_address, test_type);
  });
}

function getStatusPowerButton(indicator) {
  const computerEntry = indicator.closest('.computer-entry');
  return computerEntry ? computerEntry.querySelector('.status-power') : null;
}

function getMatchingIndicators(ip_address, test_type) {
  return Array.from(document.querySelectorAll('.status-indicator')).filter(indicator => (
    indicator.getAttribute('data-ip-address') === ip_address &&
    indicator.getAttribute('data-test-type') === test_type
  ));
}

function updateStatus(ip_address, test_type) {
  // Make an HTTP GET request to the check_status endpoint
  fetch(`${check_status_url}?ip_address=${encodeURIComponent(ip_address)}&test_type=${encodeURIComponent(test_type)}`)
    .then(response => response.text())
    .then(status => {
      getMatchingIndicators(ip_address, test_type).forEach(element => {
        const computerEntry = element.closest('.computer-entry');
        const buttonElement = getStatusPowerButton(element);

        if (computerEntry) {
          computerEntry.dataset.status = status;
        }

        // Update the class of the element based on the returned status
        if (status === 'awake') {
          element.classList.remove('asleep');
          element.classList.add('awake');
          if (buttonElement) {
            buttonElement.classList.remove('btn-success');
            buttonElement.classList.add('btn-danger');
            buttonElement.title = 'Sleep';
          }
        } else {
          element.classList.remove('awake');
          element.classList.add('asleep');
          if (buttonElement) {
            buttonElement.classList.remove('btn-danger');
            buttonElement.classList.add('btn-success');
            buttonElement.title = 'Wake';
          }
        }
      });
    });
}
