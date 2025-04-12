document.addEventListener('DOMContentLoaded', (event) => {
  const htmlElement = document.documentElement;
  const switchElement = document.getElementById('darkModeSwitch');
  const iconElementBtn = document.getElementById('darkModeBtn');
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const currentTheme = localStorage.getItem('bsTheme') || (prefersDarkScheme ? 'dark' : 'light');

  htmlElement.setAttribute('data-bs-theme', currentTheme);
  switchElement.checked = currentTheme === 'dark';

  switchElement.addEventListener('click', function () {
    switchElement.checked = !switchElement.checked; // Toggle the checkbox
    switchElement.dispatchEvent(new Event('change')); // Trigger the change event
  });

  switchElement.addEventListener('change', function () {
    const newTheme = this.checked ? 'dark' : 'light';
    htmlElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('bsTheme', newTheme);
  });

  // Add click event to the Button
  iconElementBtn.addEventListener('click', function () {
    switchElement.checked = !switchElement.checked; // Toggle the checkbox
    switchElement.dispatchEvent(new Event('change')); // Trigger the change event
  });
});
