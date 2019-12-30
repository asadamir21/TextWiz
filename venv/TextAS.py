from distutils.errors import PreprocessError
from idlelib.idle_test.test_configdialog import GenPageTest

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore, QtPrintSupport, QAxContainer
from PyQt5.QtWebEngineWidgets import *
from matplotlib.container import StemContainer
from tweepy import TweepError
from win32api import GetMonitorInfo, MonitorFromPoint
from PIL import  Image
from File import *
from spacy import displacy
from hurry.filesize import size

import glob, sys, os, getpass, ntpath, win32gui, math, csv, datetime

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

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

        elif flag == 2:
            home = os.path.join(os.path.expanduser('~'), 'Pictures')

            if os.path.isdir(home):
                self.filepath = self.getOpenFileNames(self, title, home, ext)

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

        self.languages = open('Languages.txt', 'r').read().split("\n")

        for fileRow in self.languages:
            self.languages[self.languages.index(fileRow)] = fileRow.split(',')

        self.setStyleSheet(open('Styles/DarkOrange.css', 'r').read())


        self.initWindows()

    def initWindows(self):
        self.setWindowIcon(QtGui.QIcon(WindowTitleLogo))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top, self.width, self.height)
        self.setMinimumSize(self.width/2, self.height/2)
        self.showMaximized()

        # *****************************  ToolBar ******************************************

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

        ImageAct = QAction(QtGui.QIcon('Images/ImageDataSource.png'), 'Image', self)
        ImageAct.triggered.connect(lambda checked, index="Image": self.ImportFileWindow(index))

        TwitterAct = QAction(QtGui.QIcon('Images/Twitter.png'), 'Twitter', self)
        TwitterAct.triggered.connect(lambda checked: self.ImportTweetWindow())

        WebAct = QAction(QtGui.QIcon('Images/Web.png'), 'URL', self)
        WebAct.triggered.connect(lambda checked: self.ImportURLWindow())

        YoutubeAct = QAction(QtGui.QIcon('Images/Youtube.png'), 'Youtube', self)
        YoutubeAct.triggered.connect(lambda checked: self.ImportYoutubeWindow())

        self.toolbar = self.addToolBar("Show Toolbar")
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon | QtCore.Qt.AlignLeading)  # <= Toolbuttonstyle
        self.toolbar.setMovable(False)

        self.toolbar.addAction(WordAct)
        self.toolbar.addAction(PDFAct)
        self.toolbar.addAction(NotepadAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(RTFAct)
        self.toolbar.addAction(SoundAct)
        self.toolbar.addAction(ImageAct)
        self.toolbar.addAction(TwitterAct)
        self.toolbar.addAction(WebAct)
        self.toolbar.addAction(YoutubeAct)
        self.toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        # ***********************************************************************************
        # *****************************  Menu Item ******************************************
        # ***********************************************************************************

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        importMenu = mainMenu.addMenu('Import')
        ToolMenu = mainMenu.addMenu('Tools')
        VisualizationMenu = mainMenu.addMenu('Visualization')
        helpMenu = mainMenu.addMenu('Help')

        # *****************************  FileMenuItem ***************************************

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

        # *****************************  ViewMenuItem ***************************************

        toggleToolBarButton = QAction('Show Toolbar', self, checkable=True)
        toggleToolBarButton.setChecked(True)
        toggleToolBarButton.triggered.connect(self.toolbarHide)
        viewMenu.addAction(toggleToolBarButton)

        toggleDataSourceButton = QAction('Show Data Sources', self, checkable=True)
        toggleDataSourceButton.setChecked(True)
        toggleDataSourceButton.triggered.connect(lambda : self.LeftPaneHide(self.DataSourceLabel, self.DataSourceTreeWidget))
        viewMenu.addAction(toggleDataSourceButton)

        toggleQueryButton = QAction('Show Query', self, checkable=True)
        toggleQueryButton.setChecked(True)
        toggleQueryButton.triggered.connect(lambda : self.LeftPaneHide(self.QueryLabel, self.QueryTreeWidget))
        viewMenu.addAction(toggleQueryButton)

        toggleCasesButton = QAction('Show Cases', self, checkable=True)
        toggleCasesButton.setChecked(True)
        toggleCasesButton.triggered.connect(lambda : self.LeftPaneHide(self.CasesLabel, self.CasesTreeWidget))
        viewMenu.addAction(toggleCasesButton)

        toggleSentimentsButton = QAction('Show Sentiments', self, checkable=True)
        toggleSentimentsButton.setChecked(True)
        toggleSentimentsButton.triggered.connect(lambda: self.LeftPaneHide(self.SentimentLabel, self.SentimentTreeWidget))
        viewMenu.addAction(toggleSentimentsButton)

        toggleVisualizationButton = QAction('Show Visualization', self, checkable=True)
        toggleVisualizationButton.setChecked(True)
        toggleVisualizationButton.triggered.connect(lambda: self.LeftPaneHide(self.VisualizationLabel, self.VisualizationTreeWidget))
        viewMenu.addAction(toggleVisualizationButton)

        toggleReportButton = QAction('Show Report', self, checkable=True)
        toggleReportButton.setChecked(True)
        toggleReportButton.triggered.connect(lambda: self.LeftPaneHide(self.ReportLabel, self.ReportTreeWidget))
        viewMenu.addAction(toggleReportButton)

        # *****************************  ImportMenuItem *************************************

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

        ImageFileButton = QAction(QtGui.QIcon("Images\ImageDataSource.png"), 'Image File', self)
        ImageFileButton.setStatusTip('Image File')
        ImageFileButton.triggered.connect(lambda checked, index="Image": self.ImportFileWindow(index))

        TwitterButton = QAction(QtGui.QIcon("Images\Twitter.png"), 'Twitter', self)
        TwitterButton.setStatusTip('Tweets')
        TwitterButton.triggered.connect(lambda checked: self.ImportTweetWindow())

        URLButton = QAction(QtGui.QIcon("Images\Web.png"), 'Web', self)
        URLButton.setStatusTip('Get Data From URL')
        URLButton.triggered.connect(lambda checked: self.ImportURLWindow())

        YoutubeButton = QAction(QtGui.QIcon("Images\Youtube.png"), 'Youtube', self)
        YoutubeButton.setStatusTip('Youtube Comments')
        YoutubeButton.triggered.connect(lambda checked: self.ImportYoutubeWindow())

        importMenu.addAction(WordFileButton)
        importMenu.addAction(PDFFileButton)
        importMenu.addAction(TXTFileButton)
        importMenu.addAction(RTFFileButton)
        importMenu.addAction(SoundFileButton)
        importMenu.addAction(ImageFileButton)
        importMenu.addAction(TwitterButton)
        importMenu.addAction(URLButton)
        importMenu.addAction(YoutubeButton)

        # *****************************  ToolsMenuItem **************************************


        # Show Word Frequency Tool
        ShowWordFrequencyTool = QAction('Show Word Frequency Table', self)
        ShowWordFrequencyTool.setToolTip('Show Word Frequency Table')
        ShowWordFrequencyTool.setStatusTip('Show Word Frequency Table')
        ShowWordFrequencyTool.triggered.connect(lambda: self.DataSourceShowFrequencyTableDialog())

        # Summarize Tool
        SummarizeTool = QAction('Summarize', self)
        SummarizeTool.setStatusTip('Summarize')
        SummarizeTool.triggered.connect(lambda: self.DataSourceSummarize(None))

        # Stem Word Tool
        FindStemWordTool = QAction('Find Stem Word', self)
        FindStemWordTool.setStatusTip('Find Stem Words')
        FindStemWordTool.triggered.connect(lambda: self.DataSourceFindStemWords(None))

        # Generate Question
        GenerateQuestion = QAction('Generate Questions', self)
        GenerateQuestion.setToolTip('Generate Questions')
        GenerateQuestion.triggered.connect(lambda: self.DataSourcesGenerateQuestions())

        # Find Similarity
        FindSimilarity = QAction('Find Similarity', self)
        FindSimilarity.setToolTip('Find Similarity Between Data Sources')
        FindSimilarity.triggered.connect(lambda: self.DataSourcesSimilarity())

        ToolMenu.addAction(ShowWordFrequencyTool)
        ToolMenu.addAction(SummarizeTool)
        ToolMenu.addAction(FindStemWordTool)
        ToolMenu.addAction(GenerateQuestion)
        ToolMenu.addAction(FindSimilarity)

        # *************************  VisualizationMenuItem **********************************

        # Create Dashboard
        CreateDasboard = QAction('Create Dashboard', self)
        CreateDasboard.setToolTip('Find Similarity Between Data Sources')
        CreateDasboard.triggered.connect(lambda: self.DataSourcesCreateDashboardDialog())

        # Create Word Cloud Tool
        CreateWordCloudTool = QAction('Create Word Cloud', self)
        CreateWordCloudTool.setStatusTip('Create Word Cloud')
        CreateWordCloudTool.triggered.connect(lambda: self.DataSourceCreateCloud(None))

        VisualizationMenu.addAction(CreateDasboard)
        VisualizationMenu.addAction(CreateWordCloudTool)

        # *****************************  HelpMenuItem ***************************************

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
        self.wordTreeWidget.setHidden(True)

        self.pdfTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")
        self.pdfTreeWidget.setHidden(True)

        self.txtTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")
        self.txtTreeWidget.setHidden(True)

        self.rtfTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")
        self.rtfTreeWidget.setHidden(True)

        self.audioSTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")
        self.audioSTreeWidget.setHidden(True)

        self.ImageSTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.ImageSTreeWidget.setText(0, "Image" + "(" + str(self.ImageSTreeWidget.childCount()) + ")")
        self.ImageSTreeWidget.setHidden(True)

        self.WebTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.WebTreeWidget.setText(0, "Web" + "(" + str(self.WebTreeWidget.childCount()) + ")")
        self.WebTreeWidget.setHidden(True)

        self.TweetTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.TweetTreeWidget.setText(0, "Tweet" + "(" + str(self.TweetTreeWidget.childCount()) + ")")
        self.TweetTreeWidget.setHidden(True)

        self.YoutubeTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.YoutubeTreeWidget.setText(0, "Youtube" + "(" + str(self.YoutubeTreeWidget.childCount()) + ")")
        self.YoutubeTreeWidget.setHidden(True)
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

        # Cases Widget
        self.CasesLabel = QLabel()
        self.CasesLabel.setText("Cases")
        self.CasesLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.CasesLabel)

        self.CasesTreeWidget = QTreeWidget()
        self.CasesTreeWidget.setHeaderLabel('Cases')
        self.CasesTreeWidget.setAlternatingRowColors(True)
        self.CasesTreeWidget.header().setHidden(True)
        self.CasesTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.CasesTreeWidget.customContextMenuRequested.connect(lambda checked, index=QtGui.QContextMenuEvent: self.FindCasesTreeWidgetContextMenu(index))
        self.verticalLayout.addWidget(self.CasesTreeWidget)

        # Sentiment Widget
        self.SentimentLabel = QLabel()
        self.SentimentLabel.setText("Sentiments")
        self.SentimentLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.SentimentLabel)

        self.SentimentTreeWidget = QTreeWidget()
        self.SentimentTreeWidget.setHeaderLabel('Sentiments')
        self.SentimentTreeWidget.setAlternatingRowColors(True)
        self.SentimentTreeWidget.header().setHidden(True)
        self.SentimentTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.SentimentTreeWidget.customContextMenuRequested.connect(
            lambda checked, index=QtGui.QContextMenuEvent: self.FindSentimentsTreeWidgetContextMenu(index))
        self.verticalLayout.addWidget(self.SentimentTreeWidget)

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

        self.horizontalLayoutWidget.setGeometry(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.height - titleOffset - self.menuBar().height() - self.toolbar.height())

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

    # Update Similarity Between Data Sources
    def DataSourceSimilarityUpdate(self):
        for tabindex in range(self.tabWidget.count()):
            for tabs in myFile.TabList:
                if tabs.tabWidget == self.tabWidget.widget(tabindex) and tabs.TabName == "Data Sources Similarity":
                    currentTab = self.tabWidget.currentWidget()
                    if len(myFile.DataSourceList) > 1:
                        self.DataSourcesSimilarity()
                        self.tabWidget.setCurrentWidget(currentTab)

                    else:
                        self.tabWidget.removeTab(tabindex)
                    break

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

    # Setting ContextMenu on Clicked Data Source
    def DataSourceTreeWidgetContextMenu(self, DataSourceWidgetItemName, DataSourceWidgetPos):
        try:
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

                # Data Source Preview Web Page
                DataSourcePreviewWeb = QAction('Preview Web', self.DataSourceTreeWidget)
                DataSourcePreviewWeb.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePreviewWeb(index))

                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        if hasattr(DS, 'DataSourceHTML'):
                            DataSourceRightClickMenu.addAction(DataSourcePreviewWeb)

                # Data Source Show Tweet Data
                DataSourceShowTweetData = QAction('Show Tweet Data', self.DataSourceTreeWidget)
                DataSourceShowTweetData.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowTweetData(index))

                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        if hasattr(DS, 'TweetData'):
                            DataSourceRightClickMenu.addAction(DataSourceShowTweetData)

                try:
                    # Data Source Show Youtube Comments
                    DataSourceShowYoutubeComments = QAction('Show Youtube Data', self.DataSourceTreeWidget)

                    for DS in myFile.DataSourceList:
                        if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                            if hasattr(DS, 'YoutubeURLFlag'):
                                DataSourceShowYoutubeComments.triggered.connect(
                                    lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowYoutubeCommentsURL(index))
                                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)
                            if hasattr(DS, 'YoutubeKeyWordFlag'):
                                DataSourceShowYoutubeComments.triggered.connect(
                                    lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowYoutubeCommentsKeyWord(index))
                                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)

                except Exception as e:
                    print(str(e))

                # Data Source View Images
                DataSourceViewImages = QAction('View Image', self.DataSourceTreeWidget)
                DataSourceViewImages.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceViewImage(index))

                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        if hasattr(DS, 'DataSourceImage'):
                            DataSourceRightClickMenu.addAction(DataSourceViewImages)


                # Data Sources Preview
                DataSourcePreviewText = QAction('Preview Text', self.DataSourceTreeWidget)

                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        if DS.DataSourceext == "Pdf files (*.pdf)":
                            DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePDFPreview(index))
                            DataSourceRightClickMenu.addAction(DataSourcePreviewText)
                        elif DS.DataSourceext == "Doc files (*.doc *.docx)":
                            DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceWordPreview(index))
                            DataSourceRightClickMenu.addAction(DataSourcePreviewText)
                        else:
                            DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePreview(index))
                            DataSourceRightClickMenu.addAction(DataSourcePreviewText)



                # Data Source Add Image
                DataSourceAddImage = QAction('Add Image', self.DataSourceTreeWidget)
                DataSourceAddImage.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceAddImage(index))

                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        if hasattr(DS, 'DataSourceImage'):
                            DataSourceRightClickMenu.addAction(DataSourceAddImage)

                # Data Source Stem Words
                DataSourceStemWords = QAction('Find Stem Word', self.DataSourceTreeWidget)
                DataSourceStemWords.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceFindStemWords(index))
                DataSourceRightClickMenu.addAction(DataSourceStemWords)

                # Data Source Part of Speech
                DataSourcePOS = QAction('Part of Speech', self.DataSourceTreeWidget)
                DataSourcePOS.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePOS(index))
                DataSourceRightClickMenu.addAction(DataSourcePOS)

                # Data Source Part of Speech
                DataSourceEntityRelationShip = QAction('Entity Relationship', self.DataSourceTreeWidget)
                DataSourceEntityRelationShip.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceEntityRelationShip(index))
                DataSourceRightClickMenu.addAction(DataSourceEntityRelationShip)

                # Data Source Topic Modelling
                DataSourceTopicModelling = QAction('Topic Modelling', self.DataSourceTreeWidget)
                DataSourceTopicModelling.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceTopicModelling(index))
                DataSourceRightClickMenu.addAction(DataSourceTopicModelling)

                # Data Source Create Cases
                DataSourceCreateCases = QAction('Create Cases...', self.DataSourceTreeWidget)
                DataSourceCreateCases.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceCreateCases(index))
                DataSourceRightClickMenu.addAction(DataSourceCreateCases)

                # Data Source Create Sentiments
                DataSourceCreateSentiments = QAction('Create Sentiments...', self.DataSourceTreeWidget)
                DataSourceCreateSentiments.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceCreateSentiments(index))
                DataSourceRightClickMenu.addAction(DataSourceCreateSentiments)

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
                        if not hasattr(DS, 'isEnglish') and not hasattr(DS, 'LanguageDetectionError'):
                            DS.detect()
                        if not hasattr(DS, 'isEnglish') and hasattr(DS, 'LanguageDetectionError'):
                            pass
                        elif not DS.isEnglish:
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
                DataSourceChildDetail.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceChildDetail(index))
                DataSourceRightClickMenu.addAction(DataSourceChildDetail)

                DataSourceRightClickMenu.popup(DataSourceWidgetPos)
        except Exception as e:
            print(str(e))

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

    # *************************************************************************************************
    # *************************************************************************************************
    # *********************************** Child Context Method ****************************************
    # *************************************************************************************************
    # *************************************************************************************************

    # ****************************************************************************
    # ************************** Data Sources Preview ****************************
    # ****************************************************************************

    # Data Source Web Preview
    def DataSourcePreviewWeb(self, DataSourceWidgetItemName):
        DataSourcePreviewWebTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Web Preview':
                DataSourcePreviewWebTabFlag = True
                break

        # Creating New Tab for Stem Word
        PreviewWebTab = QWidget()

        # LayoutWidget For within Stem Word Tab
        PreviewWebTabVerticalLayoutWidget = QWidget(PreviewWebTab)
        PreviewWebTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Stem Word Tab
        PreviewWebTabVerticalLayout = QHBoxLayout(PreviewWebTabVerticalLayoutWidget)
        PreviewWebTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

        PreviewHTMLWebPage = QWebEngineView()
        PreviewHTMLWebPage.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        PreviewWebTabVerticalLayout.addWidget(PreviewHTMLWebPage)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                PreviewHTMLWebPage.setHtml(DS.DataSourceHTML.decode("utf-8"))
                break

        if DataSourcePreviewWebTabFlag:
            # change tab in query
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    for query in DS.QueryList:
                        if query[1] == tabs.tabWidget:
                            query[1] = PreviewWebTab
                            break

            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(PreviewWebTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(PreviewWebTab)
            tabs.tabWidget = PreviewWebTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Web Preview", PreviewWebTab, DataSourceWidgetItemName.text(0)))

            WebPreviewQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
            WebPreviewQueryTreeWidget.setText(0, "Web Preview (" + DataSourceWidgetItemName.text(0) + ")")

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    DS.setQuery(WebPreviewQueryTreeWidget, PreviewWebTab)

            self.tabWidget.addTab(PreviewWebTab, "Web Preview")
            self.tabWidget.setCurrentWidget(PreviewWebTab)

    # Data Source Show Tweet Data
    def DataSourceShowTweetData(self, DataSourceWidgetItemName):
        DataSourceShowTweetDataTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Tweet Data':
                DataSourceShowTweetDataTabFlag = True
                break

        ShowTweetDataTab = QWidget()
        ShowTweetDataTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()))
        ShowTweetDataTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Word Frequency Tab
        ShowTweetDataTabverticalLayoutWidget = QWidget(ShowTweetDataTab)
        ShowTweetDataTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        ShowTweetDataTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        ShowTweetDataTabverticalLayout = QVBoxLayout(ShowTweetDataTabverticalLayoutWidget)
        ShowTweetDataTabverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        ShowTweetDataTable = QTableWidget(ShowTweetDataTabverticalLayoutWidget)
        ShowTweetDataTable.setColumnCount(12)
        ShowTweetDataTable.setGeometry(0, 0, ShowTweetDataTabverticalLayoutWidget.width(),
                                       ShowTweetDataTabverticalLayoutWidget.height())
        ShowTweetDataTable.setSizePolicy(self.sizePolicy)

        ShowTweetDataTable.setWindowFlags(ShowTweetDataTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        ShowTweetDataTable.setHorizontalHeaderLabels(
            ["Screen Name", "User Name", "Tweet Created At", "Tweet Text", "User Location", "Tweet Coordinates",
             "Retweet Count", "Retweeted", "Phone Type", "Favorite Count", "Favorited", "Replied"])
        ShowTweetDataTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(ShowTweetDataTable.columnCount()):
            ShowTweetDataTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            ShowTweetDataTable.horizontalHeaderItem(i).setFont(
                QFont(ShowTweetDataTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                rowList = DS.TweetData
                break

        for row in rowList:
            ShowTweetDataTable.insertRow(rowList.index(row))
            for item in row:
                intItem = QTableWidgetItem()
                intItem.setData(Qt.EditRole, QVariant(item))
                ShowTweetDataTable.setItem(rowList.index(row), row.index(item), intItem)
                ShowTweetDataTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                    Qt.AlignHCenter | Qt.AlignVCenter)
                ShowTweetDataTable.item(rowList.index(row), row.index(item)).setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        ShowTweetDataTable.resizeColumnsToContents()
        ShowTweetDataTable.resizeRowsToContents()

        ShowTweetDataTable.setSortingEnabled(True)
        # ShowTweetDataTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        row_width = 0

        # for i in range(ShowTweetDataTable.columnCount()):
        #     ShowTweetDataTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        if DataSourceShowTweetDataTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(ShowTweetDataTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowTweetDataTab)
            tabs.tabWidget = ShowTweetDataTab
        else:
            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Tweet Data", ShowTweetDataTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowTweetDataTab, "Show Tweet Data")
            self.tabWidget.setCurrentWidget(ShowTweetDataTab)

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsURL(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                DataSourceShowYoutubeCommentsTabFlag = True
                break

        ShowYoutubeCommentsTab = QWidget()
        ShowYoutubeCommentsTab.setGeometry(QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()))
        ShowYoutubeCommentsTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Word Frequency Tab
        ShowYoutubeCommentsTabverticalLayoutWidget = QWidget(ShowYoutubeCommentsTab)
        ShowYoutubeCommentsTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        ShowYoutubeCommentsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        ShowYoutubeCommentsTabverticalLayout = QVBoxLayout(ShowYoutubeCommentsTabverticalLayoutWidget)
        ShowYoutubeCommentsTabverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        ShowYoutubeCommentsTable = QTableWidget(ShowYoutubeCommentsTabverticalLayoutWidget)
        ShowYoutubeCommentsTable.setColumnCount(4)
        ShowYoutubeCommentsTable.setGeometry(0, 0, ShowYoutubeCommentsTabverticalLayoutWidget.width(),
                                                   ShowYoutubeCommentsTabverticalLayoutWidget.height())
        ShowYoutubeCommentsTable.setSizePolicy(self.sizePolicy)

        ShowYoutubeCommentsTable.setWindowFlags(ShowYoutubeCommentsTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        ShowYoutubeCommentsTable.setHorizontalHeaderLabels(["Comment", "Author Name", "Like Count", "Publish At"])
        ShowYoutubeCommentsTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(ShowYoutubeCommentsTable.columnCount()):
            ShowYoutubeCommentsTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            ShowYoutubeCommentsTable.horizontalHeaderItem(i).setFont(
                QFont(ShowYoutubeCommentsTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                rowList = DS.YoutubeData
                break

        for row in rowList:
            ShowYoutubeCommentsTable.insertRow(rowList.index(row))
            for item in row:
                if row.index(item) == 0:
                    ptext = QPlainTextEdit()
                    ptext.setReadOnly(True)
                    ptext.setPlainText(item);
                    ShowYoutubeCommentsTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                else:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    ShowYoutubeCommentsTable.setItem(rowList.index(row), row.index(item), intItem)
                    ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        ShowYoutubeCommentsTable.resizeColumnsToContents()
        ShowYoutubeCommentsTable.resizeRowsToContents()

        ShowYoutubeCommentsTable.setSortingEnabled(True)
        row_width = 0

        for i in range(ShowYoutubeCommentsTable.columnCount()):
             ShowYoutubeCommentsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        if DataSourceShowYoutubeCommentsTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(ShowTweetDataTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
            tabs.tabWidget = ShowYoutubeCommentsTab
        else:
            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsKeyWord(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                DataSourceShowYoutubeCommentsTabFlag = True
                break

        ShowYoutubeCommentsTab = QWidget()
        ShowYoutubeCommentsTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()))
        ShowYoutubeCommentsTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Word Frequency Tab
        ShowYoutubeCommentsTabverticalLayoutWidget = QWidget(ShowYoutubeCommentsTab)
        ShowYoutubeCommentsTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        ShowYoutubeCommentsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        ShowYoutubeCommentsTabverticalLayout = QVBoxLayout(ShowYoutubeCommentsTabverticalLayoutWidget)
        ShowYoutubeCommentsTabverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        ShowYoutubeCommentsTable = QTableWidget(ShowYoutubeCommentsTabverticalLayoutWidget)
        ShowYoutubeCommentsTable.setColumnCount(7)
        ShowYoutubeCommentsTable.setGeometry(0, 0, ShowYoutubeCommentsTabverticalLayoutWidget.width(),
                                             ShowYoutubeCommentsTabverticalLayoutWidget.height())
        ShowYoutubeCommentsTable.setSizePolicy(self.sizePolicy)

        ShowYoutubeCommentsTable.setWindowFlags(
            ShowYoutubeCommentsTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        ShowYoutubeCommentsTable.setHorizontalHeaderLabels(["Comment", "Video ID", "Video Title", "Video Description", "Channel", "Replies", "Like"])
        ShowYoutubeCommentsTable.horizontalHeader().setStyleSheet(
            "::section {""background-color: grey;  color: white;}")

        for i in range(ShowYoutubeCommentsTable.columnCount()):
            ShowYoutubeCommentsTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            ShowYoutubeCommentsTable.horizontalHeaderItem(i).setFont(
                QFont(ShowYoutubeCommentsTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                rowList = DS.YoutubeData
                break

        for row in rowList:
            ShowYoutubeCommentsTable.insertRow(rowList.index(row))
            for item in row:
                if row.index(item) == 0:
                    ptext = QPlainTextEdit()
                    ptext.setReadOnly(True)
                    ptext.setPlainText(item);
                    ShowYoutubeCommentsTable.setCellWidget(rowList.index(row), row.index(item), ptext)
                else:
                    intItem = QTableWidgetItem()
                    if row.index(item) == 1:
                        intItem.setData(Qt.EditRole, QVariant("https://www.youtube.com/watch?v=" + item))
                    else:
                        intItem.setData(Qt.EditRole, QVariant(item))

                    ShowYoutubeCommentsTable.setItem(rowList.index(row), row.index(item), intItem)
                    ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        ShowYoutubeCommentsTable.resizeColumnsToContents()
        ShowYoutubeCommentsTable.resizeRowsToContents()

        ShowYoutubeCommentsTable.setSortingEnabled(True)
        row_width = 0

        for i in range(ShowYoutubeCommentsTable.columnCount()):
            ShowYoutubeCommentsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        if DataSourceShowYoutubeCommentsTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(ShowTweetDataTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
            tabs.tabWidget = ShowYoutubeCommentsTab
        else:
            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)

    # Data Source View Images
    def DataSourceViewImage(self, DataSourceWidgetItemName):
        DataSourceShowImagesTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'View Image':
                DataSourceShowImagesTabFlag = True
                break

        ViewImageTab = QWidget()
        ViewImageTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()))
        ViewImageTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For left Button within View Image Tab
        ViewImageTabverticalLayoutWidget1 = QWidget(ViewImageTab)
        ViewImageTabverticalLayoutWidget1.setGeometry(0, 0, self.tabWidget.width() * 0.1, self.tabWidget.height())
        ViewImageTabverticalLayoutWidget1.setSizePolicy(self.sizePolicy)

        # Box Layout  For left Button within View Image Tab
        ViewImageTabverticalLayout1 = QVBoxLayout(ViewImageTabverticalLayoutWidget1)
        ViewImageTabverticalLayout1.setContentsMargins(0, 0, 0, 0)

        LeftButton = PicButton(QPixmap('Images/Previous Image.png'))
        ViewImageTabverticalLayout1.addWidget(LeftButton)
        LeftButton.hide()

        # LayoutWidget For within View Image Tab
        ViewImageTabverticalLayoutWidget = QWidget(ViewImageTab)
        ViewImageTabverticalLayoutWidget.setGeometry(self.tabWidget.width() * 0.1, 0, self.tabWidget.width() * 0.8,
                                                     self.tabWidget.height())
        ViewImageTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # LayoutWidget For Right Button within View Image Tab
        ViewImageTabverticalLayoutWidget2 = QWidget(ViewImageTab)
        ViewImageTabverticalLayoutWidget2.setGeometry(self.tabWidget.width() * 0.9, 0, self.tabWidget.width() * 0.1,
                                                      self.tabWidget.height())
        ViewImageTabverticalLayoutWidget2.setSizePolicy(self.sizePolicy)

        # Box Layout  For left Button within View Image Tab
        ViewImageTabverticalLayout2 = QVBoxLayout(ViewImageTabverticalLayoutWidget2)
        ViewImageTabverticalLayout2.setContentsMargins(0, 0, 0, 0)

        RightButton = PicButton(QPixmap('Images/Next Image.png'))
        ViewImageTabverticalLayout2.addWidget(RightButton)

        # Box Layout for Word Frequency Tab
        ViewImageTabverticalLayout = QVBoxLayout(ViewImageTabverticalLayoutWidget)
        ViewImageTabverticalLayout.setContentsMargins(0, 0, 0, 0)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                image_files = DS.DataSourceImage
                break


        qpixmap_file = []

        for img in image_files:
            if isinstance(img, np.ndarray):
                dummyimage = QtGui.QImage(img, img.shape[1], \
                                          img.shape[0], img.shape[1] * 3,
                                          QtGui.QImage.Format_RGB888)

                qpixmap_file.append(QtGui.QPixmap(dummyimage))


        if len(qpixmap_file) == 1:
            RightButton.hide()

        # Image Preview Label
        ImagePreviewLabel = QLabel(ViewImageTabverticalLayoutWidget)

        # Resizing label to Layout
        ImagePreviewLabel.resize(ViewImageTabverticalLayoutWidget.width(), ViewImageTabverticalLayoutWidget.height())

        self.ImagePreviewPixmap = qpixmap_file[0]
        #            ImagePreviewPixmap.scaledToWidth()

        # Scaling Pixmap image
        dummypixmap = self.ImagePreviewPixmap.scaled(ViewImageTabverticalLayoutWidget.width(),
                                                ViewImageTabverticalLayoutWidget.height(), Qt.KeepAspectRatio)
        ImagePreviewLabel.setPixmap(dummypixmap)
        ImagePreviewLabel.setGeometry((ViewImageTabverticalLayoutWidget.width() - dummypixmap.width()) / 2,
                                      (ViewImageTabverticalLayoutWidget.height() - dummypixmap.height()) / 2,
                                      dummypixmap.width(), dummypixmap.height())

        LeftButton.clicked.connect(lambda: self.PreviousImage(qpixmap_file, ImagePreviewLabel,
                                                              ViewImageTabverticalLayoutWidget, RightButton))
        RightButton.clicked.connect(lambda: self.NextImage(qpixmap_file, ImagePreviewLabel,
                                                           ViewImageTabverticalLayoutWidget, LeftButton))

        if DataSourceShowImagesTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(ViewImageTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(ViewImageTab)
            tabs.tabWidget = ViewImageTab
        else:
            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("View Image", ViewImageTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ViewImageTab, "View Image")
            self.tabWidget.setCurrentWidget(ViewImageTab)

    # Previous Image Button
    def PreviousImage(self, qpixmap_file, ImagePreviewLabel, ViewImageTabverticalLayoutWidget, RightButton):
        LeftButton = self.sender()

        for qpix in qpixmap_file:
            if qpix == self.ImagePreviewPixmap:
                if qpixmap_file.index(qpix) == len(qpixmap_file) - 1:
                    RightButton.show()
                elif qpixmap_file.index(qpix) == 1:
                    LeftButton.hide()

                currentIndex = qpixmap_file.index(qpix)
                self.ImagePreviewPixmap = qpixmap_file[currentIndex - 1]

                dummypixmap = self.ImagePreviewPixmap.scaled(ViewImageTabverticalLayoutWidget.width(),
                                                             ViewImageTabverticalLayoutWidget.height(),
                                                             Qt.KeepAspectRatio)
                ImagePreviewLabel.setPixmap(dummypixmap)
                ImagePreviewLabel.setGeometry((ViewImageTabverticalLayoutWidget.width() - dummypixmap.width()) / 2,
                                              (
                                                      ViewImageTabverticalLayoutWidget.height() - dummypixmap.height()) / 2,
                                              dummypixmap.width(), dummypixmap.height())
                break

    # Next Image Button
    def NextImage(self, qpixmap_file, ImagePreviewLabel, ViewImageTabverticalLayoutWidget, LeftButton):
        try:
            RightButton = self.sender()

            for qpix in qpixmap_file:
                if qpix == self.ImagePreviewPixmap:
                    if qpixmap_file.index(qpix) == len(qpixmap_file) - 2:
                        RightButton.hide()
                    elif qpixmap_file.index(qpix) == 0:
                        LeftButton.show()

                    currentIndex = qpixmap_file.index(qpix)
                    self.ImagePreviewPixmap = qpixmap_file[currentIndex + 1]

                    dummypixmap = self.ImagePreviewPixmap.scaled(ViewImageTabverticalLayoutWidget.width(),
                                                            ViewImageTabverticalLayoutWidget.height(), Qt.KeepAspectRatio)
                    ImagePreviewLabel.setPixmap(dummypixmap)
                    ImagePreviewLabel.setGeometry((ViewImageTabverticalLayoutWidget.width() - dummypixmap.width()) / 2,
                                                  (ViewImageTabverticalLayoutWidget.height() - dummypixmap.height()) / 2,
                                                  dummypixmap.width(), dummypixmap.height())

                    break

        except Exception as e:
            print(str(e))

    # Data Source PDF Preview
    def DataSourcePDFPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Data SourceTab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        PDFPreviewWeb = QWebEngineView()
        DataSourceverticalLayout.addWidget(PDFPreviewWeb)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                PDFPreviewWeb.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
                PDFPreviewWeb.setUrl(QtCore.QUrl(DS.DataSourcePath))
                break

        myFile.TabList.append(
            Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,
                DataSourceWidgetItemName.text(0)))
        self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

    # Data Source Word Preview
    def DataSourceWordPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()
        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Data SourceTab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                WordActivex = QAxContainer.QAxWidget()
                WordActivex.setFocusPolicy(QtCore.Qt.StrongFocus)
                #contr = WordActivex.setControl("{00460182-9E5E-11d5-B7C8-B8269041DD57}")

                WordActivex.setProperty("DisplayScrollBars", True);
                WordActivex.setControl(DS.DataSourcePath)

                DataSourceverticalLayout.addWidget(WordActivex)

        myFile.TabList.append(
            Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,
                DataSourceWidgetItemName.text(0)))
        self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

    # Data Source Preview
    def DataSourcePreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
        DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Data SourceTab
        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

        DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
        DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        DataSourcePreview.setReadOnly(True)
        DataSourcePreview.setContextMenuPolicy(Qt.CustomContextMenu)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                DataSourcePreview.setText(DS.DataSourcetext)
                break

        myFile.TabList.append(
            Tab(self.tabWidget.tabText(self.tabWidget.indexOf(DataSourcePreviewTab)), DataSourcePreviewTab,
                DataSourceWidgetItemName.text(0)))
        self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

    # Data Source Add Image
    def DataSourceAddImage(self, DataSourceWidgetItemName):
        dummyWindow = OpenWindow("Open Image File",
                                 "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)",
                                 2)
        path = dummyWindow.filepath
        dummyWindow.__del__()

        if all(path):
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    DS.AddImage(path[0])
                    break

            if len(DS.AddImagePathDoublingError) == 0:
                DataSourceAddImageSuccessBox = QMessageBox()
                DataSourceAddImageSuccessBox.setIcon(QMessageBox.Information)
                DataSourceAddImageSuccessBox.setWindowTitle("Add Image")
                DataSourceAddImageSuccessBox.setText("Image Text Added Successfully.")
                DataSourceAddImageSuccessBox.setStandardButtons(QMessageBox.Ok)
                DataSourceAddImageSuccessBox.exec_()

            else:
                DataSourceAddImageSuccessBox = QMessageBox()
                DataSourceAddImageSuccessBox.setIcon(QMessageBox.Critical)
                DataSourceAddImageSuccessBox.setWindowTitle("Add Image")

                ImagePathErrorText = ""

                for ImagePath in DS.AddImagePathDouble:
                    ImagePathErrorText += ImagePath + '\n'
                ImagePathErrorText += "Already Added"

                DataSourceAddImageSuccessBox.setText(ImagePathErrorText)
                DataSourceAddImageSuccessBox.setStandardButtons(QMessageBox.Ok)
                DataSourceAddImageSuccessBox.exec_()

    # ****************************************************************************
    # ********************** Data Sources Show Frequency *************************
    # ****************************************************************************

    # Data Source Show Frequency Table Dialog
    def DataSourceShowFrequencyTableDialog(self):
        DataSourceShowFrequencyTableDialog = QDialog()
        DataSourceShowFrequencyTableDialog.setWindowTitle("Show Word Frequency Table")
        DataSourceShowFrequencyTableDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4, self.height / 10)
        DataSourceShowFrequencyTableDialog.setParent(self)
        DataSourceShowFrequencyTableDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourceShowFrequencyTableDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)


        # Data Source Label
        DataSourcelabel = QLabel(DataSourceShowFrequencyTableDialog)
        DataSourcelabel.setGeometry(DataSourceShowFrequencyTableDialog.width() * 0.125, DataSourceShowFrequencyTableDialog.height() * 0.2,
                                    DataSourceShowFrequencyTableDialog.width() / 4, DataSourceShowFrequencyTableDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourceShowFrequencyTableDialog)
        DSComboBox.setGeometry(DataSourceShowFrequencyTableDialog.width() * 0.4, DataSourceShowFrequencyTableDialog.height() * 0.2,
                               DataSourceShowFrequencyTableDialog.width() / 2, DataSourceShowFrequencyTableDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        DataSourceShowFrequencybuttonBox = QDialogButtonBox(DataSourceShowFrequencyTableDialog)
        DataSourceShowFrequencybuttonBox.setGeometry(DataSourceShowFrequencyTableDialog.width() * 0.125, DataSourceShowFrequencyTableDialog.height() * 0.7,
                                      DataSourceShowFrequencyTableDialog.width() * 3 / 4, DataSourceShowFrequencyTableDialog.height() / 5)
        DataSourceShowFrequencybuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourceShowFrequencybuttonBox.button(QDialogButtonBox.Ok).setText('Show')

        if len(DSComboBox.currentText()) == 0:
            DataSourceShowFrequencybuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(DataSourceShowFrequencybuttonBox)

        DataSourceShowFrequencybuttonBox.accepted.connect(DataSourceShowFrequencyTableDialog.accept)
        DataSourceShowFrequencybuttonBox.rejected.connect(DataSourceShowFrequencyTableDialog.reject)

        DataSourceShowFrequencybuttonBox.accepted.connect(lambda: self.DataSourceShowFrequencyTable(DSComboBox.currentText()))

        DataSourceShowFrequencyTableDialog.exec()

    # Data Source Show Frequency Table
    def DataSourceShowFrequencyTable(self, DataSourceName):
        DataSourceShowFrequencyTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Word Frequency':
                DataSourceShowFrequencyTabFlag = True
                break

        WordFrequencyTab = QWidget()
        WordFrequencyTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height()-self.tabWidget.tabBar().geometry().height()))
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
        WordFrequencyTable.setColumnCount(7)
        # WordFrequencyTable.setModel(WordFrequencyTableModel)
        WordFrequencyTable.setGeometry(0, 0, WordFrequencyTabverticalLayoutWidget.width(),
                                       WordFrequencyTabverticalLayoutWidget.height())

        WordFrequencyTable.setSizePolicy(self.sizePolicy)

        WordFrequencyTable.setWindowFlags(WordFrequencyTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        WordFrequencyTable.setHorizontalHeaderLabels(["Word", "Length", "Frequency", "Weighted Percentage", "Definition", "Synonyms", "Antonyms"])
        WordFrequencyTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(WordFrequencyTable.columnCount()):
            WordFrequencyTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            WordFrequencyTable.horizontalHeaderItem(i).setFont(
                QFont(WordFrequencyTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                rowList = dummyQuery.FindWordFrequency(DS.DataSourcetext)
                break

        DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(WordFrequencyTable))

        if len(rowList) != 0:
            for row in rowList:
                WordFrequencyTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 4:
                        ptext = QPlainTextEdit()
                        ptext.setReadOnly(True)
                        ptext.setPlainText(item);
                        WordFrequencyTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                    else:
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
                    if DS.DataSourceName == DataSourceName:
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
                myFile.TabList.append(Tab("Word Frequency", WordFrequencyTab, DataSourceName))

                # Adding Word Frequency Query
                WordFreqencyQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                WordFreqencyQueryTreeWidget.setText(0, "Word Frequency (" + DataSourceName + ")")
                WordFreqencyQueryTreeWidget.setToolTip(0, WordFreqencyQueryTreeWidget.text(0))

                # Adding Word Frequency Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(WordFreqencyQueryTreeWidget, WordFrequencyTab)

                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(WordFrequencyTab, "Word Frequency")
                self.tabWidget.setCurrentWidget(WordFrequencyTab)

        else:

            WordFrequencyErrorBox = QMessageBox()
            WordFrequencyErrorBox.setIcon(QMessageBox.Critical)
            WordFrequencyErrorBox.setWindowTitle("Word Frequency Error")
            WordFrequencyErrorBox.setText("An Error Occurred! No Text Found in " + DataSourceName)
            WordFrequencyErrorBox.setStandardButtons(QMessageBox.Ok)
            WordFrequencyErrorBox.exec_()

    # Save Table as CSV
    def SaveTableAsCSV(self, Table):
        try:
            path = QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')

            if all(path):
                with open(path[0], 'w', newline='') as stream:
                    writer = csv.writer(stream)

                    HeaderList = []
                    for i in range(Table.columnCount()):
                        HeaderList.append(Table.horizontalHeaderItem(i).text())

                    writer.writerow(HeaderList)

                    for row in range(Table.rowCount()):
                        rowdata = []
                        for column in range(Table.columnCount()):
                            item = Table.item(row, column)
                            if item is not None:
                                rowdata.append(item.text())
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)

        except PermissionError:
            SaveAsCSVErrorBox = QMessageBox()
            SaveAsCSVErrorBox.setIcon(QMessageBox.Critical)
            SaveAsCSVErrorBox.setWindowTitle("Saving Error")
            SaveAsCSVErrorBox.setText("Permission Denied!")
            SaveAsCSVErrorBox.setStandardButtons(QMessageBox.Ok)
            SaveAsCSVErrorBox.exec_()

    # ****************************************************************************
    # *************************** Question Generator *****************************
    # ****************************************************************************

    # Data Source Generate Questions
    def DataSourcesGenerateQuestions(self):
        GenerateQuestionsDialog = QDialog()
        GenerateQuestionsDialog.setWindowTitle("Generate Questions")
        GenerateQuestionsDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                       self.height / 10)
        GenerateQuestionsDialog.setParent(self)
        GenerateQuestionsDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        GenerateQuestionsDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(GenerateQuestionsDialog)
        DataSourcelabel.setGeometry(GenerateQuestionsDialog.width() * 0.125,
                                    GenerateQuestionsDialog.height() * 0.2,
                                    GenerateQuestionsDialog.width() / 4,
                                    GenerateQuestionsDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(GenerateQuestionsDialog)
        DSComboBox.setGeometry(GenerateQuestionsDialog.width() * 0.4,
                               GenerateQuestionsDialog.height() * 0.2,
                               GenerateQuestionsDialog.width() / 2,
                               GenerateQuestionsDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        GenerateQuestionbuttonBox = QDialogButtonBox(GenerateQuestionsDialog)
        GenerateQuestionbuttonBox.setGeometry(GenerateQuestionsDialog.width() * 0.125,
                                                     GenerateQuestionsDialog.height() * 0.7,
                                                     GenerateQuestionsDialog.width() * 3 / 4,
                                                     GenerateQuestionsDialog.height() / 5)
        GenerateQuestionbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        GenerateQuestionbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            GenerateQuestionbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(GenerateQuestionbuttonBox)

        GenerateQuestionbuttonBox.accepted.connect(GenerateQuestionsDialog.accept)
        GenerateQuestionbuttonBox.rejected.connect(GenerateQuestionsDialog.reject)

        GenerateQuestionbuttonBox.accepted.connect(
            lambda: self.GenerateQuestionsTable(DSComboBox.currentText()))

        GenerateQuestionsDialog.exec()

    # Generate Questions Table
    def GenerateQuestionsTable(self, DataSourceName):
        GenerateQuestionsTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Generate Questions':
                GenerateQuestionsTabFlag = True
                break

        GenerateQuestionsTab = QWidget()
        GenerateQuestionsTab.setGeometry(
            QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height() - self.tabWidget.tabBar().geometry().height()))
        GenerateQuestionsTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Stem Word Tab
        GenerateQuestionsTabVerticalLayoutWidget2 = QWidget(GenerateQuestionsTab)
        GenerateQuestionsTabVerticalLayoutWidget2.setGeometry(self.tabWidget.width() / 4, 0, self.tabWidget.width() / 2,
                                                          self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        GenerateQuestionsTabVerticalLayout2 = QHBoxLayout(GenerateQuestionsTabVerticalLayoutWidget2)
        GenerateQuestionsTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)


        # Download Button For Frequency Table
        DownloadAsCSVButton = QPushButton('Download')
        DownloadAsCSVButton.setIcon(QIcon("Images/Download Button.png"))
        DownloadAsCSVButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

        DownloadAsCSVButtonFont = QFont("sans-serif")
        DownloadAsCSVButtonFont.setPixelSize(14)
        DownloadAsCSVButtonFont.setBold(True)

        DownloadAsCSVButton.setFont(DownloadAsCSVButtonFont)

        GenerateQuestionsTabVerticalLayout2.addWidget(DownloadAsCSVButton)

        # LayoutWidget For within Word Frequency Tab
        GenerateQuestionsTabverticalLayoutWidget = QWidget(GenerateQuestionsTab)
        GenerateQuestionsTabverticalLayoutWidget.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                         self.tabWidget.height() - self.tabWidget.height() / 10)
        GenerateQuestionsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        GenerateQuestionsverticalLayout = QVBoxLayout(GenerateQuestionsTabverticalLayoutWidget)
        GenerateQuestionsverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        GenerateQuestionsTable = QTableWidget(GenerateQuestionsTabverticalLayoutWidget)
        GenerateQuestionsTable.setColumnCount(1)
        # WordFrequencyTable.setModel(WordFrequencyTableModel)
        GenerateQuestionsTable.setGeometry(0, 0, GenerateQuestionsTabverticalLayoutWidget.width(),
                                       GenerateQuestionsTabverticalLayoutWidget.height())

        GenerateQuestionsTable.setSizePolicy(self.sizePolicy)

        GenerateQuestionsTable.setWindowFlags(GenerateQuestionsTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        GenerateQuestionsTable.setHorizontalHeaderLabels(
            ["Questions"])
        GenerateQuestionsTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(GenerateQuestionsTable.columnCount()):
            GenerateQuestionsTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            GenerateQuestionsTable.horizontalHeaderItem(i).setFont(
                QFont(GenerateQuestionsTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                rowList = dummyQuery.GenerateQuestion(DS.DataSourcetext)
                break

        DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(GenerateQuestionsTable))

        if len(rowList) != 0:
            for row in rowList:
                GenerateQuestionsTable.insertRow(rowList.index(row))

                ptext = QPlainTextEdit()
                ptext.setReadOnly(True)
                ptext.setPlainText(row);
                ptext.adjustSize()

            GenerateQuestionsTable.resizeColumnsToContents()
            GenerateQuestionsTable.resizeRowsToContents()

            GenerateQuestionsTable.setSortingEnabled(True)
            GenerateQuestionsTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(GenerateQuestionsTable.columnCount()):
                GenerateQuestionsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if GenerateQuestionsTabFlag:
                # change tab in query
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        for query in DS.QueryList:
                            if query[1] == tabs.tabWidget:
                                query[1] = GenerateQuestionsTab
                                break

                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(WordFrequencyTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(GenerateQuestionsTab)
                tabs.tabWidget = GenerateQuestionsTab
            else:
                # Adding Word Frequency Tab to TabList
                myFile.TabList.append(Tab("Generate Questions", GenerateQuestionsTab, DataSourceName))

                # Adding Word Frequency Query
                GenerateQuestionsQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                GenerateQuestionsQueryTreeWidget.setText(0, "Generate Questions (" + DataSourceName + ")")
                GenerateQuestionsQueryTreeWidget.setToolTip(0, GenerateQuestionsQueryTreeWidget.text(0))

                # Adding Word Frequency Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(GenerateQuestionsQueryTreeWidget, GenerateQuestionsTab)

                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(GenerateQuestionsTab, "Generate Questions")
                self.tabWidget.setCurrentWidget(GenerateQuestionsTab)

        else:
            GenerateQuestionsErrorBox = QMessageBox()
            GenerateQuestionsErrorBox.setIcon(QMessageBox.Critical)
            GenerateQuestionsErrorBox.setWindowTitle("Questions Generation Error")
            GenerateQuestionsErrorBox.setText("An Error Occurred! No Text Found in " + DataSourceName)
            GenerateQuestionsErrorBox.setStandardButtons(QMessageBox.Ok)
            GenerateQuestionsErrorBox.exec_()

    # ****************************************************************************
    # ************************ Data Sources Word CLoud ***************************
    # ****************************************************************************

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

        for colorname, colorhex in matplotlib.colors.cnames.items():
            WordCloudBackgroundColor.addItem(colorname)

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

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == WCDSName:
                dummyQuery = Query()
                WordCloudImage = dummyQuery.CreateWordCloud(DS.DataSourcetext, WCBGColor, maxword, maskname)
                break

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


    # ****************************************************************************
    # ************************** Data Sources Rename *****************************
    # ****************************************************************************

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

        RenameLineEdit.textChanged.connect(lambda: self.OkButtonEnable(RenamebuttonBox, True))

        RenamebuttonBox.accepted.connect(DataSourceRename.accept)
        RenamebuttonBox.rejected.connect(DataSourceRename.reject)

        RenamebuttonBox.accepted.connect(lambda: self.DSRename(DataSourceWidgetItemName, RenameLineEdit.text()))

        DataSourceRename.exec()

    # Rename Data Source and Widget
    def DSRename(self, DataSourceWidgetItemName, name):
        try:
            DataSourceRenameCheck = False

            for DSN in myFile.DataSourceList:
                if DSN.DataSourceName == name:
                    DataSourceRenameCheck = True
                    break

            if not DataSourceRenameCheck:
                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        for tab in myFile.TabList:
                            if tab.DataSourceName == DS.DataSourceName:
                                tab.DataSourceName = name

                        # ************** updating queries *****************
                        for query in DS.QueryList:
                            for letter in query[0].text(0):
                                if letter == '(':
                                    QueryName = query[0].text(0)[0: int(query[0].text(0).index(letter)) - 1]
                                    DataSourceName = query[0].text(0)[int(query[0].text(0).index(letter)) + 1: -1]

                                    if DataSourceName == DS.DataSourceName:
                                        query[0].setText(0, QueryName + "(" + name + ")")
                                        query[0].setToolTip(0, query[0].text(0))

                        # ************** updating cases *****************
                        ItemsWidget = self.CasesTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0)
                        for widgets in ItemsWidget:
                            widgets.setText(0, name)
                            widgets.setToolTip(0, widgets.text(0))

                        # *********** updating sentiments ***************
                        ItemsWidget = self.SentimentTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0)
                        for widgets in ItemsWidget:
                            widgets.setText(0, name)
                            widgets.setToolTip(0, widgets.text(0))

                        # ********* updating Visualizations *************

                        # ************ updating Reports *****************

                        DS.DataSourceName = name
                        break



                DataSourceWidgetItemName.setText(0, name)
                DataSourceWidgetItemName.setToolTip(0, DataSourceWidgetItemName.text(0))

                DataSourceRenameSuccessBox = QMessageBox()
                DataSourceRenameSuccessBox.setIcon(QMessageBox.Information)
                DataSourceRenameSuccessBox.setWindowTitle("Rename Success")
                DataSourceRenameSuccessBox.setText("Data Source Rename Successfully!")
                DataSourceRenameSuccessBox.setStandardButtons(QMessageBox.Ok)
                DataSourceRenameSuccessBox.exec_()

            else:
                DataSourceRenameErrorBox = QMessageBox()
                DataSourceRenameErrorBox.setIcon(QMessageBox.Critical)
                DataSourceRenameErrorBox.setWindowTitle("Rename Error")
                DataSourceRenameErrorBox.setText("A Data Source with Similar Name Exist!")
                DataSourceRenameErrorBox.setStandardButtons(QMessageBox.Ok)
                DataSourceRenameErrorBox.exec_()
        except Exception as e:
            print(str(e))

    # ****************************************************************************
    # ************************ Data Sources StemWords ****************************
    # ****************************************************************************

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
        StemWordLineEdit.textChanged.connect(lambda: self.OkButtonEnable(StemWordbuttonBox, True))

        StemWordDSComboBox.currentTextChanged.connect(StemWordLineEdit.clear)

        StemWordbuttonBox.accepted.connect(DataSourceStemWord.accept)
        StemWordbuttonBox.rejected.connect(DataSourceStemWord.reject)

        StemWordbuttonBox.accepted.connect(
            lambda: self.mapStemWordonTab(StemWordLineEdit.text(), StemWordDSComboBox.currentText()))

        DataSourceStemWord.exec()

    # Show StemWords on Tab
    def mapStemWordonTab(self, word, DataSourceItemWidget):
        DataSourceStemWordTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceItemWidget and tabs.TabName == 'Stem Word':
                DataSourceStemWordTabFlag = True
                break

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

        StemWordLineEdit.textChanged.connect(lambda: self.OkButtonEnable(StemWordSubmitButton, False))

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

            if DataSourceStemWordTabFlag:
                # change tab in query
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceItemWidget:
                        for query in DS.QueryList:
                            if query[1] == tabs.tabWidget:
                                query[1] = StemWordTab
                                break

                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(StemWordTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(StemWordTab)
                tabs.tabWidget = StemWordTab

            else:
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

    #Word Suggestion
    def WordSuggestion(self, StemWordModel, CurrentText, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                dummyQuery = Query()
                WordList = dummyQuery.GetDistinctWords(DS.DataSourcetext)
                matching = [s for s in WordList if CurrentText in s]
                StemWordModel.setStringList(matching)

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

    # ****************************************************************************
    # ***************************** Data Sources POS ****************************
    # ****************************************************************************

    # Data Source Part of Speech
    def DataSourcePOS(self, DataSourceWidgetItemName):
        DataSourcePOSTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Part of Speech':
                DataSourcePOSTabFlag = True
                break

        dummyQuery = Query()
        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                POSGraph, rowList, noun_count, verb_count, adj_count = dummyQuery.PartOfSpeech(DS.DataSourceName,
                                                                                               DS.DataSourcetext, 3)
                break

        # Creating New Tab for Stem Word
        POSTab = QWidget()

        # LayoutWidget For within Stem Word Tab
        POSTabVerticalLayoutWidget = QWidget(POSTab)
        POSTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        POSTabVerticalLayout = QHBoxLayout(POSTabVerticalLayoutWidget)
        POSTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

        # Noun_Count Label
        POSNounCountLabel = QLabel(POSTabVerticalLayoutWidget)
        POSNounCountLabel.setGeometry(POSTabVerticalLayoutWidget.width() * 0.05,
                                      POSTabVerticalLayoutWidget.height() * 0.142,
                                      POSTabVerticalLayoutWidget.width() / 20, POSTabVerticalLayoutWidget.height() / 7)
        POSNounCountLabel.setText("Noun Count: " + str(noun_count))
        POSNounCountLabel.setAlignment(Qt.AlignVCenter)
        POSNounCountLabel.adjustSize()

        # Verb_Count Label
        POSVerbCountLabel = QLabel(POSTabVerticalLayoutWidget)
        POSVerbCountLabel.setGeometry(POSTabVerticalLayoutWidget.width() * 0.05,
                                      POSTabVerticalLayoutWidget.height() * 0.428,
                                      POSTabVerticalLayoutWidget.width() / 20, POSTabVerticalLayoutWidget.height() / 7)
        POSVerbCountLabel.setText("Verb Count: " + str(verb_count))
        POSVerbCountLabel.setAlignment(Qt.AlignVCenter)
        POSVerbCountLabel.adjustSize()

        # Adjective_Count Label
        POSAdjCountLabel = QLabel(POSTabVerticalLayoutWidget)
        POSAdjCountLabel.setGeometry(POSTabVerticalLayoutWidget.width() * 0.05,
                                     POSTabVerticalLayoutWidget.height() * 0.714,
                                     POSTabVerticalLayoutWidget.width() / 20, POSTabVerticalLayoutWidget.height() / 7)
        POSAdjCountLabel.setText("Adjective Count: " + str(adj_count))
        POSAdjCountLabel.setAlignment(Qt.AlignVCenter)
        POSAdjCountLabel.adjustSize()

        # Part of speech ComboBox
        POSComboBox = QComboBox(POSTabVerticalLayoutWidget)
        POSComboBox.setGeometry(POSTabVerticalLayoutWidget.width() * 0.8, POSTabVerticalLayoutWidget.height() * 0.4,
                                POSTabVerticalLayoutWidget.width() / 10, POSTabVerticalLayoutWidget.height() / 5)
        POSComboBox.addItem("Show Table")
        POSComboBox.addItem("Show Graph")
        self.LineEditSizeAdjustment(POSComboBox)

        # 2nd LayoutWidget For within Stem Word Tab
        POSTabVerticalLayoutWidget2 = QWidget(POSTab)
        POSTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                self.tabWidget.height() - self.tabWidget.height() / 10)

        # 2nd Box Layout for Stem Word Tab
        POSTabVerticalLayout2 = QVBoxLayout(POSTabVerticalLayoutWidget2)
        POSTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

        POSTable = QTableWidget(POSTabVerticalLayoutWidget2)
        POSTable.setColumnCount(3)
        POSTable.setGeometry(0, 0, POSTabVerticalLayoutWidget2.width(),
                             POSTabVerticalLayoutWidget2.height())

        POSTable.setSizePolicy(self.sizePolicy)
        POSTable.setWindowFlags(POSTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        POSTable.setHorizontalHeaderLabels(["Word", "Part of Speech", "Frequency"])
        POSTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(POSTable.columnCount()):
            POSTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            POSTable.horizontalHeaderItem(i).setFont(QFont(POSTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        # StemWordSubmitButton.clicked.connect(lambda: self.StemWordWithinTab(StemWordLineEdit.text(), DataSourceWidgetItemName, POSTable))

        if len(rowList) != 0:
            for row in rowList:
                POSTable.insertRow(rowList.index(row))
                for item in row:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    POSTable.setItem(rowList.index(row), row.index(item), intItem)
                    POSTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    POSTable.item(rowList.index(row), row.index(item)).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            POSTable.resizeColumnsToContents()
            POSTable.resizeRowsToContents()

            POSTable.setSortingEnabled(True)
            POSTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(POSTable.columnCount()):
                POSTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # Label for Word Cloud Image
        POSGraphLabel = QLabel(POSTabVerticalLayoutWidget2)
        # Resizing label to Layout
        POSGraphLabel.resize(POSTabVerticalLayoutWidget2.width(), POSTabVerticalLayoutWidget2.height())

        # Converting WordCloud Image to Pixmap
        POSGraphPixmap = POSGraph.toqpixmap()

        # Scaling Pixmap image
        dummypixmap = POSGraphPixmap.scaled(POSTabVerticalLayoutWidget2.width(),
                                            POSTabVerticalLayoutWidget2.height(), Qt.KeepAspectRatio)

        POSGraphLabel.setPixmap(dummypixmap)
        POSGraphLabel.setGeometry((POSTabVerticalLayoutWidget2.width() - dummypixmap.width()) / 2,
                                  (POSTabVerticalLayoutWidget2.height() - dummypixmap.height()) / 2,
                                  dummypixmap.width(), dummypixmap.height())
        POSGraphLabel.hide()

        # Setting ContextMenu Policies on Label
        # POSGraphLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        # POSGraphLabel.customContextMenuRequested.connect(lambda index=QContextMenuEvent, index2=dummypixmap, index3=WordCloudLabel: self.WordCloudContextMenu(index, index2, index3))

        POSComboBox.currentTextChanged.connect(lambda: self.togglePOSView(POSTable, POSGraphLabel))

        if DataSourcePOSTabFlag:
            # change tab in query
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    for query in DS.QueryList:
                        if query[1] == tabs.tabWidget:
                            query[1] = POSTab
                            break

            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(POSTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(POSTab)
            tabs.tabWidget = POSTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Part of Speech", POSTab, DataSourceWidgetItemName.text(0)))

            POSQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
            POSQueryTreeWidget.setText(0, "Parts of Speech (" + DataSourceWidgetItemName.text(0) + ")")

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    DS.setQuery(POSQueryTreeWidget, POSTab)

            self.tabWidget.addTab(POSTab, "Parts of Speech")
            self.tabWidget.setCurrentWidget(POSTab)

    # Toggle POS View
    def togglePOSView(self, Table, Label):
        ComboBox = self.sender()

        if ComboBox.currentText() == "Show Table":
            Label.hide()
            Table.show()
        else:
            Table.hide()
            Label.show()

    # ****************************************************************************
    # ********************* Data Sources Entity Relationship *********************
    # ****************************************************************************

    # Data Source Entity Relationship
    def DataSourceEntityRelationShip(self, DataSourceWidgetItemName):
        DataSourceERTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Entity Relationship':
                DataSourceERTabFlag = True
                break

        dummyQuery = Query()
        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                Entity_List, EntityHTML, DependencyHTML = dummyQuery.EntityRelationShip(
                    DS.DataSourcetext)
                break

        # Creating New Tab for Stem Word
        DSERTab = QWidget()

        # LayoutWidget For within Stem Word Tab
        DSERTabVerticalLayoutWidget = QWidget(DSERTab)
        DSERTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        DSERTabVerticalLayout = QHBoxLayout(DSERTabVerticalLayoutWidget)
        DSERTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

        # Part of speech ComboBox
        DSERComboBox = QComboBox(DSERTabVerticalLayoutWidget)
        DSERComboBox.setGeometry(DSERTabVerticalLayoutWidget.width() * 0.8, DSERTabVerticalLayoutWidget.height() * 0.4,
                                 DSERTabVerticalLayoutWidget.width() / 10, DSERTabVerticalLayoutWidget.height() / 5)
        DSERComboBox.addItem("Show Table")
        DSERComboBox.addItem("Show Dependency")
        DSERComboBox.addItem("Show Entities")

        self.LineEditSizeAdjustment(DSERComboBox)

        # 2nd LayoutWidget For within Stem Word Tab
        DSERTabVerticalLayoutWidget2 = QWidget(DSERTab)
        DSERTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                 self.tabWidget.height() - self.tabWidget.height() / 10)

        # 2nd Box Layout for Stem Word Tab
        DSERTabVerticalLayout2 = QVBoxLayout(DSERTabVerticalLayoutWidget2)

        DSERTable = QTableWidget(DSERTabVerticalLayoutWidget2)
        DSERTable.setColumnCount(3)
        DSERTable.setGeometry(0, 0, DSERTabVerticalLayoutWidget2.width(), DSERTabVerticalLayoutWidget2.height())

        DSERTable.setSizePolicy(self.sizePolicy)
        DSERTable.setWindowFlags(DSERTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        DSERTable.setHorizontalHeaderLabels(["Word", "Frequency", "Entity"])
        DSERTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(DSERTable.columnCount()):
            DSERTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            DSERTable.horizontalHeaderItem(i).setFont(
                QFont(DSERTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        if len(Entity_List) != 0:
            for row in Entity_List:
                DSERTable.insertRow(Entity_List.index(row))
                for item in row:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    DSERTable.setItem(Entity_List.index(row), row.index(item), intItem)
                    DSERTable.item(Entity_List.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    DSERTable.item(Entity_List.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            DSERTable.resizeColumnsToContents()
            DSERTable.resizeRowsToContents()

            DSERTable.setSortingEnabled(True)
            DSERTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(DSERTable.columnCount()):
                DSERTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        EntityHTMLWeb = QWebEngineView()
        DSERTabVerticalLayout2.addWidget(EntityHTMLWeb)
        EntityHTMLWeb.setHtml(EntityHTML)
        EntityHTMLWeb.hide()

        DependencyHTMLWeb = QWebEngineView()
        DSERTabVerticalLayout2.addWidget(DependencyHTMLWeb)
        DependencyHTMLWeb.setHtml(DependencyHTML)
        DependencyHTMLWeb.hide()

        DSERComboBox.currentTextChanged.connect(lambda: self.toggleERView(DSERTable, EntityHTMLWeb, DependencyHTMLWeb))

        if DataSourceERTabFlag:
            # change tab in query
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    for query in DS.QueryList:
                        if query[1] == tabs.tabWidget:
                            query[1] = DSERTab
                            break

            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(DSERTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(DSERTab)
            tabs.tabWidget = DSERTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Entity Relationship", DSERTab, DataSourceWidgetItemName.text(0)))

            POSQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
            POSQueryTreeWidget.setText(0, "Entity Relationship (" + DataSourceWidgetItemName.text(0) + ")")

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    DS.setQuery(POSQueryTreeWidget, DSERTab)

            self.tabWidget.addTab(DSERTab, "Entity Relationship")
            self.tabWidget.setCurrentWidget(DSERTab)

    # Toggle POS View
    def toggleERView(self, Table, HTMLViewer1, HTMLViewer2):
        ComboBox = self.sender()

        if ComboBox.currentText() == "Show Table":
            HTMLViewer1.hide()
            HTMLViewer2.hide()
            Table.show()
        elif ComboBox.currentText() == "Show Dependency":
            HTMLViewer2.show()
            HTMLViewer1.hide()
            Table.hide()
        else:
            HTMLViewer1.show()
            Table.hide()
            HTMLViewer2.hide()

    # ****************************************************************************
    # *********************** Data Sources Topic Modelling ***********************
    # ****************************************************************************

    # Data Source Topic Modelling
    def DataSourceTopicModelling(self, DataSourceWidgetItemName):
        try:
            DataSourceTotalModellingTabFlag = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Topic Modelling':
                    DataSourceTotalModellingTabFlag = True
                    break

            TopicModellingTab = QWidget()
            TopicModellingTab.setGeometry(QtCore.QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.horizontalLayoutWidget.height()))
            TopicModellingTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Topic Modelling Tab
            TopicModellingTabVerticalLayoutWidget = QWidget(TopicModellingTab)
            TopicModellingTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Topic Modelling Tab
            TopicModellingTabVerticalLayout = QHBoxLayout(TopicModellingTabVerticalLayoutWidget)
            TopicModellingTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Data Source Topic Modelling HTML
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    dummyQuery = Query()
                    TopicModellingHTML = dummyQuery.TopicModelling(DS.DataSourcetext, 5)
                    break

            # Topic Modelling HTML Viewer
            TopicModellingHTMLWeb = QWebEngineView()
            TopicModellingTabVerticalLayout.addWidget(TopicModellingHTMLWeb)
            TopicModellingHTMLWeb.setHtml(TopicModellingHTML)

            if DataSourceTotalModellingTabFlag:
                # change tab in query
                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        for query in DS.QueryList:
                            if query[1] == tabs.tabWidget:
                                query[1] = TopicModellingTab
                                break

                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(TopicModellingTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(TopicModellingTab)
                tabs.tabWidget = TopicModellingTab
            else:
                # Adding Word Frequency Tab to TabList
                myFile.TabList.append(Tab("Topic Modelling", TopicModellingTab, DataSourceWidgetItemName.text(0)))

                # Adding Word Frequency Query
                WordFreqencyQueryTreeWidget = QTreeWidgetItem(self.QueryTreeWidget)
                WordFreqencyQueryTreeWidget.setText(0, "Topic Modelling (" + DataSourceWidgetItemName.text(0) + ")")

                # Adding Word Frequency Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                        DS.setQuery(WordFreqencyQueryTreeWidget, TopicModellingTab)

                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(TopicModellingTab, "Topic Modelling")
                self.tabWidget.setCurrentWidget(TopicModellingTab)

        except Exception as e:
            print(str(e))

    # ****************************************************************************
    # ************************ Data Sources Create Cases *************************
    # ****************************************************************************

    # Data Source Create Cases
    def DataSourceCreateCases(self, DataSourceWidgetItemName):
        DataSourceCreateCasesTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        CreateCasesPreviewTabverticalLayoutWidget = QWidget(DataSourceCreateCasesTab)
        CreateCasesPreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        CreateCasesPreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Data SourceTab
        CreateCasesverticalLayout = QVBoxLayout(CreateCasesPreviewTabverticalLayoutWidget)
        CreateCasesverticalLayout.setContentsMargins(0, 0, 0, 0)

        CreateCasesPreview = QTextEdit(CreateCasesPreviewTabverticalLayoutWidget)
        CreateCasesPreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        CreateCasesPreview.setReadOnly(True)

        CreateCasesPreview.setContextMenuPolicy(Qt.CustomContextMenu)
        CreateCasesPreview.customContextMenuRequested.connect(
            lambda checked, index=QtGui.QContextMenuEvent: self.CreateCasesContextMenu(index, DataSourceWidgetItemName))

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                CreateCasesPreview.setText(DS.DataSourcetext)
                break

        self.tabWidget.addTab(DataSourceCreateCasesTab, "Create Cases")
        self.tabWidget.setCurrentWidget(DataSourceCreateCasesTab)

    # Data Source Create Cases Context Menu
    def CreateCasesContextMenu(self, TextEditRightClickEvent, DataSourceWidgetItemName):
        TextEdit = self.sender()
        TextCursor = TextEdit.textCursor()

        if TextCursor.selectionStart() == TextCursor.selectionEnd():
            pass
        else:
            CasesSelectedTextClickMenu = QMenu(TextEdit)

            # Create Cases
            CreateCase = QAction('Create Case', TextEdit)
            CreateCase.triggered.connect(lambda: self.CreateCaseDialog(TextCursor.selectedText(), DataSourceWidgetItemName))
            CasesSelectedTextClickMenu.addAction(CreateCase)

            # Add to Case / Append
            AddToCase = QAction('Add to Case', TextEdit)
            AddToCase.triggered.connect(lambda: self.AddtoCaseDialog(TextCursor.selectedText(), DataSourceWidgetItemName))
            AddToCase.setEnabled(False)
            CasesSelectedTextClickMenu.addAction(AddToCase)

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    if len(DS.CasesList) > 0:
                        AddToCase.setEnabled(True)
                        break

            CasesSelectedTextClickMenu.popup(TextEdit.cursor().pos())

    # Create Case onClick
    def CreateCaseDialog(self, selectedText, DataSourceWidgetItemName):
        CreateCaseDialogBox = QDialog()
        CreateCaseDialogBox.setModal(True)
        CreateCaseDialogBox.setWindowTitle("Create New Case")
        CreateCaseDialogBox.setParent(self)
        CreateCaseDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        CreateCaseDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width*0.3,
                                                    self.height / 10)
        CreateCaseDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        CaseNameLabel = QLabel(CreateCaseDialogBox)
        CaseNameLabel.setText("Case Name")
        CaseNameLabel.setGeometry(CreateCaseDialogBox.width() * 0.1,
                                  CreateCaseDialogBox.height() * 0.15,
                                  CreateCaseDialogBox.width()/4,
                                  CreateCaseDialogBox.height()/5)
        CaseNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(CaseNameLabel)

        CaseNameLineEdit = QLineEdit(CreateCaseDialogBox)
        CaseNameLineEdit.setGeometry(CreateCaseDialogBox.width() * 0.4,
                                       CreateCaseDialogBox.height() * 0.15,
                                       CreateCaseDialogBox.width() / 2,
                                       CreateCaseDialogBox.height() / 5)
        CaseNameLineEdit.setAlignment(Qt.AlignVCenter)
        self.LineEditSizeAdjustment(CaseNameLineEdit)

        CreateCaseButtonBox = QDialogButtonBox(CreateCaseDialogBox)
        CreateCaseButtonBox.setGeometry(CreateCaseDialogBox.width() * 0.4, CreateCaseDialogBox.height() * 0.5,
                                        CreateCaseDialogBox.width() / 2, CreateCaseDialogBox.height()/2)
        CreateCaseButtonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        CreateCaseButtonBox.button(QDialogButtonBox.Ok).setText('Create')
        CreateCaseButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(CreateCaseButtonBox)

        CaseNameLineEdit.textChanged.connect(lambda: self.OkButtonEnable(CreateCaseButtonBox, True))

        CreateCaseButtonBox.accepted.connect(CreateCaseDialogBox.accept)
        CreateCaseButtonBox.rejected.connect(CreateCaseDialogBox.reject)

        CreateCaseButtonBox.accepted.connect(lambda : self.CreateCaseClick(CaseNameLineEdit.text(), selectedText, DataSourceWidgetItemName))

        CreateCaseDialogBox.exec_()

    # Case Create Click
    def CreateCaseClick(self, CaseTopic, selectedText, DataSourceWidgetItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                DS.CreateCase(CaseTopic, selectedText)
                break

        if not DS.CasesNameConflict:
            if (len(DS.CasesList) == 1):
                DSCaseWidget = QTreeWidgetItem(self.CasesTreeWidget)
                DSCaseWidget.setText(0, DS.DataSourceName)
                DSCaseWidget.setExpanded(True)

            ItemsWidget = self.CasesTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly, 0)

            for widgets in ItemsWidget:
                DSNewCaseNode = QTreeWidgetItem(widgets)
                DSNewCaseNode.setText(0, CaseTopic)
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

    # Add to Case onClick
    def AddtoCaseDialog(self, selectedText, DataSourceWidgetItemName):
        AddtoCaseDialogBox = QDialog()
        AddtoCaseDialogBox.setModal(True)
        AddtoCaseDialogBox.setWindowTitle("Add to Case")
        AddtoCaseDialogBox.setParent(self)
        AddtoCaseDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        AddtoCaseDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width * 0.3,
                                       self.height / 10)
        AddtoCaseDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        AddtoCaseLabel = QLabel(AddtoCaseDialogBox)
        AddtoCaseLabel.setText("Case Name")
        AddtoCaseLabel.setGeometry(AddtoCaseDialogBox.width() * 0.1,
                                   AddtoCaseDialogBox.height() * 0.15,
                                   AddtoCaseDialogBox.width() / 4,
                                   AddtoCaseDialogBox.height() / 5)
        AddtoCaseLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(AddtoCaseLabel)

        AddtoCaseComboBox = QComboBox(AddtoCaseDialogBox)
        AddtoCaseComboBox.setGeometry(AddtoCaseDialogBox.width() * 0.4,
                                      AddtoCaseDialogBox.height() * 0.15,
                                      AddtoCaseDialogBox.width() / 2,
                                      AddtoCaseDialogBox.height() / 5)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                for cases in DS.CasesList:
                    AddtoCaseComboBox.addItem(cases.CaseTopic)
                break

        self.LineEditSizeAdjustment(AddtoCaseComboBox)

        AddtoCaseButtonBox = QDialogButtonBox(AddtoCaseDialogBox)
        AddtoCaseButtonBox.setGeometry(AddtoCaseDialogBox.width() * 0.4, AddtoCaseDialogBox.height() * 0.5,
                                       AddtoCaseDialogBox.width() / 2, AddtoCaseDialogBox.height() / 2)
        AddtoCaseButtonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        AddtoCaseButtonBox.button(QDialogButtonBox.Ok).setText('Add')
        self.LineEditSizeAdjustment(AddtoCaseButtonBox)

        AddtoCaseButtonBox.accepted.connect(AddtoCaseDialogBox.accept)
        AddtoCaseButtonBox.rejected.connect(AddtoCaseDialogBox.reject)

        AddtoCaseButtonBox.accepted.connect(
            lambda: self.AddtoCaseClick(AddtoCaseComboBox.currentText(), selectedText, DataSourceWidgetItemName))

        AddtoCaseDialogBox.exec_()

    # Case Create Click
    def AddtoCaseClick(self, CaseTopic, selectedText, DataSourceWidgetItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                for cases in DS.CasesList:
                    if cases.CaseTopic == CaseTopic:
                        cases.addtoCase(selectedText)
                        break

    # ****************************************************************************
    # ********************* Data Sources Create Sentiments ***********************
    # ****************************************************************************

    # Data Source Create Sentiments
    def DataSourceCreateSentiments(self, DataSourceWidgetItemName):
        DataSourceCreateSentimentsTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        CreateSentimentsPreviewTabverticalLayoutWidget = QWidget(DataSourceCreateSentimentsTab)
        CreateSentimentsPreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        CreateSentimentsPreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

        # Box Layout for Data SourceTab
        CreateSentimentsverticalLayout = QVBoxLayout(CreateSentimentsPreviewTabverticalLayoutWidget)
        CreateSentimentsverticalLayout.setContentsMargins(0, 0, 0, 0)

        CreateSentimentsPreview = QTextEdit(CreateSentimentsPreviewTabverticalLayoutWidget)
        CreateSentimentsPreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
        CreateSentimentsPreview.setReadOnly(True)

        CreateSentimentsPreview.setContextMenuPolicy(Qt.CustomContextMenu)
        CreateSentimentsPreview.customContextMenuRequested.connect(
            lambda checked, index=QtGui.QContextMenuEvent: self.CreateSentimentsContextMenu(index, DataSourceWidgetItemName))

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                CreateSentimentsPreview.setText(DS.DataSourcetext)
                break

        self.tabWidget.addTab(DataSourceCreateSentimentsTab, "Create Sentiments")
        self.tabWidget.setCurrentWidget(DataSourceCreateSentimentsTab)

    # Data Source Create Sentiments Context Menu
    def CreateSentimentsContextMenu(self, TextEditRightClickEvent, DataSourceWidgetItemName):
        TextEdit = self.sender()
        TextCursor = TextEdit.textCursor()

        if TextCursor.selectionStart() == TextCursor.selectionEnd():
            pass
        else:
            SentimentsSelectedTextClickMenu = QMenu(TextEdit)

            # Add to Case / Append
            AddToSentiment = QAction('Add Sentiment', TextEdit)
            AddToSentiment.triggered.connect(
                lambda: self.AddtoSentimentsDialog(TextCursor.selectedText(), DataSourceWidgetItemName))
            SentimentsSelectedTextClickMenu.addAction(AddToSentiment)

            SentimentsSelectedTextClickMenu.popup(TextEdit.cursor().pos())

    # Add to Case onClick
    def AddtoSentimentsDialog(self, selectedText, DataSourceWidgetItemName):
        AddtoSentimentsDialogBox = QDialog()
        AddtoSentimentsDialogBox.setModal(True)
        AddtoSentimentsDialogBox.setWindowTitle("Add to Sentiments")
        AddtoSentimentsDialogBox.setParent(self)
        AddtoSentimentsDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        AddtoSentimentsDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width * 0.3,
                                       self.height / 10)
        AddtoSentimentsDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        AddtoSentimentsLabel = QLabel(AddtoSentimentsDialogBox)
        AddtoSentimentsLabel.setText("Sentiment")
        AddtoSentimentsLabel.setGeometry(AddtoSentimentsDialogBox.width() * 0.1,
                                         AddtoSentimentsDialogBox.height() * 0.15,
                                         AddtoSentimentsDialogBox.width() / 4,
                                         AddtoSentimentsDialogBox.height() / 5)
        AddtoSentimentsLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(AddtoSentimentsLabel)

        AddtoSentimentsComboBox = QComboBox(AddtoSentimentsDialogBox)
        AddtoSentimentsComboBox.setGeometry(AddtoSentimentsDialogBox.width() * 0.4,
                                            AddtoSentimentsDialogBox.height() * 0.15,
                                            AddtoSentimentsDialogBox.width() / 2,
                                            AddtoSentimentsDialogBox.height() / 5)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                for sentiments in DS.SentimentList:
                    AddtoSentimentsComboBox.addItem(sentiments.SentimentType)
                break

        self.LineEditSizeAdjustment(AddtoSentimentsComboBox)

        AddtoSentimentsButtonBox = QDialogButtonBox(AddtoSentimentsDialogBox)
        AddtoSentimentsButtonBox.setGeometry(AddtoSentimentsDialogBox.width() * 0.4, AddtoSentimentsDialogBox.height() * 0.5,
                                       AddtoSentimentsDialogBox.width() / 2, AddtoSentimentsDialogBox.height() / 2)
        AddtoSentimentsButtonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        AddtoSentimentsButtonBox.button(QDialogButtonBox.Ok).setText('Add')
        self.LineEditSizeAdjustment(AddtoSentimentsButtonBox)

        AddtoSentimentsButtonBox.accepted.connect(AddtoSentimentsDialogBox.accept)
        AddtoSentimentsButtonBox.rejected.connect(AddtoSentimentsDialogBox.reject)

        AddtoSentimentsButtonBox.accepted.connect(
            lambda: self.AddtoSentimentsClick(AddtoSentimentsComboBox.currentText(), selectedText, DataSourceWidgetItemName))

        AddtoSentimentsDialogBox.exec_()

    # Add to Sentiments Click
    def AddtoSentimentsClick(self, SentimentType, selectedText, DataSourceWidgetItemName):
        NewWidgetAddFlagList = []

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                for sentiments in DS.SentimentList:
                    if len(sentiments.SentimentTextList) == 0:
                        NewWidgetAddFlagList.append(True)
                    else:
                        NewWidgetAddFlagList.append(False)

        if all([ v for v in NewWidgetAddFlagList]) :
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    DSSentimentWidget = QTreeWidgetItem(self.SentimentTreeWidget)
                    DSSentimentWidget.setText(0, DS.DataSourceName)
                    DSSentimentWidget.setToolTip(0, DSSentimentWidget.text(0))
                    DSSentimentWidget.setExpanded(True)

                    ItemsWidget = self.SentimentTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly, 0)

                    for widgets in ItemsWidget:
                        for sentiments in DS.SentimentList:
                            DSNewSentimentNode = QTreeWidgetItem(widgets)
                            DSNewSentimentNode.setText(0, sentiments.SentimentType)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                for sentiments in DS.SentimentList:
                    if sentiments.SentimentType == SentimentType:
                        sentiments.addSentiment(selectedText)
                        break

    # ****************************************************************************
    # *************************** Data Sources Sumary ****************************
    # ****************************************************************************

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

        if SummarizeDSComboBox.currentText() != None:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == SummarizeDSComboBox.currentText():
                    SummarizeWord.setMaximum(len(DS.DataSourcetext.split()))
                    SummarizeWord.setMinimum(round(len(DS.DataSourcetext.split()) / 5))
                    SummarizeWord.setValue(SummarizeWord.minimum())
                    SummarizeMaxWord.setText("(Max. Words: " + str(len(DS.DataSourcetext.split())) + ")")
                    self.LabelSizeAdjustment(SummarizeMaxWord)
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


    # ****************************************************************************
    # ************************ Data Sources Translation **************************
    # ****************************************************************************

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


    # ****************************************************************************
    # *************************** Data Source Remove *****************************
    # ****************************************************************************

    #Data Source Remove
    def DataSourceRemove(self, DataSourceWidgetItemName):
        DataSourceRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this file? Doing this will remove all Queries of " + DataSourceWidgetItemName.text(0),
                                                      QMessageBox.Yes | QMessageBox.No)

        if DataSourceRemoveChoice == QMessageBox.Yes:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    if DataSourceWidgetItemName.parent().childCount() == 1:
                        DataSourceWidgetItemName.parent().setHidden(True)

                    DataSourceWidgetItemName.parent().removeChild(DataSourceWidgetItemName)

                    count = len(DS.QueryList)

                    for query in range(count):
                        self.QueryRemove(DS.QueryList[0][0])

                    myFile.DataSourceList.remove(DS)
                    DS.__del__()
                    break

            self.DataSourceSimilarityUpdate()

        else:
            pass

    # ****************************************************************************
    # ************************* Data Source Child Detail *************************
    # ****************************************************************************

    # Data Source Child Detail
    def DataSourceChildDetail(self, DataSourceWidgetItemName):
        try:
            DataSourceWidgetDetailDialogBox = QDialog()
            DataSourceWidgetDetailDialogBox.setModal(True)
            DataSourceWidgetDetailDialogBox.setWindowTitle("Details")
            DataSourceWidgetDetailDialogBox.setParent(self)

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    break

            if DS.DataSourceext == "Doc files (*.doc *.docx)" or DS.DataSourceext == "Pdf files (*.pdf)" or DS.DataSourceext == "Notepad files (*.txt)" or DS.DataSourceext == "Rich Text Format files (*.rtf)" or DS.DataSourceext == "Audio files (*.wav *.mp3)":
                DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width/3,
                                                            self.height*2/5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

                #************************************** Labels *************************************

                # Data Source Name Label
                DataSourceNameLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNameLabel.setText("Name:")
                DataSourceNameLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.1,
                                                DataSourceWidgetDetailDialogBox.width()/4,
                                                DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameLabel)

                # Data Source Path Label
                DataSourcePathLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourcePathLabel.setText("Path:")
                DataSourcePathLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.2,
                                                DataSourceWidgetDetailDialogBox.width()/4,
                                                DataSourceWidgetDetailDialogBox.height()/20)
                DataSourcePathLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourcePathLabel)

                # Data Source Ext Label
                DataSourceExtLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceExtLabel.setText("Extension:")
                DataSourceExtLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                               DataSourceWidgetDetailDialogBox.height() * 0.3,
                                               DataSourceWidgetDetailDialogBox.width()/4,
                                               DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceExtLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceExtLabel)

                # Data Source Size Label
                DataSourceSize = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceSize.setText("Size:")
                DataSourceSize.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                           DataSourceWidgetDetailDialogBox.height() * 0.4,
                                           DataSourceWidgetDetailDialogBox.width()/4,
                                           DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceSize.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceSize)


                # Data Source Access Time Label
                DataSourceAccessTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceAccessTime.setText("Last Access Time:")
                DataSourceAccessTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                 DataSourceWidgetDetailDialogBox.height() * 0.5,
                                                 DataSourceWidgetDetailDialogBox.width()/4,
                                                 DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceAccessTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceAccessTime)

                # Data Source Modified Time Label
                DataSourceModifiedTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceModifiedTime.setText("Last Modified Time:")
                DataSourceModifiedTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.width()/4,
                                                   DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceModifiedTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceModifiedTime)

                # Data Source Change Time Label
                DataSourceChangeTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceChangeTime.setText("Created Time:")
                DataSourceChangeTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                 DataSourceWidgetDetailDialogBox.height() * 0.7,
                                                 DataSourceWidgetDetailDialogBox.width()/4,
                                                 DataSourceWidgetDetailDialogBox.height()/20)
                DataSourceChangeTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceChangeTime)
    
                # Data Source Word Count Label
                DataSourceWordCount = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceWordCount.setText("Total Words:")
                DataSourceWordCount.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceWordCount.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceWordCount)
    
                # ************************************** LineEdit *************************************
    
                # Data Source Name LineEdit
                DataSourceNameLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceNameLineEdit.setText(DS.DataSourceName)
                DataSourceNameLineEdit.setReadOnly(True)
                DataSourceNameLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNameLineEdit)
    
                # Data Source Path LineEdit
                DataSourcePathLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourcePathLineEdit.setText(DS.DataSourcePath)
                DataSourcePathLineEdit.setReadOnly(True)
                DataSourcePathLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.2,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourcePathLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourcePathLineEdit)
    
                # Data Source Ext LineEdit
                DataSourceExtLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceExtLineEdit.setText(os.path.splitext(DS.DataSourcePath)[1])
                DataSourceExtLineEdit.setReadOnly(True)
                DataSourceExtLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                  DataSourceWidgetDetailDialogBox.height() * 0.3,
                                                  DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                  DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceExtLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceExtLineEdit)
    
                # Data Source Size LineEdit
                DataSourceSizeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceSizeLineEdit.setText(size(DS.DataSourceSize))
                DataSourceSizeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceSizeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceSizeLineEdit)
    
                # Data Source Access Time LineEdit
                DataSourceAccessTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceAccessTimeLineEdit.setText(DS.DataSourceAccessTime)
                DataSourceAccessTimeLineEdit.setReadOnly(True)
                DataSourceAccessTimeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.height() * 0.5,
                                                         DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceAccessTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceAccessTimeLineEdit)
    
                # Data Source Modified Time LineEdit
                DataSourceModifiedTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceModifiedTimeLineEdit.setText(DS.DataSourceModifiedTime)
                DataSourceModifiedTimeLineEdit.setReadOnly(True)
                DataSourceModifiedTimeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                           DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceModifiedTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceModifiedTimeLineEdit)
    
                # Data Source Change Time LineEdit
                DataSourceChangeTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceChangeTimeLineEdit.setText(DS.DataSourceChangeTime)
                DataSourceChangeTimeLineEdit.setReadOnly(True)
                DataSourceChangeTimeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.height() * 0.7,
                                                         DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceChangeTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceChangeTimeLineEdit)
    
                # Data Source Word Count LineEdit
                DataSourceWordCountLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext)))
                DataSourceWordCountLineEdit.setReadOnly(True)
                DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                        DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                        DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)
    
                DataSourceWidgetDetailDialogBox.exec_()

            elif DS.DataSourceext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":
                print("Hello")
            elif DS.DataSourceext == "URL":
                DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

                # Data Source Label
                DataSourceLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceLabel.setText("Type:")
                DataSourceLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                            DataSourceWidgetDetailDialogBox.height() * 0.2,
                                            DataSourceWidgetDetailDialogBox.width() / 4,
                                            DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceLabel)

                # Data Source URL Label
                DataSourceNameURLLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNameURLLabel.setText("URL:")
                DataSourceNameURLLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                   DataSourceWidgetDetailDialogBox.width() / 4,
                                                   DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNameURLLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameURLLabel)

                # Data Source Word Count Label
                DataSourceWordCountLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceWordCountLabel.setText("Word Count:")
                DataSourceWordCountLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                     DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                     DataSourceWidgetDetailDialogBox.width() / 4,
                                                     DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceWordCountLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceWordCountLabel)

                # ************************************** LineEdit *************************************

                # Data Source Name LineEdit
                DataSourceLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceLineEdit.setText("Web URL")
                DataSourceLineEdit.setReadOnly(True)
                DataSourceLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                               DataSourceWidgetDetailDialogBox.height() * 0.2,
                                               DataSourceWidgetDetailDialogBox.width() * 0.6,
                                               DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceLineEdit)

                # Data Source URL LineEdit
                DataSourceURLLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceURLLineEdit.setText(DS.DataSourcePath)
                DataSourceURLLineEdit.setReadOnly(True)
                DataSourceURLLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                  DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                  DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                  DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceURLLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceURLLineEdit)

                # Data Source Word Count LineEdit
                DataSourceWordCountLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext)))
                DataSourceWordCountLineEdit.setReadOnly(True)
                DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                        DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()

            elif DS.DataSourceext == "Tweet":
                DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

                # Data Source  Label
                DataSourceLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceLabel.setText("Type:")
                DataSourceLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                            DataSourceWidgetDetailDialogBox.height() * 0.2,
                                            DataSourceWidgetDetailDialogBox.width() / 4,
                                            DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceLabel)

                # Data Source Hashtag Label
                DataSourceNameHashtagLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNameHashtagLabel.setText("Hashtag:")
                DataSourceNameHashtagLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                       DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                       DataSourceWidgetDetailDialogBox.width() / 4,
                                                       DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNameHashtagLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameHashtagLabel)

                # Data Source No of Tweet Label
                DataSourceNoofTweetLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNoofTweetLabel.setText("No of Tweets:")
                DataSourceNoofTweetLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                     DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                     DataSourceWidgetDetailDialogBox.width() / 4,
                                                     DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofTweetLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNoofTweetLabel)


                # ************************************** LineEdit *************************************

                # Data Source Name LineEdit
                DataSourceLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceLineEdit.setText("Twitter")
                DataSourceLineEdit.setReadOnly(True)
                DataSourceLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                               DataSourceWidgetDetailDialogBox.height() * 0.2,
                                               DataSourceWidgetDetailDialogBox.width() * 0.6,
                                               DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceLineEdit)

                # Data Source Path LineEdit
                DataSourceHashTagLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceHashTagLineEdit.setText(DS.DataSourceHashtag)
                DataSourceHashTagLineEdit.setReadOnly(True)
                DataSourceHashTagLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                      DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                      DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                      DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceHashTagLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceHashTagLineEdit)

                # Data Source Ext LineEdit
                DataSourceNoofTweetsLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceNoofTweetsLineEdit.setText(str(len(DS.TweetData)))
                DataSourceNoofTweetsLineEdit.setReadOnly(True)
                DataSourceNoofTweetsLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofTweetsLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNoofTweetsLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()

            elif DS.DataSourceext == "Youtube":
                DataSourceWidgetDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

                # Data Source Label
                DataSourceLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceLabel.setText("Type:")
                DataSourceLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                            DataSourceWidgetDetailDialogBox.height() * 0.2,
                                            DataSourceWidgetDetailDialogBox.width() / 4,
                                            DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceLabel)

                # Data Source URL Label
                DataSourceNameURLLabel = QLabel(DataSourceWidgetDetailDialogBox)

                if hasattr(DS, 'YoutubeURLFlag'):
                    DataSourceNameURLLabel.setText("URL:")
                else:
                    DataSourceNameURLLabel.setText("Key Word:")

                DataSourceNameURLLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                   DataSourceWidgetDetailDialogBox.width() / 4,
                                                   DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNameURLLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameURLLabel)

                # Data Source No of Comments Label
                DataSourceNoofCommentsLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNoofCommentsLabel.setText("No of Comments:")
                DataSourceNoofCommentsLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                        DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.width() / 4,
                                                        DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofCommentsLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNoofCommentsLabel)

                # ************************************** LineEdit *************************************

                # Data Source Name LineEdit
                DataSourceLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceLineEdit.setText("Youtube Comments")
                DataSourceLineEdit.setReadOnly(True)
                DataSourceLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                               DataSourceWidgetDetailDialogBox.height() * 0.2,
                                               DataSourceWidgetDetailDialogBox.width() * 0.6,
                                               DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceLineEdit)

                # Data Source URL LineEdit
                DataSourceURLLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceURLLineEdit.setText(DS.DataSourcePath)
                DataSourceURLLineEdit.setReadOnly(True)
                DataSourceURLLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                  DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                  DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                  DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceURLLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceURLLineEdit)

                # Data Source Word Count LineEdit
                DataSourceNoofCommentsLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceNoofCommentsLineEdit.setText(str(len(DS.YoutubeData)))
                DataSourceNoofCommentsLineEdit.setReadOnly(True)
                DataSourceNoofCommentsLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                           DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofCommentsLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNoofCommentsLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()


        except Exception as e:
            print(str(e))

    # ****************************************************************************
    # ********************* Data Source Create Dashboard *************************
    # ****************************************************************************

    def DataSourcesCreateDashboardDialog(self):
        DataSourcesCreateDashboardDialog = QDialog()
        DataSourcesCreateDashboardDialog.setWindowTitle("Create Dashboard")
        DataSourcesCreateDashboardDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                       self.height / 10)
        DataSourcesCreateDashboardDialog.setParent(self)
        DataSourcesCreateDashboardDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        DataSourcesCreateDashboardDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(DataSourcesCreateDashboardDialog)
        DataSourcelabel.setGeometry(DataSourcesCreateDashboardDialog.width() * 0.125,
                                    DataSourcesCreateDashboardDialog.height() * 0.2,
                                    DataSourcesCreateDashboardDialog.width() / 4,
                                    DataSourcesCreateDashboardDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourcesCreateDashboardDialog)
        DSComboBox.setGeometry(DataSourcesCreateDashboardDialog.width() * 0.4,
                               DataSourcesCreateDashboardDialog.height() * 0.2,
                               DataSourcesCreateDashboardDialog.width() / 2,
                               DataSourcesCreateDashboardDialog.height() / 10)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        DataSourcesCreateDashboardbuttonBox = QDialogButtonBox(DataSourcesCreateDashboardDialog)
        DataSourcesCreateDashboardbuttonBox.setGeometry(DataSourcesCreateDashboardDialog.width() * 0.125,
                                                     DataSourcesCreateDashboardDialog.height() * 0.7,
                                                     DataSourcesCreateDashboardDialog.width() * 3 / 4,
                                                     DataSourcesCreateDashboardDialog.height() / 5)
        DataSourcesCreateDashboardbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourcesCreateDashboardbuttonBox.button(QDialogButtonBox.Ok).setText('Show')

        if len(myFile.DataSourceList) == 0:
            DataSourcesCreateDashboardbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            if len(myFile.DataSourceList) > 1:
                DSComboBox.addItem("All")
            for DS in myFile.DataSourceList:
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DataSourcesCreateDashboardbuttonBox)

        DataSourcesCreateDashboardbuttonBox.accepted.connect(DataSourcesCreateDashboardDialog.accept)
        DataSourcesCreateDashboardbuttonBox.rejected.connect(DataSourcesCreateDashboardDialog.reject)

        DataSourcesCreateDashboardbuttonBox.accepted.connect(
            lambda: self.DataSourcesCreateDashboard(DSComboBox.currentText()))

        DataSourcesCreateDashboardDialog.exec()

    def DataSourcesCreateDashboard(self, DataSourceName):
        print("Hello")

    # ****************************************************************************
    # ****************************** Enable/Disable ******************************
    # ****************************************************************************

    # Enable Ok Button (Line Edit)
    def OkButtonEnable(self, ButtonBox, check):
        LineEdit = self.sender()
        if check:
            if len(LineEdit.text()) > 0 and LineEdit.isEnabled():
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            if len(LineEdit.text()) > 0 and LineEdit.isEnabled():
                ButtonBox.setEnabled(True)
            else:
                ButtonBox.setEnabled(False)

    # Enable Ok Button (Combo Box)
    def OkButtonEnableCombo(self, ComboBox, ButtonBox):
        if len(ComboBox.currentText()) == 0:
            ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)

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
                self.LabelSizeAdjustment(SummarizeMaxWord)

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

    # Ok Button Enable on Youtube Radio Button Toggling
    def EnableOkonYoutubeRadioButtonToggle(self, RadioButton, FirstLineEdit, SecondLineEdit, ButtonBox):
        Button = self.sender()
        if Button.isChecked():
            FirstLineEdit.setEnabled(True)
            SecondLineEdit.setEnabled(False)

            if(len(FirstLineEdit.text()) > 0):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)

        elif RadioButton.isChecked():
            FirstLineEdit.setEnabled(False)
            SecondLineEdit.setEnabled(True)

            if (len(SecondLineEdit.text()) > 0):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    
    # ****************************************************************************
    # *************************** Query Context Menu *****************************
    # ****************************************************************************

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

    # ****************************************************************************
    # *************************** Cases Context Menu *****************************
    # ****************************************************************************

    # Get Which Cases Widget Item and its Position
    def FindCasesTreeWidgetContextMenu(self, CasesMouseRightClickEvent):
        try:
            if CasesMouseRightClickEvent.reason == CasesMouseRightClickEvent.Mouse:
                CasesMouseRightClickPos = CasesMouseRightClickEvent.globalPos()
                CasesMouseRightClickItem = self.CasesTreeWidget.itemAt(CasesMouseRightClickEvent.pos())
            else:
                CasesMouseRightClickPos = None
                Casesselection = self.CasesTreeWidget.selectedItems()

                if Casesselection:
                    CasesMouseRightClickItem = Casesselection[0]
                else:
                    CasesMouseRightClickItem = self.CasesTreeWidget.currentItem()
                    if CasesMouseRightClickItem is None:
                        CasesMouseRightClickItem = self.CasesTreeWidget.invisibleRootItem().child(0)
                if CasesMouseRightClickItem is not None:
                    CasesParent = CasesMouseRightClickItem.parent()
                    while CasesParent is not None:
                        CasesParent.setExpanded(True)
                        CasesParent = CasesParent.parent()
                    Casesitemrect = self.CasesTreeWidget.visualItemRect(CasesMouseRightClickItem)
                    Casesportrect = self.CasesTreeWidget.viewport().rect()
                    if not Casesportrect.contains(Casesitemrect.topLeft()):
                        self.CasesTreeWidget.scrollToItem(CasesMouseRightClickItem, QTreeWidget.PositionAtCenter)
                        Casesitemrect = self.CasesTreeWidget.visualItemRect(CasesMouseRightClickItem)

                    Casesitemrect.setLeft(Casesportrect.left())
                    Casesitemrect.setWidth(Casesportrect.width())
                    CasesMouseRightClickPos = self.CasesTreeWidget.mapToGlobal(Casesitemrect.center())

            if CasesMouseRightClickPos is not None:
                self.CasesTreeWidgetContextMenu(CasesMouseRightClickItem, CasesMouseRightClickPos)
        except Exception as e:
            print(str(e))

    # Setting ContextMenu on Clicked Query
    def CasesTreeWidgetContextMenu(self, CasesItemName, CasesWidgetPos):
        # Parent Data Source
        if CasesItemName.parent() == None:
            CasesRightClickMenu = QMenu(self.CasesTreeWidget)

            # Cases Expand
            CasesExpand = QAction('Expand', self.CasesTreeWidget)
            CasesExpand.triggered.connect(
                lambda checked, index=CasesItemName: self.DataSourceWidgetItemExpandCollapse(index))
            if (CasesItemName.childCount() == 0 or CasesItemName.isExpanded() == True):
                CasesExpand.setDisabled(True)
            else:
                CasesExpand.setDisabled(False)
            CasesRightClickMenu.addAction(CasesExpand)

            # Cases Collapse
            CasesCollapse = QAction('Collapse', self.CasesTreeWidget)
            CasesCollapse.triggered.connect(
                lambda checked, index=CasesItemName: self.DataSourceWidgetItemExpandCollapse(index))

            if (CasesItemName.childCount() == 0 or CasesItemName.isExpanded() == False):
                CasesCollapse.setDisabled(True)
            else:
                CasesCollapse.setDisabled(False)
            CasesRightClickMenu.addAction(CasesCollapse)

            # Cases Detail
            CasesDetail = QAction('Details', self.CasesTreeWidget)
            CasesDetail.triggered.connect(lambda: self.CasesParentDetail(CasesItemName))
            CasesRightClickMenu.addAction(CasesDetail)
            CasesRightClickMenu.popup(CasesWidgetPos)

        # Child DataSource
        else:
            CasesRightClickMenu = QMenu(self.CasesTreeWidget)

            # Case Show components
            CasesShowTopicText = QAction('Show Topic Components', self.CasesTreeWidget)
            CasesShowTopicText.triggered.connect(lambda: self.CasesShowTopicComponent(CasesItemName))
            CasesRightClickMenu.addAction(CasesShowTopicText)

            # Case Rename
            CasesRemove = QAction('Rename', self.CasesTreeWidget)
            CasesRemove.triggered.connect(lambda: self.CasesRename(CasesItemName))
            CasesRightClickMenu.addAction(CasesRemove)

            # Case Remove
            CasesRemove = QAction('Remove', self.CasesTreeWidget)
            CasesRemove.triggered.connect(lambda: self.CasesRemove(CasesItemName))
            CasesRightClickMenu.addAction(CasesRemove)

            # Case Child Detail
            CasesDetail = QAction('Details', self.CasesTreeWidget)
            CasesDetail.triggered.connect(lambda: self.CasesChildDetail(CasesItemName))
            CasesRightClickMenu.addAction(CasesDetail)

            CasesRightClickMenu.popup(CasesWidgetPos)

    # Cases Parent Detail
    def CasesParentDetail(self, CasesItemName):
        CasesParentDetailDialogBox = QDialog()
        CasesParentDetailDialogBox.setModal(True)
        CasesParentDetailDialogBox.setWindowTitle("Details")
        CasesParentDetailDialogBox.setParent(self)
        CasesParentDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        CasesParentDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width / 3,
                                                    self.height / 10)
        CasesParentDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.text(0):
                break

        # ************************************** Labels *************************************

        # Data Source Name Label
        DataSourceNameLabel = QLabel(CasesParentDetailDialogBox)
        DataSourceNameLabel.setText("Name:")
        DataSourceNameLabel.setGeometry(CasesParentDetailDialogBox.width() * 0.1,
                                        CasesParentDetailDialogBox.height() * 0.2,
                                        CasesParentDetailDialogBox.width() / 4,
                                        CasesParentDetailDialogBox.height() / 5)
        DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNameLabel)

        # Data Source Path Label
        DataSourceNoofCasesLabel = QLabel(CasesParentDetailDialogBox)
        DataSourceNoofCasesLabel.setText("No of Cases")
        DataSourceNoofCasesLabel.setGeometry(CasesParentDetailDialogBox.width() * 0.1,
                                             CasesParentDetailDialogBox.height() * 0.6,
                                             CasesParentDetailDialogBox.width() / 4,
                                             CasesParentDetailDialogBox.height() / 5)
        DataSourceNoofCasesLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNoofCasesLabel)

        # ************************************** LineEdit *************************************

        # Data Source Name LineEdit
        DataSourceNameLineEdit = QLineEdit(CasesParentDetailDialogBox)
        DataSourceNameLineEdit.setText(CasesItemName.text(0))
        DataSourceNameLineEdit.setReadOnly(True)
        DataSourceNameLineEdit.setGeometry(CasesParentDetailDialogBox.width() * 0.35,
                                           CasesParentDetailDialogBox.height() * 0.2,
                                           CasesParentDetailDialogBox.width() * 0.6,
                                           CasesParentDetailDialogBox.height() / 5)
        DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNameLineEdit)

        # Data Source Path LineEdit
        DataSourceNoofCasesLineEdit = QLineEdit(CasesParentDetailDialogBox)
        DataSourceNoofCasesLineEdit.setText(str(len(DS.CasesList)))
        DataSourceNoofCasesLineEdit.setReadOnly(True)
        DataSourceNoofCasesLineEdit.setGeometry(CasesParentDetailDialogBox.width() * 0.35,
                                                CasesParentDetailDialogBox.height() * 0.6,
                                                CasesParentDetailDialogBox.width() * 0.6,
                                                CasesParentDetailDialogBox.height() / 5)
        DataSourceNoofCasesLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNoofCasesLineEdit)

        CasesParentDetailDialogBox.exec_()

    # Cases Show Topic
    def CasesShowTopicComponent(self, CasesItemName):
        CaseShowComponentTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == CasesItemName.parent().text(0) and tabs.TabName == 'Case Show Topic Component':
                CaseShowComponentTabFlag = True
                break

        # Creating New Tab for Stem Word
        CaseShowComponentTab = QWidget()

        # LayoutWidget For within Stem Word Tab
        CaseShowComponentTabVerticalLayoutWidget = QWidget(CaseShowComponentTab)
        CaseShowComponentTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        CaseShowComponentTabVerticalLayout = QHBoxLayout(CaseShowComponentTabVerticalLayoutWidget)
        CaseShowComponentTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

        # 2nd LayoutWidget For within Stem Word Tab
        CaseShowComponentTabVerticalLayoutWidget2 = QWidget(CaseShowComponentTab)
        CaseShowComponentTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                              self.tabWidget.height() - self.tabWidget.height() / 10)

        # 2nd Box Layout for Stem Word Tab
        CaseShowComponentTabVerticalLayout2 = QVBoxLayout(CaseShowComponentTabVerticalLayoutWidget2)

        CaseShowComponentTable = QTableWidget(CaseShowComponentTabVerticalLayoutWidget2)
        CaseShowComponentTable.setColumnCount(5)
        CaseShowComponentTable.setGeometry(0, 0, CaseShowComponentTabVerticalLayoutWidget2.width(),
                                           CaseShowComponentTabVerticalLayoutWidget2.height())
        CaseShowComponentTable.setUpdatesEnabled(True)
        CaseShowComponentTable.setDragEnabled(True)
        CaseShowComponentTable.setMouseTracking(True)

        CaseShowComponentTable.setSizePolicy(self.sizePolicy)
        CaseShowComponentTable.setWindowFlags(
            CaseShowComponentTable.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        CaseShowComponentTable.setHorizontalHeaderLabels(
            ["Case", "Word Count", "Character Count", "Weighted Average", "Action"])
        CaseShowComponentTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(CaseShowComponentTable.columnCount()):
            CaseShowComponentTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            CaseShowComponentTable.horizontalHeaderItem(i).setFont(
                QFont(CaseShowComponentTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.parent().text(0):
                for cases in DS.CasesList:
                    if cases.CaseTopic == CasesItemName.text(0):
                        Case_List = cases.TopicCases
                        break

        if len(Case_List) != 0:
            for row in Case_List:
                CaseShowComponentTable.insertRow(Case_List.index(row))
                for item in row:
                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(item))
                    CaseShowComponentTable.setItem(Case_List.index(row), row.index(item), intItem)
                    CaseShowComponentTable.item(Case_List.index(row), row.index(item)).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    CaseShowComponentTable.item(Case_List.index(row), row.index(item)).setFlags(
                        Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    deleteButton = QPushButton("Remove")
                    deleteButton.clicked.connect(lambda: self.deleteComponentRow(CasesItemName, CaseShowComponentTable))
                    self.LabelSizeAdjustment(deleteButton)
                    CaseShowComponentTable.setCellWidget(Case_List.index(row), 4, deleteButton)


            CaseShowComponentTable.resizeColumnsToContents()
            CaseShowComponentTable.resizeRowsToContents()

            CaseShowComponentTable.setSortingEnabled(True)
            CaseShowComponentTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(CaseShowComponentTable.columnCount()):
                CaseShowComponentTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        if CaseShowComponentTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(CaseShowComponentTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(CaseShowComponentTab)
            tabs.tabWidget = CaseShowComponentTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(
                Tab("Case Show Topic Component", CaseShowComponentTab, CasesItemName.parent().text(0)))

            self.tabWidget.addTab(CaseShowComponentTab, "Case Show Topic Component")
            self.tabWidget.setCurrentWidget(CaseShowComponentTab)

    # Cases Remove Component Row
    def deleteComponentRow(self, CasesItemName, Table):
        try:
            button = self.sender()
            if button:
                row = Table.indexAt(button.pos()).row()
                temp = Table.item(row, 0)

                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == CasesItemName.parent().text(0):
                        for case in DS.CasesList:
                            if case.CaseTopic == CasesItemName.text(0):
                                for topicComponents in case.TopicCases:
                                    if temp.text() == topicComponents[0] and row == case.TopicCases.index(topicComponents):
                                        case.TopicCases.remove(topicComponents)
                                        break

                Table.removeRow(row)

        except Exception as e:
            print(str(e))

    # Cases Rename
    def CasesRename(self, CasesItemName):
        CaseRenameDialog = QDialog()
        CaseRenameDialog.setWindowTitle("Rename")
        CaseRenameDialog.setGeometry(self.width * 0.375, self.height * 0.425, self.width / 4, self.height * 0.15)
        CaseRenameDialog.setParent(self)
        CaseRenameDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        CaseRenameDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        RenameLabel = QLabel(CaseRenameDialog)
        RenameLabel.setGeometry(CaseRenameDialog.width() * 0.125, CaseRenameDialog.height() * 0.3,
                                CaseRenameDialog.width() / 4, CaseRenameDialog.height() * 0.15)
        RenameLabel.setText("Rename")
        RenameLabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(RenameLabel)

        RenameLineEdit = QLineEdit(CaseRenameDialog)
        RenameLineEdit.setGeometry(CaseRenameDialog.width() * 0.4, CaseRenameDialog.height() * 0.3,
                                   CaseRenameDialog.width() / 2, CaseRenameDialog.height() * 0.15)
        RenameLineEdit.setText(CasesItemName.text(0))
        self.LineEditSizeAdjustment(RenameLineEdit)

        RenamebuttonBox = QDialogButtonBox(CaseRenameDialog)
        RenamebuttonBox.setGeometry(CaseRenameDialog.width() * 0.125, CaseRenameDialog.height() * 0.7,
                                    CaseRenameDialog.width() * 3 / 4, CaseRenameDialog.height() / 5)
        RenamebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        RenamebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        RenameLineEdit.textChanged.connect(lambda: self.OkButtonEnable(RenamebuttonBox, True))

        RenamebuttonBox.accepted.connect(CaseRenameDialog.accept)
        RenamebuttonBox.rejected.connect(CaseRenameDialog.reject)

        RenamebuttonBox.accepted.connect(lambda: self.CRename(CasesItemName, RenameLineEdit.text()))

        CaseRenameDialog.exec()

    # Rename Data Source and Widget
    def CRename(self, CasesItemName, CaseName):
        CaseRenameCheck = False

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.parent().text(0):
                for case in DS.CasesList:
                    if case.CaseTopic == CaseName:
                        CaseRenameCheck = True
                        break

        if not CaseRenameCheck:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.parent().text(0):
                    for case in DS.CasesList:
                        if case.CaseTopic == CasesItemName.text(0):
                            case.CaseTopic = CaseName
                            break

            CasesItemName.setText(0, CaseName)
            CasesItemName.setToolTip(0, CasesItemName.text(0))

            CasesRenameSuccessBox = QMessageBox()
            CasesRenameSuccessBox.setIcon(QMessageBox.Information)
            CasesRenameSuccessBox.setWindowTitle("Rename Success")
            CasesRenameSuccessBox.setText("Case Rename Successfully!")
            CasesRenameSuccessBox.setStandardButtons(QMessageBox.Ok)
            CasesRenameSuccessBox.exec_()

        else:
            CaseRenameErrorBox = QMessageBox()
            CaseRenameErrorBox.setIcon(QMessageBox.Critical)
            CaseRenameErrorBox.setWindowTitle("Rename Error")
            CaseRenameErrorBox.setText("A Data Case with Similar Name Exist!")
            CaseRenameErrorBox.setStandardButtons(QMessageBox.Ok)
            CaseRenameErrorBox.exec_()

    # Cases Remove
    def CasesRemove(self, CasesItemName):
        CasesRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this Case?",
                                                 QMessageBox.Yes | QMessageBox.No)

        if CasesRemoveChoice == QMessageBox.Yes:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.parent().text(0):
                    try:
                        if CasesItemName.parent().childCount() == 1:
                            tempParent = CasesItemName.parent()
                            tempParent.removeChild(CasesItemName)
                            self.CasesTreeWidget.invisibleRootItem().removeChild(tempParent)
                        else:
                            CasesItemName.parent().removeChild(CasesItemName)

                    except Exception as e:
                        print(str(e))

                    for cases in DS.CasesList:
                        if cases.CaseTopic == CasesItemName.text(0):
                            DS.CasesList.remove(cases)
                            break
        else:
            pass

    # Cases Child Detail
    def CasesChildDetail(self, CasesItemName):
        CasesChildDetailDialogBox = QDialog()
        CasesChildDetailDialogBox.setModal(True)
        CasesChildDetailDialogBox.setWindowTitle("Details")
        CasesChildDetailDialogBox.setParent(self)
        CasesChildDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        CasesChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                               self.height / 5)
        CasesChildDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.parent().text(0):
                for case in DS.CasesList:
                    if case.CaseTopic == CasesItemName.text(0):
                        break

        # ************************************** Labels *************************************

        # Data Source Name Label
        DataSourceNameLabel = QLabel(CasesChildDetailDialogBox)
        DataSourceNameLabel.setText("Data Source Name:")
        DataSourceNameLabel.setGeometry(CasesChildDetailDialogBox.width() * 0.1,
                                        CasesChildDetailDialogBox.height() * 0.2,
                                        CasesChildDetailDialogBox.width() / 4,
                                        CasesChildDetailDialogBox.height() / 10)
        DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNameLabel)

        # Case Name Label
        CaseNameLabel = QLabel(CasesChildDetailDialogBox)
        CaseNameLabel.setText("Case Name:")
        CaseNameLabel.setGeometry(CasesChildDetailDialogBox.width() * 0.1,
                                  CasesChildDetailDialogBox.height() * 0.4,
                                  CasesChildDetailDialogBox.width() / 4,
                                  CasesChildDetailDialogBox.height() / 10)
        CaseNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(CaseNameLabel)

        # No of Case Component Label
        DataSourceNoofComponentLabel = QLabel(CasesChildDetailDialogBox)
        DataSourceNoofComponentLabel.setText("No of Components")
        DataSourceNoofComponentLabel.setGeometry(CasesChildDetailDialogBox.width() * 0.1,
                                                 CasesChildDetailDialogBox.height() * 0.6,
                                                 CasesChildDetailDialogBox.width() / 4,
                                                 CasesChildDetailDialogBox.height() / 10)
        DataSourceNoofComponentLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNoofComponentLabel)

        # ************************************** LineEdit *************************************

        # Data Source Name LineEdit
        DataSourceNameLineEdit = QLineEdit(CasesChildDetailDialogBox)
        DataSourceNameLineEdit.setText(DS.DataSourceName)
        DataSourceNameLineEdit.setReadOnly(True)
        DataSourceNameLineEdit.setGeometry(CasesChildDetailDialogBox.width() * 0.35,
                                           CasesChildDetailDialogBox.height() * 0.2,
                                           CasesChildDetailDialogBox.width() * 0.6,
                                           CasesChildDetailDialogBox.height() / 10)
        DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNameLineEdit)

        # Case Name LineEdit
        DataSourceCaseNameLineEdit = QLineEdit(CasesChildDetailDialogBox)
        DataSourceCaseNameLineEdit.setText(CasesItemName.text(0))
        DataSourceCaseNameLineEdit.setReadOnly(True)
        DataSourceCaseNameLineEdit.setGeometry(CasesChildDetailDialogBox.width() * 0.35,
                                               CasesChildDetailDialogBox.height() * 0.4,
                                               CasesChildDetailDialogBox.width() * 0.6,
                                               CasesChildDetailDialogBox.height() / 10)
        DataSourceCaseNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceCaseNameLineEdit)

        # Data Source Path LineEdit
        NoofCasesLineEdit = QLineEdit(CasesChildDetailDialogBox)
        NoofCasesLineEdit.setText(str(len(case.TopicCases)))
        NoofCasesLineEdit.setReadOnly(True)
        NoofCasesLineEdit.setGeometry(CasesChildDetailDialogBox.width() * 0.35,
                                      CasesChildDetailDialogBox.height() * 0.6,
                                      CasesChildDetailDialogBox.width() * 0.6,
                                      CasesChildDetailDialogBox.height() / 10)
        NoofCasesLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(NoofCasesLineEdit)

        CasesChildDetailDialogBox.exec_()

    # ****************************************************************************
    # ************************ Sentiments Context Menu ***************************
    # ****************************************************************************

    # Get Which Cases Widget Item and its Position
    def FindSentimentsTreeWidgetContextMenu(self, SentimentsMouseRightClickEvent):
        if SentimentsMouseRightClickEvent.reason == SentimentsMouseRightClickEvent.Mouse:
            SentimentsMouseRightClickPos = SentimentsMouseRightClickEvent.globalPos()
            SentimentsMouseRightClickItem = self.SentimentTreeWidget.itemAt(SentimentsMouseRightClickEvent.pos())
        else:
            SentimentsMouseRightClickPos = None
            Sentimentsselection = self.SentimentTreeWidget.selectedItems()

            if Sentimentsselection:
                SentimentsMouseRightClickItem = Sentimentsselection[0]
            else:
                SentimentsMouseRightClickItem = self.SentimentTreeWidget.currentItem()
                if SentimentsMouseRightClickItem is None:
                    SentimentsMouseRightClickItem = self.SentimentTreeWidget.invisibleRootItem().child(0)
            if SentimentsMouseRightClickItem is not None:
                SentimentsParent = SentimentsMouseRightClickItem.parent()
                while SentimentsParent is not None:
                    SentimentsParent.setExpanded(True)
                    SentimentsParent = SentimentsParent.parent()

                Sentimentsitemrect = self.SentimentTreeWidget.visualItemRect(SentimentsMouseRightClickItem)
                Sentimentsportrect = self.SentimentTreeWidget.viewport().rect()

                if not Sentimentsportrect.contains(Sentimentsitemrect.topLeft()):
                    self.SentimentTreeWidget.scrollToItem(SentimentsMouseRightClickItem, QTreeWidget.PositionAtCenter)
                    Sentimentsitemrect = self.SentimentTreeWidget.visualItemRect(SentimentsMouseRightClickItem)

                Sentimentsitemrect.setLeft(Sentimentsportrect.left())
                Sentimentsitemrect.setWidth(Sentimentsportrect.width())
                SentimentsMouseRightClickPos = self.SentimentTreeWidget.mapToGlobal(Sentimentsitemrect.center())

        if SentimentsMouseRightClickPos is not None:
            self.SentimentsTreeWidgetContextMenu(SentimentsMouseRightClickItem, SentimentsMouseRightClickPos)

    # Setting ContextMenu on Clicked Query
    def SentimentsTreeWidgetContextMenu(self, SentimentsItemName, SentimentsWidgetPos):
        # Parent Data Source
        if SentimentsItemName.parent() == None:
            SentimentsRightClickMenu = QMenu(self.SentimentTreeWidget)

            # Cases Expand
            SentimentsExpand = QAction('Expand', self.SentimentTreeWidget)
            SentimentsExpand.triggered.connect(lambda checked, index=SentimentsItemName: self.DataSourceWidgetItemExpandCollapse(index))
            if (SentimentsItemName.childCount() == 0 or SentimentsItemName.isExpanded() == True):
                SentimentsExpand.setDisabled(True)
            else:
                SentimentsExpand.setDisabled(False)
            SentimentsRightClickMenu.addAction(SentimentsExpand)

            # Cases Collapse
            SentimentsCollapse = QAction('Collapse', self.SentimentTreeWidget)
            SentimentsCollapse.triggered.connect(lambda checked, index=SentimentsItemName: self.DataSourceWidgetItemExpandCollapse(index))
            if (SentimentsItemName.childCount() == 0 or SentimentsItemName.isExpanded() == False):
                SentimentsCollapse.setDisabled(True)
            else:
                SentimentsCollapse.setDisabled(False)
            SentimentsRightClickMenu.addAction(SentimentsCollapse)

            SentimentsRightClickMenu.popup(SentimentsWidgetPos)

        # Child DataSource
        else:
            SentimentsRightClickMenu = QMenu(self.SentimentTreeWidget)

            # Case Show components
            SentimentsShowTopicText = QAction('Show Topic Components', self.SentimentTreeWidget)
            SentimentsShowTopicText.triggered.connect(lambda: self.SentimentsShowComponent(SentimentsItemName))
            SentimentsRightClickMenu.addAction(SentimentsShowTopicText)

            # Case Child Detail
            SentimentsDetail = QAction('Details', self.SentimentTreeWidget)
            SentimentsDetail.triggered.connect(lambda: self.SentimentsChildDetail(SentimentsItemName))
            SentimentsRightClickMenu.addAction(SentimentsDetail)

            SentimentsRightClickMenu.popup(SentimentsWidgetPos)

    # Sentiment Show Component
    def SentimentsShowComponent(self, SentimentsItemName):
        print('Hello')

    # Sentiment Child Detail
    def SentimentsChildDetail(self, SentimentsItemName):
        SentimentsChildDetailDialogBox = QDialog()
        SentimentsChildDetailDialogBox.setModal(True)
        SentimentsChildDetailDialogBox.setWindowTitle("Details")
        SentimentsChildDetailDialogBox.setParent(self)
        SentimentsChildDetailDialogBox.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        SentimentsChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                              self.height / 5)
        SentimentsChildDetailDialogBox.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == SentimentsItemName.parent().text(0):
                for sentiment in DS.SentimentList:
                    if sentiment.SentimentType == SentimentsItemName.text(0):
                        break

        # ************************************** Labels *************************************

        # Data Source Name Label
        DataSourceNameLabel = QLabel(SentimentsChildDetailDialogBox)
        DataSourceNameLabel.setText("Data Source Name:")
        DataSourceNameLabel.setGeometry(SentimentsChildDetailDialogBox.width() * 0.1,
                                        SentimentsChildDetailDialogBox.height() * 0.2,
                                        SentimentsChildDetailDialogBox.width() / 4,
                                        SentimentsChildDetailDialogBox.height() / 10)
        DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNameLabel)

        # Sentiment Name Label
        SentimentNameLabel = QLabel(SentimentsChildDetailDialogBox)
        SentimentNameLabel.setText("Case Name:")
        SentimentNameLabel.setGeometry(SentimentsChildDetailDialogBox.width() * 0.1,
                                       SentimentsChildDetailDialogBox.height() * 0.4,
                                       SentimentsChildDetailDialogBox.width() / 4,
                                       SentimentsChildDetailDialogBox.height() / 10)
        SentimentNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(SentimentNameLabel)

        # No of Case Component Label
        DataSourceNoofComponentLabel = QLabel(SentimentsChildDetailDialogBox)
        DataSourceNoofComponentLabel.setText("No of Components")
        DataSourceNoofComponentLabel.setGeometry(SentimentsChildDetailDialogBox.width() * 0.1,
                                                 SentimentsChildDetailDialogBox.height() * 0.6,
                                                 SentimentsChildDetailDialogBox.width() / 4,
                                                 SentimentsChildDetailDialogBox.height() / 10)
        DataSourceNoofComponentLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNoofComponentLabel)

        # ************************************** LineEdit *************************************

        # Data Source Name LineEdit
        DataSourceNameLineEdit = QLineEdit(SentimentsChildDetailDialogBox)
        DataSourceNameLineEdit.setText(DS.DataSourceName)
        DataSourceNameLineEdit.setReadOnly(True)
        DataSourceNameLineEdit.setGeometry(SentimentsChildDetailDialogBox.width() * 0.35,
                                           SentimentsChildDetailDialogBox.height() * 0.2,
                                           SentimentsChildDetailDialogBox.width() * 0.6,
                                           SentimentsChildDetailDialogBox.height() / 10)
        DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNameLineEdit)

        # Sentiment Name LineEdit
        DataSourceCaseNameLineEdit = QLineEdit(SentimentsChildDetailDialogBox)
        DataSourceCaseNameLineEdit.setText(SentimentsItemName.text(0))
        DataSourceCaseNameLineEdit.setReadOnly(True)
        DataSourceCaseNameLineEdit.setGeometry(SentimentsChildDetailDialogBox.width() * 0.35,
                                               SentimentsChildDetailDialogBox.height() * 0.4,
                                               SentimentsChildDetailDialogBox.width() * 0.6,
                                               SentimentsChildDetailDialogBox.height() / 10)
        DataSourceCaseNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceCaseNameLineEdit)

        # Data Source Path LineEdit
        NoofSentimentTextLineEdit = QLineEdit(SentimentsChildDetailDialogBox)
        NoofSentimentTextLineEdit.setText(str(len(sentiment.SentimentTextList)))
        NoofSentimentTextLineEdit.setReadOnly(True)
        NoofSentimentTextLineEdit.setGeometry(SentimentsChildDetailDialogBox.width() * 0.35,
                                              SentimentsChildDetailDialogBox.height() * 0.6,
                                              SentimentsChildDetailDialogBox.width() * 0.6,
                                              SentimentsChildDetailDialogBox.height() / 10)
        NoofSentimentTextLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(NoofSentimentTextLineEdit)

        SentimentsChildDetailDialogBox.exec_()

    # ****************************************************************************
    # *********************** Application Basic Features *************************
    # ****************************************************************************

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

    #Print Window
    def printWindow(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.Printdialog = QtPrintSupport.QPrintDialog(printer, self)
        self.Printdialog.setWindowTitle('Print')
        self.Printdialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)

        if self.Printdialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            self.textedit.print_(printer)

    #Hide ToolBar
    def toolbarHide(self):
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    #Hide Left Sources
    def LeftPaneHide(self, label, TreeWidget):
        if label.isHidden() and TreeWidget.isHidden():
            label.show()
            TreeWidget.show()
        else:
            label.hide()
            TreeWidget.hide()

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

    # ****************************************************************************
    # *************************** Import Features ********************************
    # ****************************************************************************

    #Import DataSource Window
    def ImportFileWindow(self, check):
        if check == "Word":
            dummyWindow = OpenWindow("Open Word File", "Doc files (*.doc *.docx)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.wordTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")

                        if self.wordTreeWidget.isHidden():
                            self.wordTreeWidget.setHidden(False)
                            self.wordTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)
                        self.DataSourceSimilarityUpdate()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()

        elif check == "PDF":
            dummyWindow = OpenWindow("Open PDF File", "Pdf files (*.pdf)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        if not dummyDataSource.DataSourceLoadError:
                            newNode = QTreeWidgetItem(self.pdfTreeWidget)
                            newNode.setText(0, ntpath.basename(path[0]))
                            self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")

                            if self.pdfTreeWidget.isHidden():
                                self.pdfTreeWidget.setHidden(False)
                                self.pdfTreeWidget.setExpanded(True)

                            newNode.setToolTip(0, newNode.text(0))
                            dummyDataSource.setNode(newNode)
                            self.DataSourceSimilarityUpdate()
                        else:
                            dummyDataSource.__del__()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()


        elif check == "Txt":
            dummyWindow = OpenWindow("Open Notepad File", "Notepad files (*.txt)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.txtTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")

                        if self.txtTreeWidget.isHidden():
                            self.txtTreeWidget.setHidden(False)
                            self.txtTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)
                        self.DataSourceSimilarityUpdate()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()

        elif check == "RTF":
            dummyWindow = OpenWindow("Open Rich Text Format File", "Rich Text Format files (*.rtf)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.rtfTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")

                        if self.rtfTreeWidget.isHidden():
                            self.rtfTreeWidget.setHidden(False)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)
                        self.DataSourceSimilarityUpdate()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()

        elif check == "Sound":
            dummyWindow = OpenWindow("Open Audio File", "Audio files (*.wav *.mp3)", 0)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.audioSTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")

                        if self.audioSTreeWidget.isHidden():
                            self.audioSTreeWidget.setHidden(False)
                            self.audioSTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)
                        self.DataSourceSimilarityUpdate()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()

        elif check == "Image":
            dummyWindow = OpenWindow("Open Image File",
                                     "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)",
                                     2)
            path = dummyWindow.filepath
            dummyWindow.__del__()

            if all(path):
                dummyDataSource = DataSource(path[0], path[1], self)

                DataSourceNameCheck = False

                for DS in myFile.DataSourceList:
                    if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                        DataSourceNameCheck = True

                if not DataSourceNameCheck:
                    if not dummyDataSource.DataSourceLoadError:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.ImageSTreeWidget)
                        newNode.setText(0, ntpath.basename(dummyDataSource.DataSourceName))
                        self.ImageSTreeWidget.setText(0, "Image" + "(" + str(self.ImageSTreeWidget.childCount()) + ")")

                        if self.ImageSTreeWidget.isHidden():
                            self.ImageSTreeWidget.setHidden(False)
                            self.ImageSTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)
                        self.DataSourceSimilarityUpdate()
                    else:
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText(
                        "A Data Source with Similar Name Exist! Please Rename the File then try Again")
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()

    # Import Tweet Window
    def ImportTweetWindow(self):
        TweetDialog = QDialog()
        TweetDialog.setWindowTitle("Import From Twitter")
        TweetDialog.setGeometry(self.width * 0.375, self.height * 0.375, self.width / 4, self.height / 4)
        TweetDialog.setParent(self)
        TweetDialog.setAttribute(Qt.WA_DeleteOnClose)
        TweetDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        TweetDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Tweet HashTag Label
        TweetHashtagLabel = QLabel(TweetDialog)
        TweetHashtagLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.1,
                                      TweetDialog.width() / 5, TweetDialog.height() / 15)
        TweetHashtagLabel.setText("Hastag")
        self.LabelSizeAdjustment(TweetHashtagLabel)

        # Tweet Date Label
        DateLabel = QLabel(TweetDialog)
        DateLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.25,
                              TweetDialog.width() / 5, TweetDialog.height() / 15)
        DateLabel.setText("Since")
        self.LabelSizeAdjustment(DateLabel)

        # Tweet Language Label
        TweetLanguageLabel = QLabel(TweetDialog)
        TweetLanguageLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.4,
                                       TweetDialog.width() / 5, TweetDialog.height() / 15)
        TweetLanguageLabel.setText("Language")
        self.LabelSizeAdjustment(TweetLanguageLabel)

        # No. of Tweets Label Label
        NTweetLabel = QLabel(TweetDialog)
        NTweetLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.55,
                                TweetDialog.width() / 5, TweetDialog.height() / 15)
        NTweetLabel.setText("No of Tweets")
        self.LabelSizeAdjustment(NTweetLabel)

        # Twitter HashTag LineEdit
        TweetHashtagLineEdit = QLineEdit(TweetDialog)
        TweetHashtagLineEdit.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.1,
                                         TweetDialog.width() / 3, TweetDialog.height() / 15)
        TweetHashtagLineEdit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.LineEditSizeAdjustment(TweetHashtagLineEdit)

        # Tweet Since Date
        DateCalendar = QDateEdit(TweetDialog)
        DateCalendar.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.25,
                                 TweetDialog.width() / 3, TweetDialog.height() / 15)
        DateCalendar.setCalendarPopup(True)
        DateCalendar.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        DateCalendar.setMaximumDate(QDate(datetime.datetime.today()))
        DateCalendar.setMinimumDate(datetime.datetime.now() - datetime.timedelta(days=365))
        DateCalendar.setDate(datetime.datetime.today())
        self.LineEditSizeAdjustment(DateCalendar)

        # Tweet Language ComboBox
        TweetLanguageComboBox = QComboBox(TweetDialog)
        TweetLanguageComboBox.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.4,
                                          TweetDialog.width() / 3, TweetDialog.height() / 15)

        for languagecode, language in self.languages:
            TweetLanguageComboBox.addItem(language)

        self.LineEditSizeAdjustment(TweetLanguageComboBox)

        # Tweet No Label
        NTweetLineEdit = QDoubleSpinBox(TweetDialog)
        NTweetLineEdit.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.55,
                                   TweetDialog.width() / 3, TweetDialog.height() / 15)
        NTweetLineEdit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        NTweetLineEdit.setDecimals(0)
        NTweetLineEdit.setMinimum(10)
        NTweetLineEdit.setMaximum(1000)
        self.LineEditSizeAdjustment(NTweetLineEdit)

        # TweetDialog ButtonBox
        TweetbuttonBox = QDialogButtonBox(TweetDialog)
        TweetbuttonBox.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.8,
                                   TweetDialog.width() / 3, TweetDialog.height() / 15)
        TweetbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        TweetbuttonBox.button(QDialogButtonBox.Ok).setText('Get')
        TweetbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(TweetbuttonBox)

        TweetHashtagLineEdit.textChanged.connect(lambda: self.GetButtonEnableTweet(TweetbuttonBox))

        TweetbuttonBox.accepted.connect(TweetDialog.accept)
        TweetbuttonBox.rejected.connect(TweetDialog.reject)

        TweetbuttonBox.accepted.connect(
            lambda: self.ImportFromTweet(str(TweetHashtagLineEdit.text()), str(DateCalendar.text()),
                                         TweetLanguageComboBox.currentText(), NTweetLineEdit.text()))

        TweetDialog.exec_()

    # Import From Tweet
    def ImportFromTweet(self, Hashtag, Since, language, NoOfTweet):
        dummyDataSource = DataSource(Hashtag, "Tweet", self)
        DataSourceNameCheck = False

        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            for languagecode, lang in self.languages:
                if lang == language:
                    dummyDataSource.TweetDataSource(Hashtag, Since, languagecode, NoOfTweet)
                    break

            if not dummyDataSource.DataSourceLoadError:
                if not dummyDataSource.DataSourceRetrieveZeroError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.TweetTreeWidget)
                    newNode.setText(0, Hashtag)
                    self.TweetTreeWidget.setText(0, "Tweet" + "(" + str(self.TweetTreeWidget.childCount()) + ")")

                    if self.TweetTreeWidget.isHidden():
                        self.TweetTreeWidget.setHidden(False)
                        self.TweetTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))
                    dummyDataSource.setNode(newNode)
                    self.DataSourceSimilarityUpdate()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox()
                    DataSourceImportNameErrorBox.setIcon(QMessageBox.Information)
                    DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                    DataSourceImportNameErrorBox.setText("No Tweet Found with Hashtag : " + Hashtag)
                    DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                    DataSourceImportNameErrorBox.exec_()
            else:
                dummyDataSource.__del__()
                DataSourceImportNameErrorBox = QMessageBox()
                DataSourceImportNameErrorBox.setIcon(QMessageBox.Information)
                DataSourceImportNameErrorBox.setWindowTitle("Import Error")
                DataSourceImportNameErrorBox.setText("TextAS is unable to retrive any tweet")
                DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
                DataSourceImportNameErrorBox.exec_()
        else:
            dummyDataSource.__del__()
            DataSourceImportNameErrorBox = QMessageBox()
            DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
            DataSourceImportNameErrorBox.setWindowTitle("Import Error")
            DataSourceImportNameErrorBox.setText("A Tweet with Similar Hashtag Exist!")
            DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceImportNameErrorBox.exec_()

    # Enable Get on perfect Hashtag
    def GetButtonEnableTweet(self, buttonbox):
        TweetHashtagLineEdit = self.sender()
        item = TweetHashtagLineEdit.text()

        if len(item) > 1 and len(item) < 256 and item.startswith("#"):
            buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            buttonbox.button(QDialogButtonBox.Ok).setEnabled(False)

    # Import URL Window
    def ImportURLWindow(self):
        URLDialog = QDialog()
        URLDialog.setWindowTitle("Import From URL")
        URLDialog.setGeometry(self.width * 0.3, self.height * 0.425, self.width*2/5 , self.height*0.15)
        URLDialog.setParent(self)
        URLDialog.setAttribute(Qt.WA_DeleteOnClose)
        URLDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        URLDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Tweet HashTag Label
        URLLabel = QLabel(URLDialog)
        URLLabel.setGeometry(URLDialog.width() * 0.1, URLDialog.height() * 0.3,
                             URLDialog.width()/10 , URLDialog.height() / 10)
        URLLabel.setText("URL")
        self.LabelSizeAdjustment(URLLabel)

        # Twitter HashTag LineEdit
        URLLineEdit = QLineEdit(URLDialog)
        URLLineEdit.setGeometry(URLDialog.width() * 0.25, URLDialog.height() * 0.3,
                                URLDialog.width() * 0.7, URLDialog.height() /10)
        URLLineEdit.setAlignment(Qt.AlignVCenter)
        self.LineEditSizeAdjustment(URLLineEdit)

        # TweetDialog ButtonBox
        URLbuttonBox = QDialogButtonBox(URLDialog)
        URLbuttonBox.setGeometry(URLDialog.width() * 0.5, URLDialog.height() * 0.7,
                                 URLDialog.width() / 3, URLDialog.height() / 10)
        URLbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        URLbuttonBox.button(QDialogButtonBox.Ok).setText('Get Data')
        URLbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(URLbuttonBox)

        URLLineEdit.textChanged.connect(lambda: self.OkButtonEnable(URLbuttonBox, True))

        URLbuttonBox.accepted.connect(URLDialog.accept)
        URLbuttonBox.rejected.connect(URLDialog.reject)

        URLbuttonBox.accepted.connect(lambda: self.ImportFromURL(URLLineEdit.text()))
        URLDialog.exec_()

    # Import From URL
    def ImportFromURL(self, URL):
        dummyDataSource = DataSource(URL, "URL", self)
        DataSourceNameCheck = False

        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            if not dummyDataSource.DataSourceLoadError:
                myFile.setDataSources(dummyDataSource)
                newNode = QTreeWidgetItem(self.WebTreeWidget)
                newNode.setText(0, URL)
                self.WebTreeWidget.setText(0, "Web" + "(" + str(self.WebTreeWidget.childCount()) + ")")

                if self.WebTreeWidget.isHidden():
                    self.WebTreeWidget.setHidden(False)
                    self.WebTreeWidget.setExpanded(True)

                newNode.setToolTip(0, newNode.text(0))
                dummyDataSource.setNode(newNode)
                self.DataSourceSimilarityUpdate()
            else:
                dummyDataSource.__del__()
        else:
            dummyDataSource.__del__()
            DataSourceImportNameErrorBox = QMessageBox()
            DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
            DataSourceImportNameErrorBox.setWindowTitle("Import Error")
            DataSourceImportNameErrorBox.setText("A Web Source with Similar URL Exist!")
            DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceImportNameErrorBox.exec_()

    # Import From Youtube Window
    def ImportYoutubeWindow(self):
        YoutubeDialog = QDialog()
        YoutubeDialog.setWindowTitle("Import Youtube Comments")
        YoutubeDialog.setGeometry(self.width * 0.3, self.height * 0.4, self.width * 2 / 5, self.height * 0.20)
        YoutubeDialog.setParent(self)
        YoutubeDialog.setAttribute(Qt.WA_DeleteOnClose)
        YoutubeDialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        YoutubeDialog.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # Summarization Default Radio Button
        VideoURLRadioButton = QRadioButton(YoutubeDialog)
        VideoURLRadioButton.setGeometry(YoutubeDialog.width() * 0.1, YoutubeDialog.height() * 0.2,
                                       YoutubeDialog.width() / 5, YoutubeDialog.height() / 10)
        VideoURLRadioButton.setText("Video URL")

        # Twitter HashTag LineEdit
        URLLineEdit = QLineEdit(YoutubeDialog)
        URLLineEdit.setGeometry(YoutubeDialog.width() * 0.3, YoutubeDialog.height() * 0.2,
                                YoutubeDialog.width() * 0.6, YoutubeDialog.height() / 10)
        URLLineEdit.setAlignment(Qt.AlignVCenter)
        URLLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(URLLineEdit)

        # Summarization Total Word Count Radio Button
        KeyWordRadioButton = QRadioButton(YoutubeDialog)
        KeyWordRadioButton.setGeometry(YoutubeDialog.width() * 0.1, YoutubeDialog.height() * 0.4,
                                       YoutubeDialog.width() / 5, YoutubeDialog.height() / 10)
        KeyWordRadioButton.setText("Key Word")
        KeyWordRadioButton.adjustSize()

        # Twitter HashTag LineEdit
        KeyWordLineEdit = QLineEdit(YoutubeDialog)
        KeyWordLineEdit.setGeometry(YoutubeDialog.width() * 0.6, YoutubeDialog.height() * 0.4,
                                    YoutubeDialog.width() * 0.3, YoutubeDialog.height() / 10)
        KeyWordLineEdit.setAlignment(Qt.AlignVCenter)
        KeyWordLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(KeyWordLineEdit)

        # TweetDialog ButtonBox
        YoutubebuttonBox = QDialogButtonBox(YoutubeDialog)
        YoutubebuttonBox.setGeometry(YoutubeDialog.width() * 0.5, YoutubeDialog.height() * 0.8,
                                     YoutubeDialog.width() / 3, YoutubeDialog.height() / 10)
        YoutubebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        YoutubebuttonBox.button(QDialogButtonBox.Ok).setText('Get Comments')
        YoutubebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(YoutubebuttonBox)

        URLLineEdit.textChanged.connect(lambda: self.OkButtonEnable(YoutubebuttonBox, True))
        KeyWordLineEdit.textChanged.connect(lambda: self.OkButtonEnable(YoutubebuttonBox, True))

        VideoURLRadioButton.toggled.connect(lambda: self.EnableOkonYoutubeRadioButtonToggle(KeyWordRadioButton, URLLineEdit, KeyWordLineEdit, YoutubebuttonBox))
        KeyWordRadioButton.toggled.connect(lambda: self.EnableOkonYoutubeRadioButtonToggle(VideoURLRadioButton, KeyWordLineEdit, URLLineEdit, YoutubebuttonBox))

        YoutubebuttonBox.accepted.connect(YoutubeDialog.accept)
        YoutubebuttonBox.rejected.connect(YoutubeDialog.reject)

        YoutubebuttonBox.accepted.connect(lambda: self.ImportFromYoutube(VideoURLRadioButton.isChecked(), KeyWordRadioButton.isChecked(), URLLineEdit.text(), KeyWordLineEdit.text()))
        YoutubeDialog.exec_()

    # Import From Youtube
    def ImportFromYoutube(self, VideoURLCheck, KeyWordCheck, URL, KeyWord):
        if VideoURLCheck:
            URL = URL.replace('https://youtu.be/', 'https://www.youtube.com/watch?v=')
            dummyDataSource = DataSource(URL, "Youtube", self)
            dummyDataSource.YoutubeURL()
            DataSourceNameCheck = False
        elif KeyWordCheck:
            dummyDataSource = DataSource(KeyWord, "Youtube", self)
            dummyDataSource.YoutubeKeyWord()
            DataSourceNameCheck = False


        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            if not dummyDataSource.DataSourceLoadError:
                myFile.setDataSources(dummyDataSource)
                newNode = QTreeWidgetItem(self.YoutubeTreeWidget)

                if VideoURLCheck:
                    newNode.setText(0, URL)
                else:
                    newNode.setText(0, KeyWord)

                self.YoutubeTreeWidget.setText(0, "Youtube" + "(" + str(self.YoutubeTreeWidget.childCount()) + ")")

                if self.YoutubeTreeWidget.isHidden():
                    self.YoutubeTreeWidget.setHidden(False)
                    self.YoutubeTreeWidget.setExpanded(True)

                newNode.setToolTip(0, newNode.text(0))
                dummyDataSource.setNode(newNode)
                self.DataSourceSimilarityUpdate()
            else:
                dummyDataSource.__del__()
        else:
            dummyDataSource.__del__()
            DataSourceImportNameErrorBox = QMessageBox()
            DataSourceImportNameErrorBox.setIcon(QMessageBox.Critical)
            DataSourceImportNameErrorBox.setWindowTitle("Import Error")

            if VideoURLCheck:
                DataSourceImportNameErrorBox.setText("A Youtube Source with Similar URL Exist!")
            else:
                DataSourceImportNameErrorBox.setText("A Youtube Source with Similar KeyWord Exist!")

            DataSourceImportNameErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceImportNameErrorBox.exec_()

    

