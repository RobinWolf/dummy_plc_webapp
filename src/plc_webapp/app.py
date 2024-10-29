from flask import Flask, render_template, request, jsonify
import socket

app = Flask(__name__)

# TCP/IP (Vision System = Server // PLC = Client)
TCP_IP = '127.0.0.1'  # Vision System IP
TCP_PORT = 5005       # Vision System port
BUFFER_SIZE = 1024    # Size of the buffer for incoming data

def send_command(command):
    """
    Sends a command to the TCP/IP server and receives a response.
    """
    try:
        # Create a socket to connect to the TCP/IP server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((TCP_IP, TCP_PORT))
            s.sendall(command.encode())
            data = s.recv(BUFFER_SIZE).decode()
            return data  # Received response from server
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command_route():
    """
    Route to handle sending a command from the web interface.
    """
    command = request.form.get('command')
    response = send_command(command)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)