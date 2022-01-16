import os
import sys
import unittest
from unittest.mock import patch
# sys.path.append(os.path.join(os.getcwd(), '..\\'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)
from server import process_client_message
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE



class TestServer(unittest.TestCase):
    mess_err = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }
    mess_ok = {
        RESPONSE: 200
    }

    def test_ok_check(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.mess_ok)

    # def test_no_action(self):
    #     self.assertEqual(process_client_message({TIME:1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.mess_err)
