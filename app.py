from flask import Flask, render_template, jsonify, request
import bambulabs_api as bl
import os
import time
from config import Config
import threading
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global printer instance
printer = None
printer_lock = threading.Lock()

def get_printer():
    """Get or create printer instance"""
    global printer
    if printer is None:
        with printer_lock:
            if printer is None:
                printer = bl.Printer(
                    app.config['PRINTER_IP'],
                    app.config['PRINTER_ACCESS_CODE'],
                    app.config['PRINTER_SERIAL']
                )
                printer.connect()
                time.sleep(2)  # Allow connection to establish
    return printer

def get_available_files():
    """Get list of available print files"""
    files_dir = app.config['PRINT_FILES_DIR']
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
        return []
    
    files = []
    for filename in os.listdir(files_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext in app.config['ALLOWED_EXTENSIONS']:
            filepath = os.path.join(files_dir, filename)
            files.append({
                'name': filename,
                'path': filepath,
                'size': os.path.getsize(filepath)
            })
    
    return sorted(files, key=lambda x: x['name'])

@app.route('/')
def index():
    """Main kiosk interface"""
    files = get_available_files()

    p = get_printer()
    ams_hub = p.ams_hub()
    filament_trays = ams_hub[0]
    AMS_SLOTS = {}

    for idx, tray in enumerate(filament_trays):
        slot_number = idx + 1
        AMS_SLOTS[str(slot_number)] = {
            'name': tray.tray_id_name,
            'color': tray.tray_color if tray.tray_color else '#FFFFFF'  # Default to white if no color provided
        
    return render_template('index.html', 
                         files=files, 
                         ams_slots=AMS_SLOTS)

@app.route('/api/status')
def get_status():
    """Get printer status"""
    try:
        p = get_printer()
        status = p.get_state()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/print', methods=['POST'])
def start_print():
    """Start a print job"""
    try:
        data = request.json
        filename = data.get('filename')
        ams_slot = data.get('ams_slot')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'No filename provided'
            }), 400
        
        # Verify file exists
        filepath = os.path.join(app.config['PRINT_FILES_DIR'], filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        p = get_printer()
        
        # Start print job
        # Note: You'll need to check the actual API method for printing
        # This is a placeholder - adjust based on actual API capabilities
        logger.info(f"Starting print: {filename} with AMS slot: {ams_slot}")
        
        # The actual print command will depend on the API
        p.start_print(filepath, 1, True, [int(slot) for slot in ams_slot.split(',')])
        
        return jsonify({
            'success': True,
            'message': f'Print started: {filename}'
        })
        
    except Exception as e:
        logger.error(f"Error starting print: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/light/<action>')
def control_light(action):
    """Control printer light"""
    try:
        p = get_printer()
        
        if action == 'on':
            p.turn_light_on()
        elif action == 'off':
            p.turn_light_off()
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action'
            }), 400
        
        return jsonify({
            'success': True,
            'action': action
        })
        
    except Exception as e:
        logger.error(f"Error controlling light: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_print():
    """Cancel current print job"""
    try:
        p = get_printer()
        p.stop_print()
        
        return jsonify({
            'success': True,
            'message': 'Print cancelled'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling print: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)