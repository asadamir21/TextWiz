import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import sys, os
from PyQt5 import QtGui, QtCore, QtPrintSupport
from PIL import  Image
import pyautogui
from DefaultLayout import *

WindowTitleLogo = "Logo.png"

class OpenWindow(QFileDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Open File'
        self.width = pyautogui.size().width / 2
        self.height = pyautogui.size().height / 2
        self.left = pyautogui.size().width * 0.25
        self.top = pyautogui.size().height * 0.25
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "TextAS"
        self.width, self.height = pyautogui.size()
        self.left = 0;
        self.top = 0;
        self.initWindows()

    def initWindows(self):
        self.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top, self.width, self.height)
        self.showMaximized()

        # ToolBar
        exitAct = QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)


        #Menu Bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        newFileButton = QAction(QtGui.QIcon('exit24.png'), 'New File', self)
        newFileButton.setShortcut('Ctrl+N')
        newFileButton.setStatusTip('New File')
        newFileButton.triggered.connect(self.NewFileWindow)

        OpenFileButton = QAction(QtGui.QIcon('exit24.png'), 'Open File', self)
        OpenFileButton.setShortcut('Ctrl+O')
        OpenFileButton.setStatusTip('Open File')
        OpenFileButton.triggered.connect(self.OpenFileWindow)

        SaveButton = QAction(QtGui.QIcon('exit24.png'), 'Save', self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('File Saved')

        printButton = QAction(QtGui.QIcon('exit24.png'), 'Print', self)
        printButton.setShortcut('Ctrl+P')
        printButton.setStatusTip('Exit application')
        printButton.triggered.connect(self.printWindow)

        exitButton = QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close_application)

        fileMenu.addAction(newFileButton)
        fileMenu.addAction(OpenFileButton)
        fileMenu.addAction(SaveButton)
        fileMenu.addAction(printButton)
        fileMenu.addAction(exitButton)

        AboutButton = QAction(QtGui.QIcon('exit24.png'), 'About Us', self)
        AboutButton.setStatusTip('About Us')
        AboutButton.triggered.connect(self.AboutWindow)
        helpMenu.addAction(AboutButton)

        self.statusBar().showMessage("Powered By TechNGate")


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("MainWindow", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("MainWindow", "Page 2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))


    def close_application(self):
        choice = QMessageBox.question(self, 'Quit', "Are You Sure?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def NewFileWindow(self):
        self.myDialog = QDialog()
        self.myDialog.setModal(True)
        self.myDialog.setWindowTitle("New File")
        self.myDialog.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.myDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.myDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        self.myDialog.show()

    def OpenFileWindow(self):
        self.w = OpenWindow()
        self.w.exec_()

    def printWindow(self):
        printer = QPrinter(QPrinter.HighResolution)
        self.dialog = QPrintDialog(printer, self)
        self.dialog.setWindowTitle('Print')
        self.dialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)

        if self.dialog.exec_() == QPrintDialog.Accepted:
            self.textedit.print_(printer)

    def AboutWindow(self):
        self.myDialog = QDialog()
        self.myDialog.setModal(True)
        self.myDialog.setWindowTitle("About Us")
        self.myDialog.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.myDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.myDialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)
        self.myDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        groupBox1 = QGroupBox()
        vBox1 = QVBoxLayout(self.myDialog)

        label = QLabel(self.myDialog)
        label.setPixmap(QtGui.QPixmap(WindowTitleLogo).scaledToWidth(self.myDialog.width()/2))

        vBox1.addWidget(label)
        groupBox1.setLayout(vBox1)

        groupBox2 = QGroupBox()
        vBox2 = QVBoxLayout(self.myDialog)
        textpane = QTextEdit()
        textpane.setText("TextAs\nAnalysis Like Never Before")
        textpane.setStyleSheet("background:transparent;")
        textpane.setReadOnly(True)

        vBox2.addWidget(textpane)
        groupBox2.setLayout(vBox2)

        hbox1 = QHBoxLayout(self.myDialog)
        hbox1.addWidget(groupBox1)
        hbox1.addWidget(groupBox2)
        self.myDialog.setLayout(hbox1)
        self.myDialog.show()




App = QApplication(sys.argv)
window = Window()
ui = Ui_MainWindow()
ui.setupUi(window, window.left, window.top, window.width, window.height, window.menuBar().height() + window.toolbar.height()+window.statusBar().height())
window.show()
sys.exit(App.exec())