import os

class Config:
    # Printer Configuration
    PRINTER_IP = os.getenv('PRINTER_IP', '192.168.1.200')
    PRINTER_SERIAL = os.getenv('PRINTER_SERIAL', 'AC12309BH109')
    PRINTER_ACCESS_CODE = os.getenv('PRINTER_ACCESS_CODE', '12347890')
    
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