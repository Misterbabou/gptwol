from flask import Flask, request, render_template, redirect, url_for
import socket
import struct
import subprocess
import os

port = os.environ.get('PORT', 5000)

app = Flask(__name__, static_folder='templates')

# Load the list of computers from the configuration file
computers = []
with open('computers.txt') as f:
  for line in f:
    name, mac_address, ip_address = line.strip().split(',')
    computers.append({'name': name, 'mac_address': mac_address, 'ip_address': ip_address})

# Load the cron schedule information for each computer
with open('/etc/cron.d/gptwol') as f:
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

def send_wol_packet(mac_address):
  # Convert the MAC address to a packed binary string
  packed_mac = struct.pack('!6B', *[int(x, 16) for x in mac_address.split(':')])

  # Create a socket and send the WOL packet
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  s.sendto(b'\xff' * 6 + packed_mac * 16, ('<broadcast>', 9))

def is_computer_awake(ip_address, timeout=1):
  # Use the ping command with a timeout to check if the computer is awake
  result = subprocess.run(['ping', '-W', str(timeout), '-c', '1', ip_address], stdout=subprocess.DEVNULL)
  return result.returncode == 0


### APP
@app.route('/')
def wol_form():
  return render_template('wol_form.html', computers=computers, is_computer_awake=is_computer_awake, os=os)

@app.route('/delete_computer', methods=['POST'])
def delete_computer():
  name = request.form['name']
  computers[:] = [computer for computer in computers if computer['name'] != name]
  # Save the updated list of computers to the configuration file
  with open('computers.txt', 'w') as f:
    for computer in computers:
      f.write('{},{},{}\n'.format(computer['name'], computer['mac_address'], computer['ip_address']))
  return redirect('/')

@app.route('/add_computer', methods=['POST'])
def add_computer():
  name = request.form['name']
  mac_address = request.form['mac_address']
  ip_address = request.form['ip_address']

  # Check if the computer name already exists
  if check_name_exist(name, computers):
    return '''
    <script>
      alert('Computer name already exists');
      window.history.back();
    </script>
    '''

  computers.append({'name': name, 'mac_address': mac_address, 'ip_address': ip_address})
  # Save the updated list of computers to the configuration file
  with open('computers.txt', 'w') as f:
    for computer in computers:
      f.write('{},{},{}\n'.format(computer['name'], computer['mac_address'], computer['ip_address']))
  return redirect(url_for('wol_form'))

@app.route('/check_status')
def check_status():
  ip_address = request.args.get('ip_address')
  if is_computer_awake(ip_address):
    return 'awake'
  else:
    return 'asleep'

@app.route('/check_name_exist')
def check_name_exist(name, computers):
  for computer in computers:
    if computer['name'] == name:
      return True
  return False


@app.route('/wakeup', methods=['POST'])
def wol_send():
  mac_address = request.form['mac_address']
  computer = next(c for c in computers if c['mac_address'] == mac_address)
  ip_address = computer['ip_address']
  if is_computer_awake(ip_address):
    return '''
    <script>
      alert('Computer is Already Awake');
      window.history.back();
    </script>
    '''
  else:
    send_wol_packet(mac_address)
    return '''
    <script>
      alert('Magic Packet Send !');
      window.history.back();
    </script>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
