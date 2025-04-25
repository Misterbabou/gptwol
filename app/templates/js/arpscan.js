document.getElementById('arpScanButton').addEventListener('click', function() {
  // Show loading message
  document.getElementById('loadingMessage').style.display = 'block';
  document.getElementById('arpScanResults').style.display = 'none';

  // Fetch ARP scan results
  fetch(`${arp_scan_url}`)
    .then(response => response.json())
    .then(data => {
      const resultsList = document.getElementById('arpScanResults');
      resultsList.innerHTML = ''; // Clear previous results

      // Hide loading message
      document.getElementById('loadingMessage').style.display = 'none';

      // Check if the response contains a message
      if (data.message) {
        resultsList.innerHTML = `<li class="list-group-item">${data.message}</li>`;
        resultsList.style.display = 'block'; // Show the message
      } else {
        resultsList.style.display = 'block'; // Show results list
        data.forEach(device => {
          const listItem = document.createElement('li');
          listItem.className = 'list-group-item list-group-item-action';
          listItem.style.cursor = 'pointer';
          listItem.textContent = `IP: ${device.ip}, MAC: ${device.mac}`;

          // Add click event to highlight the selected item
          listItem.onclick = function() {
            // Remove active class from all items
            const items = resultsList.getElementsByClassName('list-group-item');
            for (let i = 0; i < items.length; i++) {
              items[i].classList.remove('active');
            }

            // Add active class to the selected item
            listItem.classList.add('active');

            // Set the values in the Add Computer modal
            document.getElementById('ip_address').value = device.ip;
            document.getElementById('mac_address').value = device.mac;
            document.getElementById('test_type').value = 'arp';
          };

          resultsList.appendChild(listItem);
        });
      }
    })
    .catch(error => {
        console.error('Error fetching ARP scan results:', error);
        document.getElementById('loadingMessage').textContent = 'Error fetching results. Please try again.';
    });
});
