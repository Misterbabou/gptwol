from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from scapy.layers.l2 import Ether, sendp
from flask_sqlalchemy import SQLAlchemy
import socket
import struct
import subprocess
import os
import ipaddress
import re

ping_timeout = os.environ.get('PING_TIMEOUT', 300)
arp_timeout = os.environ.get('ARP_TIMEOUT', 300)
tcp_timeout = os.environ.get('TCP_TIMEOUT', 1)
arp_interface = os.environ.get('ARP_INTERFACE')
l2_wol_packet = os.environ.get('ENABLE_L2_WOL_PACKET', 'false').lower() == 'true'
l2_interface = os.environ.get('L2_INTERFACE', 'eth0')
cron_filename = '/etc/cron.d/gptwol'
computer_filename = 'db/computers.txt'

app = Flask(__name__, static_folder='templates')
app.secret_key = os.urandom(24)
enable_login = os.environ.get('ENABLE_LOGIN', 'false')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "db", "computers.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to this route if not logged in

def conditional_login_required(func):
  """
  Decorator to conditionally require login based on environment variable.
  If enable_login is set to 'false', the login requirement is skipped.
  """
  if enable_login.strip().lower() == 'false':
    return func  # Skip login requirement if enable_login is set to false
  return login_required(func)

# In-memory user store (for simplicity)
username = os.environ.get('USERNAME', 'admin')
password = os.environ.get('PASSWORD', 'admin')
users = {username: {'password': password}}

# User model
class User(UserMixin):
  def __init__(self, id):
    self.id = id

@login_manager.user_loader
def load_user(user_id):
  return User(user_id) if user_id in users else None

@app.route('/login', methods=['GET', 'POST'])
def login():
  if enable_login.strip().lower() == 'false':
    return redirect(url_for('wol_form'))  # Skip login
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
      user = User(username)
      login_user(user)
      return redirect(url_for('wol_form'))
    return redirect(f"{url_for('login')}?error=Invalid Credentials")
  return render_template('login_form.html', os=os)

# Logout route
@app.route('/logout')
@conditional_login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

def generate_modal_html(messages, title):
  message_content = '<br>'.join(messages)
  return render_template('generate_modal.html', title=title, message_content=message_content)

class Computer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), nullable=False)
  mac_address = db.Column(db.String(17), unique=True, nullable=False)
  ip_address = db.Column(db.String(45), nullable=False)
  test_type = db.Column(db.String(10), nullable=False)

def migrate_txt_to_db():
  if not os.path.exists(computer_filename):
    return

  with open(computer_filename) as f:
    for line in f:
      fields = line.strip().split(',')
      if len(fields) < 3:
        continue
      name, mac, ip = fields[0], fields[1], fields[2]
      test_type = fields[3] if len(fields) > 3 else 'icmp'

      if not Computer.query.filter_by(mac_address=mac).first():
        c = Computer(name=name, mac_address=mac, ip_address=ip, test_type=test_type)
        db.session.add(c)

  db.session.commit()
  os.rename(computer_filename, f"{computer_filename}.old")

def load_computers():
  computers = []
  db.create_all()  # Ensure tables are created

  for c in Computer.query.all():
    computers.append({
      'name': c.name,
      'mac_address': c.mac_address,
      'ip_address': c.ip_address,
      'test_type': c.test_type
    })

  # Cron loading
  if not os.path.exists(cron_filename):
    open(cron_filename, 'w').close()

  with open(cron_filename) as f:
    for line in f:
      if not line.startswith('#'):
        fields = line.strip().split()
        schedule = ' '.join(fields[:5])
        user = fields[5]
        command = ' '.join(fields[6:])
        mac_address = command.split()[-1]
        reversed_mac_address = ':'.join(reversed(mac_address.split(':')))

        # Find and add cron info to matching computer
        for computer in computers:
          if computer['mac_address'] == mac_address:
            computer['cron_wol_schedule'] = schedule
          if computer['mac_address'] == reversed_mac_address:
            computer['cron_sol_schedule'] = schedule

  return computers

def send_l2_wol_packet(mac_address, interface):
    mac_clean = mac_address.replace(':', '').replace('-', '')
    mac_bytes = bytes.fromhex(mac_clean)

    magic_packet = b'\xff' * 6 + mac_bytes * 16

    ether_frame = Ether(dst='ff:ff:ff:ff:ff:ff', type=0x0842) / magic_packet

    sendp(ether_frame, iface=interface, verbose=False)

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
  if port.lower() == 'arp':
    return is_computer_awake_arp(ip_address)
  else:
    port_int = int(port)
    return is_computer_awake_tcp(ip_address, port_int)

