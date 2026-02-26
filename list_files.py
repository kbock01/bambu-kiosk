import paho.mqtt.client as mqtt
import json
import ssl
import time

# Bambu P2S Configuration
PRINTER_IP = "192.168.0.157"  # Replace with your printer's IP
PRINTER_PORT = 8883
ACCESS_CODE = "fe24afde"  # Found in printer settings
SERIAL_NUMBER = "22E8AJ5B2901941"  # Found on printer or in app

# MQTT Topics
TOPIC_REQUEST = f"device/{SERIAL_NUMBER}/request"
TOPIC_REPORT = f"device/{SERIAL_NUMBER}/report"

files_list = []

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print("Connected to Bambu P2S")
        client.subscribe(TOPIC_REPORT)
        
        # First send pushall to get initial state
        pushall_request = {
            "pushing": {
                "sequence_id": "0",
                "command": "pushall"
            }
        }
        client.publish(TOPIC_REQUEST, json.dumps(pushall_request))
        print("Requesting initial state...")
        
        # Wait a bit then request files
        time.sleep(2)

        # Request file list from internal storage
        request_files(client)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Callback when message received"""
    try:
        payload = json.loads(msg.payload.decode())
        # Check printer state
        if "print" in payload:
            if "gcode_state" in payload["print"]:
                state = payload["print"]["gcode_state"]
                print(f"Printer state: {state}")
        # Check if this is a file list response
        if "print" in payload and "sdcard_list" in payload["print"]:
            sdcard_data = payload["print"]["sdcard_list"]
            
            print("\n=== Internal Storage Files ===")
            if isinstance(sdcard_data, list):
                for file_info in sdcard_data:
                    if isinstance(file_info, dict):
                        filename = file_info.get("name", "Unknown")
                        size = file_info.get("size", 0)
                        print(f"  - {filename} ({size} bytes)")
                        files_list.append(file_info)
            
            print(f"\nTotal files: {len(files_list)}")
            
            # Disconnect after receiving files
            client.disconnect()
            
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error processing message: {e}")

def request_files(client):
    """Send request to list files on internal storage"""
    request = {
        "pushing": {
            "sequence_id": "0",
            "command": "pushall"
        }
    }
    
    # Alternative specific request for SD card files
    request = {
        "print": {
            "sequence_id": "0",
            "command": "get_file_list"
        }
    }
    
    client.publish(TOPIC_REQUEST, json.dumps(request))
    print("Requesting file list...")

def main():
    """Main function to connect and list files"""
    
    # Create MQTT client
    client = mqtt.Client(client_id="bambu_file_lister")
    
    # Set username and password
    client.username_pw_set("bblp", ACCESS_CODE)
    
    # Configure TLS/SSL (Bambu printers use self-signed certificates)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to printer
        print(f"Connecting to Bambu P2S at {PRINTER_IP}...")
        client.connect(PRINTER_IP, PRINTER_PORT, 60)
        
        # Start loop
        client.loop_start()
        
        # Wait for response (max 10 seconds)
        time.sleep(10)
        
        # Stop loop
        client.loop_stop()
        
    except Exception as e:
        print(f"Error: {e}")
    
    return files_list

if __name__ == "__main__":
    print("Bambu P2S File Listing Script")
    print("=" * 40)
    files = main()
    
    if files:
        print(f"\n{len(files)} file(s) found on internal storage")
    else:
        print("\nNo files found or connection failed")