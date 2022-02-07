import json
import sys
import os
sys.path.append('\\common')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import MAX_PACKAGE_LENGTH,ENCODING
from decorators import logg


@logg
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response



@logg
def send_message(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
