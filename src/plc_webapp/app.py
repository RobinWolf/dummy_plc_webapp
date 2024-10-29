'''
@author: rw39401

Vision System Comand String: 
<PLCCommand>
    <Command> </Command>
    <Class> </Class>
    <Mode> </Mode>
    <Reserved> </Reserved>
</PLCCommand>

Vision System Response String:
<PLCResponse>
    <Acknowledgement> </Acknowledgement>
    <Counter> </Counter>
    <Errorcode> </Errorcode>
</PLCResponse>

'''




from flask import Flask, render_template, request, jsonify
import socket
import xml.etree.ElementTree as ET


app = Flask(__name__)

# TCP/IP (Vision System = Server // PLC = Client)
TCP_IP = '127.0.0.1'  # Vision System IP
TCP_PORT = 5005       # Vision System port
BUFFER_SIZE = 1024    # Size of the buffer for incoming data


def create_xml_command(command, class_val, mode, reserved=""):
    """
    Creates an XML command string based on provided parameters.
    """
    root = ET.Element("PLCCommand")
    ET.SubElement(root, "Command").text = command
    ET.SubElement(root, "Class").text = str(class_val)
    ET.SubElement(root, "Mode").text = mode
    ET.SubElement(root, "Reserved").text = reserved
    return ET.tostring(root, encoding="unicode")


def parse_xml_response(xml_response):
    """
    Parses XML response from the TCP/IP server.
    """
    try:
        root = ET.fromstring(xml_response)
        acknowledgement = root.find("Acknowledgement").text
        counter = root.find("Counter").text
        errorcode = root.find("Errorcode").text
        return {
            "acknowledgement": int(acknowledgement),
            "counter": int(counter),
            "errorcode": int(errorcode),
        }
    except Exception as e:
        return {"error": f"Failed to parse XML response: {e}"}


def send_command(ip, port, xml_command):
    """
    Sends the XML command to the specified TCP/IP server and receives a response.
    """
    try:
        # Create a socket to connect to the TCP/IP server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            s.sendall(xml_command.encode())
            data = s.recv(BUFFER_SIZE).decode()
            return parse_xml_response(data)
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
def send_command_route():
    """
    Route to handle sending a command from the web interface.
    """
    # Get server IP and port from the form
    ip = request.form.get('ip')
    port = request.form.get('port')
    command = request.form.get('command')
    class_val = int(request.form.get('class'))
    mode = request.form.get('mode')
    reserved = request.form.get('reserved', "")
    
    xml_command = create_xml_command(command, class_val, mode, reserved)
    response_data = send_command(ip, port, xml_command)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)