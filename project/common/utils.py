import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import ENCODING, MAX_PACKAGE_LENGTH
from decorators import logg


@logg
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@logg
def send_message(sock, message):
    js_message = json.dumps(message)
    encode_message = js_message.encode(ENCODING)
    sock.send(encode_message)
