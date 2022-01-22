import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.utils import get_message, send_message
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoding_messages = None
        self.received_message = None

    def send(self, message_to_sand):
        json_test_message = json.dumps(self.test_dict)
        self.encoding_messages = json_test_message.encode(ENCODING)
        self.received_message = message_to_sand

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.1111,
        USER: {
            ACCOUNT_NAME: 'QA'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoding_messages, test_socket.received_message)


    def test_send_message_raise(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_socket, 'wrong_dictionary')
    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)

    def test_get_message_err(self):
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)

if __name__ == '__main__':
    unittest.main()