if __name__ == "__main__":
    WindowTitleLogo = "Images/TextASLogo.png"
    isSaveAs = True
    myFile = File()
    myFile.setCreatedDate(datetime.datetime.now())
    myFile.setCreatedDate(datetime.datetime.now())
    myFile.setCreatedDate(getpass.getuser())

    App = QApplication(sys.argv)

    # TextASSplash = QSplashScreen()
    # TextASSplash.resize(200, 100)
    # TextASSplashPixmap = QPixmap("Images/TextASSplash.png")
    # TextASSplash.setPixmap(TextASSplashPixmap)
    #
    # SplahScreenProgressBar = QProgressBar(TextASSplash)
    # SplahScreenProgressBar.setGeometry(TextASSplash.width() / 10, TextASSplash.height() * 0.9,
    #                         TextASSplash.width() * 0.8, TextASSplash.height() * 0.035)
    # SplahScreenProgressBar.setTextVisible(False)
    # SplahScreenProgressBar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}")
    #
    # TextASSplash.show()
    #
    # for i in range(0, 100):
    #     SplahScreenProgressBar.setValue(i)
    #     t = time.time()
    #     while time.time() < t + 0.05:
    #         App.processEvents()
    #
    # TextASSplash.close()

    TextASMainwindow = Window()
    TextASMainwindow.show()
    sys.exit(App.exec())