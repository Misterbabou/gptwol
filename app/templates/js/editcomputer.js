// Function to populate the edit modal with the selected computer's data
document.addEventListener('DOMContentLoaded', function () {
  var editComputerModal = document.getElementById('editComputer');
  editComputerModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget; // Button that triggered the modal

    // Extract data attributes from the button
    var name = button.getAttribute('data-name');
    var macAddress = button.getAttribute('data-mac-address');
    var ipAddress = button.getAttribute('data-ip-address');
    var testType = button.getAttribute('data-test-type');

    // Update the modal's content
    var modalNameInput = editComputerModal.querySelector('#edit_name');
    var modalMacAddressInput = editComputerModal.querySelector('#edit_mac_address');
    var modalIpAddressInput = editComputerModal.querySelector('#edit_ip_address');
    var modalTestTypeInput = editComputerModal.querySelector('#edit_test_type');

    modalNameInput.value = name;
    modalMacAddressInput.value = macAddress;
    modalIpAddressInput.value = ipAddress;
    modalTestTypeInput.value = testType;
  });
});
