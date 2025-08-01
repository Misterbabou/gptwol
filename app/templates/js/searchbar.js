function filterComputers() {
  const query = document.querySelector('.search-input').value.toLowerCase();
  const cards = document.querySelectorAll('.computer-card');

  cards.forEach(card => {
    const title = card.querySelector('.title-sortable .sortable').textContent.toLowerCase();
    const ip = card.querySelector('.info-sortable .sortable:nth-of-type(1)').textContent.toLowerCase(); // IP address
    const mac = card.querySelector('.info-sortable .sortable:nth-of-type(2)').textContent.toLowerCase(); // MAC address

    if (title.includes(query) || ip.includes(query) || mac.includes(query)) {
      card.classList.remove('hidden'); // Show card
    } else {
      card.classList.add('hidden'); // Hide card
    }
  });
}

// Attach the filter function to the input event
document.querySelector('.search-input').addEventListener('input', filterComputers);

function clearSearchInput() {
  const searchInput = document.querySelector('.search-input');
  searchInput.value = '';
  filterComputers(); // Reset the filter
}

function ipToNumber(ip) {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + Number(octet), 0);
}

function sortComputers(criteria) {
  const cardsContainer = document.querySelector('.row.row-sortable');
  const cards = Array.from(cardsContainer.children); // Convert NodeList to Array

  // Update the active class in the dropdown
  const dropdownItems = document.querySelectorAll('.dropdown-item');
  dropdownItems.forEach(item => {
    item.classList.remove('active'); // Remove active class from all items
  });

  // Sort the cards based on the selected criteria
  cards.sort((a, b) => {
    let aValue, bValue;

    switch (criteria) {
      case 'name':
        aValue = a.querySelector('.title-sortable .sortable').textContent.toLowerCase();
        bValue = b.querySelector('.title-sortable .sortable').textContent.toLowerCase();
        dropdownItems[0].classList.add('active'); // Sort by Name
        return aValue.localeCompare(bValue); // Compare values for sorting

      case 'ip':
        const aIp = a.querySelector('.info-sortable .sortable:nth-of-type(1)').textContent;
        const bIp = b.querySelector('.info-sortable .sortable:nth-of-type(1)').textContent;
        dropdownItems[1].classList.add('active'); // Sort by IP

        return ipToNumber(aIp) - ipToNumber(bIp); // Compare numeric values

      case 'mac':
        aValue = a.querySelector('.info-sortable .sortable:nth-of-type(2)').textContent.toLowerCase(); // MAC address
        bValue = b.querySelector('.info-sortable .sortable:nth-of-type(2)').textContent.toLowerCase(); // MAC address
        dropdownItems[2].classList.add('active'); // Sort by MAC
        return aValue.localeCompare(bValue); // Compare values for sorting
    }
  });

  // Clear the current cards and append sorted cards
  cardsContainer.innerHTML = '';
  cards.forEach(card => cardsContainer.appendChild(card));
}

// Attach the filter function to the input event
document.querySelector('.search-input').addEventListener('input', filterComputers);
