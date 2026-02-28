from flask import Flask, render_template, jsonify, request
import bambulabs_api as bl
import os
import time
from config import Config
import threading
import logging
import base64
import sys
from io import BytesIO
import zipfile

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global printer instance
printer = None
printer_lock = threading.Lock()

def gcode_files_in_3mf(
        zipfile_path: str) -> list[str]:
    """
    Get the gcodefiles in the 3mf.

    Args:
        zipfile_path (str): location of the text file.

    Returns:
        list[str]: first gcode file, or None if not found
    """
    zf = zipfile.ZipFile(zipfile_path)

    nl = zf.namelist()
    print(nl)
    return [n for n in nl if n.endswith(".gcode") and n.startswith("Metadata/plate_")]  # noqa: E501

def get_printer():
    """Get or create printer instance"""
    global printer
    if printer is None:
        with printer_lock:
            if printer is None:
                printer = bl.Printer(
                    app.config['PRINTER_IP'],
                    app.config['PRINTER_ACCESS_CODE'],
                    app.config['PRINTER_SERIAL'],
                    app.config['CAMERA_ENABLED']
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
            basename, _ = os.path.splitext(filepath)
            with open(filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                files.append({
                    'name': basename + ".3mf",
                    'image_data': encoded_string
                })
    
    return sorted(files, key=lambda x: x['name'])

@app.route('/')
def index():
    """Main kiosk interface"""
    # files = get_available_files()
    # return render_template('index.html', 
    #                      files=files, 
    #                      ams_slots=app.config['AMS_SLOTS'])
    """Main kiosk interface"""
    files = get_available_files()

    ams_hub = printer.ams_hub()
    filament_trays = ams_hub[0].filament_trays
    AMS_SLOTS = {}

    for idx, tray in filament_trays.items():
        slot_number = idx + 1
        AMS_SLOTS[str(slot_number)] = {
            'name': tray.tray_id_name,
            'color': ("#" + tray.tray_color) if tray.tray_color else '#FFFFFF'  # Default to white if no color provided
        }
    return render_template('index.html', 
                         files=files, 
                         ams_slots=AMS_SLOTS)

@app.route('/api/status')
def get_status():
    """Get printer status"""
    try:
        status = printer.get_state()
        nozzle_temp = printer.get_nozzle_temperature()
        time_remaining = printer.get_time()

        formatted_time_remaining = "{:02d} min.".format(time_remaining)
        light_state = printer.get_light_state()
        return jsonify({
            'success': True,
            'status': {'print_state': status, 'nozzle_temp': nozzle_temp, 
                       'time_remaining': formatted_time_remaining, 'light_state': light_state}
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
        basename, _ = os.path.splitext(filename)

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
                
        # Start print job
        # Note: You'll need to check the actual API method for printing
        # This is a placeholder - adjust based on actual API capabilities
        logger.info(f"Starting print: {basename} with AMS slot: {ams_slot}")

        # gcode_location = next(
        #     (i for i in gcode_files_in_3mf(filepath)), None)

        # if gcode_location:
        #     with open(filepath, "rb") as file:
        #         io_file = BytesIO(file.read())
        #     result = printer.upload_file(io_file, filename)
        #     if "226" not in result:
        #         print("Error Uploading File to Printer", file=sys.stdout)

        #     else:
        #         print("Done Uploading/Sending Start Print Command", file=sys.stdout)
        #         printer.start_print(filename, 1)
        #         print("Start Print Command Sent", file=sys.stdout)
        # else:
        #     print("No gcode file found in 3mf", file=sys.stdout)

        # The actual print command will depend on the API
        printer.start_print(os.path.basename(filename), 1, True, [ams_slot, -1, -1, -1, -1])
        
        return jsonify({
            'success': True,
            'message': f'Print started: {basename}'
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
        if action == 'on':
            printer.turn_light_on()
        elif action == 'off':
            printer.turn_light_off()
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
        printer.stop_print()
        
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
    printer = get_printer()
    app.run(host='0.0.0.0', port=5000, debug=False)