import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import sys, os
from PyQt5 import QtGui, QtCore, QtPrintSupport
from PIL import  Image
import pyautogui
from DefaultLayout import *
from File import *
from datetime import *
import getpass

WindowTitleLogo = "Images/Logo.png"

myFile = File()
File.setCreatedDate(File, datetime.now())
File.setModifiedDate(File, datetime.now())
File.setModifiedBy(File, getpass.getuser())


class OpenWindow(QFileDialog):
    def __init__(self, title, ext):
        super().__init__()
        self.title = title
        self.width = pyautogui.size().width / 2
        self.height = pyautogui.size().height / 2
        self.left = pyautogui.size().width * 0.25
        self.top = pyautogui.size().height * 0.25

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        home = os.path.join(os.path.expanduser('~'), 'Documents')

        if os.path.isdir(home):
            self.filepath =  self.getOpenFileName(self, title, home, ext)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

    def __del__(self):
        self.delete = True

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
        WordAct = QAction(QtGui.QIcon('Images/Word.png'), 'Word', self)
        WordAct.triggered.connect(lambda checked, index="Word": self.ImportFileWindow(index))

        PDFAct = QAction(QtGui.QIcon('Images/PDF.png'), 'PDF', self)
        PDFAct.triggered.connect(lambda checked, index="PDF": self.ImportFileWindow(index))

        NotepadAct = QAction(QtGui.QIcon('Images/Notepad.png'), 'Txt', self)
        NotepadAct.triggered.connect(lambda checked, index="Txt": self.ImportFileWindow(index))

        RTFAct = QAction(QtGui.QIcon('Images/rtf.png'), 'RTF', self)
        RTFAct.triggered.connect(lambda checked, index="RTF": self.ImportFileWindow(index))

        SoundAct = QAction(QtGui.QIcon('Images/Sound.png'), 'Sound', self)
        SoundAct.triggered.connect(lambda checked, index="Sound": self.ImportFileWindow(index))



        self.toolbar = self.addToolBar("Show Toolbar")
        self.toolbar.addAction(WordAct)
        self.toolbar.addAction(PDFAct)
        self.toolbar.addAction(NotepadAct)
        self.toolbar.addAction(RTFAct)
        self.toolbar.addAction(SoundAct)

        self.toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        #Menu Bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        importMenu = mainMenu.addMenu('Import')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        newFileButton = QAction('New File', self)
        newFileButton.setShortcut('Ctrl+N')
        newFileButton.setStatusTip('New File')
        newFileButton.triggered.connect(self.NewFileWindow)

        OpenFileButton = QAction('Open File', self)
        OpenFileButton.setShortcut('Ctrl+O')
        OpenFileButton.setStatusTip('Open File')
        OpenFileButton.triggered.connect(self.OpenFileWindow)

        SaveButton = QAction('Save', self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('File Saved')

        printButton = QAction('Print', self)
        printButton.setShortcut('Ctrl+P')
        printButton.setStatusTip('Print')
        printButton.triggered.connect(self.printWindow)

        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close_application)

        fileMenu.addAction(newFileButton)
        fileMenu.addAction(OpenFileButton)
        fileMenu.addAction(SaveButton)
        fileMenu.addAction(printButton)
        fileMenu.addAction(exitButton)

        toggleToolBarButton = QAction('Show Toolbar', self, checkable=True)
        toggleToolBarButton.setChecked(True)
        toggleToolBarButton.triggered.connect(self.toolbarHide)
        viewMenu.addAction(toggleToolBarButton)

        AboutButton = QAction(QtGui.QIcon('exit24.png'), 'About Us', self)
        AboutButton.setStatusTip('About Us')
        AboutButton.triggered.connect(self.AboutWindow)
        helpMenu.addAction(AboutButton)

        self.statusBar().showMessage("Powered By TechNGate")
        self.statusBar().show()

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(self.left, self.top, self.width/8, self.height))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.verticalLayoutWidget.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")

        self.tw = QTreeWidget()
        self.tw.setHeaderLabel('Data Sources')
        self.tw.setAlternatingRowColors(True)

        word = QTreeWidgetItem(self.tw)
        word.setText(0, "Word" + "(" + str(word.childCount()) + ")")

        pdf = QTreeWidgetItem(self.tw)
        pdf.setText(0, "PDF" + "(" + str(word.childCount()) + ")")

        audioS = QTreeWidgetItem(self.tw)
        audioS.setText(0, "Audio" + "(" + str(word.childCount()) + ")")
        self.verticalLayout.addWidget(self.tw)

        #pyautogui.rightClick()


        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(), self.height))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.horizontalLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tabWidget)

        self.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        #self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)


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
        self.dummyWindow = OpenWindow("Open File", "TextAS File *.tax")

    def ImportFileWindow(self, check):
        if check == "Word":
            self.dummyWindow = OpenWindow("Open Word File", "Doc files (*.doc *.docx)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()
        elif check == "PDF":
            self.dummyWindow = OpenWindow("Open PDF File", "Pdf files (*.pdf)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()
        elif check == "Txt":
            self.dummyWindow = OpenWindow("Open Notepad File", "Notepad files (*.txt)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()
        elif check == "RTF":
            self.dummyWindow = OpenWindow("Open Rich Text Format File", "Rich Text Format files (*.rtf)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()
        elif check == "Sound":
            self.dummyWindow = OpenWindow("Open Audio File", "Audio files (*.wav *.mp3)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()



    def printWindow(self):
        printer = QPrinter(QPrinter.HighResolution)
        self.dialog = QPrintDialog(printer, self)
        self.dialog.setWindowTitle('Print')
        self.dialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)

        if self.dialog.exec_() == QPrintDialog.Accepted:
            self.textedit.print_(printer)

    def toolbarHide(self):
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()

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
#ui = Ui_MainWindow()
#ui.setupUi(window, window.left, window.top, window.width, window.height, window.menuBar().height() + window.toolbar.height()+window.statusBar().height())
window.show()
sys.exit(App.exec())