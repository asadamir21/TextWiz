import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *
from PyQt5 import QtGui, QtCore, QtPrintSupport
from matplotlib.container import StemContainer
from win32api import GetMonitorInfo, MonitorFromPoint

from PIL import  Image
from datetime import *
from File import *
import glob, sys, os, getpass, ntpath, win32gui, math, csv

#WindowTitleLogo = "Images/Logo.png"
WindowTitleLogo = "Images/DummyLogo.png"
isSaveAs = True
myFile = File()
myFile.setCreatedDate(datetime.now())
myFile.setCreatedDate(datetime.now())
myFile.setCreatedDate(getpass.getuser())

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
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        if flag == 0:
            home = os.path.join(os.path.expanduser('~'), 'Documents')

            if os.path.isdir(home):
                self.filepath =  self.getOpenFileName(self, title, home, ext)

        elif flag == 1:
            home = os.path.join(os.path.expanduser('~'), 'Pictures')

            if os.path.isdir(home):
                self.filepath = self.getSaveFileName(self, title, home, ext)

    def __del__(self):
        self.delete = True

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "TextAS"

        Monitor_Resolution_Info = GetMonitorInfo(MonitorFromPoint((0, 0)))

        self.width = Monitor_Resolution_Info.get("Work")[2]
        self.height = Monitor_Resolution_Info.get("Work")[3]

        self.left = 0;
        self.top = 0;
        self.initWindows()

    def initWindows(self):
        self.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top, self.width, self.height)
        self.setMinimumSize(self.width/2, self.height/2)
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
        ToolMenu = mainMenu.addMenu('Tools')
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

        toggleQueryButton = QAction('Show Query', self, checkable=True)
        toggleQueryButton.setChecked(True)
        toggleQueryButton.triggered.connect(self.QueryHide)
        viewMenu.addAction(toggleQueryButton)

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

        # *****************************  ToolsMenuItem ******************************************

        # Create Word Cloud Tool
        CreateWordCloudTool = QAction('Create Word Cloud', self)
        CreateWordCloudTool.setStatusTip('Create Word Cloud')
        CreateWordCloudTool.triggered.connect(lambda checked, index=None: self.DataSourceCreateCloud(index))

        # Summarize Tool
        SummarizeTool = QAction('Summarize', self)
        SummarizeTool.setStatusTip('Summarize')
        SummarizeTool.triggered.connect(lambda checked, index=None: self.DataSourceSummarize(index))

        # Find Similarity
        FindSimilarity = QAction('Find Similarity', self)
        FindSimilarity.setStatusTip('Find Similarity Between Data Sources')
        FindSimilarity.triggered.connect(lambda: self.DataSourcesSimilarity())

        # Stem Word Tool
        FindStemWordTool = QAction('Find Stem Word', self)
        FindStemWordTool.setStatusTip('Find Stem Words')
        FindStemWordTool.triggered.connect(lambda checked, index=None: self.DataSourceFindStemWords(None))

        ToolMenu.addAction(CreateWordCloudTool)
        ToolMenu.addAction(SummarizeTool)
        ToolMenu.addAction(FindStemWordTool)
        ToolMenu.addAction(FindSimilarity)


        #HelpMenu Button
        AboutButton = QAction(QtGui.QIcon('exit24.png'), 'About Us', self)
        AboutButton.setStatusTip('About Us')
        AboutButton.triggered.connect(self.AboutWindow)
        helpMenu.addAction(AboutButton)


        # ***************************Central WorkSpace***************************
        self.sizePolicy = QSizePolicy()
        self.sizePolicy.setVerticalPolicy(QSizePolicy.Minimum)
        self.sizePolicy.setHorizontalPolicy(QSizePolicy.Minimum)
        self.sizePolicy.setHeightForWidth(True)

        self.centralwidget = QWidget(self)
        self.centralwidget.setSizePolicy(self.sizePolicy)


        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setSizePolicy(self.sizePolicy)


        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # *******************************Left Pane******************************

        #DataSource Widget
        self.DataSourceLabel = QLabel()
        self.DataSourceLabel.setText("Data Sources")
        self.DataSourceLabel.setAlignment(Qt.AlignCenter)
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

        # Query Widget
        self.QueryLabel = QLabel()
        self.QueryLabel.setText("Query")
        self.QueryLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.QueryLabel)

        self.QueryTreeWidget = QTreeWidget()
        self.QueryTreeWidget.setHeaderLabel('Query')
        self.QueryTreeWidget.setAlternatingRowColors(True)
        self.QueryTreeWidget.header().setHidden(True)
        self.QueryTreeWidget.itemDoubleClicked.connect(self.QueryDoubleClickHandler)
        self.QueryTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.QueryTreeWidget.customContextMenuRequested.connect(lambda checked, index=QtGui.QContextMenuEvent: self.FindQueryTreeWidgetContextMenu(index))

        self.verticalLayout.addWidget(self.QueryTreeWidget)

        # Visualiztion Widget
        self.VisualizationLabel = QLabel()
        self.VisualizationLabel.setText("Visualization")
        self.VisualizationLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.VisualizationLabel)

        self.VisualizationTreeWidget = QTreeWidget()
        self.VisualizationTreeWidget.setHeaderLabel('Visualization')
        self.VisualizationTreeWidget.setAlternatingRowColors(True)
        self.VisualizationTreeWidget.header().setHidden(True)
        #self.VisualizationTreeWidget.itemDoubleClicked.connect(self.QueryDoubleClickHandler)
        self.VisualizationTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)


        self.verticalLayout.addWidget(self.VisualizationTreeWidget)

        # Report Widget
        self.ReportLabel = QLabel()
        self.ReportLabel.setText("Reports")
        self.ReportLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.ReportLabel)

        self.ReportTreeWidget = QTreeWidget()
        self.ReportTreeWidget.setHeaderLabel('Report')
        self.ReportTreeWidget.setAlternatingRowColors(True)
        self.ReportTreeWidget.header().setHidden(True)
        # self.VisualizationTreeWidget.itemDoubleClicked.connect(self.QueryDoubleClickHandler)
        self.ReportTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.verticalLayout.addWidget(self.ReportTreeWidget)

        # ********************************** Right Tab Widget *******************************

        # Windows Title Bar Size
        rect = win32gui.GetWindowRect(self.winId())
        clientRect = win32gui.GetClientRect(self.winId())
        windowOffset = math.floor(((rect[2] - rect[0]) - clientRect[2]) / 2)
        titleOffset = ((rect[3] - rect[1]) - clientRect[3]) - windowOffset

        self.verticalLayoutWidget.setGeometry(self.left, self.top, self.width / 8, self.height - titleOffset - self.toolbar.height())

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setSizePolicy(self.sizePolicy)

        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)


        self.tabWidget = QTabWidget(self.horizontalLayoutWidget)
        self.tabWidget.setSizePolicy(self.sizePolicy)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setElideMode(Qt.ElideRight)
        self.tabWidget.tabBar().setExpanding(True)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.tabCloseRequested.connect(self.tabCloseHandler)

        self.horizontalLayoutWidget.setGeometry(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.height - titleOffset - self.toolbar.height())

        self.horizontalLayout.addWidget(self.tabWidget)

        self.tabBoxHeight = self.tabWidget.tabBar().geometry().height()
        self.setCentralWidget(self.centralwidget)

    #Tab Close Handler
    def tabCloseHandler(self, index):
        self.tabWidget.removeTab(index)

    #Find Similarity Between Data Sources
    def DataSourcesSimilarity(self):
        DataSourceSimilarityTabFlag = False
        DataSourceSimilarityTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == len(myFile.DataSourceList) and tabs.TabName == 'Data Sources Similarity':
                if self.tabWidget.currentWidget() != tabs.tabWidget:
                    self.tabWidget.setCurrentWidget(tabs.tabWidget)
                DataSourceSimilarityTabFlag = True
                break
            elif tabs.TabName == 'Data Sources Similarity':
                DataSourceSimilarityTabFlag2 = True
                break

        if not DataSourceSimilarityTabFlag:
            # Creating New Tab for Data Sources Similarity
            DataSourcesSimilarityTab = QWidget()

            # LayoutWidget For within DataSourcesSimilarity Tab
            DataSourcesSimilarityTabVerticalLayoutWidget = QWidget(DataSourcesSimilarityTab)
            DataSourcesSimilarityTabVerticalLayoutWidget.setGeometry(0, self.tabWidget.height() / 10,
                                                                     self.tabWidget.width(),
                                                                     self.tabWidget.height() - self.tabWidget.height() / 10)

            # Box Layout for DataSourcesSimilarity Tab
            DataSourcesSimilarityTabVerticalLayout = QVBoxLayout(DataSourcesSimilarityTabVerticalLayoutWidget)
            DataSourcesSimilarityTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            DataSourcesSimilarityTable = QTableWidget(DataSourcesSimilarityTabVerticalLayoutWidget)
            DataSourcesSimilarityTable.setColumnCount(3)
            DataSourcesSimilarityTable.setGeometry(0, 0, DataSourcesSimilarityTabVerticalLayoutWidget.width(),
                                                   DataSourcesSimilarityTabVerticalLayoutWidget.height())

            DataSourcesSimilarityTable.setSizePolicy(self.sizePolicy)
            DataSourcesSimilarityTable.setWindowFlags(
                DataSourcesSimilarityTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)
            DataSourcesSimilarityTable.setHorizontalHeaderLabels(
                ["First Data Source", "Second Data Source", "Similarity Percentage (%)"])
            DataSourcesSimilarityTable.horizontalHeader().setStyleSheet(
                "::section {""background-color: grey;  color: white;}")

            for i in range(DataSourcesSimilarityTable.columnCount()):
                DataSourcesSimilarityTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
                DataSourcesSimilarityTable.horizontalHeaderItem(i).setFont(
                    QFont(DataSourcesSimilarityTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

            if len(myFile.DataSourceList) > 1:
                rowList = myFile.FindSimilarityBetweenDataSource()

                for row in rowList:
                    DataSourcesSimilarityTable.insertRow(rowList.index(row))
                    for item in row:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        DataSourcesSimilarityTable.setItem(rowList.index(row), row.index(item), intItem)
                        DataSourcesSimilarityTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        DataSourcesSimilarityTable.item(rowList.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                DataSourcesSimilarityTable.resizeColumnsToContents()
                DataSourcesSimilarityTable.resizeRowsToContents()

                DataSourcesSimilarityTable.setSortingEnabled(True)
                DataSourcesSimilarityTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                row_width = 0

                for i in range(DataSourcesSimilarityTable.columnCount()):
                    DataSourcesSimilarityTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

                if DataSourceSimilarityTabFlag2:
                    tabs.DataSourceName = len(myFile.DataSourceList)

                    if tabs.tabWidget.isHidden():
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        self.tabWidget.addTab(DataSourcesSimilarityTab, tabs.TabName)
                        self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)
                        tabs.tabWidget = DataSourcesSimilarityTab
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        self.tabWidget.addTab(DataSourcesSimilarityTab, tabs.TabName)
                        self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)
                        tabs.tabWidget = DataSourcesSimilarityTab

                else:
                    # Adding Word Cloud Tab to QTabWidget
                    myFile.TabList.append(
                        Tab("Data Sources Similarity", DataSourcesSimilarityTab, len(myFile.DataSourceList)))

                    DataSourcesSimilarityQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                    DataSourcesSimilarityQueryTreeWidget.setText(0, "Data Sources Similarity")

                    self.tabWidget.addTab(DataSourcesSimilarityTab, "Data Sources Similarity")
                    self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)

            else:
                DataSourcesSimilarityErrorBox = QMessageBox()
                DataSourcesSimilarityErrorBox.setIcon(QMessageBox.Critical)
                DataSourcesSimilarityErrorBox.setWindowTitle("Data Sources Similarity Error")
                DataSourcesSimilarityErrorBox.setText(
                    "An Error Occured! Similarity can only be found if Data Sources are more than one")
                DataSourcesSimilarityErrorBox.setStandardButtons(QMessageBox.Ok)
                DataSourcesSimilarityErrorBox.exec_()

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

            # Data Source Preview
            DataSourcePreview = QAction('Preview', self.DataSourceTreeWidget)
            DataSourcePreview.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePreview(index))
            DataSourceRightClickMenu.addAction(DataSourcePreview)

            # Data Source Frequency Table
            DataSourceShowWordFrequency = QAction('Show Word Frequency Table', self.DataSourceTreeWidget)
            DataSourceShowWordFrequency.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowFrequencyTable(index))
            DataSourceRightClickMenu.addAction(DataSourceShowWordFrequency)

            # Data Source Word Cloud
            DataSourceCreateWordCloud = QAction('Create Word Cloud', self.DataSourceTreeWidget)
            DataSourceCreateWordCloud.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceCreateCloud(index))
            DataSourceRightClickMenu.addAction(DataSourceCreateWordCloud)

            # Data Source Stem Words
            DataSourceStemWords = QAction('Find Stem Word', self.DataSourceTreeWidget)
            DataSourceStemWords.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceFindStemWords(index))
            DataSourceRightClickMenu.addAction(DataSourceStemWords)

            # Data Source Summarize
            DataSourceSummarize = QAction('Summarize', self.DataSourceTreeWidget)
            DataSourceSummarize.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceSummarize(index))
            DataSourceRightClickMenu.addAction(DataSourceSummarize)

            # Data Source Show Summary
            DataSourceSummary = QAction('Show Summary', self.DataSourceTreeWidget)
            DataSourceSummary.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceSummaryPreview(index))

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    if hasattr(DS, 'DataSourceTextSummary'):
                        DataSourceRightClickMenu.addAction(DataSourceSummary)

            # Data Source Translate
            DataSourceTranslate = QAction('Translate', self.DataSourceTreeWidget)
            DataSourceTranslate.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceTranslate(index))

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    if not hasattr(DS, 'isEnglish'):
                        DS.detect()
                    if not DS.isEnglish:
                        DataSourceRightClickMenu.addAction(DataSourceTranslate)

            # Data Source Show Translation
            DataSourceShowTranslation = QAction('Show Translation', self.DataSourceTreeWidget)
            DataSourceShowTranslation.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowTranslation(index))

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    if hasattr(DS, 'DataSourceTranslatedText'):
                        DataSourceRightClickMenu.removeAction(DataSourceTranslate)
                        DataSourceRightClickMenu.addAction(DataSourceShowTranslation)

            # Data Source Rename
            DataSourceRename = QAction('Rename', self.DataSourceTreeWidget)
            DataSourceRename.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceRename(index))
            DataSourceRightClickMenu.addAction(DataSourceRename)

            # Data Source Remove
            DataSourceRemove = QAction('Remove', self.DataSourceTreeWidget)
            DataSourceRemove.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceRemove(index))
            DataSourceRightClickMenu.addAction(DataSourceRemove)

            # Data Source Child Detail
            DataSourceChildDetail = QAction('Details', self.DataSourceTreeWidget)
            DataSourceRightClickMenu.addAction(DataSourceChildDetail)

            DataSourceRightClickMenu.popup(DataSourceWidgetPos)

    # Label Size Adjustment
    def LabelSizeAdjustment(self, label):
        exWidth = label.width()
        exHeight = label.height()
        exX = label.x()
        exY = label.y()

        label.adjustSize()
        label.setGeometry(exX + (exWidth - label.width()) / 2, exY + (exHeight - label.height()) / 2, label.width(), label.height())

    # Label Size Adjustment
    def LineEditSizeAdjustment(self, LineEdit):
        exWidth = LineEdit.width()
        exHeight = LineEdit.height()
        exX = LineEdit.x()
        exY = LineEdit.y()

        LineEdit.adjustSize()
        LineEdit.setGeometry(exX, LineEdit.y(), exWidth, LineEdit.height())

    # ***************************** Parent Context Method ************************************

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
        DataSourceWidgetDetailDialogBox.setParent(self)
        DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.4, self.height * 0.45, self.width/5, self.height/10)
        DataSourceWidgetDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        for letter in DataSourceWidgetItemName.text(0):
            if letter == '(':
                DataSourceStrTypeName = DataSourceWidgetItemName.text(0)[0: int(DataSourceWidgetItemName.text(0).index(letter))]

        DataSourceTypeLabel = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceTypeLabel.setText("Data Source Type:")
        DataSourceTypeLabel.setGeometry(DataSourceWidgetDetailDialogBox.width()*0.2, DataSourceWidgetDetailDialogBox.height()*0.2, DataSourceWidgetDetailDialogBox.width()/2, DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceTypeLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceTypeLabel)

        DataSourceTypeName = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceTypeName.setText(DataSourceStrTypeName)
        DataSourceTypeName.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.5, DataSourceWidgetDetailDialogBox.height() * 0.2, DataSourceWidgetDetailDialogBox.width()/2, DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceTypeName.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceTypeName)

        DataSourceChildLabel = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceChildLabel.setText("No. of Data Sources:")
        DataSourceChildLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.2, DataSourceWidgetDetailDialogBox.height() * 0.5, DataSourceWidgetDetailDialogBox.width()/2, DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceChildLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceChildLabel)

        DataSourceChildCountLabel = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceChildCountLabel.setText(str(DataSourceWidgetItemName.childCount()))
        DataSourceChildCountLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.5, DataSourceWidgetDetailDialogBox.height() * 0.5, DataSourceWidgetDetailDialogBox.width()/2, DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceChildCountLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceChildCountLabel)

        DataSourceWidgetDetailDialogBox.exec_()

    # ***************************** Child Context Method ************************************

    # Data Source Preview
    def DataSourcePreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Word Cloud Tab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        try:
            DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
            DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourcePreview.setReadOnly(True)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DataSourcePreview.setText(DS.DataSourcetext)
                    break

            myFile.TabList.append(Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,DataSourceWidgetItemName.text(0)))
            self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

        except Exception as e:
            print(str(e))

        # try:
        #     DataSourcePreviewTab = QWidget()
        #
        #     for DS in myFile.DataSourceList:
        #         if DS.DataSourceName == DataSourceWidgetItemName.text(0):
        #             PDFWeb = QWebView(DataSourcePreviewTab)
        #             PDFWeb.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        #             PDFWeb.show()
        #             break
        #
        #
        #     myFile.TabList.append(Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))
        #     self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
        #     self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
        #
        # except Exception as e:
        #     print(str(e))

    # Data Source Show Frequency Table
    def DataSourceShowFrequencyTable(self, DataSourceWidgetItemName):
        DataSourceShowFrequencyTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Word Frequency':
                DataSourceShowFrequencyTabFlag = True
                break

        WordFrequencyTab = QWidget()
        WordFrequencyTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()))
        WordFrequencyTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Stem Word Tab
        WordFrequencyTabVerticalLayoutWidget2 = QWidget(WordFrequencyTab)
        WordFrequencyTabVerticalLayoutWidget2.setGeometry(self.tabWidget.width() / 4, 0, self.tabWidget.width() / 2,
                                                          self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        WordFrequencyTabVerticalLayout2 = QHBoxLayout(WordFrequencyTabVerticalLayoutWidget2)
        WordFrequencyTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

        # filter proxy model
        WordFrequencyTableModel = QSortFilterProxyModel()
        # WordFrequencyTableModel.setSourceModel(model)
        WordFrequencyTableModel.setFilterKeyColumn(0)  # First column

        # line edit for filtering
        WordFrequencyTabSearchLineEdit = QLineEdit()
        WordFrequencyTabSearchLineEdit.textChanged.connect(WordFrequencyTableModel.setFilterRegExp)
        WordFrequencyTabVerticalLayout2.addWidget(WordFrequencyTabSearchLineEdit)

        # Download Button For Frequency Table
        DownloadAsCSVButton = QPushButton('Download')
        DownloadAsCSVButton.setIcon(QIcon("Images/Download Button.png"))
        DownloadAsCSVButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

        DownloadAsCSVButtonFont = QFont("sans-serif")
        DownloadAsCSVButtonFont.setPixelSize(14)
        DownloadAsCSVButtonFont.setBold(True)

        DownloadAsCSVButton.setFont(DownloadAsCSVButtonFont)

        WordFrequencyTabVerticalLayout2.addWidget(DownloadAsCSVButton)

        # LayoutWidget For within Word Frequency Tab
        WordFrequencyTabverticalLayoutWidget = QWidget(WordFrequencyTab)
        WordFrequencyTabverticalLayoutWidget.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                         self.tabWidget.height() - self.tabWidget.height() / 10)
        WordFrequencyTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        WordFrequencyverticalLayout = QVBoxLayout(WordFrequencyTabverticalLayoutWidget)
        WordFrequencyverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        WordFrequencyTable = QTableWidget(WordFrequencyTabverticalLayoutWidget)
        WordFrequencyTable.setColumnCount(4)
        # WordFrequencyTable.setModel(WordFrequencyTableModel)
        WordFrequencyTable.setGeometry(0, 0, WordFrequencyTabverticalLayoutWidget.width(),
                                       WordFrequencyTabverticalLayoutWidget.height())

        WordFrequencyTable.setSizePolicy(self.sizePolicy)

        WordFrequencyTable.setWindowFlags(WordFrequencyTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        WordFrequencyTable.setHorizontalHeaderLabels(["Word", "Length", "Frequency", "Weighted Percentage"])
        WordFrequencyTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(WordFrequencyTable.columnCount()):
            WordFrequencyTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            WordFrequencyTable.horizontalHeaderItem(i).setFont(
                QFont(WordFrequencyTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                rowList = dummyQuery.FindWordFrequency(DS.DataSourcetext)
                break

        DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(WordFrequencyTable))

        if len(rowList) != 0:
            for row in rowList:
                WordFrequencyTable.insertRow(rowList.index(row))
                for item in row:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    WordFrequencyTable.setItem(rowList.index(row), row.index(item), intItem)
                    WordFrequencyTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    WordFrequencyTable.item(rowList.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            WordFrequencyTable.resizeColumnsToContents()
            WordFrequencyTable.resizeRowsToContents()

            WordFrequencyTable.setSortingEnabled(True)
            WordFrequencyTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(WordFrequencyTable.columnCount()):
                WordFrequencyTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if DataSourceShowFrequencyTabFlag:
                # change tab in query
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                        for query in DS.QueryList:
                            if query[1] == tabs.tabWidget:
                                query[1] = WordFrequencyTab
                                break

                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(WordFrequencyTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(WordFrequencyTab)
                tabs.tabWidget = WordFrequencyTab
            else:
                # Adding Word Frequency Tab to TabList
                myFile.TabList.append(Tab("Word Frequency", WordFrequencyTab, DataSourceWidgetItemName.text(0)))

                # Adding Word Frequency Query
                WordFreqencyQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                WordFreqencyQueryTreeWidget.setText(0, "Word Frequency (" + DataSourceWidgetItemName.text(0) + ")")

                # Adding Word Frequency Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                        DS.setQuery(WordFreqencyQueryTreeWidget, WordFrequencyTab)

                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(WordFrequencyTab, "Word Frequency")
                self.tabWidget.setCurrentWidget(WordFrequencyTab)

        else:

            WordFrequencyErrorBox = QMessageBox()
            WordFrequencyErrorBox.setIcon(QMessageBox.Critical)
            WordFrequencyErrorBox.setWindowTitle("Word Frequency Error")
            WordFrequencyErrorBox.setText("An Error Occurred! No Text Found in " + DataSourceWidgetItemName.text(0))
            WordFrequencyErrorBox.setStandardButtons(QMessageBox.Ok)
            WordFrequencyErrorBox.exec_()

    # Save Table as CSV
    def SaveTableAsCSV(self, Table):
        try:
            path = QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')

            if all(path):
                with open(path[0], 'wb') as stream:
                    writer = csv.writer(stream)
                    for row in range(Table.rowCount()):
                        rowdata = []
                        for column in range(Table.columnCount()):
                            item = Table.item(row, column)
                            if item is not None:
                                rowdata.append(item.text().encode('utf8'))
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)

        except Exception as e:
            print(str(e))

    # Data Source Create World Cloud
    def DataSourceCreateCloud(self, DataSourceWidgetItemName):
        CreateWordCloudDialog = QDialog()
        CreateWordCloudDialog.setWindowTitle("Create Word Cloud")
        CreateWordCloudDialog.setGeometry(self.width * 0.35, self.height*0.35, self.width/3, self.height/3)
        CreateWordCloudDialog.setParent(self)
        CreateWordCloudDialog.setAttribute(Qt.WA_DeleteOnClose)
        CreateWordCloudDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        CreateWordCloudDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        WordCloudDSLabel = QLabel(CreateWordCloudDialog)
        WordCloudDSLabel.setGeometry(CreateWordCloudDialog.width() * 0.2, CreateWordCloudDialog.height()*0.1, CreateWordCloudDialog.width()/5, CreateWordCloudDialog.height()/15)
        WordCloudDSLabel.setText("Data Source")
        self.LabelSizeAdjustment(WordCloudDSLabel)

        WordCloudBackgroundLabel = QLabel(CreateWordCloudDialog)
        WordCloudBackgroundLabel.setGeometry(CreateWordCloudDialog.width() * 0.2, CreateWordCloudDialog.height()*0.25, CreateWordCloudDialog.width()/5, CreateWordCloudDialog.height()/15)
        WordCloudBackgroundLabel.setText("Background Color")
        self.LabelSizeAdjustment(WordCloudBackgroundLabel)

        WordCloudMaxWordLabel = QLabel(CreateWordCloudDialog)
        WordCloudMaxWordLabel.setGeometry(CreateWordCloudDialog.width() * 0.2, CreateWordCloudDialog.height()*0.4, CreateWordCloudDialog.width()/5, CreateWordCloudDialog.height()/15)
        WordCloudMaxWordLabel.setText("Max Words")
        self.LabelSizeAdjustment(WordCloudMaxWordLabel)

        WordCloudMaskLabel = QLabel(CreateWordCloudDialog)
        WordCloudMaskLabel.setGeometry(CreateWordCloudDialog.width() * 0.2, CreateWordCloudDialog.height()*0.55, CreateWordCloudDialog.width()/5, CreateWordCloudDialog.height()/15)
        WordCloudMaskLabel.setText("Mask")
        self.LabelSizeAdjustment(WordCloudMaskLabel)

        WordCloudDSComboBox = QComboBox(CreateWordCloudDialog)
        WordCloudDSComboBox.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.1, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)

        if DataSourceWidgetItemName is None:
            for DS in myFile.DataSourceList:
                WordCloudDSComboBox.addItem(DS.DataSourceName)
        else:
            WordCloudDSComboBox.addItem(DataSourceWidgetItemName.text(0))
            WordCloudDSComboBox.setDisabled(True)

        self.LineEditSizeAdjustment(WordCloudDSComboBox)

        WordCloudBackgroundColor = QComboBox(CreateWordCloudDialog)
        WordCloudBackgroundColor.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.25, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)
        WordCloudBackgroundColor.setLayoutDirection(QtCore.Qt.LeftToRight)

        for BGColor in myFile.WordCloudBackgroundList:
            WordCloudBackgroundColor.addItem(BGColor)

        self.LineEditSizeAdjustment(WordCloudBackgroundColor)

        WordCloudMaxWords = QDoubleSpinBox(CreateWordCloudDialog)
        WordCloudMaxWords.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.4, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)
        WordCloudMaxWords.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        WordCloudMaxWords.setDecimals(0)
        WordCloudMaxWords.setMinimum(10.0)
        WordCloudMaxWords.setMaximum(200.0)

        self.LineEditSizeAdjustment(WordCloudMaxWords)

        WordCloudMask = QComboBox(CreateWordCloudDialog)
        WordCloudMask.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.55, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)

        for Imagefilename in glob.glob('Word Cloud Maskes/*.png'):  # assuming gif
            WordCloudMask.addItem(os.path.splitext(ntpath.basename(Imagefilename))[0])

        self.LineEditSizeAdjustment(WordCloudMask)

        CreateWorldCloudbuttonBox = QDialogButtonBox(CreateWordCloudDialog)
        CreateWorldCloudbuttonBox.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.8, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)
        CreateWorldCloudbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        CreateWorldCloudbuttonBox.button(QDialogButtonBox.Ok).setText('Create')
        self.LineEditSizeAdjustment(CreateWorldCloudbuttonBox)

        if len(WordCloudDSComboBox.currentText()) == 0:
            CreateWorldCloudbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            CreateWorldCloudbuttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

        WordCloudDSComboBox.currentTextChanged.connect(lambda: self.OkButtonEnableCombo(WordCloudDSComboBox, CreateWorldCloudbuttonBox))

        CreateWorldCloudbuttonBox.accepted.connect(CreateWordCloudDialog.accept)
        CreateWorldCloudbuttonBox.rejected.connect(CreateWordCloudDialog.reject)

        CreateWorldCloudbuttonBox.accepted.connect(lambda : self.mapWordCloudonTab(str(WordCloudDSComboBox.currentText()), str(WordCloudBackgroundColor.currentText()), WordCloudMaxWords.value() ,str(WordCloudMask.currentText())))

        CreateWordCloudDialog.exec_()

    #map WordCloud on Tab
    def mapWordCloudonTab(self, WCDSName, WCBGColor, maxword, maskname):
        DataSourceWordCloudTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == WCDSName and tabs.TabName == 'Word Cloud':
                DataSourceWordCloudTabFlag = True
                break

        WordCloudImage = myFile.CreateWordCloud(WCDSName, WCBGColor, maxword, maskname)

        # Creating New Tab for WordCloud
        WordCloudTab = QWidget()

        # LayoutWidget For within Word Cloud Tab
        WordCloudTabverticalLayoutWidget = QWidget(WordCloudTab)
        WordCloudTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Word Cloud Tab
        WordCloudverticalLayout = QVBoxLayout(WordCloudTabverticalLayoutWidget)
        WordCloudverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Label for Word Cloud Image
        WordCloudLabel = QLabel(WordCloudTabverticalLayoutWidget)

        # Resizing label to Layout
        WordCloudLabel.resize(WordCloudTabverticalLayoutWidget.width(), WordCloudTabverticalLayoutWidget.height())

        # Converting WordCloud Image to Pixmap
        WordCloudPixmap = WordCloudImage.toqpixmap()

        # Scaling Pixmap image
        dummypixmap = WordCloudPixmap.scaled(WordCloudTabverticalLayoutWidget.width(),
                                             WordCloudTabverticalLayoutWidget.height(), Qt.KeepAspectRatio)
        WordCloudLabel.setPixmap(dummypixmap)
        WordCloudLabel.setGeometry((WordCloudTabverticalLayoutWidget.width() - dummypixmap.width()) / 2,
                                   (WordCloudTabverticalLayoutWidget.height() - dummypixmap.height()) / 2,
                                   dummypixmap.width(), dummypixmap.height())

        # Setting ContextMenu Policies on Label
        WordCloudLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        WordCloudLabel.customContextMenuRequested.connect(
            lambda index=QContextMenuEvent, index2=dummypixmap, index3=WordCloudLabel: self.WordCloudContextMenu(index,
                                                                                                                 index2,
                                                                                                                 index3))
        if DataSourceWordCloudTabFlag:
            # change tab in query
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == WCDSName:
                    for query in DS.QueryList:
                        if query[1] == tabs.tabWidget:
                            query[1] = WordCloudTab
                            break

            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(WordCloudTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(WordCloudTab)
            tabs.tabWidget = WordCloudTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Word Cloud", WordCloudTab, WCDSName))

            WordCloudQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
            WordCloudQueryTreeWidget.setText(0, "Word Cloud (" + WCDSName + ")")

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == WCDSName:
                    DS.setQuery(WordCloudQueryTreeWidget, WordCloudTab)

            self.tabWidget.addTab(WordCloudTab, "Word Cloud")
            self.tabWidget.setCurrentWidget(WordCloudTab)

    #Word Cloud ContextMenu
    def WordCloudContextMenu(self, WordCloudClickEvent, dummypixmap, WordCloudLabel):
        WordCloudClickMenu = QMenu()

        WordCloudImageDownload = QAction('Download Image')
        WordCloudImageDownload.triggered.connect(lambda: self.WordCloudDownload(dummypixmap))
        WordCloudClickMenu.addAction(WordCloudImageDownload)

        WordCloudClickMenu.exec(WordCloudClickEvent)

    #WordCloud Download
    def WordCloudDownload(self, dummypixmap):
        dummyWindow = OpenWindow("Save Word Cloud", ".png", 1)
        path = dummyWindow.filepath

        if all(path):
            dummypixmap.save(path[0] + ".png", "PNG")

    # Data Source Rename
    def DataSourceRename(self, DataSourceWidgetItemName):
        DataSourceRename = QDialog()
        DataSourceRename.setWindowTitle("Rename")
        DataSourceRename.setGeometry(self.width * 0.375, self.height * 0.425, self.width/4, self.height*0.15)
        DataSourceRename.setParent(self)
        DataSourceRename.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourceRename.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        RenameLabel = QLabel(DataSourceRename)
        RenameLabel.setGeometry(DataSourceRename.width()*0.125, DataSourceRename.height()*0.3, DataSourceRename.width()/4, DataSourceRename.height()*0.15)
        RenameLabel.setText("Rename")
        RenameLabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(RenameLabel)

        RenameLineEdit = QLineEdit(DataSourceRename)
        RenameLineEdit.setGeometry(DataSourceRename.width()*0.4, DataSourceRename.height()*0.3, DataSourceRename.width()/2, DataSourceRename.height()*0.15)
        RenameLineEdit.setText(DataSourceWidgetItemName.text(0))
        self.LineEditSizeAdjustment(RenameLineEdit)

        RenamebuttonBox = QDialogButtonBox(DataSourceRename)
        RenamebuttonBox.setGeometry(DataSourceRename.width()*0.125, DataSourceRename.height()*0.7, DataSourceRename.width()*3/4, DataSourceRename.height()/5)
        RenamebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        RenamebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        RenameLineEdit.textChanged.connect(lambda: self.OkButtonEnable(RenameLineEdit, RenamebuttonBox))

        RenamebuttonBox.accepted.connect(DataSourceRename.accept)
        RenamebuttonBox.rejected.connect(DataSourceRename.reject)

        RenamebuttonBox.accepted.connect(lambda: DataSourceWidgetItemName.setText(0, RenameLineEdit.text()))

        DataSourceRename.exec()

    # Data Source Create Query
    def DataSourceFindStemWords(self, DataSourceWidgetItemName):
        DataSourceStemWord = QDialog()
        DataSourceStemWord.setWindowTitle("Find Stem Words")
        DataSourceStemWord.setGeometry(self.width * 0.375, self.height * 0.4, self.width / 4, self.height / 5)
        DataSourceStemWord.setParent(self)
        DataSourceStemWord.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourceStemWord.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        WordStemDSlabel = QLabel(DataSourceStemWord)
        WordStemDSlabel.setGeometry(DataSourceStemWord.width() * 0.125, DataSourceStemWord.height() * 0.2,
                                    DataSourceStemWord.width() / 4, DataSourceStemWord.height() * 0.1)

        WordStemDSlabel.setText("Data Source")
        WordStemDSlabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(WordStemDSlabel)

        # Word Label
        WordStemlabel = QLabel(DataSourceStemWord)
        WordStemlabel.setGeometry(DataSourceStemWord.width() * 0.125, DataSourceStemWord.height() * 0.45,
                                  DataSourceStemWord.width() / 4, DataSourceStemWord.height() * 0.1)
        WordStemlabel.setText("Word")
        WordStemlabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(WordStemlabel)

        # Data Source ComboBox
        StemWordDSComboBox = QComboBox(DataSourceStemWord)
        StemWordDSComboBox.setGeometry(DataSourceStemWord.width() * 0.4, DataSourceStemWord.height() * 0.2,
                                       DataSourceStemWord.width() / 2, DataSourceStemWord.height() / 10)

        if DataSourceWidgetItemName is None:
            for DS in myFile.DataSourceList:
                StemWordDSComboBox.addItem(DS.DataSourceName)
        else:
            StemWordDSComboBox.addItem(DataSourceWidgetItemName.text(0))
            StemWordDSComboBox.setDisabled(True)

        self.LineEditSizeAdjustment(StemWordDSComboBox)

        # Stem Word Line Edit
        StemWordLineEdit = QLineEdit(DataSourceStemWord)
        StemWordLineEdit.setGeometry(DataSourceStemWord.width() * 0.4, DataSourceStemWord.height() * 0.45,
                                     DataSourceStemWord.width() / 2, DataSourceStemWord.height() * 0.1)
        StemWordCompleter = QCompleter()
        StemWordLineEdit.setCompleter(StemWordCompleter)
        StemWordModel = QStringListModel()
        StemWordCompleter.setModel(StemWordModel)
        self.LineEditSizeAdjustment(StemWordLineEdit)

        # Stem Word Button Box
        StemWordbuttonBox = QDialogButtonBox(DataSourceStemWord)
        StemWordbuttonBox.setGeometry(DataSourceStemWord.width() * 0.125, DataSourceStemWord.height() * 0.7,
                                      DataSourceStemWord.width() * 3 / 4, DataSourceStemWord.height() / 5)
        StemWordbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        StemWordbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(StemWordbuttonBox)

        StemWordLineEdit.textChanged.connect(
            lambda: self.WordSuggestion(StemWordModel, StemWordLineEdit.text(), StemWordDSComboBox.currentText()))
        StemWordLineEdit.textChanged.connect(lambda: self.OkButtonEnable(StemWordLineEdit, StemWordbuttonBox, True))

        StemWordDSComboBox.currentTextChanged.connect(StemWordLineEdit.clear)

        StemWordbuttonBox.accepted.connect(DataSourceStemWord.accept)
        StemWordbuttonBox.rejected.connect(DataSourceStemWord.reject)

        StemWordbuttonBox.accepted.connect(
            lambda: self.mapStemWordonTab(StemWordLineEdit.text(), StemWordDSComboBox.currentText()))

        DataSourceStemWord.exec()

    # Show StemWords on Tab
    def mapStemWordonTab(self, word, DataSourceItemWidget):
        try:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceItemWidget:
                    dummyText = DS.DataSourcetext
                    break

            # Creating New Tab for Stem Word
            StemWordTab = QWidget()

            # LayoutWidget For within Stem Word Tab
            StemWordTabVerticalLayoutWidget = QWidget(StemWordTab)
            StemWordTabVerticalLayoutWidget.setGeometry(self.tabWidget.width() / 4, 0, self.tabWidget.width() / 2,
                                                        self.tabWidget.height() / 10)

            # Box Layout for Stem Word Tab
            StemWordTabVerticalLayout = QHBoxLayout(StemWordTabVerticalLayoutWidget)
            StemWordTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # StemWord Text Edit
            StemWordLineEdit = QLineEdit(StemWordTabVerticalLayoutWidget)
            StemWordLineEdit.setGeometry(StemWordTabVerticalLayoutWidget.width() * 0.25,
                                         StemWordTabVerticalLayoutWidget.height() * 0.375,
                                         StemWordTabVerticalLayoutWidget.width() / 4,
                                         StemWordTabVerticalLayoutWidget.height() / 4)
            StemWordCompleter = QCompleter()
            StemWordLineEdit.setCompleter(StemWordCompleter)
            StemWordModel = QStringListModel()
            StemWordCompleter.setModel(StemWordModel)

            StemWordLineEdit.textChanged.connect(
                lambda: self.WordSuggestion(StemWordModel, StemWordLineEdit.text(), DataSourceItemWidget))

            # StemWord Submit Button
            StemWordSubmitButton = QPushButton(StemWordTabVerticalLayoutWidget)
            StemWordSubmitButton.setGeometry(StemWordTabVerticalLayoutWidget.width() * 0.55,
                                             StemWordTabVerticalLayoutWidget.height() * 0.375,
                                             StemWordTabVerticalLayoutWidget.width() / 4,
                                             StemWordTabVerticalLayoutWidget.height() / 4)
            StemWordSubmitButton.setText("Find Stem Words")
            StemWordSubmitButton.setEnabled(False)

            StemWordLineEdit.textChanged.connect(lambda: self.OkButtonEnable(StemWordLineEdit, StemWordSubmitButton, False))

            # 2nd LayoutWidget For within Stem Word Tab
            StemWordTabVerticalLayoutWidget2 = QWidget(StemWordTab)
            StemWordTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                         self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Stem Word Tab
            StemWordTabVerticalLayout2 = QVBoxLayout(StemWordTabVerticalLayoutWidget2)
            StemWordTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

            StemWordTable = QTableWidget(StemWordTabVerticalLayoutWidget2)
            StemWordTable.setColumnCount(2)
            StemWordTable.setGeometry(0, 0, StemWordTabVerticalLayoutWidget2.width(),
                                      StemWordTabVerticalLayoutWidget2.height())

            StemWordTable.setSizePolicy(self.sizePolicy)
            StemWordTable.setWindowFlags(StemWordTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)
            StemWordTable.setHorizontalHeaderLabels(["Word", "Frequency"])
            StemWordTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

            for i in range(StemWordTable.columnCount()):
                StemWordTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
                StemWordTable.horizontalHeaderItem(i).setFont(
                    QFont(StemWordTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

            StemWordSubmitButton.clicked.connect(
                lambda: self.StemWordWithinTab(StemWordLineEdit.text(), DataSourceItemWidget, StemWordTable))

            dummyQuery = Query()

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceItemWidget:
                    rowList = dummyQuery.FindStemmedWords(word, DS.DataSourcetext)
                    break

            if len(rowList) != 0:
                for row in rowList:
                    StemWordTable.insertRow(rowList.index(row))
                    for item in row:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        StemWordTable.setItem(rowList.index(row), row.index(item), intItem)
                        StemWordTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        StemWordTable.item(rowList.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                StemWordTable.resizeColumnsToContents()
                StemWordTable.resizeRowsToContents()

                StemWordTable.setSortingEnabled(True)
                StemWordTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                row_width = 0

                for i in range(StemWordTable.columnCount()):
                    StemWordTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

                # Adding Word Cloud Tab to QTabWidget
                myFile.TabList.append(Tab("Stem Word", StemWordTab, DataSourceItemWidget))

                StemWordQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                StemWordQueryTreeWidget.setText(0, "Stem Word (" + DataSourceItemWidget + ")")

                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceItemWidget:
                        DS.setQuery(StemWordQueryTreeWidget, StemWordTab)

                self.tabWidget.addTab(StemWordTab, "Stem Word")
                self.tabWidget.setCurrentWidget(StemWordTab)

            else:
                StemWordErrorBox = QMessageBox()
                StemWordErrorBox.setIcon(QMessageBox.Critical)
                StemWordErrorBox.setWindowTitle("Stem Word Error")
                StemWordErrorBox.setText("An Error Occurred! No Stem Word Found of the Word \"" + word + "\"")
                StemWordErrorBox.setStandardButtons(QMessageBox.Ok)
                StemWordErrorBox.exec_()

        except Exception as e:
            print(str(e))

    #Word Suggestion
    def WordSuggestion(self, StemWordModel, CurrentText, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                dummyQuery = Query()
                WordList = dummyQuery.GetDistinctWords(DS.DataSourcetext)
                matching = [s for s in WordList if CurrentText in s]
                StemWordModel.setStringList(matching)

    # Enable Ok Button (Line Edit)
    def OkButtonEnable(self, LineEdit, ButtonBox, check):
        if check:
            if len(LineEdit.text()) > 0:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            if len(LineEdit.text()) > 0:
                ButtonBox.setEnabled(True)
            else:

                ButtonBox.setEnabled(False)

    # Enable Ok Button (Combo Box)
    def OkButtonEnableCombo(self, ComboBox, ButtonBox):
        if len(ComboBox.currentText()) == 0:
            ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    #Get Stem Word From Column
    def StemWordWithinTab(self, word, DataSourceItemWidget, StemWordTable):
        while StemWordTable.rowCount() > 0:
            StemWordTable.removeRow(0)

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceItemWidget:
                rowList = dummyQuery.FindStemmedWords(word, DS.DataSourcetext)
                break

        if len(rowList) != 0:
            for row in rowList:
                StemWordTable.insertRow(rowList.index(row))
                for item in row:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    StemWordTable.setItem(rowList.index(row), row.index(item), intItem)
                    StemWordTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    StemWordTable.item(rowList.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            StemWordTable.resizeColumnsToContents()
            StemWordTable.resizeRowsToContents()
            StemWordTable.setSortingEnabled(True)
            StemWordTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

            for i in range(StemWordTable.columnCount()):
                StemWordTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        else:
            StemWordErrorBox = QMessageBox()
            StemWordErrorBox.setIcon(QMessageBox.Critical)
            StemWordErrorBox.setWindowTitle("Stem Word Error")
            StemWordErrorBox.setText("An Error Occurred! No Stem Word Found of the Word \"" + word + "\"")
            StemWordErrorBox.setStandardButtons(QMessageBox.Ok)
            StemWordErrorBox.exec_()

    # Data Source Summary
    def DataSourceSummarize(self, DataSourceWidgetItemName):
        # Summarization Dialog Box
        SummarizeDialog = QDialog()
        SummarizeDialog.setWindowTitle("Summarize")
        SummarizeDialog.setGeometry(self.width * 0.35, self.height * 0.35, self.width / 3, self.height / 3)
        SummarizeDialog.setParent(self)
        SummarizeDialog.setAttribute(Qt.WA_DeleteOnClose)
        SummarizeDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        SummarizeDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Summarization Data Source Label
        SummarizeDSLabel = QLabel(SummarizeDialog)
        SummarizeDSLabel.setGeometry(SummarizeDialog.width() * 0.2, SummarizeDialog.height() * 0.1,
                                     SummarizeDialog.width() / 5, SummarizeDialog.height() / 15)
        SummarizeDSLabel.setText("Data Source")
        self.LabelSizeAdjustment(SummarizeDSLabel)

        # Summarization Default Radio Button
        DefaultRadioButton = QRadioButton(SummarizeDialog)
        DefaultRadioButton.setGeometry(SummarizeDialog.width() * 0.2, SummarizeDialog.height() * 0.25,
                                       SummarizeDialog.width() / 5, SummarizeDialog.height() / 15)
        DefaultRadioButton.setText("Default")

        # Summarization Total Word Count Radio Button
        TotalWordCountRadioButton = QRadioButton(SummarizeDialog)
        TotalWordCountRadioButton.setGeometry(SummarizeDialog.width() * 0.2, SummarizeDialog.height() * 0.4,
                                              SummarizeDialog.width() / 5, SummarizeDialog.height() / 15)
        TotalWordCountRadioButton.setText("Word Count")
        TotalWordCountRadioButton.adjustSize()

        # Summarization Ratio Radio Button
        RatioRadioButton = QRadioButton(SummarizeDialog)
        RatioRadioButton.setGeometry(SummarizeDialog.width() * 0.2, SummarizeDialog.height() * 0.65,
                                     SummarizeDialog.width() / 5, SummarizeDialog.height() / 15)
        RatioRadioButton.setText("Ratio")
        RatioRadioButton.adjustSize()

        # Summarization Data Source ComboBox
        SummarizeDSComboBox = QComboBox(SummarizeDialog)
        SummarizeDSComboBox.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.1,
                                        SummarizeDialog.width() / 3, SummarizeDialog.height() / 15)

        if DataSourceWidgetItemName is None:
            for DS in myFile.DataSourceList:
                SummarizeDSComboBox.addItem(DS.DataSourceName)
        else:
            SummarizeDSComboBox.addItem(DataSourceWidgetItemName.text(0))
            SummarizeDSComboBox.setDisabled(True)
        self.LineEditSizeAdjustment(SummarizeDSComboBox)


        # Summarize Word QSpinBox
        SummarizeWord = QDoubleSpinBox(SummarizeDialog)
        SummarizeWord.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.4,
                                  SummarizeDialog.width() / 3, SummarizeDialog.height() / 15)
        SummarizeWord.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        SummarizeWord.setDecimals(0)
        SummarizeWord.setEnabled(False)
        self.LineEditSizeAdjustment(SummarizeWord)


        # Max Word Label
        SummarizeMaxWord = QLabel(SummarizeDialog)
        SummarizeMaxWord.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.5,
                                     SummarizeDialog.width() / 3, SummarizeDialog.height() / 15)
        SummarizeMaxWord.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        MaxWordFont = QFont()
        MaxWordFont.setPixelSize(9)
        SummarizeMaxWord.setFont(MaxWordFont)
        self.LabelSizeAdjustment(SummarizeMaxWord)

        if SummarizeDSComboBox.currentText() != None:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == SummarizeDSComboBox.currentText():
                    SummarizeWord.setMaximum(len(DS.DataSourcetext.split()))
                    SummarizeWord.setMinimum(round(len(DS.DataSourcetext.split()) / 5))
                    SummarizeWord.setValue(SummarizeWord.minimum())
                    SummarizeMaxWord.setText("(Max. Words: " + str(len(DS.DataSourcetext.split())) + ")")
                    break

        TotalWordCountRadioButton.toggled.connect(lambda: self.RadioButtonTrigger(SummarizeWord))

        # SummarizeRatio
        SummarizeRatio = QDoubleSpinBox(SummarizeDialog)
        SummarizeRatio.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.65,
                                   SummarizeDialog.width() / 3, SummarizeDialog.height() / 15)
        SummarizeRatio.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        SummarizeRatio.setEnabled(False)
        SummarizeRatio.setDecimals(2)
        SummarizeRatio.setSingleStep(0.01)
        SummarizeRatio.setMinimum(.20)
        SummarizeRatio.setMaximum(1.00)
        self.LineEditSizeAdjustment(SummarizeRatio)

        RatioRadioButton.toggled.connect(lambda: self.RadioButtonTrigger(SummarizeRatio))

        SummarizeDSComboBox.currentTextChanged.connect(lambda: self.ComboBoxTextChange(SummarizeWord, SummarizeMaxWord))

        SummarizebuttonBox = QDialogButtonBox(SummarizeDialog)
        SummarizebuttonBox.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.8,
                                       SummarizeDialog.width() / 3, SummarizeDialog.height() / 5)
        SummarizebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        SummarizebuttonBox.button(QDialogButtonBox.Ok).setText('Summarize')
        SummarizebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(SummarizebuttonBox)

        SummarizeDSComboBox.currentTextChanged.connect(lambda: self.OkButtonEnableCombo(SummarizeDSComboBox, SummarizebuttonBox))

        DefaultRadioButton.toggled.connect(lambda: self.EnableOkonRadioButtonToggle(TotalWordCountRadioButton, RatioRadioButton, SummarizebuttonBox, SummarizeDSComboBox))
        TotalWordCountRadioButton.toggled.connect(lambda: self.EnableOkonRadioButtonToggle(DefaultRadioButton, RatioRadioButton, SummarizebuttonBox, SummarizeDSComboBox))
        RatioRadioButton.toggled.connect(lambda: self.EnableOkonRadioButtonToggle(DefaultRadioButton, TotalWordCountRadioButton, SummarizebuttonBox, SummarizeDSComboBox))

        SummarizebuttonBox.accepted.connect(SummarizeDialog.accept)
        SummarizebuttonBox.rejected.connect(SummarizeDialog.reject)

        # if Selected using Context Menu
        if DataSourceWidgetItemName is not None:
            SummarizebuttonBox.accepted.connect(
                lambda: self.DSSummarizeFromDialog(DataSourceWidgetItemName, SummarizeDSComboBox.currentText(), DefaultRadioButton.isChecked(),
                                                   TotalWordCountRadioButton.isChecked(), RatioRadioButton.isChecked(),
                                                   SummarizeWord.value(), SummarizeRatio.value()))

        # if Selected using Toolbar
        else:
            SummarizebuttonBox.accepted.connect(
                lambda: self.DSSummarizeFromDialog(None, SummarizeDSComboBox.currentText(), DefaultRadioButton.isChecked(),
                                                   TotalWordCountRadioButton.isChecked(), RatioRadioButton.isChecked(),
                                                   SummarizeWord.value(), SummarizeRatio.value()))

        SummarizeDialog.exec()

    # Data Source Translate
    def DataSourceTranslate(self, DataSourceWidgetItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                DS.translate()
                break

    # Data Source Show Translation
    def DataSourceShowTranslation(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Word Cloud Tab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        try:
            DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
            DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourcePreview.setReadOnly(True)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DataSourcePreview.setText(str(DS.DataSourceTranslatedText))
                    break

            myFile.TabList.append(
                Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,
                    DataSourceWidgetItemName.text(0)))
            self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

        except Exception as e:
            print(str(e))

    # Radio Button Toggle
    def RadioButtonTrigger(self, Widget):
        RadioButton = self.sender()

        if RadioButton.isChecked():
            Widget.setEnabled(True)
        else:
            Widget.setEnabled(False)

    # Combo Box Text Change
    def ComboBoxTextChange(self, SummarizeWord, SummarizeMaxWord):
        ComboBox = self.sender()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == ComboBox.currentText():
                SummarizeWord.setMaximum(len(DS.DataSourcetext.split()))
                SummarizeMaxWord.setText("Max. Words: " + str(len(DS.DataSourcetext.split())))
                SummarizeWord.setMinimum(round(len(DS.DataSourcetext.split()) / 5))
                SummarizeWord.setValue(SummarizeWord.minimum())

    # Ok Button Enable on Radio Button Toggling
    def EnableOkonRadioButtonToggle(self, SecondButton, ThirdButton, ButtonBox, ComboBox):
        if len(ComboBox.currentText()) != 0:
            Button = self.sender()
            if(not Button.isChecked() and not SecondButton.isChecked() and not ThirdButton.isChecked()):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    # Data Source Summarize
    def DSSummarizeFromDialog(self, DataSourceWidgetItemName, DSName, DefaultRadioButton, TotalWordCountRadioButton, RatioRadioButton, SummarizeWord, SummarizeRatio):
        # if Selected using Context Menu
        if DataSourceWidgetItemName is not None:
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    if DefaultRadioButton:
                        DS.Summarize(True, None, None)
                    elif TotalWordCountRadioButton:
                        DS.Summarize(False, "Total Word Count", SummarizeWord)
                    elif RatioRadioButton:
                        DS.Summarize(False, "Ratio", SummarizeRatio)
                    break

        # if Selected using Toolbar
        else:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DSName:
                    if DefaultRadioButton:
                        DS.Summarize(True, None, None)
                    elif TotalWordCountRadioButton:
                        DS.Summarize(False, "Total Word Count", SummarizeWord)
                    elif RatioRadioButton:
                        DS.Summarize(False, "Ratio", SummarizeRatio)
                    break

        if (len(DS.DataSourceTextSummary.split()) > 0):
            SummarySuccess = QMessageBox()
            SummarySuccess.setIcon(QMessageBox.Information)
            SummarySuccess.setText(
                DS.DataSourceName + " summarize successfully! The Summarize Text now contains " + str(
                    len(DS.DataSourceTextSummary.split())))
            SummarySuccess.setWindowTitle("Success")
            SummarySuccess.setStandardButtons(QMessageBox.Ok)
            SummarySuccess.exec_()
        else:
            delattr(DS, 'DataSourceTextSummary')
            SummaryError = QMessageBox()
            SummaryError.setIcon(QMessageBox.Warning)
            SummaryError.setText(
                DS.DataSourceName + " summarization failed! The Text may contains no words or is already summarized")
            SummaryError.setWindowTitle("Error")
            SummaryError.setStandardButtons(QMessageBox.Ok)
            SummaryError.exec_()

    #Data Source Summary Preview
    def DataSourceSummaryPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Word Cloud Tab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        try:
            DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
            DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourcePreview.setReadOnly(True)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DataSourcePreview.setText(DS.DataSourceTextSummary)
                    break

            myFile.TabList.append(
                Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,
                    DataSourceWidgetItemName.text(0)))
            self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

        except Exception as e:
            print(str(e))

    #Data Source Remove
    def DataSourceRemove(self, DataSourceWidgetItemName):
        DataSourceRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this file? Doing this will remove all Queries of " + DataSourceWidgetItemName.text(0),
                                                      QMessageBox.Yes | QMessageBox.No)

        if DataSourceRemoveChoice == QMessageBox.Yes:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DataSourceWidgetItemName.parent().setText(0, DataSourceWidgetItemName.parent().text(0)[0:-2] + str(
                        DataSourceWidgetItemName.parent().childCount() - 1) + ")")
                    DataSourceWidgetItemName.parent().removeChild(DataSourceWidgetItemName)

                    count = len(DS.QueryList)

                    for query in range(count):
                        self.QueryRemove(DS.QueryList[0][0])

                    myFile.DataSourceList.remove(DS)
                    DS.__del__()
                    break
        else:
            pass

    # Get Which Query Widget Item and its Position
    def FindQueryTreeWidgetContextMenu(self, QueryMouseRightClickEvent):
        if QueryMouseRightClickEvent.reason == QueryMouseRightClickEvent.Mouse:
            QueryMouseRightClickPos = QueryMouseRightClickEvent.globalPos()
            QueryMouseRightClickItem = self.QueryTreeWidget.itemAt(QueryMouseRightClickEvent.pos())
        else:
            QueryMouseRightClickPos = None
            Queryselection = self.QueryTreeWidget.selectedItems()

            if Queryselection:
                QueryMouseRightClickItem = Queryselection[0]
            else:
                QueryMouseRightClickItem = self.QueryTreeWidget.currentItem()
                if QueryMouseRightClickItem is None:
                    QueryMouseRightClickItem = self.QueryTreeWidget.invisibleRootItem().child(0)
            if QueryMouseRightClickItem is not None:
                QueryParent = QueryMouseRightClickItem.parent()
                while QueryParent is not None:
                    QueryParent.setExpanded(True)
                    QueryParent = QueryParent.parent()
                Queryitemrect = self.QueryTreeWidget.visualItemRect(QueryMouseRightClickItem)
                Queryportrect = self.QueryTreeWidget.viewport().rect()
                if not Queryportrect.contains(Queryitemrect.topLeft()):
                    self.QueryTreeWidget.scrollToItem(QueryMouseRightClickItem, QTreeWidget.PositionAtCenter)
                    Queryitemrect = self.QueryTreeWidget.visualItemRect(QueryMouseRightClickItem)

                Queryitemrect.setLeft(Queryportrect.left())
                Queryitemrect.setWidth(Queryportrect.width())
                QueryMouseRightClickPos = self.QueryTreeWidget.mapToGlobal(Queryitemrect.center())

        if QueryMouseRightClickPos is not None:
            self.QueryTreeWidgetContextMenu(QueryMouseRightClickItem, QueryMouseRightClickPos)

    # Setting ContextMenu on Clicked Query
    def QueryTreeWidgetContextMenu(self, QueryItemName, QueryWidgetPos):
        QueryRightClickMenu = QMenu(self.QueryTreeWidget)

        QueryRemove = QAction('Remove', self.QueryTreeWidget)
        QueryRemove.triggered.connect(lambda checked, index=QueryItemName: self.QueryRemove(index))

        QueryRightClickMenu.addAction(QueryRemove)
        QueryRightClickMenu.popup(QueryWidgetPos)

    # Remove Query (Tab)
    def QueryRemove(self, QueryItemName):
        if QueryItemName.text(0) == 'Data Sources Similarity':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Data Sources Similarity':
                    myFile.TabList.remove(tabs)
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    tabs.__del__()

        else:
            for letter in QueryItemName.text(0):
                if letter == '(':
                    QueryName = QueryItemName.text(0)[0: int(QueryItemName.text(0).index(letter)) - 1]
                    DataSourceName = QueryItemName.text(0)[int(QueryItemName.text(0).index(letter)) + 1: -1]

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceName:
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == tabs.DataSourceName:
                            for query in DS.QueryList:
                                if query[0] == QueryItemName and query[1] == tabs.tabWidget:
                                    myFile.TabList.remove(tabs)
                                    DS.QueryList.remove(query)
                                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                                    tabs.__del__()
                                    break

        self.QueryTreeWidget.invisibleRootItem().removeChild(QueryItemName)

    # Preview Query/Tab on double click
    def QueryDoubleClickHandler(self, QueryItemName):
        if QueryItemName.text(0) == 'Data Sources Similarity':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Data Sources Similarity':
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                    break
        else:
            for letter in QueryItemName.text(0):
                if letter == '(':
                    QueryName = QueryItemName.text(0)[0: int(QueryItemName.text(0).index(letter)) - 1]
                    DataSourceName = QueryItemName.text(0)[int(QueryItemName.text(0).index(letter)) + 1: -1]

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceName:
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == tabs.DataSourceName:
                            for query in DS.QueryList:
                                if query[0] == QueryItemName and query[1] == tabs.tabWidget:
                                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                                    break

    #Close Application / Exit
    def close_application(self):
        choice = QMessageBox.question(self, 'Quit', "Are You Sure?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    #Open New File
    def NewFileWindow(self):
        myDialog = QDialog()
        myDialog.setModal(True)
        myDialog.setWindowTitle("New File")
        myDialog.setParent(self)
        myDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        myDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        myDialog.show()

    #Open File
    def OpenFileWindow(self):
        self.dummyWindow = OpenWindow("Open File", "TextAS File *.tax", 0)

    #Import DataSource Window
    def ImportFileWindow(self, check):
        if check == "Word":
            dummyWindow = OpenWindow("Open Word File", "Doc files (*.doc *.docx)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                if not dummyDataSource.DataSourceLoadError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.wordTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")
                    dummyDataSource.setNode(newNode)
                else:
                    dummyDataSource.__del__()

        elif check == "PDF":
            dummyWindow = OpenWindow("Open PDF File", "Pdf files (*.pdf)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                if not dummyDataSource.DataSourceLoadError:
                    myFile.setDataSources(dummyDataSource)
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
            dummyWindow = OpenWindow("Open Notepad File", "Notepad files (*.txt)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                if not dummyDataSource.DataSourceLoadError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.txtTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")
                    dummyDataSource.setNode(newNode)
                else:
                    dummyDataSource.__del__()


        elif check == "RTF":
            dummyWindow = OpenWindow("Open Rich Text Format File", "Rich Text Format files (*.rtf)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                if not dummyDataSource.DataSourceLoadError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.rtfTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")
                    dummyDataSource.setNode(newNode)
                else:
                    dummyDataSource.__del__()

        elif check == "Sound":
            dummyWindow = OpenWindow("Open Audio File", "Audio files (*.wav *.mp3)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                if not dummyDataSource.DataSourceLoadError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.audioSTreeWidget)
                    newNode.setText(0, ntpath.basename(path[0]))
                    self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")
                    dummyDataSource.setNode(newNode)
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

    # Hide Query
    def QueryHide(self):
        if self.QueryLabel.isHidden() and self.QueryLabel.isHidden():
            self.QueryLabel.show()
            self.QueryTreeWidget.show()
        else:
            self.QueryLabel.hide()
            self.QueryTreeWidget.hide()

    # About Window Tab
    def AboutWindow(self):
        self.AboutWindowDialog = QDialog()
        self.AboutWindowDialog.setModal(True)
        self.AboutWindowDialog.setWindowTitle("About Us")
        self.AboutWindowDialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width / 2, self.height / 2)
        self.AboutWindowDialog.setParent(self)
        self.AboutWindowDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
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
TextASMainwindow = Window()
TextASMainwindow.show()
sys.exit(App.exec())