function filterComputers() {
  const query = document.querySelector('.search-input').value.toLowerCase();
  const cards = document.querySelectorAll('.computer-card');

  cards.forEach(card => {
    const title = card.querySelector('.card-title').textContent.toLowerCase();
    const ip = card.querySelector('.text-end:nth-of-type(1)').textContent.toLowerCase(); // IP address
    const mac = card.querySelector('.text-end:nth-of-type(2)').textContent.toLowerCase(); // MAC address

    if (title.includes(query) || ip.includes(query) || mac.includes(query)) {
      card.style.display = ''; // Show card
    } else {
      card.style.display = 'none'; // Hide card
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

function sortComputers(criteria) {
  const cardsContainer = document.querySelector('.row.justify-content-center');
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
        aValue = a.querySelector('.card-title').textContent.toLowerCase();
        bValue = b.querySelector('.card-title').textContent.toLowerCase();
        dropdownItems[0].classList.add('active'); // Sort by Name
        break;
      case 'ip':
        aValue = a.querySelector('.text-end:nth-of-type(1)').textContent.toLowerCase(); // IP address
        bValue = b.querySelector('.text-end:nth-of-type(1)').textContent.toLowerCase(); // IP address
        dropdownItems[1].classList.add('active'); // Sort by IP
        break;
      case 'mac':
        aValue = a.querySelector('.text-end:nth-of-type(2)').textContent.toLowerCase(); // MAC address
        bValue = b.querySelector('.text-end:nth-of-type(2)').textContent.toLowerCase(); // MAC address
        dropdownItems[2].classList.add('active'); // Sort by MAC
        break;
    }

    return aValue.localeCompare(bValue); // Compare values for sorting
  });

  // Clear the current cards and append sorted cards
  cardsContainer.innerHTML = '';
  cards.forEach(card => cardsContainer.appendChild(card));
}

// Attach the filter function to the input event
document.querySelector('.search-input').addEventListener('input', filterComputers);
