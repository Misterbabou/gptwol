from flask import Flask, request, render_template, redirect, url_for
import socket
import struct
import subprocess
import os
import ipaddress
import re

port = os.environ.get('PORT', 5000)
ping_timeout = os.environ.get('PING_TIMEOUT', 300)
tcp_timeout = os.environ.get('TCP_TIMEOUT', 1)
cron_filename = '/etc/cron.d/gptwol'
computer_filename = 'db/computers.txt'
computer_old_filename = 'computers.txt'

app = Flask(__name__, static_folder='templates')

def generate_modal_html(messages, title):
  message_content = '<br>'.join(messages)
  return f'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="Wake On LAN tool to manage and wake computers on your network.">
      <title>GPTWOL</title>
      <link rel="shortcut icon" href="/">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
      <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js" integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r" crossorigin="anonymous"></script>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>
      <script src="https://code.jquery.com/jquery-3.6.0.js"></script>
    </head>
    <body>
      <!-- Modal -->
      <div class="modal fade" id="messageModal" tabindex="-1" aria-labelledby="messageModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="messageModalLabel">{title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              {message_content}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" id="closeModalButton">Close</button>
            </div>
          </div>
        </div>
      </div>

      <script>
        // Show the modal when the page loads
        var myModal = new bootstrap.Modal(document.getElementById('messageModal'));
        myModal.show();

        // Redirect to root index when the close button is clicked
        document.getElementById('closeModalButton').addEventListener('click', function() {{
          window.history.back();
        }});

        // Redirect to root index when the modal is closed (backdrop click or escape key)
        document.getElementById('messageModal').addEventListener('hidden.bs.modal', function () {{
          window.history.back();
        }});
      </script>
    </body>
    </html>
  '''

def load_computers():
  # Load the list of computers from the configuration file
  computers = []
  # Check for warning
  if os.path.exists(computer_old_filename):
    os.environ['OLD_COMPUTER_FILE_WARNING'] = 'true'
  directory = "db"
  if not os.path.exists(directory):
    os.makedirs(directory)
  if not os.path.exists(computer_filename):
    open(computer_filename, 'w').close()  # create the file if it doesn't exist
  with open(computer_filename) as f:
    for line in f:
      fields = line.strip().split(',')
      name = fields[0]
      mac_address = fields[1]
      ip_address = fields[2]
      test_type = fields[3] if len(fields) >= 4 else 'icmp'  # Default to 'icmp' if test_type is not specified
      if not test_type.strip():  # Check if test_type is empty or whitespace
        test_type = 'icmp'
        line = f"{name},{mac_address},{ip_address},{test_type}\n"  # Update the line with 'icmp'
        with open(computer_filename, 'a') as f:
          f.write(line)  # Write the updated line to the file
      computers.append({'name': name, 'mac_address': mac_address, 'ip_address': ip_address, 'test_type': test_type})

  # Load the cron schedule information for each computer
  if not os.path.exists(cron_filename):
    open(cron_filename, 'w').close()  # create the file if it doesn't exist
  with open(cron_filename) as f:
    for line in f:
      if not line.startswith('#'):
        fields = line.strip().split()
        schedule = ' '.join(fields[:5])
        user = fields[5]
        command = ' '.join(fields[6:])
        mac_address = command.split()[-1]
        computer = next((c for c in computers if c['mac_address'] == mac_address), None)
        if computer:
          computer['cron_schedule'] = schedule

  return computers

computers = load_computers()

def send_wol_packet(mac_address):
  # Convert the MAC address to a packed binary string
  packed_mac = struct.pack('!6B', *[int(x, 16) for x in mac_address.split(':')])

  # Create a socket and send the WOL packet
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  s.sendto(b'\xff' * 6 + packed_mac * 16, ('<broadcast>', 9))

def is_computer_awake(ip_address, port, timeout=ping_timeout):
  if not port or port.lower() == 'icmp':
    return is_computer_awake_icmp(ip_address)
  else:
    port_int = int(port)
    return is_computer_awake_tcp(ip_address, port_int)

def is_computer_awake_icmp(ip_address, timeout=ping_timeout):
  # Use the fping command with a timeout to check if the computer is awake
  result = subprocess.run(['fping', '-t', str(timeout), '-c', '1', ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  return result.returncode == 0

def is_computer_awake_tcp(ip_address, port, timeout=tcp_timeout):
  # Use nc (netcat) to check if the TCP port is open
  result = subprocess.run(['nc', '-z', '-w', str(timeout), ip_address, str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  return result.returncode == 0

def search_computers(computers, query):
  query = query.lower()
  return [computer for computer in computers if query in computer['name'].lower() or query in computer['mac_address'].lower() or query in computer['ip_address'].lower()]

def initial_computer_status(ip_address, test_type):
  return "asleep"

def check_name_exist(name, computers):
  for computer in computers:
    if computer['name'] == name:
      return True
  return False

def check_mac_exist(mac_address, computers):
  for computer in computers:
    if computer['mac_address'] == mac_address:
      return True
  return False

def check_invalid_ip(ip):
  try:
    ipaddress.ip_address(ip)
    return False # Valid IP
  except ValueError:
    return True # Invalid IP

def check_invalid_mac(mac):
  # Regular expression for validating a MAC address
  mac_pattern = r'^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$'
  # Check if the MAC address matches the pattern
  if re.match(mac_pattern, mac):
    return False  # Valid MAC address
  else:
    return True   # Invalid Mac address

def check_invalid_test_type(test_type):
  # Check if test_type is "icmp" or a valid port number
  if test_type == "icmp":
    return False  # "icmp" is valid
  return not (test_type.isdigit() and 0 <= int(test_type) <= 65535)

def check_invalid_cron(cron):
  # Regular expressions for each field
  patterns = [
    r'^(\*|[1-5]?[0-9](-[1-5]?[0-9])?)(\/[1-9][0-9]*)?(,(\*|[1-5]?[0-9](-[1-5]?[0-9])?)(\/[1-9][0-9]*)?)*$',
    r'^(\*|(1?[0-9]|2[0-3])(-(1?[0-9]|2[0-3]))?)(\/[1-9][0-9]*)?(,(\*|(1?[0-9]|2[0-3])(-(1?[0-9]|2[0-3]))?)(\/[1-9][0-9]*)?)*$',
    r'^(\*|([1-9]|[1-2][0-9]?|3[0-1])(-([1-9]|[1-2][0-9]?|3[0-1]))?)(\/[1-9][0-9]*)?(,(\*|([1-9]|[1-2][0-9]?|3[0-1])(-([1-9]|[1-2][0-9]?|3[0-1]))?)(\/[1-9][0-9]*)?)*$',
    r'^(\*|([1-9]|1[0-2]?)(-([1-9]|1[0-2]?))?)(\/[1-9][0-9]*)?(,(\*|([1-9]|1[0-2]?)(-([1-9]|1[0-2]?))?)(\/[1-9][0-9]*)?)*$',
    r'^(\*|[0-6](-[0-6])?)(\/[1-9][0-9]*)?(,(\*|[0-6](-[0-6])?)(\/[1-9][0-9]*)?)*$'
  ]

  # Split the cron expression into its components
  parts = cron.split()
  if len(parts) != 5:
    return True  # Invalid if not exactly 5 parts

  # Validate each part using the corresponding regex
  return any(not re.match(pattern, part) for pattern, part in zip(patterns, parts))

def delete_cron_entry(request_mac_address):
  with open(cron_filename, 'r') as f:
    lines = f.readlines()

  # Look for the line with the specified MAC address and remove it
  new_lines = []
  deleted = False
  for line in lines:
    if line.startswith('#'):
      new_lines.append(line)
    else:
      fields = line.strip().split()
      schedule = ' '.join(fields[:5])
      user = fields[5]
      command = ' '.join(fields[6:])
      mac_address = command.split()[-1]
      if mac_address == request_mac_address:
        deleted = True
      else:
        new_lines.append(line)

    # If a line was deleted, write the new contents to the file
  if deleted:
    with open(cron_filename, 'w') as f:
      f.writelines(new_lines)
  return redirect(url_for('wol_form'))

@app.route('/')
def wol_form():
  query = request.args.get('query')
  computers = load_computers()

  if query:
    computers = search_computers(computers, query)
  return render_template('wol_form.html', computers=computers, is_computer_awake=initial_computer_status, os=os, query=query)

@app.route('/delete_computer', methods=['POST'])
def delete_computer():
  name = request.form['name']

  # Get the mac_address of the computer being deleted
  mac_address = next((computer['mac_address'] for computer in computers if computer['name'] == name), None)

  # Delete the cron schedule for the mac_address
  delete_cron_entry(mac_address)

  computers[:] = [computer for computer in computers if computer['name'] != name]
  # Save the updated list of computers to the configuration file
  with open(computer_filename, 'w') as f:
    for computer in computers:
      f.write('{},{},{},{}\n'.format(computer['name'], computer['mac_address'], computer['ip_address'], computer['test_type']))
  return redirect(url_for('wol_form'))

@app.route('/add_computer', methods=['POST'])
def add_computer():
  name = request.form['name']
  mac_address = request.form['mac_address']
  ip_address = request.form['ip_address']
  test_type = request.form['test_type']

  messages = []
  # Check Entries
  if check_name_exist(name, computers):
    messages.append(f'Computer name: {name} already exists.')
  if check_mac_exist(mac_address, computers):
    messages.append(f'Computer mac: {mac_address} already exists.')
  if check_invalid_ip(ip_address):
    messages.append(f'IP: {ip_address} is invalid.')
  if check_invalid_mac(mac_address):
    messages.append(f'MAC: {mac_address} is invalid.')
  if check_invalid_test_type(test_type):
    messages.append(f'Status check: {test_type} is invalid. Enter "icmp" or a valid TCP port number.')
  if messages:
    return generate_modal_html(messages, 'Add Computer Error')

  computers.append({'name': name, 'mac_address': mac_address, 'ip_address': ip_address, 'test_type': test_type})
  # Save the updated list of computers to the configuration file
  with open(computer_filename, 'w') as f:
    for computer in computers:
      f.write('{},{},{},{}\n'.format(computer['name'], computer['mac_address'], computer['ip_address'], computer['test_type']))
  return redirect(url_for('wol_form'))

@app.route('/edit_computer', methods=['POST'])
def edit_computer():
  name = request.form['name']
  mac_address = request.form['mac_address']
  ip_address = request.form['ip_address']
  test_type = request.form['test_type']

  messages = []
  if check_invalid_ip(ip_address):
    messages.append(f'IP: {ip_address} is invalid.')
  if check_invalid_mac(mac_address):
    messages.append(f'MAC: {mac_address} is invalid.')
  if check_invalid_test_type(test_type):
    messages.append(f'Status check: {test_type} is invalid. Enter "icmp" or a valid TCP port number.')
  if messages:
    return generate_modal_html(messages, 'Edit Computer Error')

  for computer in computers:
    if computer['name'] == name:
      computer['ip_address'] = ip_address
      computer['test_type'] = test_type
      break

  # Save the updated list of computers to the configuration file
  with open(computer_filename, 'w') as f:
    for computer in computers:
      f.write('{},{},{},{}\n'.format(computer['name'], computer['mac_address'], computer['ip_address'], computer['test_type']))
  return redirect(url_for('wol_form'))

@app.route('/add_cron', methods=['POST'])
def add_cron():
  # Add Cron function
  request_mac_address = request.form['mac_address']
  request_cron = request.form['cron_request']

  messages = []
  # Check Entries
  if check_invalid_cron(request_cron):
    messages.append('Invalid cron expression!')
    messages.append('See : <a href="https://crontab.guru/" target="_blank" rel="noopener noreferrer">Crontab maker</a>')
    return generate_modal_html(messages, 'Add Cron Error')

  cron_command = f"{request_cron} root /usr/local/bin/wakeonlan {request_mac_address}"
  with open(cron_filename, "a") as f:
    f.write(f"{cron_command}\n")
  return redirect(url_for('wol_form'))

@app.route('/delete_cron', methods=['POST'])
def delete_cron():
  request_mac_address = request.form['mac_address']
  delete_cron_entry(request_mac_address)
  return redirect(url_for('wol_form'))

@app.route('/check_status')
def check_status():
  ip_address = request.args.get('ip_address')
  test_type = request.args.get('test_type')
  if is_computer_awake(ip_address,test_type):
    return 'awake'
  else:
    return 'asleep'

@app.route('/wakeup', methods=['POST'])
def wol_send():
  mac_address = request.form['mac_address']
  computer = next(c for c in computers if c['mac_address'] == mac_address)
  ip_address = computer['ip_address']
  test_type = computer['test_type']

  title = "Wakeup"
  messages = []
  if is_computer_awake(ip_address, test_type):
    messages.append('Computer is Already Awake')
  else:
    send_wol_packet(mac_address)
    messages.append('Magic Packet Sent !')

  return generate_modal_html(messages, title)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
