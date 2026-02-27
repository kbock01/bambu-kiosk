import socket
import ssl
import threading
import json
import time
import hashlib
from datetime import datetime
import ipaddress
from typing import Dict, Any, Optional
import struct
import random

class BambuP2SSimulator:
    """
    Simulator for Bambu Lab P2S 3D Printer with AMS and Camera support.
    Handles TLS/TCP connections and simulates printer responses.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8883, 
                 camera_port: int = 6000,
                 access_code: str = 'test1234', serial_number: str = '01S00A123456789',
                 certfile: str = None, keyfile: str = None):
        self.host = host
        self.port = port
        self.camera_port = camera_port
        self.access_code = access_code
        self.serial_number = serial_number
        self.certfile = certfile
        self.keyfile = keyfile
        
        # Add print history storage
        self.print_history = [
            {
                'id': '1',
                'gcode_file': 'test_print_1.gcode',
                'subtask_name': 'Test Print 1',
                'profile_id': '0',
                'task_id': '1',
                'weight': 15.5,
                'length': 3500,
                'start_time': int(time.time()) - 7200,
                'end_time': int(time.time()) - 3600,
                'cost_time': 3600,
                'result': 'success',
                'reason': 0,
                'bed_type': 'auto',
                'nozzle_diameter': 0.4,
                'filament_used_g': 15.5,
                'filament_used_mm': 3500,
                'layers': 100,
                'thumbnail': '',
            },
            {
                'id': '2',
                'gcode_file': 'test_print_2.gcode',
                'subtask_name': 'Test Print 2',
                'profile_id': '0',
                'task_id': '2',
                'weight': 25.3,
                'length': 5700,
                'start_time': int(time.time()) - 14400,
                'end_time': int(time.time()) - 10800,
                'cost_time': 3600,
                'result': 'success',
                'reason': 0,
                'bed_type': 'auto',
                'nozzle_diameter': 0.4,
                'filament_used_g': 25.3,
                'filament_used_mm': 5700,
                'layers': 150,
                'thumbnail': '',
            },
            {
                'id': '3',
                'gcode_file': 'failed_print.gcode',
                'subtask_name': 'Failed Print',
                'profile_id': '0',
                'task_id': '3',
                'weight': 10.0,
                'length': 2000,
                'start_time': int(time.time()) - 21600,
                'end_time': int(time.time()) - 20400,
                'cost_time': 1200,
                'result': 'failed',
                'reason': 16777216,
                'bed_type': 'auto',
                'nozzle_diameter': 0.4,
                'filament_used_g': 5.2,
                'filament_used_mm': 1100,
                'layers': 35,
                'thumbnail': '',
            }
        ]
    
        # Track completed prints
        self.completed_prints = []

        # Printer state
        self.state = {
            'print_status': 'IDLE',
            'progress': 0,
            'remaining_time': 0,
            'bed_temp': 25.0,
            'bed_target_temp': 0.0,
            'nozzle_temp': 25.0,
            'nozzle_target_temp': 0.0,
            'chamber_temp': 25.0,
            'speed_level': 2,
            'fan_speed': 0,
            'layer_num': 0,
            'total_layers': 0,
            'print_error': 0,
            'wifi_signal': -45,
            'led_mode': 'on',
            'online': True,
        }
        
        # AMS (Automatic Material System) state
        self.ams = {
            "ams": {
                'ams': [
                    {
                        'id': '0',
                        'humidity': 3,
                        'temp': 25.0,
                        "tray": [
                            {
                                "bed_temp": 0,
                                "bed_temp_type": "0",
                                "cols": [
                                    "FF0000FF"
                                ],
                                "drying_temp": 0,
                                "drying_time": 0,
                                "id": "0",
                                "nozzle_temp_max": 240,
                                "nozzle_temp_min": 190,
                                "remain": 0,
                                "tag_uid": "0000000000000000",
                                "tray_color": "FF0000FF",
                                "tray_diameter": 0.00,
                                "tray_id_name": "",
                                "tray_info_idx": "GFA00",
                                "tray_sub_brands": "",
                                "tray_type": "PLA",
                                "tray_uuid": "00000000000000000000000000000000",
                                "tray_weight": 0,
                                "xcam_info": "000000000000000000000000",
                                "k": 0.024,
                                "n": 0.1,
                                "tray_temp": 240,
                                "tray_time": 0
                            },
                            {
                                "bed_temp": 0,
                                "bed_temp_type": "0",
                                "cols": [
                                    "000000FF"
                                ],
                                "drying_temp": 0,
                                "drying_time": 0,
                                "id": "1",
                                "nozzle_temp_max": 240,
                                "nozzle_temp_min": 190,
                                "remain": 0,
                                "tag_uid": "0000000000000000",
                                "tray_color": "000000FF",
                                "tray_diameter": 0.00,
                                "tray_id_name": "",
                                "tray_info_idx": "GFA00",
                                "tray_sub_brands": "",
                                "tray_type": "PLA",
                                "tray_uuid": "00000000000000000000000000000000",
                                "tray_weight": 0,
                                "xcam_info": "000000000000000000000000",
                                "k": 0.024,
                                "n": 0.1,
                                "tray_temp": 240,
                                "tray_time": 0
                            },
                            {
                                "bed_temp": 0,
                                "bed_temp_type": "0",
                                "cols": [
                                    "DFE2E3FF"
                                ],
                                "drying_temp": 0,
                                "drying_time": 0,
                                "id": "2",
                                "nozzle_temp_max": 240,
                                "nozzle_temp_min": 190,
                                "remain": 0,
                                "tag_uid": "0000000000000000",
                                "tray_color": "DFE2E3FF",
                                "tray_diameter": 0.00,
                                "tray_id_name": "",
                                "tray_info_idx": "GFA05",
                                "tray_sub_brands": "",
                                "tray_type": "PLA",
                                "tray_uuid": "00000000000000000000000000000000",
                                "tray_weight": 0,
                                "xcam_info": "000000000000000000000000",
                                "k": 0.024,
                                "n": 0.1,
                                "tray_temp": 240,
                                "tray_time": 0
                            },
                            {
                                "bed_temp": 0,
                                "bed_temp_type": "0",
                                "cols": [
                                    "F95959FF"
                                ],
                                "drying_temp": 0,
                                "drying_time": 0,
                                "id": "3",
                                "nozzle_temp_max": 240,
                                "nozzle_temp_min": 190,
                                "remain": 0,
                                "tag_uid": "0000000000000000",
                                "tray_color": "F95959FF",
                                "tray_diameter": 0.00,
                                "tray_id_name": "",
                                "tray_info_idx": "GFL00",
                                "tray_sub_brands": "",
                                "tray_type": "PLA",
                                "tray_uuid": "00000000000000000000000000000000",
                                "tray_weight": 0,
                                "xcam_info": "000000000000000000000000",
                                "k": 0.024,
                                "n": 0.1,
                                "tray_temp": 240,
                                "tray_time": 0
                            }
                        ]
                    }
                ],
                "ams_exist_bits": "1",
                "insert_flag": True,
                "power_on_flag": False,
                "tray_exist_bits": "e",
                "tray_is_bbl_bits": "e",
                "tray_now": 255, # 254 if external spool / vt_tray, otherwise is ((ams_id * 4) + tray_id) for current tray (ams 2 tray 2 would be (1*4)+1 = 5)
                "tray_pre": 255,
                "tray_read_done_bits": "e",
                "tray_reading_bits": "0",
                "tray_tar": 255,
                "version": 4
            }
        }
        
        self.current_file = ''
        self.gcode_file_path = ''
        
        # Connection management
        self.server_socket: Optional[socket.socket] = None
        self.camera_socket: Optional[socket.socket] = None
        self.running = False
        self.clients = []
        self.camera_clients = []
        self.authenticated_clients = set()
        
        # Simulation threads
        self.simulation_thread: Optional[threading.Thread] = None
        self.camera_thread: Optional[threading.Thread] = None
        
        # Generate self-signed certificate if not provided
        self._ensure_certificates()
        
    def _ensure_certificates(self):
        """Ensure SSL certificates exist, generate self-signed if needed"""
        if self.certfile is None or self.keyfile is None:
            import tempfile
            import os
            
            # Create temporary directory for certificates
            self.temp_cert_dir = tempfile.mkdtemp()
            self.certfile = os.path.join(self.temp_cert_dir, 'cert.pem')
            self.keyfile = os.path.join(self.temp_cert_dir, 'key.pem')
            
            # Generate self-signed certificate
            self._generate_self_signed_cert()
            
    def _generate_self_signed_cert(self):
        """Generate a self-signed certificate for testing"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Bambu Lab Simulator"),
                x509.NameAttribute(NameOID.COMMON_NAME, "bambu-simulator.local"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("bambu-simulator.local"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write private key
            with open(self.keyfile, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(self.certfile, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
                
            print(f"Generated self-signed certificate: {self.certfile}")
            
        except ImportError:
            # Fallback to OpenSSL command if cryptography not available
            import subprocess
            import os
            
            print("Generating self-signed certificate using OpenSSL...")
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
                '-keyout', self.keyfile,
                '-out', self.certfile,
                '-days', '365', '-nodes',
                '-subj', '/CN=bambu-simulator.local'
            ], check=True)
    
    def _start_camera_server(self):
        """Start the camera streaming server on port 6000"""
        try:
            # Create raw socket for camera
            self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.camera_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.camera_socket.bind((self.host, self.camera_port))
            self.camera_socket.listen(5)
            
            # Wrap with SSL using same certificate
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            # context.load_cert_chain(self.certfile, self.keyfile)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            self.camera_ssl_context = context
            
            print(f"Bambu Camera Server started on {self.host}:{self.camera_port} (TLS)")
            
            # Accept camera connections
            while self.running:
                try:
                    self.camera_socket.settimeout(1.0)
                    client_socket, address = self.camera_socket.accept()

                    # Wrap client socket with SSL
                    try:
                        ssl_client = self.camera_ssl_context.wrap_socket(client_socket, server_side=True)
                        print(f"Camera client connected from {address} (TLS established)")
                        
                        client_thread = threading.Thread(
                            target=self._handle_camera_client,
                            args=(ssl_client, address)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        self.camera_clients.append(ssl_client)
                        
                    except ssl.SSLError as e:
                        print(f"Camera SSL handshake failed with {address}: {e}")
                        client_socket.close()
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Camera server error: {e}")
                        
        except Exception as e:
            print(f"Failed to start camera server: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_camera_client(self, client_socket: socket.socket, address):
        """Handle camera client connections"""
        try:
            # Send camera stream header (simulated JPEG stream)
            header = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
                b"Cache-Control: no-cache\r\n"
                b"Connection: close\r\n"
                b"\r\n"
            )
            client_socket.sendall(header)
            
            frame_count = 0
            
            # Stream simulated frames
            while self.running:
                try:
                    # Generate a fake JPEG frame (placeholder data)
                    frame_data = self._generate_fake_frame(frame_count)
                    
                    # Send frame with multipart boundary
                    frame_header = (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(frame_data)).encode() + b"\r\n"
                        b"\r\n"
                    )
                    
                    client_socket.sendall(frame_header + frame_data + b"\r\n")
                    
                    frame_count += 1
                    time.sleep(0.1)  # ~10 FPS
                    
                except (BrokenPipeError, ConnectionResetError):
                    break
                except Exception as e:
                    print(f"Camera stream error: {e}")
                    break
                    
        except Exception as e:
            print(f"Camera client handler error: {e}")
        finally:
            if client_socket in self.camera_clients:
                self.camera_clients.remove(client_socket)
            try:
                client_socket.close()
            except:
                pass
            print(f"Camera client {address} disconnected")
    
    def _generate_fake_frame(self, frame_count: int) -> bytes:
        """Generate a fake JPEG frame for testing"""
        # This is a minimal valid JPEG header + some random data
        # In a real implementation, you'd generate actual images
        
        # JPEG header
        jpeg_header = bytes([
            0xFF, 0xD8,  # SOI (Start of Image)
            0xFF, 0xE0,  # APP0
            0x00, 0x10,  # Length
            0x4A, 0x46, 0x49, 0x46, 0x00,  # "JFIF\0"
            0x01, 0x01,  # Version
            0x00,  # Units
            0x00, 0x01, 0x00, 0x01,  # X/Y density
            0x00, 0x00,  # Thumbnail
        ])
        
        # Add some random data to simulate image content
        random_data = bytes([random.randint(0, 255) for _ in range(1024)])
        
        # JPEG footer
        jpeg_footer = bytes([0xFF, 0xD9])  # EOI (End of Image)
        
        # Combine to create a "fake" JPEG
        frame = jpeg_header + random_data + jpeg_footer
        
        return frame
            
    def start(self):
        """Start the simulator server"""
        self.running = True
        
        # Create raw socket for MQTT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Wrap with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.certfile, self.keyfile)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.ssl_context = context
        
        print(f"Bambu P2S Simulator started on {self.host}:{self.port} (TLS)")
        print(f"Serial Number: {self.serial_number}")
        print(f"Access Code: {self.access_code}")
        print(f"Certificate: {self.certfile}")
        
        # Start camera server thread
        self.camera_thread = threading.Thread(target=self._start_camera_server)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulate_printer)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Accept MQTT connections
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                
                # Wrap client socket with SSL
                try:
                    ssl_client = self.ssl_context.wrap_socket(client_socket, server_side=True)
                    print(f"Client connected from {address} (TLS established)")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(ssl_client, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.clients.append(ssl_client)
                    
                except ssl.SSLError as e:
                    print(f"SSL handshake failed with {address}: {e}")
                    client_socket.close()
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                    
    def stop(self):
        """Stop the simulator server"""
        self.running = False
        
        # Close all MQTT clients
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Close all camera clients
        for client in self.camera_clients:
            try:
                client.close()
            except:
                pass
        
        # Close server sockets
        if self.server_socket:
            self.server_socket.close()
        if self.camera_socket:
            self.camera_socket.close()
            
        print("Simulator stopped")
        
    def _handle_client(self, client_socket: socket.socket, address):
       """Handle individual client connections"""
       authenticated = False
       
       try:
           while self.running:
               # Read MQTT packet header
               first_byte = client_socket.recv(1)
               if not first_byte:
                   break

               packet_type = (first_byte[0] >> 4) & 0x0F
               
               # Read remaining length (variable length encoding)
               remaining_length = 0
               multiplier = 1
               while True:
                   byte_data = client_socket.recv(1)
                   if not byte_data:
                       return
                   byte = byte_data[0]
                   remaining_length += (byte & 0x7F) * multiplier
                   if (byte & 0x80) == 0:
                       break
                   multiplier *= 128

               # Read the packet payload
               if remaining_length > 0:
                   payload = client_socket.recv(remaining_length)
                   if len(payload) != remaining_length:
                       print(f"Incomplete packet received")
                       break
               else:
                   payload = b''

               # Handle different MQTT packet types
               if packet_type == 1:  # CONNECT
                   self._handle_mqtt_connect(client_socket, payload)
                   authenticated = True
                   
               elif packet_type == 3:  # PUBLISH
                   if authenticated:
                       self._handle_mqtt_publish(client_socket, first_byte[0], payload)
                       
               elif packet_type == 8:  # SUBSCRIBE
                   if authenticated:
                       self._handle_mqtt_subscribe(client_socket, payload)
                       
               elif packet_type == 12:  # PINGREQ
                   # Send PINGRESP
                   client_socket.send(bytearray([0xD0, 0x00]))
                   
               elif packet_type == 14:  # DISCONNECT
                   print(f"Client {address} disconnecting")
                   break
                   
               else:
                   print(f"Unknown packet type: {packet_type}")
                   
       except Exception as e:
           print(f"Client handler error: {e}")
           import traceback
           traceback.print_exc()
       finally:
           if client_socket in self.authenticated_clients:
               self.authenticated_clients.remove(client_socket)
           if client_socket in self.clients:
               self.clients.remove(client_socket)
           try:
               client_socket.close()
           except:
               pass
           print(f"Client {address} disconnected")

    def _handle_mqtt_connect(self, client_socket: socket.socket, payload: bytes):
       """Handle MQTT CONNECT packet"""
       try:
           offset = 0
           
           # Protocol Name Length (2 bytes)
           protocol_name_len = struct.unpack(">H", payload[offset:offset+2])[0]
           offset += 2
           
           # Protocol Name
           protocol_name = payload[offset:offset+protocol_name_len].decode('utf-8')
           offset += protocol_name_len
           
           # Protocol Level (1 byte)
           protocol_level = payload[offset]
           offset += 1
           
           # Connect Flags (1 byte)
           connect_flags = payload[offset]
           offset += 1
           
           username_flag = (connect_flags >> 7) & 1
           password_flag = (connect_flags >> 6) & 1
           
           # Keep Alive (2 bytes)
           keep_alive = struct.unpack(">H", payload[offset:offset+2])[0]
           offset += 2
           
           # Client ID Length (2 bytes)
           client_id_len = struct.unpack(">H", payload[offset:offset+2])[0]
           offset += 2
           
           # Client ID
           client_id = payload[offset:offset+client_id_len].decode('utf-8')
           offset += client_id_len
           
           # Username (if flag is set)
           username = None
           if username_flag:
               username_len = struct.unpack(">H", payload[offset:offset+2])[0]
               offset += 2
               username = payload[offset:offset+username_len].decode('utf-8')
               offset += username_len
           
           # Password (if flag is set)
           password = None
           if password_flag:
               password_len = struct.unpack(">H", payload[offset:offset+2])[0]
               offset += 2
               password = payload[offset:offset+password_len].decode('utf-8')
               offset += password_len
           
           print(f"MQTT CONNECT - Client: {client_id}, User: {username}, Pass: {password}")
           
           # Authenticate
           if username == 'bblp' and password == self.access_code:
               # Send CONNACK - connection accepted
               connack = bytearray([0x20, 0x02, 0x00, 0x00])
               client_socket.send(connack)
               self.authenticated_clients.add(client_socket)
               print("Authentication successful")
               
               # Send initial status
               time.sleep(0.1)
               self._send_full_status_mqtt(client_socket, '0')
           else:
               # Send CONNACK - connection refused
               connack = bytearray([0x20, 0x02, 0x00, 0x05])  # 0x05 = not authorized
               client_socket.send(connack)
               print("Authentication failed")
               
       except Exception as e:
           print(f"Error handling CONNECT: {e}")
           import traceback
           traceback.print_exc()

    def _handle_mqtt_publish(self, client_socket: socket.socket, flags: int, payload: bytes):
       """Handle MQTT PUBLISH packet"""
       try:
           qos = (flags >> 1) & 0x03
           offset = 0
           
           # Topic length
           topic_len = struct.unpack(">H", payload[offset:offset+2])[0]
           offset += 2
           
           # Topic
           topic = payload[offset:offset+topic_len].decode('utf-8')
           offset += topic_len
           
           # Packet ID (if QoS > 0)
           packet_id = None
           if qos > 0:
               packet_id = struct.unpack(">H", payload[offset:offset+2])[0]
               offset += 2
           
           # Message payload
           message_payload = payload[offset:]
           
           print(f"PUBLISH - Topic: {topic}, QoS: {qos}, Payload length: {len(message_payload)}")
           
           # Send PUBACK if QoS = 1
           if qos == 1 and packet_id is not None:
               puback = bytearray([0x40, 0x02])
               puback.extend(struct.pack(">H", packet_id))
               client_socket.send(puback)
           
           # Parse and handle the JSON message
           try:
               message = json.loads(message_payload.decode('utf-8'))
               self._handle_command(client_socket, message)
           except json.JSONDecodeError as e:
               print(f"Invalid JSON in PUBLISH: {e}")
               
       except Exception as e:
           print(f"Error handling PUBLISH: {e}")
           import traceback
           traceback.print_exc()

    def _handle_mqtt_subscribe(self, client_socket: socket.socket, payload: bytes):
       """Handle MQTT SUBSCRIBE packet"""
       try:
           offset = 0
           
           # Packet ID
           packet_id = struct.unpack(">H", payload[offset:offset+2])[0]
           offset += 2
           
           granted_qos = []
           
           while offset < len(payload):
               # Topic length
               topic_len = struct.unpack(">H", payload[offset:offset+2])[0]
               offset += 2
               
               # Topic
               topic = payload[offset:offset+topic_len].decode('utf-8')
               offset += topic_len
               
               # Requested QoS
               qos = payload[offset]
               offset += 1
               
               print(f"SUBSCRIBE - Topic: {topic}, QoS: {qos}")
               granted_qos.append(qos)
           
           # Send SUBACK
           suback = bytearray([0x90, 1 + len(granted_qos)])
           suback.extend(struct.pack(">H", packet_id))
           suback.extend(granted_qos)
           client_socket.send(suback)
           
       except Exception as e:
           print(f"Error handling SUBSCRIBE: {e}")
           import traceback
           traceback.print_exc()

    def _send_message(self, client_socket: socket.socket, message: Dict[str, Any]):
       """Send JSON message to client via MQTT PUBLISH"""
       self._send_mqtt_publish(client_socket, 'device/01S00A123456789/report', message)

    def _send_mqtt_publish(self, client_socket: socket.socket, topic: str, message: Dict[str, Any], qos: int = 0):
       """Send MQTT PUBLISH packet"""
       try:
           json_str = json.dumps(message)
           payload = json_str.encode('utf-8')
           
           # Build PUBLISH packet
           topic_bytes = topic.encode('utf-8')
           
           # Fixed header
           packet_type = 0x30 | (qos << 1)  # PUBLISH with QoS
           
           # Variable header + payload
           variable_header = bytearray()
           variable_header.extend(struct.pack(">H", len(topic_bytes)))
           variable_header.extend(topic_bytes)
           
           # Add packet ID if QoS > 0
           if qos > 0:
               packet_id = 1  # Simplified - should track packet IDs
               variable_header.extend(struct.pack(">H", packet_id))
           
           variable_header.extend(payload)
           
           # Encode remaining length
           remaining_length = len(variable_header)
           encoded_length = bytearray()
           while True:
               byte = remaining_length % 128
               remaining_length = remaining_length // 128
               if remaining_length > 0:
                   byte |= 0x80
               encoded_length.append(byte)
               if remaining_length == 0:
                   break
           
           # Send packet
           packet = bytearray([packet_type])
           packet.extend(encoded_length)
           packet.extend(variable_header)
           
           client_socket.sendall(packet)
           
       except Exception as e:
           print(f"Send MQTT message error: {e}")
           import traceback
           traceback.print_exc()

    def _send_full_status_mqtt(self, client_socket: socket.socket, sequence_id: str):
       """Send full printer status via MQTT"""
       status = {
           'print': {
               'command': 'push_status',
               'msg': 0,
               'sequence_id': sequence_id,
               'gcode_state': self.state['print_status'],
               'mc_print_stage': self.state['print_status'],
               'mc_percent': self.state['progress'],
               'mc_remaining_time': self.state['remaining_time'],
               'bed_temper': self.state['bed_temp'],
               'bed_target_temper': self.state['bed_target_temp'],
               'nozzle_temper': self.state['nozzle_temp'],
               'nozzle_target_temper': self.state['nozzle_target_temp'],
               'chamber_temper': self.state['chamber_temp'],
               'speed_level': self.state['speed_level'],
               'fan_gear': self.state['fan_speed'],
               'layer_num': self.state['layer_num'],
               'total_layer_num': self.state['total_layers'],
               'print_error': self.state['print_error'],
               'wifi_signal': self.state['wifi_signal'],
               'lights_report': [{'mode': self.state['led_mode']}],
               'online': {'version': 1},
               'ipcam': {'ipcam_dev': '1', 'ipcam_record': 'enable'},
               'gcode_file': self.current_file,
               'subtask_name': self.current_file,
               'stg': [],
               'stg_cur': 0,
               **self.ams
           }
       }
       self._send_mqtt_publish(client_socket, f'device/{self.serial_number}/report', status)
       
    def _handle_command(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle authenticated commands from client"""
        try:
            print(message)
            for key, command in message.items():
                command_data = message.get(key, {})
                command = command_data.get('command', '')
                sequence_id = command_data.get('sequence_id', '0')
                
                print(f"Received command: {command}")
                
                if command == 'push_all':
                    self._send_full_status(client_socket, sequence_id)
                    
                elif command == 'get_history':
                    self._send_history(client_socket, sequence_id, command_data)

                elif command == 'get_version':
                    self._send_version(client_socket, sequence_id)
                    
                elif command == 'start_print' or command == 'project_file' :
                    self.current_file = command_data.get('gcode_file', 'test.gcode')
                    self.state['print_status'] = 'RUNNING'
                    self.state['progress'] = 0
                    self.state['layer_num'] = 0
                    self.state['total_layers'] = 100
                    self.state['remaining_time'] = 3600
                    
                    tray_id = command_data.get('ams_tray', 0)
                    if tray_id < len(self.ams['ams']['ams'][0]['tray']):
                        tray = self.ams['ams']['ams'][0]['tray'][tray_id]
                        self.state['bed_target_temp'] = tray['bed_temp']
                        self.state['nozzle_target_temp'] = tray['nozzle_temp_min'] + 10
                        self.ams['ams']['tray_now'] = tray_id
                    
                    response = {
                        'print': {
                            'command': 'start_print',
                            'result': 'success',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                    
                elif command == 'pause':
                    self.state['print_status'] = 'PAUSED'
                    response = {
                        'print': {
                            'command': 'pause',
                            'result': 'success',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                    
                elif command == 'resume':
                    self.state['print_status'] = 'RUNNING'
                    response = {
                        'print': {
                            'command': 'resume',
                            'result': 'success',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                    
                elif command == 'stop':
                    # Record as failed/cancelled
                    self._record_print_completion(success=False, reason=50331648)
                    
                    self.state['print_status'] = 'IDLE'
                    self.state['progress'] = 0
                    self.state['bed_target_temp'] = 0
                    self.state['nozzle_target_temp'] = 0
                    self.ams['ams']['tray_now'] = 255
                    response = {
                        'print': {
                            'command': 'stop',
                            'result': 'success',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                    
                elif command == 'gcode_line':
                    gcode = command_data.get('gcode', '')
                    self._execute_gcode(gcode)
                    response = {
                        'print': {
                            'command': 'gcode_line',
                            'result': 'success',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                    
                elif command == 'change_filament':
                    tray_id = command_data.get('target_ams', 0)
                    if tray_id < len(self.ams['ams']['ams'][0]['tray']):
                        self.ams['ams']['tray_now'] = tray_id
                        response = {
                            'print': {
                                'command': 'change_filament',
                                'result': 'success',
                                'sequence_id': sequence_id
                            }
                        }
                    else:
                        response = {
                            'print': {
                                'command': 'change_filament',
                                'result': 'failed',
                                'reason': 'Invalid tray',
                                'sequence_id': sequence_id
                            }
                        }
                    self._send_message(client_socket, response)
                    
                else:
                    response = {
                        'print': {
                            'command': command,
                            'result': 'unknown_command',
                            'sequence_id': sequence_id
                        }
                    }
                    self._send_message(client_socket, response)
                
        except Exception as e:
            print(f"Command handler error: {e}")
            
    def _execute_gcode(self, gcode: str):
        """Simulate G-code execution"""
        gcode = gcode.strip().upper()
        
        if gcode.startswith('M104'):
            try:
                temp = float(gcode.split('S')[1])
                self.state['nozzle_target_temp'] = temp
            except:
                pass
                
        elif gcode.startswith('M140'):
            try:
                temp = float(gcode.split('S')[1])
                self.state['bed_target_temp'] = temp
            except:
                pass
                
        elif gcode.startswith('M106'):
            try:
                speed = int(gcode.split('S')[1])
                self.state['fan_speed'] = int((speed / 255) * 100)
            except:
                pass
                
        elif gcode.startswith('M107'):
            self.state['fan_speed'] = 0
            
    def _record_print_completion(self, success: bool, reason: int = 0):
        """Record a completed print in history"""
        if not hasattr(self, 'state') or 'print_start_time' not in self.state:
            return
        
        end_time = int(time.time())
        start_time = self.state.get('print_start_time', end_time)
        
        # Calculate statistics
        cost_time = end_time - start_time
        
        # Estimate filament usage (simplified)
        filament_used_mm = int(self.state['progress'] * 50)
        filament_used_g = filament_used_mm * 0.0075
        
        history_entry = {
            'id': str(len(self.print_history) + 1),
            'gcode_file': self.current_file,
            'subtask_name': self.current_file,
            'profile_id': '0',
            'task_id': str(len(self.print_history) + 1),
            'weight': round(filament_used_g, 1),
            'length': filament_used_mm,
            'start_time': start_time,
            'end_time': end_time,
            'cost_time': cost_time,
            'result': 'success' if success else 'failed',
            'reason': reason,
            'bed_type': 'auto',
            'nozzle_diameter': 0.4,
            'filament_used_g': round(filament_used_g, 1),
            'filament_used_mm': filament_used_mm,
            'layers': self.state['layer_num'],
            'thumbnail': '',
        }
        
        self.print_history.insert(0, history_entry)
        
        if len(self.print_history) > 50:
            self.print_history = self.print_history[:50]
        
        print(f"Recorded print completion: {history_entry['result']}")
        
    def _send_history(self, client_socket: socket.socket, sequence_id: str, command_data: Dict[str, Any]):
        """Send print history records"""
        try:
            start = command_data.get('start', 0)
            count = command_data.get('count', 10)
            filter_type = command_data.get('filter', 'all')
            
            filtered_history = self.print_history.copy()
            
            if filter_type == 'success':
                filtered_history = [h for h in filtered_history if h['result'] == 'success']
            elif filter_type == 'failed':
                filtered_history = [h for h in filtered_history if h['result'] == 'failed']
            
            filtered_history.sort(key=lambda x: x['start_time'], reverse=True)
            
            total_count = len(filtered_history)
            end = min(start + count, total_count)
            paginated_history = filtered_history[start:end]
            
            response = {
                'print': {
                    'command': 'get_history',
                    'sequence_id': sequence_id,
                    'result': 'success',
                    'total': total_count,
                    'start': start,
                    'count': len(paginated_history),
                    'records': paginated_history
                }
            }
            self._send_message(client_socket, response)
            print(f"Sent {len(paginated_history)} history records (total: {total_count})")
            
        except Exception as e:
            print(f"Error sending history: {e}")
            import traceback
            traceback.print_exc()
            
    def _send_version(self, client_socket: socket.socket, sequence_id: str):
        """Send version information"""
        version_info = {
            'print': {
                'command': 'get_version',
                'sequence_id': sequence_id,
                'module': [
                    {'name': 'ota', 'sw_ver': '1.02.00.00', 'hw_ver': ''},
                    {'name': 'mc', 'sw_ver': '1.02.00.00', 'hw_ver': 'AP04'},
                    {'name': 'esp32', 'sw_ver': '1.02.00.00', 'hw_ver': ''},
                    {'name': 'ams', 'sw_ver': '1.02.00.00', 'hw_ver': 'AMS01'},
                ]
            }
        }
        self._send_message(client_socket, version_info)
        
    def _broadcast_status(self):
        """Broadcast status to all authenticated clients"""
        for client in list(self.authenticated_clients):
            try:
                self._send_full_status_mqtt(client, '0')
            except:
                pass
                
    def _simulate_printer(self):
        """Simulate printer behavior"""
        last_update = time.time()
        
        while self.running:
            time.sleep(0.1)
            current_time = time.time()
            
            # Update temperatures
            if self.state['nozzle_target_temp'] > 0:
                diff = self.state['nozzle_target_temp'] - self.state['nozzle_temp']
                self.state['nozzle_temp'] += diff * 0.05
                
            if self.state['bed_target_temp'] > 0:
                diff = self.state['bed_target_temp'] - self.state['bed_temp']
                self.state['bed_temp'] += diff * 0.03
                
            # Cool down when targets are 0
            if self.state['nozzle_target_temp'] == 0:
                self.state['nozzle_temp'] = max(25, self.state['nozzle_temp'] - 0.5)
                
            if self.state['bed_target_temp'] == 0:
                self.state['bed_temp'] = max(25, self.state['bed_temp'] - 0.3)
                
            # Update print progress
            if self.state['print_status'] == 'RUNNING':
                if self.state['progress'] < 100:
                    self.state['progress'] += 10
                    self.state['remaining_time'] = int((100 - self.state['progress']) * 36)
                    self.state['layer_num'] = int(self.state['progress'])
                    
                    # Simulate material usage
                    if self.ams['ams']['tray_now'] != 255:
                        tray = self.ams['ams']['ams'][0]['tray'][self.ams['ams']['tray_now']]
                        if tray['remain'] > 0:
                            tray['remain'] = max(0, tray['remain'] - 0.01)
                else:
                    # Record successful completion
                    self._record_print_completion(success=True)

                    self.state['print_status'] = 'IDLE'
                    self.state['progress'] = 100
                    self.state['remaining_time'] = 0
                    
            # Broadcast status every 2 seconds
            if current_time - last_update >= 2.0:
                self._broadcast_status()
                last_update = current_time


def main():
    """Main function to run the simulator"""
    HOST = '0.0.0.0'
    PORT = 8883
    CAMERA_PORT = 6000
    ACCESS_CODE = 'test1234'
    SERIAL_NUMBER = '01S00A123456789'
    
    simulator = BambuP2SSimulator(
        host=HOST,
        port=PORT,
        camera_port=CAMERA_PORT,
        access_code=ACCESS_CODE,
        serial_number=SERIAL_NUMBER
    )
    
    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\nShutting down simulator...")
        simulator.stop()


if __name__ == '__main__':
    main()