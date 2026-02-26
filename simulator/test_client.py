import socket
import json
import threading
import time

class BambuTestClient:
    """Simple test client for the Bambu P2S simulator"""
    
    def __init__(self, host='localhost', port=8883):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def connect(self):
        """Connect to the simulator"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.running = True
        
        # Start receive thread
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        print(f"Connected to Bambu P2S simulator at {self.host}:{self.port}")
        
    def disconnect(self):
        """Disconnect from the simulator"""
        self.running = False
        if self.socket:
            self.socket.close()
            
    def _receive_messages(self):
        """Receive and display messages from the simulator"""
        buffer = b''
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                buffer += data
                
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line.decode('utf-8'))
                            self._display_message(message)
                        except json.JSONDecodeError:
                            pass
                            
            except Exception as e:
                if self.running:
                    print(f"Error receiving: {e}")
                break
                
    def _display_message(self, message):
        """Display received message"""
        if 'print' in message:
            print_state = message['print']
            print(f"\rState: {print_state.get('gcode_state', 'UNKNOWN')} | "
                  f"Progress: {print_state.get('print_percentage', 0)}% | "
                  f"Layer: {print_state.get('layer_num', 0)}/{print_state.get('total_layer_num', 0)} | "
                  f"Nozzle: {print_state.get('nozzle_temper', 0):.1f}°C | "
                  f"Bed: {print_state.get('bed_temper', 0):.1f}°C", end='')
            
    def send_command(self, command):
        """Send a command to the simulator"""
        message = json.dumps(command) + '\n'
        self.socket.sendall(message.encode('utf-8'))
        
    def start_print(self, filename='test.gcode', layers=100, time_estimate=300):
        """Start a print job"""
        command = {
            'print': {
                'command': 'start',
                'file': filename,
                'total_layers': layers,
                'estimated_time': time_estimate
            }
        }
        self.send_command(command)
        print(f"\nStarting print: {filename}")
        
    def pause_print(self):
        """Pause the current print"""
        command = {'print': {'command': 'pause'}}
        self.send_command(command)
        print("\nPausing print")
        
    def resume_print(self):
        """Resume the current print"""
        command = {'print': {'command': 'resume'}}
        self.send_command(command)
        print("\nResuming print")
        
    def stop_print(self):
        """Stop the current print"""
        command = {'print': {'command': 'stop'}}
        self.send_command(command)
        print("\nStopping print")
        
    def change_filament(self, tray_id):
        """Change to a different filament tray"""
        command = {
            'ams': {
                'command': 'ams_change_filament',
                'target': tray_id
            }
        }
        self.send_command(command)
        print(f"\nChanging to filament tray {tray_id}")


# Example usage
if __name__ == '__main__':
    client = BambuTestClient()
    
    try:
        client.connect()
        time.sleep(2)
        
        # Start a print
        client.start_print('demo_print.gcode', layers=50, time_estimate=120)
        
        # Wait a bit
        time.sleep(10)
        
        # Pause
        client.pause_print()
        time.sleep(5)
        
        # Resume
        client.resume_print()
        time.sleep(10)
        
        # Change filament
        client.change_filament(1)
        time.sleep(5)
        
        # Let it run
        time.sleep(30)
        
        # Stop
        client.stop_print()
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        client.disconnect()