import json
import paho.mqtt.client as mqtt
import ssl
from paho.mqtt.enums import CallbackAPIVersion
import time

BROKER = "192.168.0.157"
PORT = 8883
PRINTER_SERIAL = "22E8AJ5B2901941"
REQUEST_TOPIC = f"device/{PRINTER_SERIAL}/request"
REPORT_TOPIC = f"device/{PRINTER_SERIAL}/report"

# File already on the printer's SD card or cache
PRINTER_FILE = "Career_Quest_Logo_Spinner.gcode.3mf"  # File name on printer

def send_print_command(client, filename):
    """Send the print command for a file already on the printer"""
    payload = {
        "print": {
            "command": "project_file",
            "url": f"file:///{filename}",  # Reference file on printer's storage
            "param": "Metadata/plate_1.gcode",
            "subtask_id": "0",
            "use_ams": True,
            "ams_mapping": [0, -1, -1, -1],  # Use AMS slot 1 (index 0)
            "timelapse": False,
            "flow_cali": False,
            "bed_leveling": True,
            "layer_inspect": False,
            "vibration_cali": False
        }
    }
    
    client.publish(REQUEST_TOPIC, json.dumps(payload))
    print(f"Print command sent for file: {filename}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribe to the report topic to receive status updates
    client.subscribe(REPORT_TOPIC)
    print(f"Subscribed to {REPORT_TOPIC}")
    
    # Wait a moment after connecting
    time.sleep(1)
    
    # Send print command for file already on printer
    send_print_command(client, PRINTER_FILE)

def on_message(client, userdata, msg):
    print(f"\n--- Message received on {msg.topic} ---")
    try:
        data = json.loads(msg.payload.decode())
        
        # Extract key status information if available
        if 'print' in data:
            print_info = data['print']
            print(f"Status: {print_info.get('gcode_state', 'N/A')}")
            print(f"Progress: {print_info.get('mc_percent', 0)}%")
            print(f"Layer: {print_info.get('layer_num', 0)}/{print_info.get('total_layer_num', 0)}")
            print(f"Nozzle Temp: {print_info.get('nozzle_temper', 0)}°C")
            print(f"Bed Temp: {print_info.get('bed_temper', 0)}°C")
            if 'subtask_name' in print_info:
                print(f"File: {print_info['subtask_name']}")
        
    except json.JSONDecodeError:
        print("Received non-JSON message")
        print(msg.payload.decode())

def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Disconnected with result code {reason_code}")

# Create client
client = mqtt.Client(CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
client.username_pw_set('bblp', 'fe24afde')
client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect and start loop
client.connect(BROKER, PORT, 60)

# Keep the client running to receive messages
try:
    print("Listening for status updates... (Press Ctrl+C to stop)")
    client.loop_forever()
except KeyboardInterrupt:
    print("\nStopping...")
    client.disconnect()