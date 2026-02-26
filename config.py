import os

class Config:
    # Left Printer Configuration
    PRINTER_IP = os.getenv('PRINTER_IP', '192.168.0.157')
    PRINTER_SERIAL = os.getenv('PRINTER_SERIAL', '22E8AJ5B2901941')
    PRINTER_ACCESS_CODE = os.getenv('PRINTER_ACCESS_CODE', 'fe24afde')

    # Right Printer Configuration
    # PRINTER_IP = os.getenv('PRINTER_IP', '192.168.0.84')
    # PRINTER_SERIAL = os.getenv('PRINTER_SERIAL', '22E8AJ5C0201826')
    # PRINTER_ACCESS_CODE = os.getenv('PRINTER_ACCESS_CODE', 'fa1cb76f')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    PRINT_FILES_DIR = os.path.join(os.path.dirname(__file__), 'print_files')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.3mf', '.gcode'}
    
    # AMS Color Slots (customize based on your setup)
    AMS_SLOTS = {
        '1': {'name': 'Slot 1', 'color': '#FF0000'},
        '2': {'name': 'Slot 2', 'color': '#00FF00'},
        '3': {'name': 'Slot 3', 'color': '#0000FF'},
        '4': {'name': 'Slot 4', 'color': '#FFFF00'},
    }

    CAMERA_ENABLED = False