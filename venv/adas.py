from PyQt5 import QtCore, QtGui, QtWidgets
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class MainWindow(QtWidgets.QMainWindow):
                #(self,  parent=None) <- original code
    def __init__(self, image_files, parent=None):
        QtWidgets.QMainWindow.__init__(self,  parent)
        self.setupUi(self)

        #Initialized Widget here
        self.slides_widget = Slides(image_files, self)
        self.setCentralWidget(self.slides_widget)

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(1012, 532)

        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(470, 130, 451, 301))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))



class Slides(QtWidgets.QWidget):
    def __init__(self, image_files, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.image_files = image_files
        self.label = QtWidgets.QLabel("", self)
        self.label.setGeometry(50, 150, 450, 350)

        #button
        self.button = QtWidgets.QPushButton(". . .", self)
        self.button.setGeometry(200, 100, 140, 30)
        self.button.clicked.connect(self.timerEvent)
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        self.delay = 3000 #ms
        sTitle = "DIT Erasmus Page : {} seconds"
        self.setWindowTitle(sTitle.format(self.delay/1000.0))


    def timerEvent(self, e=None):
        if self.step >= len(self.image_files):
            self.timer.start(self.delay, self)
            self.step = 0
            return
        self.timer.start(self.delay, self)
        file = self.image_files[self.step]
        image = QtGui.QPixmap(file)
        self.label.setPixmap(image)
        self.setWindowTitle("{} --> {}".format(str(self.step), file))
        self.step += 1

image_files = ["Images/Notepad.png", "Images/Word.png", "Images/PDF.png", "Images/Twitter.png"]


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = MainWindow(image_files)
    ui = MainWindow(image_files)
    Form.show()
    sys.exit(app.exec_())