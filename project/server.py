import argparse
import configparser
import os
import threading
import time
import socket
import sys
from select import select
import logging
from decorators import logg
from metaclasses import ServerMeta
from server_database import ServerDataBase
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import HistoryWidget, ConfWindow, MainWindow, gui_create_model, create_stat_model

sys.path.append('common\\')
from tests.err import IncorrectDataRecivedError
from common.variables import ACTION, DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, EXIT, DESTINATION, RESPONSE_200, RESPONSE_400, RESPONSE_202, LIST_INFO, ADD_CONTACT, \
    CONTACT_DEL, USERS_LIST, GET_CONTACTS
from common.utils import get_message, send_message
from descriptors import Port

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

z