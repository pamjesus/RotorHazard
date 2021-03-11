import sys

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import Config

sys.path.append('../interface')
sys.path.append('/home/pi/RotorHazard/src/interface')  # Needed to run on startup

import RHInterface

if len(sys.argv) < 2:
    print('Please specify serial port, e.g. COM12.')
    exit()

Config.SERIAL_PORTS = [sys.argv[1]]
INTERFACE = RHInterface.get_hardware_interface(config=Config)
print("Nodes detected: {}".format(len(INTERFACE.nodes)))

def log(s):
    print(s)

INTERFACE.hardware_log_callback=log

for node in INTERFACE.nodes:
    INTERFACE.set_value_8(node, RHInterface.WRITE_MODE, 2)
    INTERFACE.set_frequency(node.index, 5840)

def write_buffer(fname, buf):
    with open(fname, 'w') as f:
        for v in buf:
            f.write('{}\n'.format(v))

count = 1
buffer = []
try:
    while True:
        gevent.sleep(0.1)
    
        for node in INTERFACE.nodes:
            #data = node.read_block(INTERFACE, RHInterface.READ_NODE_RSSI_HISTORY, 16)
            data = node.read_block(INTERFACE, RHInterface.READ_NODE_RSSI_PEAK, 1)
            for rssi in data:
                if rssi == 0xFF:
                    fname = 'rssi_dump_{}.csv'.format(count)
                    write_buffer(fname, buffer)
                    print('Written {} ({})'.format(fname, len(buffer)))
                    count += 1
                elif rssi > 0:
                    buffer.append(rssi)
except:
    write_buffer('rssi_dump.csv', buffer)
