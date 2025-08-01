function loadCronSettings(computerName, wolSchedule, solSchedule, macAddress) {
  const header = `<h5 class="text-primary">${computerName} (${macAddress})</h5>`;

  const helpSection = `
    <hr>
    <div>
      <div><strong>Help:</strong></div>
      <div>- <a class="text-decoration-none" href="https://crontab.guru/" target="_blank" rel="noopener noreferrer">Generate cron entry</a></div>
      <div>- <a class="text-decoration-none" href="https://github.com/Misterbabou/gptwol#configure-sleep-on-lan" target="_blank" rel="noopener noreferrer">Configure Sleep on Lan</a></div>
    </div>
    `;

  const wolContent = wolSchedule ? `
    <div class="row align-items-center g-0">
      <div class="col-md-auto w-auto">Wake cron: <span class="badge bg-secondary rounded-pill fs-6">${wolSchedule}</span></div>
      <div class="col-md-auto w-auto">
        <button class="delete-button" type="button" title="Delete Wake Cron" onclick="deleteCron('${macAddress}', 'wol')">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      </div>
    </div>` : `
    <div class="row align-items-center g-0">
      <div class="col-md-auto w-auto">Wake cron:</div>
      <div class="col-md-auto w-auto">
        <form method="POST" action="${add_wol_cron_url}">
          <input type="hidden" name="mac_address" value="${macAddress}">
          <input class="pt-1" type="text" name="cron_request" placeholder="0 12 * * *" required>
          <button class="add-button" type="submit" title="Add Cron">
            <i class="fa-solid fa-plus"></i>
          </button>
        </form>
      </div>
    </div>`;

  const solContent = solSchedule ? `
    <div class="row align-items-center g-0">
      <div class="col-md-auto w-auto">Sleep cron: <span class="badge bg-secondary rounded-pill fs-6">${solSchedule}</span></div>
      <div class="col-md-auto w-auto">
        <button class="delete-button" type="button" title="Delete Sleep Cron" onclick="deleteCron('${macAddress}', 'sol')">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      </div>
    </div>` : `
    <div class="row align-items-center g-0">
      <div class="col-md-auto w-auto">Sleep cron:</div>
      <div class="col-md-auto w-auto">
        <form method="POST" action="${add_sol_cron_url}">
          <input type="hidden" name="mac_address" value="${macAddress}">
          <input class="pt-1" type="text" name="cron_request" placeholder="0 12 * * *" required>
          <button class="add-button" type="submit" title="Add Cron">
            <i class="fa-solid fa-plus"></i>
          </button>
        </form>
      </div>
    </div>`;

  const content = header + wolContent + solContent + helpSection;

  document.getElementById('cronSettingsContent').innerHTML = content;
}

function deleteCron(macAddress, type) {
  const url = type === 'wol' ? delete_wol_cron_url : delete_sol_cron_url;

  // Create a form to submit the delete request
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = url;

  const input = document.createElement('input');
  input.type = 'hidden';
  input.name = 'mac_address';
  input.value = macAddress;

  form.appendChild(input);
  document.body.appendChild(form);
  form.submit();
}