def is_computer_awake_icmp(ip_address, timeout=ping_timeout):
  # Use the fping command with a timeout to check if the computer is awake
  result = subprocess.run(['fping', '-t', str(timeout), '-c', '1', ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  return result.returncode == 0

def is_computer_awake_arp(ip_address, timeout=arp_timeout):
  # Use the arp-scan command to check if the computer is awake
  command = ['arp-scan', '-qx', '-t', str(timeout), ip_address]
  if arp_interface:
    command += ['-I', arp_interface]

  result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
  # Check if there is any output in stdout
  return bool(result.stdout.strip())

def is_computer_awake_tcp(ip_address, port, timeout=tcp_timeout):
  # Use nc (netcat) to check if the TCP port is open
  result = subprocess.run(['nc', '-z', '-w', str(timeout), ip_address, str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  return result.returncode == 0

def check_mac_exist(mac_address):
  return db.session.query(Computer.id).filter_by(mac_address=mac_address).first() is not None

def check_invalid_name(name):
  return ',' in name

def check_invalid_ip(ip):
  try:
    ipaddress.ip_address(ip)
    return False # Valid IP
  except ValueError:
    return True # Invalid IP

def check_invalid_mac(mac):
  # Regular expression for validating a MAC address
  mac_pattern = r'^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$'
  # Check if the MAC address matches the pattern
  if re.match(mac_pattern, mac):
    return False  # Valid MAC address
  else:
    return True   # Invalid Mac address

def check_invalid_test_type(test_type):
  # Check if test_type is "icmp" or a valid port number
  if test_type == "icmp" or test_type == "arp":
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
@conditional_login_required
def wol_form():
  computers = load_computers()
  return render_template('wol_form.html', computers=computers, is_computer_awake=lambda *_: "asleep", os=os)

@app.route('/delete_computer', methods=['POST'])
@conditional_login_required
def delete_computer():
  mac_address = request.form['mac_address']

  # Delete the wol cron schedule for the mac_address
  delete_cron_entry(mac_address)
  # Delete the sol cron schedule for the reversed_mac_address
  reversed_mac_address = ':'.join(reversed(mac_address.split(':')))
  delete_cron_entry(reversed_mac_address)

  Computer.query.filter_by(mac_address=mac_address).delete()
  db.session.commit()

  return redirect(url_for('wol_form'))

@app.route('/add_computer', methods=['POST'])
@conditional_login_required
def add_computer():
  name = request.form['name']
  mac_address = request.form['mac_address']
  ip_address = request.form['ip_address']
  test_type = request.form['test_type']

  messages = []
  # Check Entries
  if check_mac_exist(mac_address):
    messages.append(f'Computer mac: {mac_address} already exists.')
  if check_invalid_name(name):
    messages.append(f'NAME: {name} is invalid. Character , is invalid')
  if check_invalid_ip(ip_address):
    messages.append(f'IP: {ip_address} is invalid.')
  if check_invalid_mac(mac_address):
    messages.append(f'MAC: {mac_address} is invalid.')
  if check_invalid_test_type(test_type):
    messages.append(f'Status check: {test_type} is invalid. Enter "icmp", "arp" or a valid TCP port number.')
  if messages:
    return generate_modal_html(messages, 'Add Computer Error')

  new_computer = Computer(name=name, mac_address=mac_address, ip_address=ip_address, test_type=test_type)
  db.session.add(new_computer)
  db.session.commit()

  return redirect(url_for('wol_form'))

@app.route('/edit_computer', methods=['POST'])
@conditional_login_required
def edit_computer():
  name = request.form['name']
  mac_address = request.form['mac_address']
  ip_address = request.form['ip_address']
  test_type = request.form['test_type']

  # Find the computer being edited
  computer_to_edit = Computer.query.filter_by(mac_address=mac_address).first()

  messages = []
  if computer_to_edit is None:
    messages.append(f'Computer with MAC address: {mac_address} not found.')
  if check_invalid_name(name):
    messages.append(f'NAME: {name} is invalid. Character , is invalid')
  if check_invalid_ip(ip_address):
    messages.append(f'IP: {ip_address} is invalid.')
  if check_invalid_test_type(test_type):
    messages.append(f'Status check: {test_type} is invalid. Enter "icmp", "arp" or a valid TCP port number.')
  if messages:
    return generate_modal_html(messages, 'Edit Computer Error')

  if (computer_to_edit.name == name and computer_to_edit.ip_address == ip_address and computer_to_edit.test_type == test_type):
    messages.append(f'No change was made.')
    return generate_modal_html(messages, 'Edit Computer Info')

  computer_to_edit.name = name
  computer_to_edit.ip_address = ip_address
  computer_to_edit.test_type = test_type
  db.session.commit()

  return redirect(url_for('wol_form'))

def add_cron(mac_address, request_cron):
  messages = []
  # Check Entries
  if check_invalid_cron(request_cron):
    messages.append('Invalid cron expression!')
    messages.append('See : <a href="https://crontab.guru/" target="_blank" rel="noopener noreferrer">Crontab maker</a>')
    return generate_modal_html(messages, 'Add Cron Error')

  cron_command = f"{request_cron} root /usr/local/bin/wakeonlan {mac_address}"
  with open(cron_filename, "a") as f:
    f.write(f"{cron_command}\n")
  return redirect(url_for('wol_form'))

@app.route('/add_wol_cron', methods=['POST'])
@conditional_login_required
def add_wol_cron():
  request_mac_address = request.form['mac_address']
  request_cron = request.form['cron_request']
  return add_cron(request_mac_address, request_cron)

@app.route('/add_sol_cron', methods=['POST'])
@conditional_login_required
def add_sol_cron():
  request_mac_address = request.form['mac_address']
  reversed_mac_address = ':'.join(reversed(request_mac_address.split(':')))
  request_cron = request.form['cron_request']
  return add_cron(reversed_mac_address, request_cron)

def delete_cron(mac_address):
  delete_cron_entry(mac_address)
  return redirect(url_for('wol_form'))

@app.route('/delete_wol_cron', methods=['POST'])
@conditional_login_required
def delete_wol_cron():
  request_mac_address = request.form['mac_address']
  return delete_cron(request_mac_address)

@app.route('/delete_sol_cron', methods=['POST'])
@conditional_login_required
def delete_sol_cron():
  request_mac_address = request.form['mac_address']
  reversed_mac_address = ':'.join(reversed(request_mac_address.split(':')))
  return delete_cron(reversed_mac_address)

@app.route('/check_status')
@conditional_login_required
def check_status():
  ip_address = request.args.get('ip_address')
  test_type = request.args.get('test_type')
  if is_computer_awake(ip_address,test_type):
    return 'awake'
  else:
    return 'asleep'

@app.route('/wol_or_sol_send', methods=['POST'])
@conditional_login_required
def wol_or_sol_send():
  mac_address = request.form['mac_address']
  computers = load_computers()

  computer = next(c for c in computers if c['mac_address'] == mac_address)
  ip_address = computer['ip_address']
  test_type = computer['test_type']

  messages = []
  if is_computer_awake(ip_address, test_type):
    reversed_mac_address = ':'.join(reversed(mac_address.split(':')))
    send_wol_packet(reversed_mac_address)
    title = "Shutdown"
    messages.append(f"Sleep On Lan Magic Packet Sent to {computer['name']}!")
    messages.append('See : <a href="https://github.com/Misterbabou/gptwol#configure-sleep-on-lan" target="_blank" rel="noopener noreferrer">how to configure Sleep on LAN</a>')
  else:
    if l2_wol_packet:
      messages.append(f"Wake On Lan Mode: L2 Packet")
      send_l2_wol_packet(mac_address, l2_interface)
    else:
      messages.append(f"Wake On Lan Mode: L4 Packet")
      send_wol_packet(mac_address)
    title = "Wakeup"
    messages.append(f"Wake On Lan Magic Packet Sent to {computer['name']}!")

  return generate_modal_html(messages, title)

@app.route('/arp_scan', methods=['GET'])
@conditional_login_required
def arp_scan():
  try:
    # Load the list of active computers
    computers = load_computers()
    active_mac_addresses = {computer['mac_address'] for computer in computers}

    command = ['arp-scan', '-lqx', '-t', str(arp_timeout)]
    if arp_interface:
      command += ['-I', arp_interface]

    result = subprocess.check_output(command, universal_newlines=True)
    lines = result.strip().split('\n')

    devices = []
    for line in lines:
      parts = line.split()
      if len(parts) >= 2:
        ip_address = parts[0]
        mac_address = parts[1]
        # Exclude MAC addresses that are already in the active computers list
        if mac_address not in active_mac_addresses:
          devices.append({'ip': ip_address, 'mac': mac_address})

    if not devices:
      return jsonify({'message': 'No new devices found.'})
    return jsonify(devices)

  except Exception as e:
    return jsonify({'message': str(e)}), 500

with app.app_context():
  db.create_all()
  migrate_txt_to_db()
