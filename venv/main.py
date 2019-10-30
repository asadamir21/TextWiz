import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import sys, os
from PyQt5 import QtGui, QtCore, QtPrintSupport
from PIL import  Image
import pyautogui

from File import *
from datetime import *
import getpass
import ntpath

WindowTitleLogo = "Images/Logo.png"
isSaveAs = True
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

        NotepadAct = QAction(QtGui.QIcon('Images/Notepad.png'), 'txt', self)
        NotepadAct.triggered.connect(lambda checked, index="Txt": self.ImportFileWindow(index))

        RTFAct = QAction(QtGui.QIcon('Images/rtf.png'), 'RTF', self)
        RTFAct.triggered.connect(lambda checked, index="RTF": self.ImportFileWindow(index))

        SoundAct = QAction(QtGui.QIcon('Images/Sound.png'), 'Audio', self)
        SoundAct.triggered.connect(lambda checked, index="Sound": self.ImportFileWindow(index))

        self.toolbar = self.addToolBar("Show Toolbar")
        self.toolbar.addAction(WordAct)
        self.toolbar.addAction(PDFAct)
        self.toolbar.addAction(NotepadAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(RTFAct)
        self.toolbar.addAction(SoundAct)

        self.toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        #Menu Bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        importMenu = mainMenu.addMenu('Import')
        VisualizationMenu = mainMenu.addMenu('Visualization')
        helpMenu = mainMenu.addMenu('Help')

        #FileMenu Button
        newFileButton = QAction('New File', self)
        newFileButton.setShortcut('Ctrl+N')
        newFileButton.setStatusTip('New File')
        newFileButton.triggered.connect(self.NewFileWindow)

        OpenFileButton = QAction('Open File', self)
        OpenFileButton.setShortcut('Ctrl+O')
        OpenFileButton.setStatusTip('Open File')
        OpenFileButton.triggered.connect(self.OpenFileWindow)

        SaveButton = QAction(QtGui.QIcon("Images/Save.png"), 'Save', self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('File Saved')

        printButton = QAction(QtGui.QIcon("Images/Printer.png"), 'Print', self)
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

        #ViewMenu Button
        toggleToolBarButton = QAction('Show Toolbar', self, checkable=True)
        toggleToolBarButton.setChecked(True)
        toggleToolBarButton.triggered.connect(self.toolbarHide)
        viewMenu.addAction(toggleToolBarButton)

        toggleDataSourceButton = QAction('Show Data Sources', self, checkable=True)
        toggleDataSourceButton.setChecked(True)
        toggleDataSourceButton.triggered.connect(self.DataSoureHide)
        viewMenu.addAction(toggleDataSourceButton)

        #ImportMenu Button
        WordFileButton = QAction(QtGui.QIcon("Images/Word.png"),'Word File', self)
        WordFileButton.setStatusTip('Word File')
        WordFileButton.triggered.connect(lambda checked, index="Word": self.ImportFileWindow(index))

        PDFFileButton = QAction(QtGui.QIcon("Images/PDF.png"), 'PDF File', self)
        PDFFileButton.setStatusTip('PDF File')
        PDFFileButton.triggered.connect(lambda checked, index="PDF": self.ImportFileWindow(index))

        TXTFileButton = QAction(QtGui.QIcon("Images/Notepad.png"), 'Notepad File', self)
        TXTFileButton.setStatusTip('Notepad File')
        TXTFileButton.triggered.connect(lambda checked, index="Txt": self.ImportFileWindow(index))

        RTFFileButton = QAction(QtGui.QIcon("Images/rtf.png"), 'RTF File', self)
        RTFFileButton.setStatusTip('RTF File')
        RTFFileButton.triggered.connect(lambda checked, index="RTF": self.ImportFileWindow(index))

        SoundFileButton = QAction(QtGui.QIcon("Images/Sound.png"), 'Audio File', self)
        SoundFileButton.setStatusTip('Word File')
        SoundFileButton.triggered.connect(lambda checked, index="Sound": self.ImportFileWindow(index))

        importMenu.addAction(WordFileButton)
        importMenu.addAction(PDFFileButton)
        importMenu.addAction(TXTFileButton)
        importMenu.addAction(RTFFileButton)
        importMenu.addAction(SoundFileButton)



        #HelpMenu Button
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
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(self.left, self.top, self.width/8, self.height/8))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.verticalLayoutWidget.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")

        #DataSource Widget
        self.DataSourceLabel = QLabel()
        self.DataSourceLabel.setText("Data Sources")
        self.verticalLayout.addWidget(self.DataSourceLabel)

        self.DataSourceTreeWidget = QTreeWidget()
        self.DataSourceTreeWidget.setHeaderLabel('Data Sources')
        self.DataSourceTreeWidget.setAlternatingRowColors(True)
        self.DataSourceTreeWidget.header().setHidden(True)
        self.DataSourceTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.DataSourceTreeWidget.customContextMenuRequested.connect(lambda checked, index=QtGui.QContextMenuEvent: self.FindDataSourceTreeWidgetContextMenu(index))

        #DataSource Widget Item
        self.wordTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")

        self.pdfTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")

        self.txtTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")

        self.rtfTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")

        self.audioSTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")
        self.verticalLayout.addWidget(self.DataSourceTreeWidget)











        #Right Tab Widget
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.height))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QTabWidget(self.horizontalLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.horizontalLayout.addWidget(self.tabWidget)

        self.TabCreation()
        self.setCentralWidget(self.centralwidget)

    #Tab Creation
    def TabCreation(self):
        _translate = QtCore.QCoreApplication.translate
        self.tab = QWidget()
        self.tab.setObjectName("tab")

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))

    #Get Which Data Source Widget Item and its Position
    def FindDataSourceTreeWidgetContextMenu(self, DataSourceMouseRightClickEvent):
        if DataSourceMouseRightClickEvent.reason == DataSourceMouseRightClickEvent.Mouse:
            DataSourceMouseRightClickPos = DataSourceMouseRightClickEvent.globalPos()
            DataSourceMouseRightClickItem = self.DataSourceTreeWidget.itemAt(DataSourceMouseRightClickEvent.pos())
        else:
            DataSourceMouseRightClickPos = None
            DataSourceselection = self.DataSourceTreeWidget.selectedItems()

            if DataSourceselection:
                DataSourceMouseRightClickItem = DataSourceselection[0]
            else:
                DataSourceMouseRightClickItem = self.DataSourceTreeWidget.currentItem()
                if DataSourceMouseRightClickItem is None:
                    DataSourceMouseRightClickItem = self.DataSourceTreeWidget.invisibleRootItem().child(0)
            if DataSourceMouseRightClickItem is not None:
                DataSourceParent = DataSourceMouseRightClickItem.parent()
                while DataSourceParent is not None:
                    DataSourceParent.setExpanded(True)
                    DataSourceParent = DataSourceParent.parent()
                DataSourceitemrect = self.DataSourceTreeWidget.visualItemRect(DataSourceMouseRightClickItem)
                DataSourceportrect = self.DataSourceTreeWidget.viewport().rect()
                if not DataSourceportrect.contains(DataSourceitemrect.topLeft()):
                    self.DataSourceTreeWidget.scrollToItem(DataSourceMouseRightClickItem, QTreeWidget.PositionAtCenter)
                    DataSourceitemrect = self.DataSourceTreeWidget.visualItemRect(DataSourceMouseRightClickItem)

                DataSourceitemrect.setLeft(DataSourceportrect.left())
                DataSourceitemrect.setWidth(DataSourceportrect.width())
                DataSourceMouseRightClickPos = self.DataSourceTreeWidget.mapToGlobal(DataSourceitemrect.center())

        if DataSourceMouseRightClickPos is not None:
            self.DataSourceTreeWidgetContextMenu(DataSourceMouseRightClickItem, DataSourceMouseRightClickPos)


    #Setting ContextMenu on Clicked Data Source
    def DataSourceTreeWidgetContextMenu(self, DataSourceWidgetItemName, DataSourceWidgetPos):
        #Parent Data Source
        if DataSourceWidgetItemName.parent() == None:
            DataSourceRightClickMenu = QMenu(self.DataSourceTreeWidget)

            DataSourceExpand = QAction('Expand', self.DataSourceTreeWidget)
            DataSourceExpand.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceWidgetItemExpandCollapse(index))

            if(DataSourceWidgetItemName.childCount() == 0 or DataSourceWidgetItemName.isExpanded() == True):
                DataSourceExpand.setDisabled(True)
            else:
                DataSourceExpand.setDisabled(False)

            DataSourceCollapse = QAction('Collapse', self.DataSourceTreeWidget)
            DataSourceCollapse.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceWidgetItemExpandCollapse(index))

            if (DataSourceWidgetItemName.childCount() == 0 or DataSourceWidgetItemName.isExpanded() == False):
                DataSourceCollapse.setDisabled(True)
            else:
                DataSourceCollapse.setDisabled(False)

            DataSourceDetail = QAction('Details', self.DataSourceTreeWidget)
            DataSourceDetail.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceWidgetItemDetail(index))

            DataSourceRightClickMenu.addAction(DataSourceExpand)
            DataSourceRightClickMenu.addAction(DataSourceCollapse)
            DataSourceRightClickMenu.addAction(DataSourceDetail)
            DataSourceRightClickMenu.popup(DataSourceWidgetPos)

        #Child DataSource
        else:
            DataSourceRightClickMenu = QMenu(self.DataSourceTreeWidget)

            DataSourcePreview = QAction('Preview', self.DataSourceTreeWidget)

            DataSourceShowWordFrequency = QAction('Show Word Frequency Table', self.DataSourceTreeWidget)

            DataSourceCreateWordCloud = QAction('Create Word Cloud', self.DataSourceTreeWidget)

            DataSourceQuery = QAction('Query', self.DataSourceTreeWidget)

            DataSourceRename = QAction('Rename', self.DataSourceTreeWidget)

            DataSourceRemove = QAction('Remove', self.DataSourceTreeWidget)

            DataSourceChildDetail = QAction('Details', self.DataSourceTreeWidget)


            DataSourceRightClickMenu.addAction(DataSourcePreview)
            DataSourceRightClickMenu.addAction(DataSourceShowWordFrequency)
            DataSourceRightClickMenu.addAction(DataSourceCreateWordCloud)
            DataSourceRightClickMenu.addAction(DataSourceQuery)
            DataSourceRightClickMenu.addAction(DataSourceRename)
            DataSourceRightClickMenu.addAction(DataSourceRemove)
            DataSourceRightClickMenu.addAction(DataSourceChildDetail)
            DataSourceRightClickMenu.popup(DataSourceWidgetPos)



    #Data Sources Expand/Collapse
    def DataSourceWidgetItemExpandCollapse(self, DataSourceWidgetItemName):
        if DataSourceWidgetItemName.isExpanded():
            DataSourceWidgetItemName.setExpanded(False)
        else:
            DataSourceWidgetItemName.setExpanded(True)

    #Parent Data Sources Details
    def DataSourceWidgetItemDetail(self, DataSourceWidgetItemName):
        DataSourceWidgetDetailDialogBox = QDialog()
        DataSourceWidgetDetailDialogBox.setModal(True)
        DataSourceWidgetDetailDialogBox.setWindowTitle("Details")
        DataSourceWidgetDetailDialogBox.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.35, self.width / 3, self.height / 3)
        DataSourceWidgetDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        groupBox1 = QGroupBox()
        vBox1 = QVBoxLayout(DataSourceWidgetDetailDialogBox)


        label = QLabel(DataSourceWidgetDetailDialogBox)
        label.setText("No of Data Sources")

        vBox1.addWidget(label)
        groupBox1.setLayout(vBox1)
        #
        # groupBox2 = QGroupBox()
        # vBox2 = QVBoxLayout(self.AboutWindowDialog)
        # textpane = QTextEdit()
        # textpane.setText("TextAs\nAnalysis Like Never Before")
        # textpane.setStyleSheet("background:transparent;")
        # textpane.setReadOnly(True)
        #
        # vBox2.addWidget(textpane)
        # groupBox2.setLayout(vBox2)
        #
        hbox1 = QHBoxLayout(DataSourceWidgetDetailDialogBox)
        hbox1.addWidget(groupBox1)
        hbox1.setContentsMargins(0,0,0,0)
        #hbox1.addWidget(groupBox2)

        DataSourceWidgetDetailDialogBox.exec()

    #Close Application / Exit
    def close_application(self):
        choice = QMessageBox.question(self, 'Quit', "Are You Sure?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    #Open New File
    def NewFileWindow(self):
        self.myDialog = QDialog()
        self.myDialog.setModal(True)
        self.myDialog.setWindowTitle("New File")
        self.myDialog.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.myDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.myDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        self.myDialog.show()

    #Open File
    def OpenFileWindow(self):
        self.dummyWindow = OpenWindow("Open File", "TextAS File *.tax")

    #Import DataSource Window
    def ImportFileWindow(self, check):
        if check == "Word":
            self.dummyWindow = OpenWindow("Open Word File", "Doc files (*.doc *.docx)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1])

                if not dummyDataSource.DataSourceLoadError:
                    File.setDataSources(myFile, dummyDataSource)
                    newNode = QTreeWidgetItem(self.wordTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")
                else:
                    dummyDataSource.__del__()

        elif check == "PDF":
            self.dummyWindow = OpenWindow("Open PDF File", "Pdf files (*.pdf)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1])

                if not dummyDataSource.DataSourceLoadError:
                    File.setDataSources(myFile, dummyDataSource)
                    if not dummyDataSource.DataSourceLoadError:
                        newNode = QTreeWidgetItem(self.pdfTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")
                        dummyDataSource.setNode(newNode)
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()


        elif check == "Txt":
            self.dummyWindow = OpenWindow("Open Notepad File", "Notepad files (*.txt)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1])

                if not dummyDataSource.DataSourceLoadError:
                    File.setDataSources(myFile, dummyDataSource)
                    newNode = QTreeWidgetItem(self.txtTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")
                else:
                    dummyDataSource.__del__()


        elif check == "RTF":
            self.dummyWindow = OpenWindow("Open Rich Text Format File", "Rich Text Format files (*.rtf)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1])

                if not dummyDataSource.DataSourceLoadError:
                    File.setDataSources(myFile, dummyDataSource)
                    newNode = QTreeWidgetItem(self.rtfTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")
                else:
                    dummyDataSource.__del__()

        elif check == "Sound":
            self.dummyWindow = OpenWindow("Open Audio File", "Audio files (*.wav *.mp3)")
            path = self.dummyWindow.filepath
            self.dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1])

                if not dummyDataSource.DataSourceLoadError:
                    File.setDataSources(myFile, dummyDataSource)
                    newNode = QTreeWidgetItem(self.audioSTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")
                else:
                    dummyDataSource.__del__()

    #Print Window
    def printWindow(self):
        printer = QPrinter(QPrinter.HighResolution)
        self.Printdialog = QPrintDialog(printer, self)
        self.Printdialog.setWindowTitle('Print')
        self.Printdialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)

        if self.Printdialog.exec_() == QPrintDialog.Accepted:
            self.textedit.print_(printer)

    #Hide ToolBar
    def toolbarHide(self):
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    #Hide Data Sources
    def DataSoureHide(self):
        if self.DataSourceLabel.isHidden() and self.DataSourceTreeWidget.isHidden():
            self.DataSourceLabel.show()
            self.DataSourceTreeWidget.show()
        else:
            self.DataSourceLabel.hide()
            self.DataSourceTreeWidget.hide()


    def AboutWindow(self):
        self.AboutWindowDialog = QDialog()
        self.AboutWindowDialog.setModal(True)
        self.AboutWindowDialog.setWindowTitle("About Us")
        self.AboutWindowDialog.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.AboutWindowDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.AboutWindowDialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)
        self.AboutWindowDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        groupBox1 = QGroupBox()
        vBox1 = QVBoxLayout(self.AboutWindowDialog)

        label = QLabel(self.AboutWindowDialog)
        label.setPixmap(QtGui.QPixmap(WindowTitleLogo).scaledToWidth(self.AboutWindowDialog.width()/2))

        vBox1.addWidget(label)
        groupBox1.setLayout(vBox1)

        groupBox2 = QGroupBox()
        vBox2 = QVBoxLayout(self.AboutWindowDialog)
        textpane = QTextEdit()
        textpane.setText("TextAs\nAnalysis Like Never Before")
        textpane.setStyleSheet("background:transparent;")
        textpane.setReadOnly(True)

        vBox2.addWidget(textpane)
        groupBox2.setLayout(vBox2)

        hbox1 = QHBoxLayout(self.AboutWindowDialog)
        hbox1.addWidget(groupBox1)
        hbox1.addWidget(groupBox2)
        self.AboutWindowDialog.setLayout(hbox1)
        self.AboutWindowDialog.show()


App = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(App.exec())