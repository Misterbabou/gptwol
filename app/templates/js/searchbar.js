const sortDirections = {};

document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input');
  if (searchInput) {
    searchInput.addEventListener('input', filterComputers);
  }

  document.querySelectorAll('.view-toggle').forEach(button => {
    button.addEventListener('click', () => setViewMode(button.dataset.view));
  });

  document.querySelectorAll('.sortable-column').forEach(column => {
    column.addEventListener('click', () => sortComputers(column.dataset.sort));
  });
});

function filterComputers() {
  const query = document.querySelector('.search-input').value.toLowerCase();
  const computers = document.querySelectorAll('.computer-entry');

  computers.forEach(computer => {
    const title = computer.dataset.name.toLowerCase();
    const ip = computer.dataset.ip.toLowerCase();
    const mac = computer.dataset.mac.toLowerCase();

    if (title.includes(query) || ip.includes(query) || mac.includes(query)) {
      computer.classList.remove('hidden');
    } else {
      computer.classList.add('hidden');
    }
  });
}

function clearSearchInput() {
  const searchInput = document.querySelector('.search-input');
  searchInput.value = '';
  filterComputers(); // Reset the filter
}

function setViewMode(viewMode) {
  const cardsView = document.getElementById('cardsView');
  const listView = document.getElementById('listView');

  if (viewMode === 'list') {
    if (cardsView) {
      cardsView.classList.add('hidden');
    }
    if (listView) {
      listView.classList.remove('hidden');
    }
  } else {
    if (listView) {
      listView.classList.add('hidden');
    }
    if (cardsView) {
      cardsView.classList.remove('hidden');
    }
  }

  document.querySelectorAll('.view-toggle').forEach(button => {
    button.classList.toggle('active', button.dataset.view === viewMode);
  });
}

function ipToNumber(ip) {
  if (!/^(\d{1,3}\.){3}\d{1,3}$/.test(ip)) {
    return null;
  }

  const octets = ip.split('.').map(Number);
  if (octets.some(octet => octet < 0 || octet > 255)) {
    return null;
  }

  return octets.reduce((acc, octet) => (acc * 256) + octet, 0);
}

function getSortValue(computer, criteria) {
  switch (criteria) {
    case 'name':
      return computer.dataset.name.toLowerCase();
    case 'ip':
      return computer.dataset.ip;
    case 'mac':
      return computer.dataset.mac.toLowerCase();
    case 'check':
      return computer.dataset.check.toLowerCase();
    case 'status':
      return computer.dataset.status || 'unknown';
    default:
      return '';
  }
}

function compareComputers(a, b, criteria, direction) {
  const directionFactor = direction === 'desc' ? -1 : 1;

  if (criteria === 'ip') {
    const aIpNumber = ipToNumber(a.dataset.ip);
    const bIpNumber = ipToNumber(b.dataset.ip);

    if (aIpNumber !== null && bIpNumber !== null) {
      return (aIpNumber - bIpNumber) * directionFactor;
    }
  }

  return String(getSortValue(a, criteria)).localeCompare(
    String(getSortValue(b, criteria)),
    undefined,
    { numeric: true }
  ) * directionFactor;
}

function sortComputers(criteria) {
  sortDirections[criteria] = sortDirections[criteria] === 'asc' ? 'desc' : 'asc';
  const direction = sortDirections[criteria];

  // Update the active class in the dropdown
  const dropdownItems = document.querySelectorAll('.dropdown-item');
  dropdownItems.forEach(item => {
    item.classList.remove('active'); // Remove active class from all items
  });

  const activeDropdownItem = Array.from(dropdownItems).find(item => item.getAttribute('onclick') === `sortComputers('${criteria}')`);
  if (activeDropdownItem) {
    activeDropdownItem.classList.add('active');
  }

  document.querySelectorAll('.sortable-column').forEach(column => {
    column.classList.remove('sorted-asc', 'sorted-desc');
    if (column.dataset.sort === criteria) {
      column.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
    }
  });

  document.querySelectorAll('.computer-sortable').forEach(computersContainer => {
    const computers = Array.from(computersContainer.children);
    computers.sort((a, b) => compareComputers(a, b, criteria, direction));

    computersContainer.innerHTML = '';
    computers.forEach(computer => computersContainer.appendChild(computer));
  });
}
