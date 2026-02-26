import ftplib
import time

# Bambu printer settings
PRINTER_IP = "192.168.0.157"  # Your printer's IP
PRINTER_ACCESS_CODE = "fe24afde"  # From printer screen
GCODE_FILE = "print_files/Career_Quest_Logo_Spinner.gcode.3mf"

def start_print_ftp(printer_ip, access_code, gcode_path):
    try:
        # Connect via FTPS
        ftp = ftplib.FTP_TLS()
        ftp.connect(printer_ip, 990)
        print("Connected")
        ftp.login("bblp", access_code)
        print("Logged in")
        ftp.prot_p()  # Secure data connection
        
        # Upload gcode file
        with open(gcode_path, 'rb') as file:
            ftp.storbinary(f'STOR {gcode_path}', file)
        
        print(f"File uploaded successfully")
        ftp.quit()
        
    except Exception as e:
        print(f"Error: {e}")

start_print_ftp(PRINTER_IP, PRINTER_ACCESS_CODE, GCODE_FILE)