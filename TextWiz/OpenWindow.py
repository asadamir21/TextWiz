from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
import pyautogui

class OpenWindow(QFileDialog):
    def __init__(self, title, ext, flag):
        super().__init__()
        self.title = title
        self.width = pyautogui.size().width / 2
        self.height = pyautogui.size().height / 2
        self.left = pyautogui.size().width * 0.25
        self.top = pyautogui.size().height * 0.25

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        if flag == 0:
            self.filepath =  self.getOpenFileNames(self, title, "", ext)
        elif flag == -1:
            self.filepath =  self.getOpenFileName(self, title, "", ext)
        elif flag == 1:
            self.filepath = self.getSaveFileName(self, title, "", ext)
        elif flag == 2:
            self.filepath = self.getOpenFileNames(self, title, "", ext)