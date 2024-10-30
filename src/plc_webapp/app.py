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
from flask_socketio import SocketIO, emit
import socket
import time
import struct


app = Flask(__name__)
socketio = SocketIO(app)

# TCP/IP (Vision System = Server // PLC = Client)
TCP_IP = '127.0.0.1'  # Vision System IP
TCP_PORT = 65432       # Vision System port
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
    "nut_bottom": 0x01,
    "all": 0x64 #100
}


def build_command(timestamp, command, mode, class_type, reserved):
    """
    Build a bytearray command from provided parameters.
    """

    command_bytes = struct.pack('>QBBBB', timestamp, command, mode, class_type, reserved)

    return command_bytes


def parse_response(response_bytes):
    """
    Parses the bytearray response into its components.
    
    """
    if len(response_bytes) < 17: 
        return {"error": "Response data is too short."}
    
    timestamp,status,counter,errorcode,reserved = struct.unpack('>QBQBB', response_bytes)

    return {
        'timestamp': timestamp,
        'status': status,
        'counter': counter,
        'errorcode': errorcode,
        'reserved': reserved
    }

 
def tcp_connection(ip, port, command_bytes):
    """
    Connects to the TCP/IP server, sends a command, and listens continuously for responses.
    """
    try:
        # Open the socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            s.sendall(command_bytes)
            
            # Listen for responses continuously
            while True:
                response_bytes = s.recv(BUFFER_SIZE)
                if not response_bytes:
                    break  # Exit loop if no data received
                
                # Parse and emit each response to the frontend
                response_data = parse_response(response_bytes)
                socketio.emit('server_response', response_data)

    except Exception as e:
        socketio.emit('server_response', {"error": f"Connection error: {e}"})



###################################################################### Flask Routes #########################################################################

@app.route('/')
def index():
    """
    Route to load main page of the web interface.
    """
    return render_template('index.html')


@socketio.on('send_command')
def handle_send_command(data):
    """
    Route which is executed on button click "Send Command".
    """
    TCP_IP = data['ip']
    TCP_PORT = data['port']
    timestamp = int(time.time())
    command = COMMANDS.get(data['command'])
    mode = MODES.get(data['mode'])
    class_type = CLASSES.get(data['class'])
    reserved = int(data.get('reserved', 0)) if data.get('reserved', '').isdigit() else 0

    command_bytes = build_command(timestamp, command, mode, class_type, reserved)
   
    # Start TCP communication in a separate thread
    socketio.start_background_task(tcp_connection, TCP_IP, TCP_PORT, command_bytes)



if __name__ == '__main__':
    socketio.run(app, debug=True)