'''
@author: rw39401

Vision System Comand Bytes: 
    Timestamp: 8 bytes
    Command: 1 byte [0001_Start, 0002_Stop, 0003_Pause]
    Mode: 1 byte [0001_Single, 0002_Continous]
    Class: 1 byte [0000_Nut Top, 0001_Nut Bottom]
    Reserved: 1 byte

Vision System Response String:
    Timestamp: 8 bytes
    Status: 1 byte [0000_Succes, 0001_Fault]
    Counter: 8 bytes
    Errorcode: 1 byte [0001_Capture Error, 0002_No Items detected, 0003_Publishing Collision Geometry failed, 0004_6DoF Pose Estimation failed, 0005_Robot Motion failed]

'''




from flask import Flask, render_template, request, jsonify
import socket
import time
import struct


app = Flask(__name__)

# TCP/IP (Vision System = Server // PLC = Client)
TCP_IP = '127.0.0.1'  # Vision System IP
TCP_PORT = 5005       # Vision System port
BUFFER_SIZE = 1024    # Size of the buffer for incoming data

# Constants for commands and statuses
COMMANDS = {
    "start": 0x01,
    "stop": 0x02,
    "pause": 0x03
}

MODES = {
    "single": 0x01,
    "continuous": 0x02
}

CLASSES = {
    "nut_top": 0x00,
    "nut_bottom": 0x01
}


def build_command(timestamp, command, mode, class_type, reserved):
    """
    Build a bytearray command from provided parameters.
    """
    # 8 bytes for timestamp, 1 byte each for command, mode, class, and reserved
    command_bytes = bytearray(8 + 1 + 1 + 1 + 1)

    # Pack the timestamp (assuming it's an integer or a timestamp in milliseconds)
    command_bytes[0:8] = struct.pack('>Q', timestamp)  # Big-endian unsigned long long

    # Fill in the command, status, mode, class, and reserved
    command_bytes[8] = command
    command_bytes[9] = mode
    command_bytes[10] = class_type
    command_bytes[11] = reserved

    return command_bytes


def parse_response(response_bytes):
    """
    Parses the bytearray response into its components.
    
    :param response_bytes: The bytearray received from the server
    :return: Dictionary with parsed data or error message
    """
    if len(response_bytes) < 17:  # Ensure there's enough data
        return {"error": "Response data is too short."}

    # Unpack the response
    timestamp = struct.unpack('>Q', response_bytes[0:8])[0]  # Unpack the first 8 bytes for timestamp
    status = response_bytes[8]  # 1 byte for status
    counter = struct.unpack('>Q', response_bytes[9:17])[0]  # Unpack the next 8 bytes for counter
    errorcode = response_bytes[17]  # 1 byte for error code

    return {
        'timestamp': timestamp,
        'status': status,
        'counter': counter,
        'errorcode': errorcode
    }


def send_command(ip, port, command_bytes):
    """
    Sends the bytearray command to the specified TCP/IP server and receives a response.
    
    :param ip: The IP address of the server
    :param port: The port number of the server
    :param command_bytes: The bytearray command to send
    :return: Response from the server in bytes
    """
    try:
        # Create a socket to connect to the TCP/IP server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))  # Connect to the server
            s.sendall(command_bytes)  # Send the bytearray command
            data = s.recv(BUFFER_SIZE)  # Receive response
            return data
    except Exception as e:
        return {"error": f"Connection error: {e}"}



###################################################################### Flask Routes #########################################################################

@app.route('/')
def index():
    """
    Route to load main page of the web interface.
    """
    return render_template('index.html')



@app.route('/send_command', methods=['POST'])
def send_command():
    # Automatically get the current timestamp
    timestamp = int(time.time())  # Get current time in seconds

    # Get parameters from request
    command = request.form.get('command')  # 'start', 'stop', or 'pause'
    mode = request.form.get('mode')  # 'single' or 'continuous'
    class_type = request.form.get('class')  # 'nut_top' or 'nut_bottom'
    reserved = int(request.form.get('reserved', 0))  # Default reserved to 0 if not provided

    # Map command, mode, class
    command_byte = COMMANDS.get(command)
    mode_byte = MODES.get(mode)
    class_byte = CLASSES.get(class_type)

    # Build the command bytearray and send it
    command_bytes = build_command(timestamp, command_byte, mode_byte, class_byte, reserved)
    response_bytes = send_command(TCP_IP, TCP_PORT, command_bytes)

    # Parse the response bytes
    response_data = parse_response(response_bytes)

    # Prepare the JSON response
    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True)