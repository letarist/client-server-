import os
import sys
import unittest
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)
from client import create_presence, process_ans
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE


class TestClient(unittest.TestCase):
    """Tests class"""

    def test_create_presence_not_arguments(self):
        self.assertNotEqual(create_presence(), '')

    def test_presence(self):
        def_t = create_presence()
        def_t[TIME] = 1.1
        self.assertEqual(def_t, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_req_200(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200: OK')

    def test_req_400(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'bad request'}), '400 : bad request')

    def test_no_resp(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'bad request'})

    # @patch.object(sys, 'argv', ['client.py', '7779'])
    # def test_port_main(self):
    #     self.assertRaises(IndexError, project.client.main)

    @patch.object(sys, 'argv', ['client.py', '-a', 'localhost', '-p', 7777777])
    def test_unbel_port_client(self):
        self.assertNotEqual(None, '200 : OK')


if __name__ == '__main__':
    unittest.main()
