from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
import os
import sys

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = self.resource_path("view/admin.ui")
        uic.loadUi(ui_path, self)
    
    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)