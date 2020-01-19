from distutils.errors import PreprocessError
from idlelib.idle_test.test_configdialog import GenPageTest

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtPrintSupport, QAxContainer, QtQuickWidgets, QtPositioning
from PyQt5.QtWebEngineWidgets import *
from win32api import GetMonitorInfo, MonitorFromPoint
from PIL import  Image
from File import *
import humanfriendly

import glob, sys, os, getpass, ntpath, win32gui, math, csv, datetime

class MarkerModel(QAbstractListModel):
    PositionRole, SourceRole = range(Qt.UserRole, Qt.UserRole + 2)

    def __init__(self, parent=None):
        super(MarkerModel, self).__init__(parent)
        self._markers = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._markers)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount():
            if role == MarkerModel.PositionRole:
                return self._markers[index.row()]["position"]
            elif role == MarkerModel.SourceRole:
                return self._markers[index.row()]["source"]
        return QVariant()

    def roleNames(self):
        return {MarkerModel.PositionRole: b"position_marker", MarkerModel.SourceRole: b"source_marker"}

    def appendMarker(self, marker):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._markers.append(marker)
        self.endInsertRows()

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
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
        self.title = "TextWiz"

        Monitor_Resolution_Info = GetMonitorInfo(MonitorFromPoint((0, 0)))

        self.width = Monitor_Resolution_Info.get("Work")[2]
        self.height = Monitor_Resolution_Info.get("Work")[3]

        self.settings = QSettings('TextWiz', 'TextWiz')

        self.theme = self.settings.value('theme', '')

        if self.theme == '' or self.theme == 'Light':
            self.setStyleSheet(open('Styles/Light.css', 'r').read())
        elif self.theme == 'Dark':
            self.setStyleSheet(open('Styles/Dark.css', 'r').read())
        elif self.theme == 'DarkOrange':
            self.setStyleSheet(open('Styles/DarkOrange.css', 'r').read())

            self.settings.setValue('theme', 'DarkOrange')

        self.left = 0;
        self.top = 0;

        self.languages = open('Languages.txt', 'r').read().split("\n")

        for fileRow in self.languages:
            self.languages[self.languages.index(fileRow)] = fileRow.split(',')

        coordinatecsvreader = csv.reader(open('Coordinates.csv'))

        self.Coordinates = []

        for row in coordinatecsvreader:
            self.Coordinates.append([row[0], row[1], row[2]])



        self.initWindows()

    def initWindows(self):
        self.setWindowIcon(QIcon(WindowTitleLogo))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top, self.width, self.height)
        self.setMinimumSize(self.width/2, self.height/2)
        self.showMaximized()

        # *****************************  ToolBar ******************************************

        WordAct = QAction(QIcon('Images/Word.png'), 'Word', self)
        WordAct.triggered.connect(lambda checked, index="Word": self.ImportFileWindow(index))

        PDFAct = QAction(QIcon('Images/PDF.png'), 'PDF', self)
        PDFAct.triggered.connect(lambda checked, index="PDF": self.ImportFileWindow(index))

        NotepadAct = QAction(QIcon('Images/Notepad.png'), 'txt', self)
        NotepadAct.triggered.connect(lambda checked, index="Txt": self.ImportFileWindow(index))

        RTFAct = QAction(QIcon('Images/rtf.png'), 'RTF', self)
        RTFAct.triggered.connect(lambda checked, index="RTF": self.ImportFileWindow(index))

        SoundAct = QAction(QIcon('Images/Sound.png'), 'Audio', self)
        SoundAct.triggered.connect(lambda checked, index="Sound": self.ImportFileWindow(index))

        ImageAct = QAction(QIcon('Images/ImageDataSource.png'), 'Image', self)
        ImageAct.triggered.connect(lambda checked, index="Image": self.ImportFileWindow(index))

        TwitterAct = QAction(QIcon('Images/Twitter.png'), 'Twitter', self)
        TwitterAct.triggered.connect(lambda checked: self.ImportTweetWindow())

        WebAct = QAction(QIcon('Images/Web.png'), 'URL', self)
        WebAct.triggered.connect(lambda checked: self.ImportURLWindow())

        YoutubeAct = QAction(QIcon('Images/Youtube.png'), 'Youtube', self)
        YoutubeAct.triggered.connect(lambda checked: self.ImportYoutubeWindow())

        self.toolbar = self.addToolBar("Show Toolbar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon | Qt.AlignLeading)  # <= Toolbuttonstyle
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
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

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

        SaveButton = QAction(QIcon("Images/Save.png"), 'Save', self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('File Saved')

        printButton = QAction(QIcon("Images/Printer.png"), 'Print', self)
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

        ChangeThemeButton = QAction('Change Theme', self)
        ChangeThemeButton.triggered.connect(lambda: self.ChangeThemeDialog())
        viewMenu.addAction(ChangeThemeButton)

        # *****************************  ImportMenuItem *************************************

        WordFileButton = QAction(QIcon("Images/Word.png"),'Word File', self)
        WordFileButton.setStatusTip('Word File')
        WordFileButton.triggered.connect(lambda checked, index="Word": self.ImportFileWindow(index))

        PDFFileButton = QAction(QIcon("Images/PDF.png"), 'PDF File', self)
        PDFFileButton.setStatusTip('PDF File')
        PDFFileButton.triggered.connect(lambda checked, index="PDF": self.ImportFileWindow(index))

        TXTFileButton = QAction(QIcon("Images/Notepad.png"), 'Notepad File', self)
        TXTFileButton.setStatusTip('Notepad File')
        TXTFileButton.triggered.connect(lambda checked, index="Txt": self.ImportFileWindow(index))

        RTFFileButton = QAction(QIcon("Images/rtf.png"), 'RTF File', self)
        RTFFileButton.setStatusTip('RTF File')
        RTFFileButton.triggered.connect(lambda checked, index="RTF": self.ImportFileWindow(index))

        SoundFileButton = QAction(QIcon("Images/Sound.png"), 'Audio File', self)
        SoundFileButton.setStatusTip('Word File')
        SoundFileButton.triggered.connect(lambda checked, index="Sound": self.ImportFileWindow(index))

        ImageFileButton = QAction(QIcon("Images\ImageDataSource.png"), 'Image File', self)
        ImageFileButton.setStatusTip('Image File')
        ImageFileButton.triggered.connect(lambda checked, index="Image": self.ImportFileWindow(index))

        TwitterButton = QAction(QIcon("Images\Twitter.png"), 'Twitter', self)
        TwitterButton.setStatusTip('Tweets')
        TwitterButton.triggered.connect(lambda checked: self.ImportTweetWindow())

        URLButton = QAction(QIcon("Images\Web.png"), 'Web', self)
        URLButton.setStatusTip('Get Data From URL')
        URLButton.triggered.connect(lambda checked: self.ImportURLWindow())

        YoutubeButton = QAction(QIcon("Images\Youtube.png"), 'Youtube', self)
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
        ToolMenu.addAction(ShowWordFrequencyTool)

        # Summarize Tool
        SummarizeTool = QAction('Summarize', self)
        SummarizeTool.setStatusTip('Summarize')
        SummarizeTool.triggered.connect(lambda: self.DataSourceSummarize())
        ToolMenu.addAction(SummarizeTool)

        # Summarize Tool
        TranslateTool = QAction('Translate', self)
        TranslateTool.setStatusTip('Translate')
        TranslateTool.triggered.connect(lambda: self.DataSourceTranslateDialog())
        ToolMenu.addAction(TranslateTool)

        # Stem Word Tool
        FindStemWordTool = QAction('Find Stem Word', self)
        FindStemWordTool.setStatusTip('Find Stem Words')
        FindStemWordTool.triggered.connect(lambda: self.DataSourceFindStemWords())
        ToolMenu.addAction(FindStemWordTool)

        # Part of Speech
        PartOfSpeech = QAction('Part of Speech', self)
        PartOfSpeech.setToolTip('Part of Speech')
        PartOfSpeech.triggered.connect(lambda: self.DataSourcePOSDialog())
        ToolMenu.addAction(PartOfSpeech)

        # Entity Relationship
        EntityRelationship = QAction('Entity Relationship', self)
        EntityRelationship.setToolTip('Entity Relationship')
        EntityRelationship.triggered.connect(lambda: self.DataSourceEntityRelationShipDialog())
        ToolMenu.addAction(EntityRelationship)

        # Sentiment Analysis
        SentimentAnalysis = QAction('Sentiments Analysis', self)
        SentimentAnalysis.setToolTip('Sentiments Analysis')
        SentimentAnalysis.triggered.connect(lambda: self.DataSourcesSentimentAnalysis())
        ToolMenu.addAction(SentimentAnalysis)

        # Topic Modelling
        TopicModelling = QAction('Topic Modelling', self)
        TopicModelling.setToolTip('Topic Modelling')
        TopicModelling.triggered.connect(lambda: self.DataSourceTopicModellingDialog())
        ToolMenu.addAction(TopicModelling)

        # Generate Question
        GenerateQuestion = QAction('Generate Questions', self)
        GenerateQuestion.setToolTip('Generate Questions')
        GenerateQuestion.triggered.connect(lambda: self.DataSourcesGenerateQuestions())
        ToolMenu.addAction(GenerateQuestion)

        # Find Similarity
        FindSimilarity = QAction('Find Similarity', self)
        FindSimilarity.setToolTip('Find Similarity Between Data Sources')
        FindSimilarity.triggered.connect(lambda: self.DataSourcesSimilarity())
        ToolMenu.addAction(FindSimilarity)

        # *************************  VisualizationMenuItem **********************************

        # Create Dashboard
        CreateDasboard = QAction('Create Dashboard', self)
        CreateDasboard.setToolTip('Find Similarity Between Data Sources')
        CreateDasboard.triggered.connect(lambda: self.DataSourcesCreateDashboardDialog())
        VisualizationMenu.addAction(CreateDasboard)

        # Create Word Cloud Tool
        CreateWordCloudTool = QAction('Create Word Cloud', self)
        CreateWordCloudTool.setStatusTip('Create Word Cloud')
        CreateWordCloudTool.triggered.connect(lambda: self.DataSourceCreateCloud())
        VisualizationMenu.addAction(CreateWordCloudTool)

        # Document Clustering
        DocumentClusteringTool = QAction('Document Clustering', self)
        DocumentClusteringTool.setStatusTip('Document Clustering')
        DocumentClusteringTool.triggered.connect(lambda: self.DataSourceDocumentClustering())
        VisualizationMenu.addAction(DocumentClusteringTool)

        # Create Coordinate Map Tool
        CreateCoordinateMapTool = QAction('Coordinate Map', self)
        CreateCoordinateMapTool.setStatusTip('Coordinate Map')
        CreateCoordinateMapTool.triggered.connect(lambda: self.DataSourceCoordinateMapDialog())
        VisualizationMenu.addAction(CreateCoordinateMapTool)

        # *****************************  HelpMenuItem ***************************************

        AboutButton = QAction(QIcon('exit24.png'), 'About Us', self)
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
        self.DataSourceTreeWidget.customContextMenuRequested.connect(lambda: self.FindDataSourceTreeWidgetContextMenu(QContextMenuEvent))

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
        self.QueryTreeWidget.customContextMenuRequested.connect(lambda: self.FindQueryTreeWidgetContextMenu(QContextMenuEvent))

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
        self.CasesTreeWidget.customContextMenuRequested.connect(lambda: self.FindCasesTreeWidgetContextMenu(QContextMenuEvent))
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
        self.SentimentTreeWidget.customContextMenuRequested.connect(lambda: self.FindSentimentsTreeWidgetContextMenu(QContextMenuEvent))

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
        self.VisualizationTreeWidget.itemDoubleClicked.connect(self.VisualizationDoubleClickHandler)
        self.VisualizationTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.VisualizationTreeWidget.customContextMenuRequested.connect(lambda: self.FindVisualizationTreeWidgetContextMenu(QContextMenuEvent))

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

        #self.WelcomePage()

    # Welcome Page
    def WelcomePage(self):
        # Welcome Tab
        TextWizWelcomeTab = QWidget()

        # LayoutWidget For within Welcome Tab
        TextWizWelcomeTabverticalLayoutWidget = QWidget(TextWizWelcomeTab)
        TextWizWelcomeTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        TextWizWelcomeTabverticalLayoutWidget.setGeometry(0, 0, self.horizontalLayoutWidget.width(), self.horizontalLayoutWidget.height())

        # Box Layout for Welcome Tab
        TextWizWelcomeTabverticalLayout = QVBoxLayout(TextWizWelcomeTabverticalLayoutWidget)
        TextWizWelcomeTabverticalLayout.setContentsMargins(0, 0, 0, 0)

        TextWizWelcomeWeb = QWebEngineView()
        TextWizWelcomeWeb.setContextMenuPolicy(Qt.PreventContextMenu)
        TextWizWelcomeWeb.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        TextWizWelcomeWeb.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        TextWizWelcomeTabverticalLayout.addWidget(TextWizWelcomeWeb)
        #TextWizWelcomeWeb.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        #TextWizWelcomeWeb.load(QUrl(os.getcwd() + "\welcomepage\Light\welcome.html"))
        TextWizWelcomeWeb.setHtml(open("welcomepage/Light/welcome.html").read())

        self.tabWidget.addTab(TextWizWelcomeTab, "Welcome")
        self.tabWidget.setCurrentWidget(TextWizWelcomeTab)

    # Change Theme Dialog
    def ChangeThemeDialog(self):
        ChangeThemeDialog = QDialog()
        ChangeThemeDialog.setWindowTitle("Show Word Frequency Table")
        ChangeThemeDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                       self.height / 10)
        ChangeThemeDialog.setParent(self)
        ChangeThemeDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        ChangeThemeDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Theme Label
        Themelabel = QLabel(ChangeThemeDialog)
        Themelabel.setGeometry(ChangeThemeDialog.width() * 0.125,
                               ChangeThemeDialog.height() * 0.2,
                               ChangeThemeDialog.width() / 4,
                               ChangeThemeDialog.height() * 0.1)

        Themelabel.setText("Theme")
        Themelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(Themelabel)

        # Data Source ComboBox
        ThemeComboBox = QComboBox(ChangeThemeDialog)
        ThemeComboBox.setGeometry(ChangeThemeDialog.width() * 0.4,
                                  ChangeThemeDialog.height() * 0.2,
                                  ChangeThemeDialog.width() / 2,
                                  ChangeThemeDialog.height() / 10)

        ThemeComboBox.addItem('Light')
        ThemeComboBox.addItem('Dark')
        ThemeComboBox.addItem('DarkOrange')

        ThemeComboBox.setCurrentText(self.theme)

        self.LineEditSizeAdjustment(ThemeComboBox)

        # Stem Word Button Box
        ChangeThemebuttonBox = QDialogButtonBox(ChangeThemeDialog)
        ChangeThemebuttonBox.setGeometry(ChangeThemeDialog.width() * 0.125,
                                         ChangeThemeDialog.height() * 0.7,
                                         ChangeThemeDialog.width() * 3 / 4,
                                         ChangeThemeDialog.height() / 5)
        ChangeThemebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        ChangeThemebuttonBox.button(QDialogButtonBox.Ok).setText('Change')


        self.LineEditSizeAdjustment(ChangeThemebuttonBox)

        ChangeThemebuttonBox.accepted.connect(ChangeThemeDialog.accept)
        ChangeThemebuttonBox.rejected.connect(ChangeThemeDialog.reject)

        ChangeThemebuttonBox.accepted.connect(lambda: self.ChangeTheme(ThemeComboBox.currentText()))

        ChangeThemeDialog.exec()

    # Change Theme
    def ChangeTheme(self, ThemeText):
        self.theme = ThemeText

        if self.theme == 'Light':
            self.setStyleSheet(open('Styles/Light.css', 'r').read())
        elif self.theme == 'Dark':
            self.setStyleSheet(open('Styles/Dark.css', 'r').read())
        elif self.theme == 'DarkOrange':
            self.setStyleSheet(open('Styles/DarkOrange.css', 'r').read())

        self.settings.setValue('theme', self.theme)

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
                DataSourcesSimilarityTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
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

                    # Adding Word Frequency Query
                    ItemsWidget = self.QueryTreeWidget.findItems("Data Sources Similarity", Qt.MatchExactly, 0)

                    if len(ItemsWidget) == 0:
                        DSVisualWidget = QTreeWidgetItem(self.QueryTreeWidget)
                        DSVisualWidget.setText(0, "Data Sources Similarity")
                        DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))

                    self.tabWidget.addTab(DataSourcesSimilarityTab, "Data Sources Similarity")
                    self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)

            else:
                DataSourceLoadErrorBox = QMessageBox.critical(self, "Data Sources Similarity Error",
                                                              "An Error Occured! Similarity can only be found if Data Sources are more than one",
                                                              QMessageBox.Ok)

    # Update Similarity Between Data Sources
    def DataSourceSimilarityUpdate(self):
        for tabs in myFile.TabList:
            if tabs.TabName == "Data Sources Similarity":
                if self.tabWidget.indexOf(tabs.tabWidget) >= 0:
                    currentTab = self.tabWidget.currentWidget()
                    if len(myFile.DataSourceList) > 1:
                        self.DataSourcesSimilarity()
                        self.tabWidget.setCurrentWidget(currentTab)
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                        ItemsWidget = self.QueryTreeWidget.findItems("Data Sources Similarity", Qt.MatchExactly, 0)
                        for widget in ItemsWidget:
                            self.QueryTreeWidget.invisibleRootItem().removeChild(widget)
                    break
                else:
                    if len(myFile.DataSourceList) > 1:
                        self.DataSourcesSimilarity()
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                        ItemsWidget = self.QueryTreeWidget.findItems("Data Sources Similarity", Qt.MatchExactly, 0)
                        for widget in ItemsWidget:
                            self.QueryTreeWidget.invisibleRootItem().removeChild(widget)
                    break

    # Document Clustering
    def DataSourceDocumentClustering(self):
        DataSourceDocumentClusteringTabFlag = False
        DataSourceDocumentClusteringTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == len(myFile.DataSourceList) and tabs.TabName == 'Document Clustering':
                if self.tabWidget.currentWidget() != tabs.tabWidget:
                    self.tabWidget.setCurrentWidget(tabs.tabWidget)
                DataSourceDocumentClusteringTabFlag = True
                break
            elif tabs.TabName == 'Document Clustering':
                DataSourceDocumentClusteringTabFlag2 = True
                break

        myFile.DocumnetClustering()

        if not DataSourceDocumentClusteringTabFlag:
            if not myFile.DocumnetClusteringDataSourceError:
                # Creating New Tab for Data Sources Similarity
                DataSourceDocumentClusteringTab = QWidget()

                # LayoutWidget For within DataSourcesSimilarity Tab
                DataSourceDocumentClusteringTabVerticalLayoutWidget = QWidget(DataSourceDocumentClusteringTab)
                DataSourceDocumentClusteringTabVerticalLayoutWidget.setGeometry(0, 0,
                                                                          self.tabWidget.width(),
                                                                          self.tabWidget.height() / 10)

                # Box Layout for DataSourcesSimilarity Tab
                DataSourceDocumentClusteringTabVerticalLayout = QVBoxLayout(DataSourceDocumentClusteringTabVerticalLayoutWidget)
                DataSourceDocumentClusteringTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

                # Document Clustering ComboBox
                DocumentClusteringComboBox = QComboBox(DataSourceDocumentClusteringTabVerticalLayoutWidget)
                DocumentClusteringComboBox.setGeometry(DataSourceDocumentClusteringTabVerticalLayoutWidget.width() * 0.8,
                                                       DataSourceDocumentClusteringTabVerticalLayoutWidget.height() * 0.4,
                                                       DataSourceDocumentClusteringTabVerticalLayoutWidget.width() / 10,
                                                       DataSourceDocumentClusteringTabVerticalLayoutWidget.height() / 5)
                DocumentClusteringComboBox.addItem('Scatter Plot')
                DocumentClusteringComboBox.addItem('Dendrogram')
                self.LineEditSizeAdjustment(DocumentClusteringComboBox)


                # LayoutWidget For within DataSourcesSimilarity Tab
                DataSourceDocumentClusteringTabVerticalLayoutWidget2 = QWidget(DataSourceDocumentClusteringTab)
                DataSourceDocumentClusteringTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10,
                                                                         self.tabWidget.width(),
                                                                         self.tabWidget.height() - self.tabWidget.height() / 10)

                # Box Layout for DataSourcesSimilarity Tab
                DataSourceDocumentClusteringTabVerticalLayout2 = QVBoxLayout(DataSourceDocumentClusteringTabVerticalLayoutWidget2)
                DataSourceDocumentClusteringTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

                canvas = FigureCanvas(myFile.ScatterFigure)
                DataSourceDocumentClusteringTabVerticalLayout2.addWidget(canvas)

                canvas2 = myFile.plot_canvas
                DataSourceDocumentClusteringTabVerticalLayout2.addWidget(canvas2)
                canvas2.hide()

                #canvas.draw()

                DocumentClusteringComboBox.currentTextChanged.connect(lambda: self.toggleDCCanvasView(DataSourceDocumentClusteringTabVerticalLayoutWidget2, canvas, canvas2))

                if DataSourceDocumentClusteringTabFlag2:
                    tabs.DataSourceName = len(myFile.DataSourceList)

                    if tabs.tabWidget.isHidden():
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        self.tabWidget.addTab(DataSourceDocumentClusteringTab, tabs.TabName)
                        self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)
                        tabs.tabWidget = DataSourceDocumentClusteringTab
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        self.tabWidget.addTab(DataSourceDocumentClusteringTab, tabs.TabName)
                        self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)
                        tabs.tabWidget = DataSourceDocumentClusteringTab

                else:
                    # Adding Word Cloud Tab to QTabWidget
                    myFile.TabList.append(
                        Tab("Document Clustering", DataSourceDocumentClusteringTab, len(myFile.DataSourceList)))

                    # Adding Word Frequency Query
                    ItemsWidget = self.VisualizationTreeWidget.findItems("Document Clustering", Qt.MatchExactly, 0)

                    if len(ItemsWidget) == 0:
                        DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                        DSVisualWidget.setText(0, "Document Clustering")
                        DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))

                    self.tabWidget.addTab(DataSourceDocumentClusteringTab, "Document Clustering")
                    self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)

            else:
                DataSourceDocumnetClusteringErrorBox = QMessageBox.critical(self, "Data Sources Documnet Clustering",
                                                                           "An Error Occured! Clustering can only be done if Data Sources are more than three",
                                                                            QMessageBox.Ok)

    # Update Similarity Between Data Sources
    def DataSourceDocumentClusteringUpdate(self):
        for tabs in myFile.TabList:
            if tabs.TabName == "Document Clustering":
                if self.tabWidget.indexOf(tabs.tabWidget) >= 0:
                    currentTab = self.tabWidget.currentWidget()
                    if len(myFile.DataSourceList) > 3:
                        self.DataSourceDocumentClustering()
                        self.tabWidget.setCurrentWidget(currentTab)
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                        ItemsWidget = self.VisualizationTreeWidget.findItems("Document Clustering", Qt.MatchExactly, 0)
                        for widget in ItemsWidget:
                            self.VisualizationTreeWidget.invisibleRootItem().removeChild(widget)
                    break
                else:
                    if len(myFile.DataSourceList) > 3:
                        self.DataSourceDocumentClustering()
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                        ItemsWidget = self.VisualizationTreeWidget.findItems("Document Clustering", Qt.MatchExactly, 0)
                        for widget in ItemsWidget:
                            self.VisualizationTreeWidget.invisibleRootItem().removeChild(widget)
                    break

    # Toggle POS View
    def toggleDCCanvasView(self, LayoutWidget, canvas, canvas2):
        ComboBox = self.sender()

        if ComboBox.currentText() == 'Scatter Plot':
            canvas2.hide()
            canvas.show()
        else:
            canvas.hide()
            canvas2.show()

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
        #Parent Data Source7
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
            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    break

            DataSourceRightClickMenu = QMenu(self.DataSourceTreeWidget)

            # Data Source Preview Web Page
            if hasattr(DS, 'DataSourceHTML'):
                DataSourcePreviewWeb = QAction('Preview Web', self.DataSourceTreeWidget)
                DataSourcePreviewWeb.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePreviewWeb(index))
                DataSourceRightClickMenu.addAction(DataSourcePreviewWeb)

            # Data Source Show Tweet Data
            if hasattr(DS, 'TweetData'):
                DataSourceShowTweetData = QAction('Show Tweet Data', self.DataSourceTreeWidget)
                DataSourceShowTweetData.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowTweetData(index))
                DataSourceRightClickMenu.addAction(DataSourceShowTweetData)

            # Data Source Show Youtube Comments
            DataSourceShowYoutubeComments = QAction('Show Youtube Data', self.DataSourceTreeWidget)

            if hasattr(DS, 'YoutubeURLFlag'):
                DataSourceShowYoutubeComments.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowYoutubeCommentsURL(index))
                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)

            if hasattr(DS, 'YoutubeKeyWordFlag'):
                DataSourceShowYoutubeComments.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceShowYoutubeCommentsKeyWord(index))
                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)

            # Data Source View Images
            if hasattr(DS, 'DataSourceImage'):
                DataSourceViewImages = QAction('View Image', self.DataSourceTreeWidget)
                DataSourceViewImages.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceViewImage(index))
                DataSourceRightClickMenu.addAction(DataSourceViewImages)

            # Data Sources Preview
            DataSourcePreviewText = QAction('Preview Text', self.DataSourceTreeWidget)

            if DS.DataSourceext == "Pdf files (*.pdf)":
                DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePDFPreview(index))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)
            elif DS.DataSourceext == "Doc files (*.doc *.docx)":
                DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceWordPreview(index))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)
            elif DS.DataSourceext == 'Notepad files (*.txt)' or DS.DataSourceext == 'Rich Text Format files (*.rtf)':
                DataSourcePreviewText.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourcePreview(index))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)

            # Data Source Add Image
            if hasattr(DS, 'DataSourceImage'):
                DataSourceAddImage = QAction('Add Image', self.DataSourceTreeWidget)
                DataSourceAddImage.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceAddImage(index))
                DataSourceRightClickMenu.addAction(DataSourceAddImage)

            # Data Source Create Cases
            DataSourceCreateCases = QAction('Create Cases...', self.DataSourceTreeWidget)
            DataSourceCreateCases.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceCreateCases(index))
            DataSourceRightClickMenu.addAction(DataSourceCreateCases)

            # Data Source Create Sentiments
            DataSourceCreateSentiments = QAction('Create Sentiments...', self.DataSourceTreeWidget)
            DataSourceCreateSentiments.triggered.connect(lambda checked, index=DataSourceWidgetItemName: self.DataSourceCreateSentiments(index))
            DataSourceRightClickMenu.addAction(DataSourceCreateSentiments)

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
        DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width*0.3, self.height*0.1)
        DataSourceWidgetDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        for letter in DataSourceWidgetItemName.text(0):
            if letter == '(':
                DataSourceStrTypeName = DataSourceWidgetItemName.text(0)[0: int(DataSourceWidgetItemName.text(0).index(letter))]

        # Data Source Type label
        DataSourceTypeLabel = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceTypeLabel.setText("Data Source Type:")
        DataSourceTypeLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                        DataSourceWidgetDetailDialogBox.height() * 0.3,
                                        DataSourceWidgetDetailDialogBox.width()/4,
                                        DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceTypeLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceTypeLabel)

        # Data Source Type lineEdit
        DataSourceTypeName = QLineEdit(DataSourceWidgetDetailDialogBox)
        DataSourceTypeName.setText(DataSourceStrTypeName)
        DataSourceTypeName.setReadOnly(True)
        DataSourceTypeName.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.4,
                                       DataSourceWidgetDetailDialogBox.height() * 0.3,
                                       DataSourceWidgetDetailDialogBox.width()/2,
                                       DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceTypeName.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceTypeName)

        # Data Source Child label
        DataSourceChildLabel = QLabel(DataSourceWidgetDetailDialogBox)
        DataSourceChildLabel.setText("No. of Data Sources:")
        DataSourceChildLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                         DataSourceWidgetDetailDialogBox.height() * 0.6,
                                         DataSourceWidgetDetailDialogBox.width()/4,
                                         DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceChildLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceChildLabel)

        # Data Source Child lineEdit
        DataSourceChildCountLabel = QLineEdit(DataSourceWidgetDetailDialogBox)
        DataSourceChildCountLabel.setReadOnly(True)
        DataSourceChildCountLabel.setText(str(DataSourceWidgetItemName.childCount()))
        DataSourceChildCountLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.4,
                                              DataSourceWidgetDetailDialogBox.height() * 0.6,
                                              DataSourceWidgetDetailDialogBox.width()/2,
                                              DataSourceWidgetDetailDialogBox.height()/5)
        DataSourceChildCountLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceChildCountLabel)

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

        if not DataSourcePreviewWebTabFlag:
            # Creating New Tab for Stem Word
            PreviewWebTab = QWidget()

            # LayoutWidget For within Stem Word Tab
            PreviewWebTabVerticalLayoutWidget = QWidget(PreviewWebTab)
            PreviewWebTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Stem Word Tab
            PreviewWebTabVerticalLayout = QHBoxLayout(PreviewWebTabVerticalLayoutWidget)
            PreviewWebTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            PreviewHTMLWebPage = QWebEngineView()
            PreviewHTMLWebPage.setContextMenuPolicy(Qt.PreventContextMenu)
            PreviewWebTabVerticalLayout.addWidget(PreviewHTMLWebPage)

            for DS in myFile.DataSourceList:
                if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                    PreviewHTMLWebPage.setHtml(DS.DataSourceHTML.decode("utf-8"))
                    break

            # Adding Preview Tab to TabList
            myFile.TabList.append(Tab("Preview", PreviewWebTab, DataSourceWidgetItemName.text(0)))

            # Adding Preview Tab to QTabWidget
            self.tabWidget.addTab(PreviewWebTab, "Preview")
            self.tabWidget.setCurrentWidget(PreviewWebTab)
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)

    # Data Source Show Tweet Data
    def DataSourceShowTweetData(self, DataSourceWidgetItemName):
        DataSourceShowTweetDataTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Tweet Data':
                DataSourceShowTweetDataTabFlag = True
                break

        if not DataSourceShowTweetDataTabFlag:
            ShowTweetDataTab = QWidget()
            ShowTweetDataTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
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

            ShowTweetDataTable.setWindowFlags(ShowTweetDataTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Tweet Data", ShowTweetDataTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowTweetDataTab, "Show Tweet Data")
            self.tabWidget.setCurrentWidget(ShowTweetDataTab)
        else:
            # updating tab
            self.tabWidget.addTab(ShowTweetDataTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowTweetDataTab)

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsURL(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                DataSourceShowYoutubeCommentsTabFlag = True
                break

        if not DataSourceShowYoutubeCommentsTabFlag:
            ShowYoutubeCommentsTab = QWidget()
            ShowYoutubeCommentsTab.setGeometry(QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
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

            ShowYoutubeCommentsTable.setWindowFlags(ShowYoutubeCommentsTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

            # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsKeyWord(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                DataSourceShowYoutubeCommentsTabFlag = True
                break

        if DataSourceShowYoutubeCommentsTabFlag:
            ShowYoutubeCommentsTab = QWidget()
            ShowYoutubeCommentsTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
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
                ShowYoutubeCommentsTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
                # Adding Word Frequency Tab to TabList
            myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))

            # Adding Word Frequency Tab to QTabWidget
            self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
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
            QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
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
                dummyimage = QImage(img, img.shape[1], \
                                          img.shape[0], img.shape[1] * 3,
                                          QImage.Format_RGB888)

                qpixmap_file.append(QPixmap(dummyimage))


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
        DataSourcePreviewTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                DataSourcePreviewTabFlag = True
                break

        if not DataSourcePreviewTabFlag:
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
                    PDFPreviewWeb.setUrl(QUrl(DS.DataSourcePath))
                    break

            # Adding Preview Tab to TabList
            myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

            # Adding Preview Tab to QTabWidget
            self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)

    # Data Source Word Preview
    def DataSourceWordPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                DataSourcePreviewTabFlag = True
                break

        if not DataSourcePreviewTabFlag:
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
                    WordActivex.setFocusPolicy(Qt.StrongFocus)
                    #contr = WordActivex.setControl("{00460182-9E5E-11d5-B7C8-B8269041DD57}")

                    WordActivex.setProperty("DisplayScrollBars", True);
                    WordActivex.setControl(DS.DataSourcePath)

                    DataSourceverticalLayout.addWidget(WordActivex)

            # Adding Preview Tab to TabList
            myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

            # Adding Preview Tab to QTabWidget
            self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)

    # Data Source Preview
    def DataSourcePreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                DataSourcePreviewTabFlag = True
                break

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

        if DataSourcePreviewTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(DataSourcePreviewTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
            tabs.tabWidget = DataSourcePreviewTab
        else:
            # Adding Preview Tab to TabList
            myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

            # Adding Preview Tab to QTabWidget
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
                DataSourceAddImageSuccessBox = QMessageBox.information(self, "Add Image",  "Images Added Successfully", QMessageBox.Ok)
                self.DataSourceSimilarityUpdate()
                self.DataSourceDocumentClusteringUpdate()
            else:
                ImagePathErrorText = ""

                for ImagePath in DS.AddImagePathDouble:
                    if DS.AddImagePathDouble.index(ImagePath) == len(DS.AddImagePathDouble) - 1:
                        ImagePathErrorText += ImagePath
                    else:
                        ImagePathErrorText += ImagePath + ', '

                if len(DS.AddImagePathDouble) > 1:
                    ImagePathErrorText += " are Already Added"
                else:
                    ImagePathErrorText += " is Already Added"

                DataSourceAddImageErrorBox = QMessageBox.critical(self, "Add Image",
                                                                       "Image Files : " + ImagePathErrorText,
                                                                       QMessageBox.Ok)

    # ****************************************************************************
    # ********************** Data Sources Show Frequency *************************
    # ****************************************************************************

    # Data Source Show Frequency Table Dialog
    def DataSourceShowFrequencyTableDialog(self):
        DataSourceShowFrequencyTableDialog = QDialog()
        DataSourceShowFrequencyTableDialog.setWindowTitle("Show Word Frequency Table")
        DataSourceShowFrequencyTableDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4, self.height / 10)
        DataSourceShowFrequencyTableDialog.setParent(self)
        DataSourceShowFrequencyTableDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceShowFrequencyTableDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)


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
            QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
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

        WordFrequencyTable.setWindowFlags(WordFrequencyTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
                ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:
                    DSVisualWidget = QTreeWidgetItem(self.QueryTreeWidget)
                    DSVisualWidget.setText(0, DataSourceName)
                    DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                    DSVisualWidget.setExpanded(True)

                    DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                    DSNewCaseNode.setText(0, 'Word Frequency')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Word Frequency')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                # Adding Word Frequency Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(DSNewCaseNode, WordFrequencyTab)

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
            QMessageBox.critical(self, "Saving Error", "Permission Denied!", QMessageBox.Ok)

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
        GenerateQuestionsDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        GenerateQuestionsDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        #Generate Question Tab
        GenerateQuestionsTab = QWidget()
        GenerateQuestionsTab.setGeometry(
            QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                         self.horizontalLayoutWidget.height() - self.tabWidget.tabBar().geometry().height()))
        GenerateQuestionsTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Generate Question Tab
        GenerateQuestionsTabVerticalLayoutWidget2 = QWidget(GenerateQuestionsTab)
        GenerateQuestionsTabVerticalLayoutWidget2.setGeometry(self.tabWidget.width() / 4, 0, self.tabWidget.width() / 2,
                                                          self.tabWidget.height() / 10)

        # Box Layout for Generate Question Tab
        GenerateQuestionsTabVerticalLayout2 = QHBoxLayout(GenerateQuestionsTabVerticalLayoutWidget2)
        GenerateQuestionsTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)


        # Download Button For Generate Question Table
        DownloadAsCSVButton = QPushButton('Download')
        DownloadAsCSVButton.setIcon(QIcon("Images/Download Button.png"))
        DownloadAsCSVButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

        DownloadAsCSVButtonFont = QFont("sans-serif")
        DownloadAsCSVButtonFont.setPixelSize(14)
        DownloadAsCSVButtonFont.setBold(True)

        DownloadAsCSVButton.setFont(DownloadAsCSVButtonFont)

        GenerateQuestionsTabVerticalLayout2.addWidget(DownloadAsCSVButton)

        # LayoutWidget For within Generate Question Tab
        GenerateQuestionsTabverticalLayoutWidget = QWidget(GenerateQuestionsTab)
        GenerateQuestionsTabverticalLayoutWidget.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                         self.tabWidget.height() - self.tabWidget.height() / 10)
        GenerateQuestionsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Generate Question Tab
        GenerateQuestionsverticalLayout = QVBoxLayout(GenerateQuestionsTabverticalLayoutWidget)
        GenerateQuestionsverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Generate Question
        GenerateQuestionsTable = QTableWidget(GenerateQuestionsTabverticalLayoutWidget)
        GenerateQuestionsTable.setColumnCount(1)
        # WordFrequencyTable.setModel(WordFrequencyTableModel)
        GenerateQuestionsTable.setGeometry(0, 0, GenerateQuestionsTabverticalLayoutWidget.width(),
                                       GenerateQuestionsTabverticalLayoutWidget.height())

        GenerateQuestionsTable.setSizePolicy(self.sizePolicy)

        GenerateQuestionsTable.setWindowFlags(GenerateQuestionsTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
                ptext.setPlainText(row)
                ptext.adjustSize()

                GenerateQuestionsTable.setCellWidget(rowList.index(row), 0, ptext)

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
                # Adding Generate Question Tab to TabList
                myFile.TabList.append(Tab("Generate Questions", GenerateQuestionsTab, DataSourceName))

                ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:                                   # if no Parent Widget
                    # Adding Parent Query
                    DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                    DSQueryWidget.setText(0, DataSourceName)
                    DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                    DSQueryWidget.setExpanded(True)

                    # Adding Generate Questions Query
                    DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                    DSNewCaseNode.setText(0, 'Generate Questions')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        # Adding Generate Questions Query
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Generate Questions')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                # Adding Generate Questions Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(DSNewCaseNode, GenerateQuestionsTab)

                # Adding Generate Questions Tab to QTabWidget
                self.tabWidget.addTab(GenerateQuestionsTab, "Generate Questions")
                self.tabWidget.setCurrentWidget(GenerateQuestionsTab)

        else:
            QMessageBox.information(self, "Questions Generation Error",
                                    "An Error Occurred! No Text Found in " + DataSourceName, QMessageBox.Ok)

    # ****************************************************************************
    # ********************* Data Sources Sentiment Analysis **********************
    # ****************************************************************************

    # Data Source Sentiment Analysis
    def DataSourcesSentimentAnalysis(self):
        SentimentAnalysisDialog = QDialog()
        SentimentAnalysisDialog.setWindowTitle("Sentiment Analysis")
        SentimentAnalysisDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                            self.height / 10)
        SentimentAnalysisDialog.setParent(self)
        SentimentAnalysisDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        SentimentAnalysisDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(SentimentAnalysisDialog)
        DataSourcelabel.setGeometry(SentimentAnalysisDialog.width() * 0.125,
                                    SentimentAnalysisDialog.height() * 0.2,
                                    SentimentAnalysisDialog.width() / 4,
                                    SentimentAnalysisDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(SentimentAnalysisDialog)
        DSComboBox.setGeometry(SentimentAnalysisDialog.width() * 0.4,
                               SentimentAnalysisDialog.height() * 0.2,
                               SentimentAnalysisDialog.width() / 2,
                               SentimentAnalysisDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        SentimentAnalysisbuttonBox = QDialogButtonBox(SentimentAnalysisDialog)
        SentimentAnalysisbuttonBox.setGeometry(SentimentAnalysisDialog.width() * 0.125,
                                               SentimentAnalysisDialog.height() * 0.7,
                                               SentimentAnalysisDialog.width() * 3 / 4,
                                               SentimentAnalysisDialog.height() / 5)
        SentimentAnalysisbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        SentimentAnalysisbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            SentimentAnalysisbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(SentimentAnalysisbuttonBox)

        SentimentAnalysisbuttonBox.accepted.connect(SentimentAnalysisDialog.accept)
        SentimentAnalysisbuttonBox.rejected.connect(SentimentAnalysisDialog.reject)

        SentimentAnalysisbuttonBox.accepted.connect(
            lambda: self.SentimentAnalysisTable(DSComboBox.currentText()))

        SentimentAnalysisDialog.exec()

    # Sentiment Analysis Tabel
    def SentimentAnalysisTable(self, DataSourceName):
        DataSourceSentimentAnalysisFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Automatic Sentiment Analysis':
                DataSourceSentimentAnalysisFlag = True
                break

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                DS.SentimentAnalysis()
                rowList = DS.AutomaticSentimentList
                break

        SentimentAnalysisTab = QWidget()
        SentimentAnalysisTab.setGeometry(QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(),
                                                      self.horizontalLayoutWidget.height() - self.tabWidget.tabBar().geometry().height()))
        SentimentAnalysisTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Stem Word Tab
        SentimentAnalysisTabVerticalLayoutWidget2 = QWidget(SentimentAnalysisTab)
        SentimentAnalysisTabVerticalLayoutWidget2.setGeometry(self.tabWidget.width() / 4, 0, self.tabWidget.width() / 2,
                                                              self.tabWidget.height() / 10)

        # Box Layout for Stem Word Tab
        SentimentAnalysisTabVerticalLayout2 = QHBoxLayout(SentimentAnalysisTabVerticalLayoutWidget2)
        SentimentAnalysisTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

        # Positive_Count Label
        PositiveCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget2)
        PositiveCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget2.width() * 0.05,
                                       SentimentAnalysisTabVerticalLayoutWidget2.height() * 0.142,
                                       SentimentAnalysisTabVerticalLayoutWidget2.width() / 20,
                                       SentimentAnalysisTabVerticalLayoutWidget2.height() / 7)
        PositiveCountLabel.setText("Positive: " + str(DS.PositiveSentimentCount))
        PositiveCountLabel.setAlignment(Qt.AlignVCenter)
        PositiveCountLabel.adjustSize()

        # Neutral_Count Label
        NeutralCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget2)
        NeutralCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget2.width() * 0.05,
                                      SentimentAnalysisTabVerticalLayoutWidget2.height() * 0.428,
                                      SentimentAnalysisTabVerticalLayoutWidget2.width() / 20,
                                      SentimentAnalysisTabVerticalLayoutWidget2.height() / 7)
        NeutralCountLabel.setText("Neutral: " + str(DS.NeutralSentimentCount))
        NeutralCountLabel.setAlignment(Qt.AlignVCenter)
        NeutralCountLabel.adjustSize()

        # Negative_Count Label
        NegativeCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget2)
        NegativeCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget2.width() * 0.05,
                                       SentimentAnalysisTabVerticalLayoutWidget2.height() * 0.714,
                                       SentimentAnalysisTabVerticalLayoutWidget2.width() / 20,
                                       SentimentAnalysisTabVerticalLayoutWidget2.height() / 7)
        NegativeCountLabel.setText("Negative: " + str(DS.NegativeSentimentCount))
        NegativeCountLabel.setAlignment(Qt.AlignVCenter)
        NegativeCountLabel.adjustSize()

        # Download Button For Frequency Table
        DownloadAsCSVButton = QPushButton('Download')
        DownloadAsCSVButton.setIcon(QIcon("Images/Download Button.png"))
        DownloadAsCSVButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

        DownloadAsCSVButtonFont = QFont("sans-serif")
        DownloadAsCSVButtonFont.setPixelSize(14)
        DownloadAsCSVButtonFont.setBold(True)

        DownloadAsCSVButton.setFont(DownloadAsCSVButtonFont)

        SentimentAnalysisTabVerticalLayout2.addWidget(DownloadAsCSVButton)

        # LayoutWidget For within Word Frequency Tab
        SentimentAnalysisTabverticalLayoutWidget = QWidget(SentimentAnalysisTab)
        SentimentAnalysisTabverticalLayoutWidget.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                                self.tabWidget.height() - self.tabWidget.height() / 10)
        SentimentAnalysisTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

        # Box Layout for Word Frequency Tab
        SentimentAnalysisverticalLayout = QVBoxLayout(SentimentAnalysisTabverticalLayoutWidget)
        SentimentAnalysisverticalLayout.setContentsMargins(0, 0, 0, 0)

        # Table for Word Frequency
        SentimentAnalysisTable = QTableWidget(SentimentAnalysisTabverticalLayoutWidget)
        SentimentAnalysisTable.setColumnCount(2)
        SentimentAnalysisTable.setGeometry(0, 0, SentimentAnalysisTabverticalLayoutWidget.width(),
                                                 SentimentAnalysisTabverticalLayoutWidget.height())

        SentimentAnalysisTable.setSizePolicy(self.sizePolicy)

        SentimentAnalysisTable.setWindowFlags(SentimentAnalysisTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        SentimentAnalysisTable.setHorizontalHeaderLabels(["Sentence", "Sentiments"])
        SentimentAnalysisTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(SentimentAnalysisTable.columnCount()):
            SentimentAnalysisTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            SentimentAnalysisTable.horizontalHeaderItem(i).setFont(QFont(SentimentAnalysisTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(SentimentAnalysisTable))

        if len(rowList) != 0:
            for row in rowList:
                SentimentAnalysisTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 0:
                        ptext = QPlainTextEdit()
                        ptext.setReadOnly(True)
                        ptext.setPlainText(item);
                        SentimentAnalysisTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                    else:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        SentimentAnalysisTable.setItem(rowList.index(row), row.index(item), intItem)
                        SentimentAnalysisTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        SentimentAnalysisTable.item(rowList.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            SentimentAnalysisTable.resizeColumnsToContents()
            SentimentAnalysisTable.resizeRowsToContents()

            SentimentAnalysisTable.setSortingEnabled(True)
            SentimentAnalysisTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

            for i in range(SentimentAnalysisTable.columnCount()):
                SentimentAnalysisTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if DataSourceSentimentAnalysisFlag:
                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(WordFrequencyTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(SentimentAnalysisTab)
                tabs.tabWidget = SentimentAnalysisTab

            else:
                # Adding Word Frequency Tab to TabList
                myFile.TabList.append(Tab("Automatic Sentiment Analysis", SentimentAnalysisTab, DataSourceName))

                # Adding Word Frequency Query
                ItemsWidget = self.SentimentTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:
                    DSVisualWidget = QTreeWidgetItem(self.SentimentTreeWidget)
                    DSVisualWidget.setText(0, DataSourceName)
                    DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                    DSVisualWidget.setExpanded(True)

                    DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                    DSNewCaseNode.setText(0, 'Automatic Sentiment Analysis')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Automatic Sentiment Analysis')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(SentimentAnalysisTab, "Automatic Sentiment Analysis")
                self.tabWidget.setCurrentWidget(SentimentAnalysisTab)

        else:
            QMessageBox.information(self, "Word Frequency Error",
                                    "An Error Occurred! No Text Found in " + DataSourceName, QMessageBox.Ok)

    # ****************************************************************************
    # ************************** Data Sources Rename *****************************
    # ****************************************************************************

    # Data Source Rename
    def DataSourceRename(self, DataSourceWidgetItemName):
        DataSourceRename = QDialog()
        DataSourceRename.setWindowTitle("Rename")
        DataSourceRename.setGeometry(self.width * 0.375, self.height * 0.425, self.width/4, self.height*0.15)
        DataSourceRename.setParent(self)
        DataSourceRename.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceRename.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

                    # ************ updating File Name *****************
                    DS.DataSourceName = name

                    self.DataSourceSimilarityUpdate()
                    self.DataSourceDocumentClusteringUpdate()
                    break



            DataSourceWidgetItemName.setText(0, name)
            DataSourceWidgetItemName.setToolTip(0, DataSourceWidgetItemName.text(0))

            QMessageBox.information(self, "Rename Success",
                                    "Data Source Rename Successfully!",
                                    QMessageBox.Ok)

        else:
            QMessageBox.critical(self, "Rename Error",
                                    "A Data Source with Similar Name Exist!",
                                    QMessageBox.Ok)

    # ****************************************************************************
    # ************************ Data Sources StemWords ****************************
    # ****************************************************************************

    # Data Source Create Query
    def DataSourceFindStemWords(self):
        DataSourceStemWord = QDialog()
        DataSourceStemWord.setWindowTitle("Find Stem Words")
        DataSourceStemWord.setGeometry(self.width * 0.375, self.height * 0.4, self.width / 4, self.height / 5)
        DataSourceStemWord.setParent(self)
        DataSourceStemWord.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceStemWord.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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


        for DS in myFile.DataSourceList:
            StemWordDSComboBox.addItem(DS.DataSourceName)

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
    def mapStemWordonTab(self, word, DataSourceName):
        DataSourceStemWordTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Stem Word':
                DataSourceStemWordTabFlag = True
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
            lambda: self.WordSuggestion(StemWordModel, StemWordLineEdit.text(), DataSourceName))

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
        StemWordTable.setWindowFlags(StemWordTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
        StemWordTable.setHorizontalHeaderLabels(["Word", "Frequency"])
        StemWordTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

        for i in range(StemWordTable.columnCount()):
            StemWordTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
            StemWordTable.horizontalHeaderItem(i).setFont(
                QFont(StemWordTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

        StemWordSubmitButton.clicked.connect(
            lambda: self.StemWordWithinTab(StemWordLineEdit.text(), DataSourceName, StemWordTable))

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
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
                    if DS.DataSourceName == DataSourceName:
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
                # Adding Stem Word Tab to QTabWidget
                myFile.TabList.append(Tab("Stem Word", StemWordTab, DataSourceName))

                ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:  # if no Parent Widget
                    # Adding Parent Query
                    DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                    DSQueryWidget.setText(0, DataSourceName)
                    DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                    DSQueryWidget.setExpanded(True)

                    # Adding Stem Word Query
                    DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                    DSNewCaseNode.setText(0, 'Stem Word')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        # Adding Stem Word Query
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Stem Word')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                # Adding Stem Word Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(DSNewCaseNode, StemWordTab)

                # Adding Stem Word Tab to QTabWidget
                self.tabWidget.addTab(StemWordTab, "Stem Word")
                self.tabWidget.setCurrentWidget(StemWordTab)

        else:
            QMessageBox(self, "Stem Word Error",
                        "An Error Occurred! No Stem Word Found of the Word \"" + word + "\"",
                        QMessageBox.Ok)

    #Word Suggestion
    def WordSuggestion(self, StemWordModel, CurrentText, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                dummyQuery = Query()
                WordList = dummyQuery.GetDistinctWords(DS.DataSourcetext)
                matching = [s for s in WordList if CurrentText in s]
                StemWordModel.setStringList(matching)

    #Get Stem Word From Column
    def StemWordWithinTab(self, word, DataSourceName, StemWordTable):
        while StemWordTable.rowCount() > 0:
            StemWordTable.removeRow(0)

        dummyQuery = Query()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
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

    # Data Source Part of Speech Dialog
    def DataSourcePOSDialog(self):
        PartOfSpeechDialog = QDialog()
        PartOfSpeechDialog.setWindowTitle("Part of Speech")
        PartOfSpeechDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                            self.height / 10)
        PartOfSpeechDialog.setParent(self)
        PartOfSpeechDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        PartOfSpeechDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(PartOfSpeechDialog)
        DataSourcelabel.setGeometry(PartOfSpeechDialog.width() * 0.125,
                                    PartOfSpeechDialog.height() * 0.2,
                                    PartOfSpeechDialog.width() / 4,
                                    PartOfSpeechDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(PartOfSpeechDialog)
        DSComboBox.setGeometry(PartOfSpeechDialog.width() * 0.4,
                               PartOfSpeechDialog.height() * 0.2,
                               PartOfSpeechDialog.width() / 2,
                               PartOfSpeechDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        PartOfSpeechbuttonBox = QDialogButtonBox(PartOfSpeechDialog)
        PartOfSpeechbuttonBox.setGeometry(PartOfSpeechDialog.width() * 0.125,
                                              PartOfSpeechDialog.height() * 0.7,
                                              PartOfSpeechDialog.width() * 3 / 4,
                                              PartOfSpeechDialog.height() / 5)
        PartOfSpeechbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        PartOfSpeechbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            PartOfSpeechbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(PartOfSpeechbuttonBox)

        PartOfSpeechbuttonBox.accepted.connect(PartOfSpeechDialog.accept)
        PartOfSpeechbuttonBox.rejected.connect(PartOfSpeechDialog.reject)

        PartOfSpeechbuttonBox.accepted.connect(
            lambda: self.DataSourcePOS(DSComboBox.currentText()))

        PartOfSpeechDialog.exec()

    # Data Source Part of Speech
    def DataSourcePOS(self, DataSourceName):
        DataSourcePOSTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Part of Speech':
                DataSourcePOSTabFlag = True
                break

        dummyQuery = Query()
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                POSGraph, rowList, noun_count, verb_count, adj_count = dummyQuery.PartOfSpeech(DS.DataSourceName,
                                                                                               DS.DataSourcetext, 3)
                break

        # Creating New Tab for Part of Speech
        POSTab = QWidget()

        # LayoutWidget For within Part of Speech Tab
        POSTabVerticalLayoutWidget = QWidget(POSTab)
        POSTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

        # Box Layout for Part of Speech Tab
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
        POSTable.setWindowFlags(POSTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
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
                if DS.DataSourceName == DataSourceName:
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
            # Adding Part of Speech Tab to QTabWidget
            myFile.TabList.append(Tab("Part of Speech", POSTab, DataSourceName))

            ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:  # if no Parent Widget
                # Adding Parent Query
                DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                DSQueryWidget.setText(0, DataSourceName)
                DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                DSQueryWidget.setExpanded(True)

                # Adding Part of Speech Query
                DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                DSNewCaseNode.setText(0, 'Parts of Speech')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    # Adding Part of Speech Query
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Parts of Speech')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            # Adding Part of Speech Query to QueryList
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DS.setQuery(DSNewCaseNode, POSTab)

            # Adding Part of Speech Tab to QTabWidget
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

    # Data Source Entity Relationship Dialog
    def DataSourceEntityRelationShipDialog(self):
        EntityRelationShipDialog = QDialog()
        EntityRelationShipDialog.setWindowTitle("Entity RelationShip")
        EntityRelationShipDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                       self.height / 10)
        EntityRelationShipDialog.setParent(self)
        EntityRelationShipDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        EntityRelationShipDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(EntityRelationShipDialog)
        DataSourcelabel.setGeometry(EntityRelationShipDialog.width() * 0.125,
                                    EntityRelationShipDialog.height() * 0.2,
                                    EntityRelationShipDialog.width() / 4,
                                    EntityRelationShipDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(EntityRelationShipDialog)
        DSComboBox.setGeometry(EntityRelationShipDialog.width() * 0.4,
                               EntityRelationShipDialog.height() * 0.2,
                               EntityRelationShipDialog.width() / 2,
                               EntityRelationShipDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        EntityRelationShipbuttonBox = QDialogButtonBox(EntityRelationShipDialog)
        EntityRelationShipbuttonBox.setGeometry(EntityRelationShipDialog.width() * 0.125,
                                                EntityRelationShipDialog.height() * 0.7,
                                                EntityRelationShipDialog.width() * 3 / 4,
                                                EntityRelationShipDialog.height() / 5)
        EntityRelationShipbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        EntityRelationShipbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            EntityRelationShipbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(EntityRelationShipbuttonBox)

        EntityRelationShipbuttonBox.accepted.connect(EntityRelationShipDialog.accept)
        EntityRelationShipbuttonBox.rejected.connect(EntityRelationShipDialog.reject)

        EntityRelationShipbuttonBox.accepted.connect(
            lambda: self.DataSourceEntityRelationShip(DSComboBox.currentText()))

        EntityRelationShipDialog.exec()

    # Data Source Entity Relationship
    def DataSourceEntityRelationShip(self, DataSourceName):
        DataSourceERTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Entity Relationship':
                DataSourceERTabFlag = True
                break

        dummyQuery = Query()
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                Entity_List, EntityHTML, DependencyHTML = dummyQuery.EntityRelationShip(
                    DS.DataSourcetext)
                break

        # Creating New Tab for Entity Relationship
        DSERTab = QWidget()

        # LayoutWidget For within Entity Relationship Tab
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

        # 2nd LayoutWidget For within Entity Relationship Tab
        DSERTabVerticalLayoutWidget2 = QWidget(DSERTab)
        DSERTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                 self.tabWidget.height() - self.tabWidget.height() / 10)

        # 2nd Box Layout for Stem Word Tab
        DSERTabVerticalLayout2 = QVBoxLayout(DSERTabVerticalLayoutWidget2)

        DSERTable = QTableWidget(DSERTabVerticalLayoutWidget2)
        DSERTable.setColumnCount(3)
        DSERTable.setGeometry(0, 0, DSERTabVerticalLayoutWidget2.width(), DSERTabVerticalLayoutWidget2.height())

        DSERTable.setSizePolicy(self.sizePolicy)
        DSERTable.setWindowFlags(DSERTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
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
        EntityHTMLWeb.setContextMenuPolicy(Qt.PreventContextMenu)
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
                if DS.DataSourceName == DataSourceName:
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
            # Adding Entity Relationship Tab to QTabWidget
            myFile.TabList.append(Tab("Entity Relationship", DSERTab, DataSourceName))

            ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:  # if no Parent Widget
                # Adding Parent Query
                DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                DSQueryWidget.setText(0, DataSourceName)
                DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                DSQueryWidget.setExpanded(True)

                # Adding Entity Relationship Query
                DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                DSNewCaseNode.setText(0, 'Entity Relationship')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    # Adding Entity Relationship Query
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Entity Relationship')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            # Adding Entity Relationship Query to QueryList
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DS.setQuery(DSNewCaseNode, DSERTab)

            # Adding Entity Relationship Tab to QTabWidget
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

    # Data Source Topic Modelling Dialog
    def DataSourceTopicModellingDialog(self):
        TopicModellingDialog = QDialog()
        TopicModellingDialog.setWindowTitle("Entity RelationShip")
        TopicModellingDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                             self.height / 10)
        TopicModellingDialog.setParent(self)
        TopicModellingDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        TopicModellingDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(TopicModellingDialog)
        DataSourcelabel.setGeometry(TopicModellingDialog.width() * 0.125,
                                    TopicModellingDialog.height() * 0.2,
                                    TopicModellingDialog.width() / 4,
                                    TopicModellingDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(TopicModellingDialog)
        DSComboBox.setGeometry(TopicModellingDialog.width() * 0.4,
                               TopicModellingDialog.height() * 0.2,
                               TopicModellingDialog.width() / 2,
                               TopicModellingDialog.height() / 10)

        for DS in myFile.DataSourceList:
            DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        TopicModellingbuttonBox = QDialogButtonBox(TopicModellingDialog)
        TopicModellingbuttonBox.setGeometry(TopicModellingDialog.width() * 0.125,
                                            TopicModellingDialog.height() * 0.7,
                                            TopicModellingDialog.width() * 3 / 4,
                                            TopicModellingDialog.height() / 5)
        TopicModellingbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        TopicModellingbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            TopicModellingbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(TopicModellingbuttonBox)

        TopicModellingbuttonBox.accepted.connect(TopicModellingDialog.accept)
        TopicModellingbuttonBox.rejected.connect(TopicModellingDialog.reject)

        TopicModellingbuttonBox.accepted.connect(
            lambda: self.DataSourceTopicModelling(DSComboBox.currentText()))

        TopicModellingDialog.exec()

    # Data Source Topic Modelling
    def DataSourceTopicModelling(self, DataSourceName):
        DataSourceTotalModellingTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Topic Modelling':
                DataSourceTotalModellingTabFlag = True
                break

        TopicModellingTab = QWidget()
        TopicModellingTab.setGeometry(QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.horizontalLayoutWidget.height()))
        TopicModellingTab.setSizePolicy(self.sizePolicy)

        # LayoutWidget For within Topic Modelling Tab
        TopicModellingTabVerticalLayoutWidget = QWidget(TopicModellingTab)
        TopicModellingTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height()/10)

        # Box Layout for Topic Modelling Tab
        TopicModellingTabVerticalLayout = QHBoxLayout(TopicModellingTabVerticalLayoutWidget)
        TopicModellingTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

        # ComboBox for Topic Modelling Tab
        TopicModellingComboBox = QComboBox(TopicModellingTabVerticalLayoutWidget)
        TopicModellingComboBox.setGeometry(TopicModellingTabVerticalLayoutWidget.width() * 0.8,
                                           TopicModellingTabVerticalLayoutWidget.height() * 0.4,
                                           TopicModellingTabVerticalLayoutWidget.width() / 10,
                                           TopicModellingTabVerticalLayoutWidget.height() / 5)

        TopicModellingComboBox.addItem("Show Word CLoud")
        TopicModellingComboBox.addItem("Show Table")
        TopicModellingComboBox.addItem("Show Word CLoud")
        self.LineEditSizeAdjustment(TopicModellingComboBox)


        # LayoutWidget For within Topic Modelling Tab
        TopicModellingTabVerticalLayoutWidget2 = QWidget(TopicModellingTab)
        TopicModellingTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height()/10, self.tabWidget.width(), self.tabWidget.height() - self.tabWidget.height()/10)

        # Box Layout for Topic Modelling Tab
        TopicModellingTabVerticalLayout2 = QHBoxLayout(TopicModellingTabVerticalLayoutWidget2)
        TopicModellingTabVerticalLayout2.setContentsMargins(0, 0, 0, 0)

        # Data Source Topic Modelling HTML
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                dummyQuery = Query()
                TopicModellingHTML = dummyQuery.TopicModelling(DS.DataSourcetext, 5)
                break

        # Topic Modelling HTML Viewer
        TopicModellingHTMLWeb = QWebEngineView()
        TopicModellingTabVerticalLayout2.addWidget(TopicModellingHTMLWeb)
        TopicModellingHTMLWeb.setHtml(TopicModellingHTML)

        if DataSourceTotalModellingTabFlag:
            # change tab in query
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
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
            # Adding Topic Modelling Tab to TabList
            myFile.TabList.append(Tab("Topic Modelling", TopicModellingTab, DataSourceName))


            ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:                                   # if no Parent Widget
                # Adding Parent Query
                DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                DSQueryWidget.setText(0, DataSourceName)
                DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                DSQueryWidget.setExpanded(True)

                # Adding Topic Modelling Query
                DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                DSNewCaseNode.setText(0, 'Topic Modelling')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    # Adding Topic Modelling Query
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Topic Modelling')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            # Adding Topic Modelling Query to QueryList
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DS.setQuery(DSNewCaseNode, TopicModellingTab)

            # Adding Topic Modelling Tab to QTabWidget
            self.tabWidget.addTab(TopicModellingTab, "Topic Modelling")
            self.tabWidget.setCurrentWidget(TopicModellingTab)

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
            lambda checked, index=QContextMenuEvent: self.CreateCasesContextMenu(index, DataSourceWidgetItemName))

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
        CreateCaseDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        CreateCaseDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width*0.3,
                                                    self.height / 10)
        CreateCaseDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
        AddtoCaseDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        AddtoCaseDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width * 0.3,
                                       self.height / 10)
        AddtoCaseDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            lambda checked, index=QContextMenuEvent: self.CreateSentimentsContextMenu(index, DataSourceWidgetItemName))

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
        AddtoSentimentsDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        AddtoSentimentsDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width * 0.3,
                                       self.height / 10)
        AddtoSentimentsDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        ItemsWidget = self.SentimentTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly, 0)

        if all([ v for v in NewWidgetAddFlagList]) and len(ItemsWidget) == 0:
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
    def DataSourceSummarize(self):
        # Summarization Dialog Box
        SummarizeDialog = QDialog()
        SummarizeDialog.setWindowTitle("Summarize")
        SummarizeDialog.setGeometry(self.width * 0.35, self.height * 0.35, self.width / 3, self.height / 3)
        SummarizeDialog.setParent(self)
        SummarizeDialog.setAttribute(Qt.WA_DeleteOnClose)
        SummarizeDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        SummarizeDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        for DS in myFile.DataSourceList:
            SummarizeDSComboBox.addItem(DS.DataSourceName)
        self.LineEditSizeAdjustment(SummarizeDSComboBox)

        # Summarize Word QSpinBox
        SummarizeWord = QDoubleSpinBox(SummarizeDialog)
        SummarizeWord.setGeometry(SummarizeDialog.width() * 0.5, SummarizeDialog.height() * 0.4,
                                  SummarizeDialog.width() / 3, SummarizeDialog.height() / 15)
        SummarizeWord.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
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
        SummarizeRatio.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
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


        SummarizebuttonBox.accepted.connect(
            lambda: self.DSSummarizeFromDialog(SummarizeDSComboBox.currentText(), DefaultRadioButton.isChecked(),
                                               TotalWordCountRadioButton.isChecked(), RatioRadioButton.isChecked(),
                                               SummarizeWord.value(), SummarizeRatio.value()))

        SummarizeDialog.exec()

    # Data Source Summarize
    def DSSummarizeFromDialog(self, DSName, DefaultRadioButton, TotalWordCountRadioButton, RatioRadioButton, SummarizeWord, SummarizeRatio):
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
            QMessageBox.information(self, "Success",
                                    DS.DataSourceName + " summarize successfully! The Summarize Text now contains " + str(len(DS.DataSourceTextSummary.split())), 
                                    QMessageBox.Ok)
            self.DataSourceSummaryPreview(DS.DataSourceName)
        else:
            delattr(DS, 'DataSourceTextSummary')
            QMessageBox.warning(self, "Error",
                                DS.DataSourceName + " summarization failed! The Text may contains no words or is already summarized",
                                QMessageBox.Ok)

    #Data Source Summary Preview
    def DataSourceSummaryPreview(self, DataSourceName):
        DataSourceSummaryPreviewTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Summary':
                DataSourceSummaryPreviewTabFlag = True
                break

        if not DataSourceSummaryPreviewTabFlag:
            DataSourceSummaryPreviewTab = QWidget()

            # LayoutWidget For within DataSource Preview Tab
            DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourceSummaryPreviewTab)
            DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
            DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Word Cloud Tab
            DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
            DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)


            DataSourceSummaryPreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
            DataSourceSummaryPreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourceSummaryPreview.setReadOnly(True)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DataSourceSummaryPreview.setText(DS.DataSourceTextSummary)
                    break

            # Adding Preview Tab to TabList
            myFile.TabList.append(Tab("Summary", DataSourceSummaryPreviewTab, DataSourceName))

            # Adding Word Frequency Query
            ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:
                DSVisualWidget = QTreeWidgetItem(self.QueryTreeWidget)
                DSVisualWidget.setText(0, DataSourceName)
                DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                DSVisualWidget.setExpanded(True)

                DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                DSNewCaseNode.setText(0, 'Summary')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Summary')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            # Adding Word Frequency Query to QueryList
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DS.setQuery(DSNewCaseNode, DataSourceSummaryPreviewTab)

            # Adding Preview Tab to QTabWidget
            self.tabWidget.addTab(DataSourceSummaryPreviewTab, "Summary")
            self.tabWidget.setCurrentWidget(DataSourceSummaryPreviewTab)

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)

    # ****************************************************************************
    # ************************ Data Sources Translation **************************
    # ****************************************************************************

    # Data Source Translate
    def DataSourceTranslateDialog(self):
        DataSourceTranslateDialog = QDialog()
        DataSourceTranslateDialog.setWindowTitle("Translate")
        DataSourceTranslateDialog.setGeometry(self.width * 0.35, self.height * 0.35, self.width / 3, self.height / 3)
        DataSourceTranslateDialog.setParent(self)
        DataSourceTranslateDialog.setAttribute(Qt.WA_DeleteOnClose)
        DataSourceTranslateDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceTranslateDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        TranslateDSLabel = QLabel(DataSourceTranslateDialog)
        TranslateDSLabel.setGeometry(DataSourceTranslateDialog.width() * 0.2, DataSourceTranslateDialog.height() * 0.1,
                                     DataSourceTranslateDialog.width() / 5, DataSourceTranslateDialog.height() / 15)
        TranslateDSLabel.setText("Data Source")
        self.LabelSizeAdjustment(TranslateDSLabel)

        # Data Source Original Text Label
        TranslateOriginalTextLabel = QLabel(DataSourceTranslateDialog)
        TranslateOriginalTextLabel.setGeometry(DataSourceTranslateDialog.width() * 0.2, DataSourceTranslateDialog.height() * 0.25,
                                               DataSourceTranslateDialog.width() / 5, DataSourceTranslateDialog.height() / 15)
        TranslateOriginalTextLabel.setText("Original Text")
        self.LabelSizeAdjustment(TranslateOriginalTextLabel)

        # Translate To Label
        TranslateToLabel = QLabel(DataSourceTranslateDialog)
        TranslateToLabel.setGeometry(DataSourceTranslateDialog.width() * 0.2, DataSourceTranslateDialog.height() * 0.4,
                                     DataSourceTranslateDialog.width() / 5, DataSourceTranslateDialog.height() / 15)
        TranslateToLabel.setText("Translate To:")
        self.LabelSizeAdjustment(TranslateToLabel)

        # Data Source ComboBox
        TranslateDSComboBox = QComboBox(DataSourceTranslateDialog)
        TranslateDSComboBox.setGeometry(DataSourceTranslateDialog.width() * 0.5, DataSourceTranslateDialog.height() * 0.1,
                                        DataSourceTranslateDialog.width() / 3, DataSourceTranslateDialog.height() / 15)

        for DS in myFile.DataSourceList:
            TranslateDSComboBox.addItem(DS.DataSourceName)
        self.LineEditSizeAdjustment(TranslateDSComboBox)

        # Data Source Original Text LineEdit
        TranslateOriginalTextLineEdit = QLineEdit(DataSourceTranslateDialog)
        TranslateOriginalTextLineEdit.setGeometry(DataSourceTranslateDialog.width() * 0.5, DataSourceTranslateDialog.height() * 0.25,
                                                  DataSourceTranslateDialog.width() / 3, DataSourceTranslateDialog.height() / 15)
        TranslateOriginalTextLineEdit.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        TranslateOriginalTextLineEdit.setReadOnly(True)
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == TranslateDSComboBox.currentText():
                if not hasattr(DS, 'OriginalText'):
                    DS.detect()
                    if not DS.LanguageDetectionError:
                        for langcode, lang in self.languages:
                            if langcode == DS.OriginalText:
                                TranslateOriginalTextLineEdit.setText(lang)
                                break
                    else:
                        TranslateOriginalTextLineEdit.setText("undetectable")
                else:
                    for langcode, lang in self.languages:
                        if langcode == DS.OriginalText:
                            TranslateOriginalTextLineEdit.setText(lang)
                            break
        self.LineEditSizeAdjustment(TranslateOriginalTextLineEdit)

        # Translate To ComboBox
        TranslateToComboBox = QComboBox(DataSourceTranslateDialog)
        TranslateToComboBox.setGeometry(DataSourceTranslateDialog.width() * 0.5, DataSourceTranslateDialog.height() * 0.4,
                                        DataSourceTranslateDialog.width() / 3, DataSourceTranslateDialog.height() / 15)
        TranslateToComboBox.setLayoutDirection(Qt.LeftToRight)

        for langcode, lang in self.languages:
            if not lang == TranslateOriginalTextLineEdit.text():
                TranslateToComboBox.addItem(lang)

        self.LineEditSizeAdjustment(TranslateToComboBox)

        TranslatebuttonBox = QDialogButtonBox(DataSourceTranslateDialog)
        TranslatebuttonBox.setGeometry(DataSourceTranslateDialog.width() * 0.5, DataSourceTranslateDialog.height() * 0.8,
                                       DataSourceTranslateDialog.width() / 3, DataSourceTranslateDialog.height() / 15)
        TranslatebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        TranslatebuttonBox.button(QDialogButtonBox.Ok).setText('Translate')
        self.LineEditSizeAdjustment(TranslatebuttonBox)

        if len(TranslateDSComboBox.currentText()) == 0 or TranslateOriginalTextLineEdit.text() == "undetectable":
            TranslatebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            TranslatebuttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

        TranslateDSComboBox.currentTextChanged.connect(
            lambda: self.TranslateDSComboboxTextChanged(TranslatebuttonBox, TranslateOriginalTextLineEdit, TranslateToComboBox))

        TranslatebuttonBox.accepted.connect(DataSourceTranslateDialog.accept)
        TranslatebuttonBox.rejected.connect(DataSourceTranslateDialog.reject)

        TranslatebuttonBox.accepted.connect(lambda: self.DataSourceTranslate(TranslateDSComboBox.currentText(), TranslateToComboBox.currentText()))
        DataSourceTranslateDialog.exec_()

    # Translate DSCombobox Text Changed       
    def TranslateDSComboboxTextChanged(self, buttonBox, OriginalText, TranslateTo):
        DSComboBox = self.sender()

        # Original Text LineEdit
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DSComboBox.currentText():
                if not hasattr(DS, 'OriginalText'):
                    DS.detect()
                    if not DS.LanguageDetectionError:
                        for langcode, lang in self.languages:
                            if langcode == DS.OriginalText:
                                OriginalText.setText(lang)
                                break
                    else:
                        OriginalText.setText("undetectable")
                else:
                    for langcode, lang in self.languages:
                        if langcode == DS.OriginalText:
                            OriginalText.setText(lang)
                            break

        # Translate To ComboBox
        TranslateTo.clear()
        for langcode, lang in self.languages:
            if not lang == OriginalText.text():
                TranslateTo.addItem(lang)

        if OriginalText.text() == "undetectable":
            TranslatebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    # Data Source Translate
    def DataSourceTranslate(self, DataSourceName, TranslateTo):
        for langcode, lang in self.languages:
            if lang == TranslateTo:
                break

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                DS.translate(langcode)
                break

        if not DS.TranslationError:
            DataSourceShowTranslationTabFlag = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Translated Text':
                    DataSourceShowTranslationTabFlag = True
                    break

            DataSourceShowTranslationTab = QWidget()
            DataSourceShowTranslationTab.setGeometry(QRect(self.verticalLayoutWidget.width(), self.top, self.width - self.verticalLayoutWidget.width(), self.horizontalLayoutWidget.height()))
            DataSourceShowTranslationTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Translation Tab
            DataSourceShowTranslationTabVerticalLayoutWidget = QWidget(DataSourceShowTranslationTab)
            DataSourceShowTranslationTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Translation Tab
            DataSourceShowTranslationTabVerticalLayout = QHBoxLayout(DataSourceShowTranslationTabVerticalLayoutWidget)
            DataSourceShowTranslationTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Data Source Translation Text Edit
            DataSourceTranslationPreview = QTextEdit(DataSourceShowTranslationTabVerticalLayoutWidget)
            DataSourceTranslationPreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourceTranslationPreview.setReadOnly(True)
            DataSourceTranslationPreview.setText(str(DS.DataSourceTranslatedText))

            if DataSourceShowTranslationTabFlag:
                # change tab in query
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        for query in DS.QueryList:
                            if query[1] == tabs.tabWidget:
                                query[1] = DataSourceShowTranslationTab
                                break

                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(DataSourceShowTranslationTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(DataSourceShowTranslationTab)
                tabs.tabWidget = DataSourceShowTranslationTab
            else:
                # Adding Translation Tab to TabList
                myFile.TabList.append(Tab("Translated Text", DataSourceShowTranslationTab, DataSourceName))

                ItemsWidget = self.QueryTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:  # if no Parent Widget
                    # Adding Parent Query
                    DSQueryWidget = QTreeWidgetItem(self.QueryTreeWidget)
                    DSQueryWidget.setText(0, DataSourceName)
                    DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                    DSQueryWidget.setExpanded(True)

                    # Adding Translation Query
                    DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                    DSNewCaseNode.setText(0, 'Translated Text')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        # Adding Translation Query
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Translated Text')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                # Adding Translation Query to QueryList
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == DataSourceName:
                        DS.setQuery(DSNewCaseNode, DataSourceShowTranslationTab)

                # Adding Translation Tab to QTabWidget
                self.tabWidget.addTab(DataSourceShowTranslationTab, "Translated Text")
                self.tabWidget.setCurrentWidget(DataSourceShowTranslationTab)

    # ****************************************************************************
    # *************************** Data Source Remove *****************************
    # ****************************************************************************

    #Data Source Remove
    def DataSourceRemove(self, DataSourceWidgetItemName):
        DataSourceRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this file? Doing this will remove all task related to " + DataSourceWidgetItemName.text(0),
                                                      QMessageBox.Yes | QMessageBox.No)

        if DataSourceRemoveChoice == QMessageBox.Yes:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    if DataSourceWidgetItemName.parent().childCount() == 1:
                        DataSourceWidgetItemName.parent().setHidden(True)


                    DataSourceWidgetItemName.parent().setText(0, DataSourceWidgetItemName.parent().text(0).replace(
                        ''.join(x for x in DataSourceWidgetItemName.parent().text(0) if x.isdigit()),
                        str(DataSourceWidgetItemName.parent().childCount()-1)
                    ))

                    DataSourceWidgetItemName.parent().removeChild(DataSourceWidgetItemName)

                    # Removing Queries
                    for query in range(len(DS.QueryList)):
                        self.QueryChildRemove(DS.QueryList[0][0])

                    # Removing Cases
                    for cases in DS.CasesList:
                        ItemsWidget = self.CasesTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0)
                        for widgets in ItemsWidget:
                            self.CasesParentRemove(widgets)

                    # Removing Queries
                    for sentiments in range(len(DS.SentimentList)):
                        ItemsWidget = self.SentimentTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0)
                        for widgets in ItemsWidget:
                            self.SentimentsRemove(widgets)

                    # Removing Queries
                    for visuals in range(len(DS.VisualizationList)):
                        self.VisualizationChildRemove(DS.VisualizationList[0][0])

                    # Removing all tabs related to Data Source
                    for tabs in myFile.TabList:
                        if DS.DataSourceName == tabs.DataSourceName:
                            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                            myFile.TabList.remove(tabs)

                    myFile.DataSourceList.remove(DS)
                    DS.__del__()
                    break

            self.DataSourceSimilarityUpdate()
            self.DataSourceDocumentClusteringUpdate()

        else:
            pass

    # ****************************************************************************
    # ************************* Data Source Child Detail *************************
    # ****************************************************************************

    # Data Source Child Detail
    def DataSourceChildDetail(self, DataSourceWidgetItemName):
        DataSourceWidgetDetailDialogBox = QDialog()
        DataSourceWidgetDetailDialogBox.setModal(True)
        DataSourceWidgetDetailDialogBox.setWindowTitle("Details")
        DataSourceWidgetDetailDialogBox.setParent(self)

        for DS in myFile.DataSourceList:
            if DS.DataSourceTreeWidgetItemNode == DataSourceWidgetItemName:
                break

        if DS.DataSourceext == "Doc files (*.doc *.docx)" or DS.DataSourceext == "Pdf files (*.pdf)" or DS.DataSourceext == "Notepad files (*.txt)" or DS.DataSourceext == "Rich Text Format files (*.rtf)" or DS.DataSourceext == "Audio files (*.wav *.mp3)":
            DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width/3,
                                                        self.height*2/5)
            DataSourceWidgetDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            DataSourceSizeLineEdit.setText(humanfriendly.format_size(DS.DataSourceSize, binary=True))
            DataSourceSizeLineEdit.setReadOnly(True)
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
            if len(DS.DataSourceImage) == 1:
                DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width / 3,
                                                            self.height * 2 / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

                # ************************************** Labels *************************************

                # Data Source Name Label
                DataSourceNameLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNameLabel.setText("Name:")
                DataSourceNameLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.1,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameLabel)

                # Data Source Path Label
                DataSourcePathLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourcePathLabel.setText("Path:")
                DataSourcePathLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.2,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourcePathLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourcePathLabel)

                # Data Source Ext Label
                DataSourceExtLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceExtLabel.setText("Extension:")
                DataSourceExtLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                               DataSourceWidgetDetailDialogBox.height() * 0.3,
                                               DataSourceWidgetDetailDialogBox.width() / 4,
                                               DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceExtLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceExtLabel)

                # Data Source Size Label
                DataSourceSize = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceSize.setText("Size:")
                DataSourceSize.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                           DataSourceWidgetDetailDialogBox.height() * 0.4,
                                           DataSourceWidgetDetailDialogBox.width() / 4,
                                           DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceSize.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceSize)

                # Data Source Access Time Label
                DataSourceAccessTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceAccessTime.setText("Last Access Time:")
                DataSourceAccessTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                 DataSourceWidgetDetailDialogBox.height() * 0.5,
                                                 DataSourceWidgetDetailDialogBox.width() / 4,
                                                 DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceAccessTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceAccessTime)

                # Data Source Modified Time Label
                DataSourceModifiedTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceModifiedTime.setText("Last Modified Time:")
                DataSourceModifiedTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.width() / 4,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceModifiedTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceModifiedTime)

                # Data Source Change Time Label
                DataSourceChangeTime = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceChangeTime.setText("Created Time:")
                DataSourceChangeTime.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                 DataSourceWidgetDetailDialogBox.height() * 0.7,
                                                 DataSourceWidgetDetailDialogBox.width() / 4,
                                                 DataSourceWidgetDetailDialogBox.height() / 20)
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
                DataSourceNameLineEdit.setText(ntpath.basename(DS.DataSourcePath[0]))
                DataSourceNameLineEdit.setReadOnly(True)
                DataSourceNameLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.1,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNameLineEdit)

                # Data Source Path LineEdit
                DataSourcePathLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourcePathLineEdit.setText(DS.DataSourcePath[0])
                DataSourcePathLineEdit.setReadOnly(True)
                DataSourcePathLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.2,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourcePathLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourcePathLineEdit)

                # Data Source Ext LineEdit
                DataSourceExtLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceExtLineEdit.setText(os.path.splitext(DS.DataSourcePath[0])[1])
                DataSourceExtLineEdit.setReadOnly(True)
                DataSourceExtLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                  DataSourceWidgetDetailDialogBox.height() * 0.3,
                                                  DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                  DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceExtLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceExtLineEdit)

                # Data Source Size LineEdit
                DataSourceSizeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceSizeLineEdit.setText(humanfriendly.format_size(DS.DataSourceSize[0], binary=True))
                DataSourceSizeLineEdit.setReadOnly(True)
                DataSourceSizeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.4,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceSizeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceSizeLineEdit)

                # Data Source Access Time LineEdit
                DataSourceAccessTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceAccessTimeLineEdit.setText(DS.DataSourceAccessTime[0])
                DataSourceAccessTimeLineEdit.setReadOnly(True)
                DataSourceAccessTimeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.height() * 0.5,
                                                         DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceAccessTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceAccessTimeLineEdit)

                # Data Source Modified Time LineEdit
                DataSourceModifiedTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceModifiedTimeLineEdit.setText(DS.DataSourceModifiedTime[0])
                DataSourceModifiedTimeLineEdit.setReadOnly(True)
                DataSourceModifiedTimeLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                           DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                           DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceModifiedTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceModifiedTimeLineEdit)

                # Data Source Change Time LineEdit
                DataSourceChangeTimeLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceChangeTimeLineEdit.setText(DS.DataSourceChangeTime[0])
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

            else:
                DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

                # ************************************** Labels *************************************

                # Data Source Name Label
                DataSourceNameLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNameLabel.setText("Name:")
                DataSourceNameLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.15,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNameLabel)

                # Data Source No of Images Label
                DataSourceNoofImagesLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceNoofImagesLabel.setText("No of Images:")
                DataSourceNoofImagesLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                      DataSourceWidgetDetailDialogBox.height() * 0.35,
                                                      DataSourceWidgetDetailDialogBox.width() / 4,
                                                      DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofImagesLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceNoofImagesLabel)


                # Data Source Word Count Label
                DataSourceWordCount = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceWordCount.setText("Total Words:")
                DataSourceWordCount.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.55,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceWordCount.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceWordCount)

                # ************************************** LineEdit *************************************

                # Data Source Name LineEdit
                DataSourceNameLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceNameLineEdit.setText(ntpath.basename(DS.DataSourcePath[0]))
                DataSourceNameLineEdit.setReadOnly(True)
                DataSourceNameLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                   DataSourceWidgetDetailDialogBox.height() * 0.15,
                                                   DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                   DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNameLineEdit)

                # Data Source No of Images LineEdit
                DataSourceNoofImagesLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceNoofImagesLineEdit.setText(str(len(DS.DataSourceImage)))
                DataSourceNoofImagesLineEdit.setReadOnly(True)
                DataSourceNoofImagesLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.height() * 0.35,
                                                         DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                         DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceNoofImagesLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceNoofImagesLineEdit)

                # Data Source Word Count LineEdit
                DataSourceWordCountLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext)))
                DataSourceWordCountLineEdit.setReadOnly(True)
                DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                        DataSourceWidgetDetailDialogBox.height() * 0.55,
                                                        DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)

                # Data Source Show Image Details
                DataSourceShowImageDetails = QPushButton(DataSourceWidgetDetailDialogBox)
                DataSourceShowImageDetails.setText('Show Images Detail')
                DataSourceShowImageDetails.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                       DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                       DataSourceWidgetDetailDialogBox.width() / 4,
                                                       DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceShowImageDetails.clicked.connect(lambda : self.DataSourceShowImagesDetails(DS, DataSourceWidgetDetailDialogBox))
                self.LabelSizeAdjustment(DataSourceShowImageDetails)

                DataSourceWidgetDetailDialogBox.exec_()

        elif DS.DataSourceext == "URL":
            DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                        self.height / 5)
            DataSourceWidgetDetailDialogBox.setWindowFlags(
                self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                        self.height / 5)
            DataSourceWidgetDetailDialogBox.setWindowFlags(
                self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
                DataSourceWidgetDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)
                DataSourceWidgetDetailDialogBox.setWindowFlags(
                    self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

    # Data Source Show Image Detail
    def DataSourceShowImagesDetails(self, DataSource, ParentWindow):
        DataSourceShowImagesDetailsBox = QDialog()
        DataSourceShowImagesDetailsBox.setModal(True)
        DataSourceShowImagesDetailsBox.setWindowTitle("Images Details")
        DataSourceShowImagesDetailsBox.setParent(ParentWindow)

        DataSourceShowImagesDetailsBox.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceShowImagesDetailsBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width / 3,
                                                    self.height * 2 / 5)
        DataSourceShowImagesDetailsBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # ************************************** Labels *************************************

        # Data Source Name Label
        DataSourceNameLabel = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceNameLabel.setText("Name:")
        DataSourceNameLabel.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                        DataSourceShowImagesDetailsBox.height() * 0.1,
                                        DataSourceShowImagesDetailsBox.width() / 4,
                                        DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNameLabel)

        # Data Source Path Label
        DataSourcePathLabel = QLabel(DataSourceShowImagesDetailsBox)
        DataSourcePathLabel.setText("Path:")
        DataSourcePathLabel.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                        DataSourceShowImagesDetailsBox.height() * 0.2,
                                        DataSourceShowImagesDetailsBox.width() / 4,
                                        DataSourceShowImagesDetailsBox.height() / 20)
        DataSourcePathLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourcePathLabel)

        # Data Source Ext Label
        DataSourceExtLabel = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceExtLabel.setText("Extension:")
        DataSourceExtLabel.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                       DataSourceShowImagesDetailsBox.height() * 0.3,
                                       DataSourceShowImagesDetailsBox.width() / 4,
                                       DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceExtLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceExtLabel)

        # Data Source Size Label
        DataSourceSize = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceSize.setText("Size:")
        DataSourceSize.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                   DataSourceShowImagesDetailsBox.height() * 0.4,
                                   DataSourceShowImagesDetailsBox.width() / 4,
                                   DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceSize.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceSize)

        # Data Source Access Time Label
        DataSourceAccessTime = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceAccessTime.setText("Last Access Time:")
        DataSourceAccessTime.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                         DataSourceShowImagesDetailsBox.height() * 0.5,
                                         DataSourceShowImagesDetailsBox.width() / 4,
                                         DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceAccessTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceAccessTime)

        # Data Source Modified Time Label
        DataSourceModifiedTime = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceModifiedTime.setText("Last Modified Time:")
        DataSourceModifiedTime.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                           DataSourceShowImagesDetailsBox.height() * 0.6,
                                           DataSourceShowImagesDetailsBox.width() / 4,
                                           DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceModifiedTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceModifiedTime)

        # Data Source Change Time Label
        DataSourceChangeTime = QLabel(DataSourceShowImagesDetailsBox)
        DataSourceChangeTime.setText("Created Time:")
        DataSourceChangeTime.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.1,
                                         DataSourceShowImagesDetailsBox.height() * 0.7,
                                         DataSourceShowImagesDetailsBox.width() / 4,
                                         DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceChangeTime.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceChangeTime)

        # ************************************** LineEdit *************************************

        # Data Source Name LineEdit
        DataSourceNameComboBox = QComboBox(DataSourceShowImagesDetailsBox)
        for DSImage in DataSource.DataSourcePath:
            DataSourceNameComboBox.addItem(ntpath.basename(DSImage))
        DataSourceNameComboBox.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                           DataSourceShowImagesDetailsBox.height() * 0.1,
                                           DataSourceShowImagesDetailsBox.width() * 0.6,
                                           DataSourceShowImagesDetailsBox.height() / 20)

        self.LineEditSizeAdjustment(DataSourceNameComboBox)

        # Data Source Path LineEdit
        DataSourcePathLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourcePathLineEdit.setText(DataSource.DataSourcePath[0])
        DataSourcePathLineEdit.setReadOnly(True)
        DataSourcePathLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                           DataSourceShowImagesDetailsBox.height() * 0.2,
                                           DataSourceShowImagesDetailsBox.width() * 0.6,
                                           DataSourceShowImagesDetailsBox.height() / 20)
        DataSourcePathLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourcePathLineEdit)

        # Data Source Ext LineEdit
        DataSourceExtLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourceExtLineEdit.setText(os.path.splitext(DataSource.DataSourcePath[0])[1])
        DataSourceExtLineEdit.setReadOnly(True)
        DataSourceExtLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                          DataSourceShowImagesDetailsBox.height() * 0.3,
                                          DataSourceShowImagesDetailsBox.width() * 0.6,
                                          DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceExtLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceExtLineEdit)

        # Data Source Size LineEdit
        DataSourceSizeLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourceSizeLineEdit.setText(humanfriendly.format_size(DataSource.DataSourceSize[0], binary=True))
        DataSourceSizeLineEdit.setReadOnly(True)
        DataSourceSizeLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                           DataSourceShowImagesDetailsBox.height() * 0.4,
                                           DataSourceShowImagesDetailsBox.width() * 0.6,
                                           DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceSizeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceSizeLineEdit)

        # Data Source Access Time LineEdit
        DataSourceAccessTimeLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourceAccessTimeLineEdit.setText(DataSource.DataSourceAccessTime[0])
        DataSourceAccessTimeLineEdit.setReadOnly(True)
        DataSourceAccessTimeLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                                 DataSourceShowImagesDetailsBox.height() * 0.5,
                                                 DataSourceShowImagesDetailsBox.width() * 0.6,
                                                 DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceAccessTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceAccessTimeLineEdit)

        # Data Source Modified Time LineEdit
        DataSourceModifiedTimeLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourceModifiedTimeLineEdit.setText(DataSource.DataSourceModifiedTime[0])
        DataSourceModifiedTimeLineEdit.setReadOnly(True)
        DataSourceModifiedTimeLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                                   DataSourceShowImagesDetailsBox.height() * 0.6,
                                                   DataSourceShowImagesDetailsBox.width() * 0.6,
                                                   DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceModifiedTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceModifiedTimeLineEdit)

        # Data Source Change Time LineEdit
        DataSourceChangeTimeLineEdit = QLineEdit(DataSourceShowImagesDetailsBox)
        DataSourceChangeTimeLineEdit.setText(DataSource.DataSourceChangeTime[0])
        DataSourceChangeTimeLineEdit.setReadOnly(True)
        DataSourceChangeTimeLineEdit.setGeometry(DataSourceShowImagesDetailsBox.width() * 0.35,
                                                 DataSourceShowImagesDetailsBox.height() * 0.7,
                                                 DataSourceShowImagesDetailsBox.width() * 0.6,
                                                 DataSourceShowImagesDetailsBox.height() / 20)
        DataSourceChangeTimeLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceChangeTimeLineEdit)
        DataSourceNameComboBox.currentText()
        DataSourceNameComboBox.currentTextChanged.connect(lambda: self.DataSourceImageDetailComboBoxtoggle(DataSource, DataSourcePathLineEdit, DataSourceExtLineEdit, DataSourceSizeLineEdit, DataSourceAccessTimeLineEdit, DataSourceModifiedTimeLineEdit, DataSourceChangeTimeLineEdit))
        DataSourceShowImagesDetailsBox.exec_()

    # Data Source Show Image Detail Toogle
    def DataSourceImageDetailComboBoxtoggle(self, DS, Path, Ext, Size, AccessTime, ModifiedTime, ChangedTime):
        ComboBox = self.sender()
        currentText = ComboBox.currentText()


        for DSImageName in DS.DataSourcePath:
            if ntpath.basename(DSImageName) == currentText:
                currentIndex = DS.DataSourcePath.index(DSImageName)
                break

        Path.setText(DS.DataSourcePath[currentIndex])
        Ext.setText(os.path.splitext(DS.DataSourcePath[currentIndex])[1])
        Size.setText(humanfriendly.format_size(DS.DataSourceSize[currentIndex], binary=True))
        AccessTime.setText(DS.DataSourceAccessTime[currentIndex])
        ModifiedTime.setText(DS.DataSourceModifiedTime[currentIndex])
        ChangedTime.setText(DS.DataSourceChangeTime[currentIndex])

    # ****************************************************************************
    # ********************* Data Source Create Dashboard *************************
    # ****************************************************************************

    # Create Dashboard Dialog
    def DataSourcesCreateDashboardDialog(self):
        DataSourcesCreateDashboardDialog = QDialog()
        DataSourcesCreateDashboardDialog.setWindowTitle("Create Dashboard")
        DataSourcesCreateDashboardDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                       self.height / 10)
        DataSourcesCreateDashboardDialog.setParent(self)
        DataSourcesCreateDashboardDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourcesCreateDashboardDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
        print()

    # Create Dashboard
    def DataSourcesCreateDashboard(self, DataSourceName):
        print("Hello")

    # ****************************************************************************
    # ************************ Data Sources Word CLoud ***************************
    # ****************************************************************************

    # Data Source Create World Cloud
    def DataSourceCreateCloud(self):
        CreateWordCloudDialog = QDialog()
        CreateWordCloudDialog.setWindowTitle("Create Word Cloud")
        CreateWordCloudDialog.setGeometry(self.width * 0.35, self.height*0.35, self.width/3, self.height/3)
        CreateWordCloudDialog.setParent(self)
        CreateWordCloudDialog.setAttribute(Qt.WA_DeleteOnClose)
        CreateWordCloudDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        CreateWordCloudDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        for DS in myFile.DataSourceList:
            WordCloudDSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(WordCloudDSComboBox)

        WordCloudBackgroundColor = QComboBox(CreateWordCloudDialog)
        WordCloudBackgroundColor.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.25, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)
        WordCloudBackgroundColor.setLayoutDirection(Qt.LeftToRight)

        for colorname, colorhex in matplotlib.colors.cnames.items():
            WordCloudBackgroundColor.addItem(colorname)

        self.LineEditSizeAdjustment(WordCloudBackgroundColor)

        WordCloudMaxWords = QDoubleSpinBox(CreateWordCloudDialog)
        WordCloudMaxWords.setGeometry(CreateWordCloudDialog.width() * 0.5, CreateWordCloudDialog.height()*0.4, CreateWordCloudDialog.width()/3, CreateWordCloudDialog.height()/15)
        WordCloudMaxWords.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
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
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(WordCloudTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(WordCloudTab)
            tabs.tabWidget = WordCloudTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Word Cloud", WordCloudTab, WCDSName))

            ItemsWidget = self.VisualizationTreeWidget.findItems(WCDSName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:
                DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                DSVisualWidget.setText(0, WCDSName)
                DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                DSVisualWidget.setExpanded(True)

                DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                DSNewCaseNode.setText(0, 'Word Cloud')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Word Cloud')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))


            for DS in myFile.DataSourceList:
                if DS.DataSourceName == WCDSName:
                     DS.setVisual(DSNewCaseNode, WordCloudTab)

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
    # ********************** Data Source Coordinate Map **************************
    # ****************************************************************************

    # Create Coordinate Map Dialog
    def DataSourceCoordinateMapDialog(self):
        DataSourceCoordinateMapDialog = QDialog()
        DataSourceCoordinateMapDialog.setWindowTitle("Coordinate Map")
        DataSourceCoordinateMapDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                     self.height / 10)
        DataSourceCoordinateMapDialog.setParent(self)
        DataSourceCoordinateMapDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        DataSourceCoordinateMapDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Data Source Label
        DataSourcelabel = QLabel(DataSourceCoordinateMapDialog)
        DataSourcelabel.setGeometry(DataSourceCoordinateMapDialog.width() * 0.125,
                                    DataSourceCoordinateMapDialog.height() * 0.2,
                                    DataSourceCoordinateMapDialog.width() / 4,
                                    DataSourceCoordinateMapDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourceCoordinateMapDialog)
        DSComboBox.setGeometry(DataSourceCoordinateMapDialog.width() * 0.4,
                               DataSourceCoordinateMapDialog.height() * 0.2,
                               DataSourceCoordinateMapDialog.width() / 2,
                               DataSourceCoordinateMapDialog.height() / 10)
        # if len(myFile.DataSourceList) > 1:
        #     DSComboBox.addItem("All")
        for DS in myFile.DataSourceList:
            if DS.DataSourceext == 'Tweet':
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Stem Word Button Box
        DataSourcesCoordinateMapbuttonBox = QDialogButtonBox(DataSourceCoordinateMapDialog)
        DataSourcesCoordinateMapbuttonBox.setGeometry(DataSourceCoordinateMapDialog.width() * 0.125,
                                                        DataSourceCoordinateMapDialog.height() * 0.7,
                                                        DataSourceCoordinateMapDialog.width() * 3 / 4,
                                                        DataSourceCoordinateMapDialog.height() / 5)
        DataSourcesCoordinateMapbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourcesCoordinateMapbuttonBox.button(QDialogButtonBox.Ok).setText('Show')

        if DSComboBox.count() == 0:
            DataSourcesCoordinateMapbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(DataSourcesCoordinateMapbuttonBox)

        DataSourcesCoordinateMapbuttonBox.accepted.connect(DataSourceCoordinateMapDialog.accept)
        DataSourcesCoordinateMapbuttonBox.rejected.connect(DataSourceCoordinateMapDialog.reject)

        DataSourcesCoordinateMapbuttonBox.accepted.connect(
            lambda: self.DataSourceCoordinateMap(DSComboBox.currentText()))

        DataSourceCoordinateMapDialog.exec()

    # Create Coordinate Map
    def DataSourceCoordinateMap(self, DataSourceName):
        DataSourceCoordinateMapTabFlag = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Coordinate Map':
                DataSourceCoordinateMapTabFlag = True
                break


        DataSourceCoordinateMapTab = QWidget()

        # LayoutWidget For within DataSource Preview Tab
        DataSourceCoordinateMapTabverticalLayoutWidget = QWidget(DataSourceCoordinateMapTab)
        DataSourceCoordinateMapTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)

        if self.tabWidget.width() > 800 and self.tabWidget.height() > 600:
            DataSourceCoordinateMapTabverticalLayoutWidget.setGeometry((self.tabWidget.width() - 800)/2, (self.tabWidget.height() - 600)/2, 800, 600)
        else:
            DataSourceCoordinateMapTabverticalLayoutWidget.setGeometry(abs(self.tabWidget.width() - 800)/2, abs(self.tabWidget.height() - 600)/2, self.tabWidget.width(), self.tabWidget.height())

        DataSourceCoordinateMap = QtQuickWidgets.QQuickWidget(DataSourceCoordinateMapTabverticalLayoutWidget)
        model = MarkerModel(DataSourceCoordinateMap)
        DataSourceCoordinateMap.rootContext().setContextProperty("markermodel", model)

        qml_path = os.path.join(os.path.dirname(__file__), "map.qml")
        DataSourceCoordinateMap.setSource(QUrl.fromLocalFile(qml_path))

        positions = []

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                break

        for data in DS.TweetData:
            for coordinates in self.Coordinates:
                if data[4].split(',')[0].strip() == coordinates[0]:
                    positions.append((float(coordinates[1]), float(coordinates[2])))

        urls = []

        for items in positions:
            urls.append("Images/Marker.png")

        for c, u in zip(positions, urls):
            coord = QtPositioning.QGeoCoordinate(*c)
            source = QUrl(u)
            model.appendMarker({"position": coord, "source": source})

        if DataSourceCoordinateMapTabFlag:
            # updating tab
            self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
            self.tabWidget.addTab(DataSourceCoordinateMapTab, tabs.TabName)
            self.tabWidget.setCurrentWidget(DataSourceCoordinateMapTab)
            tabs.tabWidget = DataSourceCoordinateMapTab

        else:
            # Adding Word Cloud Tab to QTabWidget
            myFile.TabList.append(Tab("Coordinate Map", DataSourceCoordinateMapTab, DataSourceName))

            ItemsWidget = self.VisualizationTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:
                DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                DSVisualWidget.setText(0, DataSourceName)
                DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                DSVisualWidget.setExpanded(True)

                DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                DSNewCaseNode.setText(0, 'Coordinate Map')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Coordinate Map')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    DS.setVisual(DSNewCaseNode, DataSourceCoordinateMapTab)

            self.tabWidget.addTab(DataSourceCoordinateMapTab, "Coordinate Map")
            self.tabWidget.setCurrentWidget(DataSourceCoordinateMapTab)

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
        if QueryItemName.parent() == None:
            if QueryItemName.text(0) == "Data Sources Similarity":
                QueryRightClickMenu = QMenu(self.QueryTreeWidget)

                QueryShow = QAction('Show', self.QueryTreeWidget)
                QueryShow.triggered.connect(lambda: self.QueryDoubleClickHandler(QueryItemName))
                QueryRightClickMenu.addAction(QueryShow)

                QueryRemove = QAction('Remove', self.QueryTreeWidget)
                QueryRemove.triggered.connect(lambda: self.QueryParentRemove(QueryItemName))
                QueryRightClickMenu.addAction(QueryRemove)

                QueryRightClickMenu.popup(QueryWidgetPos)

            else:
                QueryRightClickMenu = QMenu(self.QueryTreeWidget)

                # Query Expand
                QueryExpand = QAction('Expand', self.QueryTreeWidget)
                QueryExpand.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(QueryItemName))
                if (QueryItemName.childCount() == 0 or QueryItemName.isExpanded() == True):
                    QueryExpand.setDisabled(True)
                else:
                    QueryExpand.setDisabled(False)
                QueryRightClickMenu.addAction(QueryExpand)

                # Query Collapse
                QueryCollapse = QAction('Collapse', self.QueryTreeWidget)
                QueryCollapse.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(QueryItemName))

                if (QueryItemName.childCount() == 0 or QueryItemName.isExpanded() == False):
                    QueryCollapse.setDisabled(True)
                else:
                    QueryCollapse.setDisabled(False)
                QueryRightClickMenu.addAction(QueryCollapse)

                # Query Remove
                QueryRemove = QAction('Remove', self.QueryTreeWidget)
                QueryRemove.triggered.connect(lambda: self.QueryParentRemove(QueryItemName))

                QueryRightClickMenu.addAction(QueryRemove)

                QueryRightClickMenu.popup(QueryWidgetPos)
        else:
            QueryRightClickMenu = QMenu(self.QueryTreeWidget)

            QueryShow = QAction('Show', self.QueryTreeWidget)
            QueryShow.triggered.connect(lambda: self.QueryDoubleClickHandler(QueryItemName))
            QueryRightClickMenu.addAction(QueryShow)

            QueryRemove = QAction('Remove', self.QueryTreeWidget)
            QueryRemove.triggered.connect(lambda: self.QueryChildRemoveDialog(QueryItemName))
            QueryRightClickMenu.addAction(QueryRemove)

            QueryRightClickMenu.popup(QueryWidgetPos)

    # Remove Parent Query (Tab)
    def QueryParentRemove(self, QueryItemName):
        QueryRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's all Queries?",
                                                         QMessageBox.Yes | QMessageBox.No)

        if QueryRemoveChoice == QMessageBox.Yes:
            if QueryItemName.text(0) == 'Data Sources Similarity':
                for tabs in myFile.TabList:
                    if tabs.TabName == 'Data Sources Similarity':
                        myFile.TabList.remove(tabs)
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        tabs.__del__()

                self.QueryTreeWidget.invisibleRootItem().removeChild(QueryItemName)

            else:
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == QueryItemName.text(0):
                        for tabs in myFile.TabList:
                            if tabs.DataSourceName == DS.DataSourceName:
                                myFile.TabList.remove(tabs)
                                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                                tabs.__del__()

                        self.QueryTreeWidget.invisibleRootItem().removeChild(QueryItemName)
                        DS.QueryList.clear()
                        break
        else:
            pass

    # Remove Child Query (Tab) Dialog
    def QueryChildRemoveDialog(self, QueryItemName):
        QueryRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's Query?",
                                                        QMessageBox.Yes | QMessageBox.No)

        if QueryRemoveChoice == QMessageBox.Yes:
            self.QueryChildRemove(QueryItemName)
        else:
            pass

    # Remove Child Query (Tab)
    def QueryChildRemove(self, QueryItemName):
        for tabs in myFile.TabList:
            if tabs.DataSourceName == QueryItemName.parent().text(0):
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == tabs.DataSourceName:
                        for query in DS.QueryList:
                            if query[0] == QueryItemName and query[1] == tabs.tabWidget:
                                myFile.TabList.remove(tabs)
                                DS.QueryList.remove(query)
                                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                                tabs.__del__()
                                break

        if QueryItemName.parent().childCount() == 1:
            tempParent = QueryItemName.parent()
            tempParent.removeChild(QueryItemName)
            self.QueryTreeWidget.invisibleRootItem().removeChild(tempParent)
        else:
            QueryItemName.parent().removeChild(QueryItemName)

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
            for tabs in myFile.TabList:
                if tabs.DataSourceName == QueryItemName.parent().text(0):
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

            # Case Remove
            CasesParentRemove = QAction('Remove', self.CasesTreeWidget)
            CasesParentRemove.triggered.connect(lambda: self.CasesParentRemoveDialog(CasesItemName))
            CasesRightClickMenu.addAction(CasesParentRemove)

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
            CasesRename = QAction('Rename', self.CasesTreeWidget)
            CasesRename.triggered.connect(lambda: self.CasesRename(CasesItemName))
            CasesRightClickMenu.addAction(CasesRename)

            # Case Remove
            CasesChildRemove = QAction('Remove', self.CasesTreeWidget)
            CasesChildRemove.triggered.connect(lambda: self.CasesChildRemoveDialog(CasesItemName))
            CasesRightClickMenu.addAction(CasesChildRemove)

            # Case Child Detail
            CasesDetail = QAction('Details', self.CasesTreeWidget)
            CasesDetail.triggered.connect(lambda: self.CasesChildDetail(CasesItemName))
            CasesRightClickMenu.addAction(CasesDetail)

            CasesRightClickMenu.popup(CasesWidgetPos)

    # Cases Parent Remove Dialog
    def CasesParentRemoveDialog(self, CasesItemName):
        CasesRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                      "Are you sure you want to remove this Data Source's Cases?",
                                                      QMessageBox.Yes | QMessageBox.No)

        if CasesRemoveChoice == QMessageBox.Yes:
            self.CasesParentRemove(CasesItemName)
        else:
            pass

    # Cases Parent Remove
    def CasesParentRemove(self, CasesItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.text(0):
                self.CasesTreeWidget.invisibleRootItem().removeChild(CasesItemName)
                DS.CasesList.clear()
                break

    # Cases Parent Detail
    def CasesParentDetail(self, CasesItemName):
        CasesParentDetailDialogBox = QDialog()
        CasesParentDetailDialogBox.setModal(True)
        CasesParentDetailDialogBox.setWindowTitle("Details")
        CasesParentDetailDialogBox.setParent(self)
        CasesParentDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        CasesParentDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width / 3,
                                                    self.height / 10)
        CasesParentDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            CaseShowComponentTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
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
                    deleteButton.clicked.connect(lambda: self.deleteCaseComponentRow(CasesItemName, CaseShowComponentTable))
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
    def deleteCaseComponentRow(self, CasesItemName, Table):
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
        CaseRenameDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        CaseRenameDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

            CasesRenameSuccessBox = QMessageBox.Information(self, "Rename Success", "Case Rename Successfully!", QMessageBox.Ok)
        else:
            CasesRenameSuccessBox = QMessageBox.Critical(self, "Rename Error", "A Case with Similar Name Exist!",QMessageBox.Ok)

    # Cases Remove Dialog
    def CasesChildRemoveDialog(self, CasesItemName):
        CasesRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this Case?",
                                                 QMessageBox.Yes | QMessageBox.No)

        if CasesRemoveChoice == QMessageBox.Yes:
            self.CasesChildRemove(CasesItemName)
        else:
            pass

    # Cases Remove Dialog
    def CasesChildRemove(self, CasesItemName):
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

    # Cases Child Detail
    def CasesChildDetail(self, CasesItemName):
        CasesChildDetailDialogBox = QDialog()
        CasesChildDetailDialogBox.setModal(True)
        CasesChildDetailDialogBox.setWindowTitle("Details")
        CasesChildDetailDialogBox.setParent(self)
        CasesChildDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        CasesChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                               self.height / 5)
        CasesChildDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        # No of Cases LineEdit
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

    # Get Which Sentiments Widget Item and its Position
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

    # Setting ContextMenu on Clicked Sentiments
    def SentimentsTreeWidgetContextMenu(self, SentimentsItemName, SentimentsWidgetPos):
        # Parent Sentiments
        if SentimentsItemName.parent() == None:
            SentimentsRightClickMenu = QMenu(self.SentimentTreeWidget)

            # Sentiments Expand
            SentimentsExpand = QAction('Expand', self.SentimentTreeWidget)
            SentimentsExpand.triggered.connect(lambda checked, index=SentimentsItemName: self.DataSourceWidgetItemExpandCollapse(index))
            if (SentimentsItemName.childCount() == 0 or SentimentsItemName.isExpanded() == True):
                SentimentsExpand.setDisabled(True)
            else:
                SentimentsExpand.setDisabled(False)
            SentimentsRightClickMenu.addAction(SentimentsExpand)

            # Sentiments Collapse
            SentimentsCollapse = QAction('Collapse', self.SentimentTreeWidget)
            SentimentsCollapse.triggered.connect(lambda checked, index=SentimentsItemName: self.DataSourceWidgetItemExpandCollapse(index))
            if (SentimentsItemName.childCount() == 0 or SentimentsItemName.isExpanded() == False):
                SentimentsCollapse.setDisabled(True)
            else:
                SentimentsCollapse.setDisabled(False)
            SentimentsRightClickMenu.addAction(SentimentsCollapse)

            # Sentiments Remove
            SentimentsRemove = QAction('Remove', self.SentimentTreeWidget)
            SentimentsRemove.triggered.connect(lambda checked, index=SentimentsItemName: self.SentimentsRemoveDialog(index))

            SentimentsRightClickMenu.addAction(SentimentsRemove)

            SentimentsRightClickMenu.popup(SentimentsWidgetPos)

        # Child Sentiments
        else:
            SentimentsRightClickMenu = QMenu(self.SentimentTreeWidget)

            # Sentiments Show components
            SentimentsShowTopicText = QAction('Show Topic Components', self.SentimentTreeWidget)
            SentimentsShowTopicText.triggered.connect(lambda: self.SentimentsShowComponent(SentimentsItemName))
            SentimentsRightClickMenu.addAction(SentimentsShowTopicText)

            # Sentiments Child Detail
            SentimentsDetail = QAction('Details', self.SentimentTreeWidget)
            SentimentsDetail.triggered.connect(lambda: self.SentimentsChildDetail(SentimentsItemName))
            SentimentsRightClickMenu.addAction(SentimentsDetail)

            SentimentsRightClickMenu.popup(SentimentsWidgetPos)

    # Sentiment Show Component
    def SentimentsShowComponent(self, SentimentsItemName):
        SentimentTextEmptyFlagList = []

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == SentimentsItemName.parent().text(0):
                for sentiments in DS.SentimentList:
                    if len(sentiments.SentimentTextList) == 0:
                        SentimentTextEmptyFlagList.append(True)
                    else:
                        SentimentTextEmptyFlagList.append(False)
                break

        if all([v for v in SentimentTextEmptyFlagList]):
            SentimenShowComponentErrorBox = QMessageBox.critical(self, "No Sentiment Error",
                                                                "No Sentiment Component to Show of Data source: " + DS.DataSourceName,
                                                                QMessageBox.Ok)
        else:
            SentimentsShowComponentTabFlag = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == SentimentsItemName.parent().text(0) and tabs.TabName == 'Sentiments Show Topic Component':
                    SentimentsShowComponentTabFlag = True
                    break


            for DS in myFile.DataSourceList:
                if DS.DataSourceName == SentimentsItemName.parent().text(0):
                    for sentiments in DS.SentimentList:
                        if sentiments.SentimentType == SentimentsItemName.text(0):
                            Sentiments_List = sentiments.SentimentTextList
                            break

            # Creating New Tab for Sentiment Show Component
            SentimentsShowComponentTab = QWidget()

            # LayoutWidget For within Stem Word Tab
            SentimentsShowComponentTabVerticalLayoutWidget = QWidget(SentimentsShowComponentTab)
            SentimentsShowComponentTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

            # Box Layout for Stem Word Tab
            SentimentsShowComponentTabVerticalLayout = QHBoxLayout(SentimentsShowComponentTabVerticalLayoutWidget)
            SentimentsShowComponentTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Sentiments ComboBox

            SentimentsComboBox = QComboBox(SentimentsShowComponentTabVerticalLayoutWidget)
            SentimentsComboBox.setGeometry(SentimentsShowComponentTabVerticalLayoutWidget.width() * 0.8,
                                           SentimentsShowComponentTabVerticalLayoutWidget.height() * 0.4,
                                           SentimentsShowComponentTabVerticalLayoutWidget.width() / 10,
                                           SentimentsShowComponentTabVerticalLayoutWidget.height() / 5)
            SentimentsComboBox.addItem(SentimentsItemName.text(0))
            SentimentsComboBox.setCurrentText(SentimentsItemName.text(0))

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == SentimentsItemName.parent().text(0):
                    for sentiments in DS.SentimentList:
                        if not sentiments.SentimentType == SentimentsItemName.text(0):
                            SentimentsComboBox.addItem(sentiments.SentimentType)

            self.LineEditSizeAdjustment(SentimentsComboBox)

            # 2nd LayoutWidget For within Stem Word Tab
            SentimentsShowComponentTabVerticalLayoutWidget2 = QWidget(SentimentsShowComponentTab)
            SentimentsShowComponentTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                                  self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Stem Word Tab
            SentimentsShowComponentTabVerticalLayout2 = QVBoxLayout(SentimentsShowComponentTabVerticalLayoutWidget2)

            SentimentsShowComponentTable = QTableWidget(SentimentsShowComponentTabVerticalLayoutWidget2)
            SentimentsShowComponentTable.setColumnCount(5)
            SentimentsShowComponentTable.setGeometry(0, 0, SentimentsShowComponentTabVerticalLayoutWidget2.width(),
                                                           SentimentsShowComponentTabVerticalLayoutWidget2.height())
            SentimentsShowComponentTable.setUpdatesEnabled(True)
            SentimentsShowComponentTable.setDragEnabled(True)
            SentimentsShowComponentTable.setMouseTracking(True)

            SentimentsShowComponentTable.setSizePolicy(self.sizePolicy)
            SentimentsShowComponentTable.setWindowFlags(
                SentimentsShowComponentTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
            SentimentsShowComponentTable.setHorizontalHeaderLabels(
                ["Sentiment", "Word Count", "Character Count", "Weighted Average", "Action"])
            SentimentsShowComponentTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

            for i in range(SentimentsShowComponentTable.columnCount()):
                SentimentsShowComponentTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
                SentimentsShowComponentTable.horizontalHeaderItem(i).setFont(
                    QFont(SentimentsShowComponentTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))


            if len(Sentiments_List) != 0:
                for row in Sentiments_List:
                    SentimentsShowComponentTable.insertRow(Sentiments_List.index(row))
                    for item in row:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        SentimentsShowComponentTable.setItem(Sentiments_List.index(row), row.index(item), intItem)
                        SentimentsShowComponentTable.item(Sentiments_List.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        SentimentsShowComponentTable.item(Sentiments_List.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                        deleteButton = QPushButton("Remove")
                        deleteButton.clicked.connect(lambda: self.deleteSentimentsComponentRow(SentimentsItemName, SentimentsShowComponentTable, None))
                        self.LabelSizeAdjustment(deleteButton)
                        SentimentsShowComponentTable.setCellWidget(Sentiments_List.index(row), 4, deleteButton)

                SentimentsShowComponentTable.resizeColumnsToContents()
                SentimentsShowComponentTable.resizeRowsToContents()

                SentimentsShowComponentTable.setSortingEnabled(True)
                SentimentsShowComponentTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                row_width = 0

                for i in range(SentimentsShowComponentTable.columnCount()):
                    SentimentsShowComponentTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            SentimentsComboBox.currentTextChanged.connect(lambda: self.ToggleSentimentsComponent(SentimentsShowComponentTable, SentimentsItemName))

            if SentimentsShowComponentTabFlag:
                # updating tab
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                self.tabWidget.addTab(SentimentsShowComponentTab, tabs.TabName)
                self.tabWidget.setCurrentWidget(SentimentsShowComponentTab)
                tabs.tabWidget = SentimentsShowComponentTab

            else:
                # Adding Word Cloud Tab to QTabWidget
                myFile.TabList.append(
                    Tab("Sentiments Show Topic Component", SentimentsShowComponentTab, SentimentsItemName.parent().text(0)))

                self.tabWidget.addTab(SentimentsShowComponentTab, "Sentiments Show Topic Component")
                self.tabWidget.setCurrentWidget(SentimentsShowComponentTab)

    #Toggle Sentiments Components
    def ToggleSentimentsComponent(self, Table, SentimentsItemName):
        ComboBox = self.sender()

        while Table.rowCount() > 0:
            Table.removeRow(0)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == SentimentsItemName.parent().text(0):
                for sentiments in DS.SentimentList:
                    if sentiments.SentimentType == ComboBox.currentText():
                        Sentiments_List = sentiments.SentimentTextList
                        break

        for row in Sentiments_List:
            Table.insertRow(Sentiments_List.index(row))
            for item in row:
                intItem = QTableWidgetItem()
                intItem.setData(Qt.EditRole, QVariant(item))
                Table.setItem(Sentiments_List.index(row), row.index(item), intItem)
                Table.item(Sentiments_List.index(row), row.index(item)).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                Table.item(Sentiments_List.index(row), row.index(item)).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                deleteButton = QPushButton("Remove")
                deleteButton.clicked.connect(lambda: self.deleteSentimentsComponentRow(SentimentsItemName, Table, ComboBox.currentText()))
                self.LabelSizeAdjustment(deleteButton)
                Table.setCellWidget(Sentiments_List.index(row), 4, deleteButton)

        Table.resizeColumnsToContents()
        Table.resizeRowsToContents()

        Table.setSortingEnabled(True)
        Table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        row_width = 0

        for i in range(Table.columnCount()):
            Table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

    # Sentiments Remove Component Row
    def deleteSentimentsComponentRow(self, SentimentsItemName, Table, ComboBoxText):
        button = self.sender()
        if button:
            row = Table.indexAt(button.pos()).row()
            temp = Table.item(row, 0)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == SentimentsItemName.parent().text(0):
                    for sentiments in DS.SentimentList:
                        if ComboBoxText is None:
                            if sentiments.SentimentType == SentimentsItemName.text(0):
                                for SentimentsText in sentiments.SentimentTextList:
                                    if temp.text() == SentimentsText[0] and row == sentiments.SentimentTextList.index(SentimentsText):
                                        sentiments.SentimentTextList.remove(SentimentsText)
                                        break
                        else:
                            if sentiments.SentimentType == ComboBoxText:
                                for SentimentsText in sentiments.SentimentTextList:
                                    if temp.text() == SentimentsText[0] and row == sentiments.SentimentTextList.index(SentimentsText):
                                        sentiments.SentimentTextList.remove(SentimentsText)
                                        break

            Table.removeRow(row)

    # Sentiments Remove Dialog
    def SentimentsRemoveDialog(self, SentimentsItemName):
        SentimentsRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this Data Source's Sentiments?",
                                                     QMessageBox.Yes | QMessageBox.No)

        if SentimentsRemoveChoice == QMessageBox.Yes:
            self.SentimentsRemove(SentimentsItemName)
        else:
            pass

    # Sentiments Remove
    def SentimentsRemove(self, SentimentsItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == SentimentsItemName.text(0):
                self.SentimentTreeWidget.invisibleRootItem().removeChild(SentimentsItemName)

                for sentiments in DS.SentimentList:
                    sentiments.SentimentTextList.clear()
                break

    # Sentiment Child Detail
    def SentimentsChildDetail(self, SentimentsItemName):
        SentimentsChildDetailDialogBox = QDialog()
        SentimentsChildDetailDialogBox.setModal(True)
        SentimentsChildDetailDialogBox.setWindowTitle("Details")
        SentimentsChildDetailDialogBox.setParent(self)
        SentimentsChildDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        SentimentsChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                              self.height / 5)
        SentimentsChildDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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

        # No of Sentiments Component Label
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

        # No of Sentiments LineEdit
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
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == SentimentsItemName.text(0):
                self.SentimentTreeWidget.invisibleRootItem().removeChild(SentimentsItemName)

                for sentiments in DS.SentimentList:
                    sentiments.SentimentTextList.clear()

                break

    # ****************************************************************************
    # *********************** Visualization Context Menu *************************
    # ****************************************************************************

    # Get Which Visualization Widget Item and its Position
    def FindVisualizationTreeWidgetContextMenu(self, VisualizationMouseRightClickEvent):
        if VisualizationMouseRightClickEvent.reason == VisualizationMouseRightClickEvent.Mouse:
            VisualizationMouseRightClickPos = VisualizationMouseRightClickEvent.globalPos()
            VisualizationMouseRightClickItem = self.VisualizationTreeWidget.itemAt(VisualizationMouseRightClickEvent.pos())
        else:
            VisualizationMouseRightClickPos = None
            Visualizationselection = self.VisualizationTreeWidget.selectedItems()

            if Visualizationselection:
                VisualizationMouseRightClickItem = Visualizationselection[0]
            else:
                VisualizationMouseRightClickItem = self.VisualizationTreeWidget.currentItem()
                if VisualizationMouseRightClickItem is None:
                    VisualizationMouseRightClickItem = self.VisualizationTreeWidget.invisibleRootItem().child(0)
            if VisualizationMouseRightClickItem is not None:
                VisualizationParent = VisualizationMouseRightClickItem.parent()
                while VisualizationParent is not None:
                    VisualizationParent.setExpanded(True)
                    VisualizationParent = VisualizationParent.parent()

                Visualizationitemrect = self.VisualizationTreeWidget.visualItemRect(VisualizationMouseRightClickItem)
                Visualizationportrect = self.VisualizationTreeWidget.viewport().rect()

                if not Visualizationportrect.contains(Visualizationitemrect.topLeft()):
                    self.VisualizationTreeWidget.scrollToItem(VisualizationMouseRightClickItem, QTreeWidget.PositionAtCenter)
                    Visualizationitemrect = self.VisualizationTreeWidget.visualItemRect(VisualizationMouseRightClickItem)

                Visualizationitemrect.setLeft(Visualizationportrect.left())
                Visualizationitemrect.setWidth(Visualizationportrect.width())
                VisualizationMouseRightClickPos = self.VisualizationTreeWidget.mapToGlobal(Visualizationitemrect.center())

        if VisualizationMouseRightClickPos is not None:
            self.VisualizationTreeWidgetContextMenu(VisualizationMouseRightClickItem, VisualizationMouseRightClickPos)

    # Setting ContextMenu on Clicked Sentiments
    def VisualizationTreeWidgetContextMenu(self, VisualizationItemName, VisualizationWidgetPos):
        # Parent Sentiments
        if VisualizationItemName.parent() == None:
            if VisualizationItemName.text(0) == "Document Clustering":
                VisualizationRightClickMenu = QMenu(self.VisualizationTreeWidget)

                # Show Tab
                VisualizationShow = QAction('Show', self.VisualizationTreeWidget)
                VisualizationShow.triggered.connect(lambda: self.VisualizationDoubleClickHandler(VisualizationItemName))
                VisualizationRightClickMenu.addAction(VisualizationShow)

                # Visualization Remove
                VisualizationRemove = QAction('Remove', self.VisualizationTreeWidget)
                VisualizationRemove.triggered.connect(
                    lambda: self.VisualizationParentRemove(VisualizationItemName))
                VisualizationRightClickMenu.addAction(VisualizationRemove)

                VisualizationRightClickMenu.popup(VisualizationWidgetPos)

            else:
                VisualizationRightClickMenu = QMenu(self.VisualizationTreeWidget)

                # Visualization Expand
                VisualizationExpand = QAction('Expand', self.VisualizationTreeWidget)
                VisualizationExpand.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(VisualizationItemName))
                if (VisualizationItemName.childCount() == 0 or VisualizationItemName.isExpanded() == True):
                    VisualizationExpand.setDisabled(True)
                else:
                    VisualizationExpand.setDisabled(False)
                VisualizationRightClickMenu.addAction(VisualizationExpand)

                # Visualization Collapse
                VisualizationCollapse = QAction('Collapse', self.VisualizationTreeWidget)
                VisualizationCollapse.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(VisualizationItemName))
                if (VisualizationItemName.childCount() == 0 or VisualizationItemName.isExpanded() == False):
                    VisualizationCollapse.setDisabled(True)
                else:
                    VisualizationCollapse.setDisabled(False)
                VisualizationRightClickMenu.addAction(VisualizationCollapse)

                # Visualization Remove
                VisualizationRemove = QAction('Remove', self.VisualizationTreeWidget)
                VisualizationRemove.triggered.connect(lambda: self.VisualizationParentRemove(VisualizationItemName))
                VisualizationRightClickMenu.addAction(VisualizationRemove)

                # Visualization Detail
                VisualizationDetail = QAction('Detail', self.VisualizationTreeWidget)
                VisualizationDetail.triggered.connect(lambda: self.VisualizationDetail(VisualizationItemName))
                VisualizationRightClickMenu.addAction(VisualizationDetail)

                VisualizationRightClickMenu.popup(VisualizationWidgetPos)

        # Child Sentiments
        else:
            VisualizationRightClickMenu = QMenu(self.VisualizationTreeWidget)

            # Show Tab
            VisualizationShow = QAction('Show', self.VisualizationTreeWidget)
            VisualizationShow.triggered.connect(lambda: self.VisualizationDoubleClickHandler(VisualizationItemName))
            VisualizationRightClickMenu.addAction(VisualizationShow)

            # Visualization Remove
            VisualizationRemove = QAction('Remove', self.VisualizationTreeWidget)
            VisualizationRemove.triggered.connect(lambda: self.VisualizationChildRemoveDialog(VisualizationItemName))
            VisualizationRightClickMenu.addAction(VisualizationRemove)

            VisualizationRightClickMenu.popup(VisualizationWidgetPos)

    # Visualization Parent Remove
    def VisualizationParentRemove(self, VisualizationItemName):
        VisualizationRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's all Visualization?",
                                                        QMessageBox.Yes | QMessageBox.No)

        if VisualizationRemoveChoice == QMessageBox.Yes:
            if VisualizationItemName.text(0) == 'Document Clustering':
                for tabs in myFile.TabList:
                    if tabs.TabName == 'Document Clustering':
                        myFile.TabList.remove(tabs)
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        tabs.__del__()

                self.VisualizationTreeWidget.invisibleRootItem().removeChild(VisualizationItemName)
            else:
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == VisualizationItemName.text(0):
                        for tabs in myFile.TabList:
                            if tabs.DataSourceName == DS.DataSourceName:
                                myFile.TabList.remove(tabs)
                                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                                tabs.__del__()

                        self.VisualizationTreeWidget.invisibleRootItem().removeChild(VisualizationItemName)
                        DS.VisualizationList.clear()
                        break
        else:
            pass

    # Visualization Parent Detail
    def VisualizationDetail(self, VisualizationItemName):
        VisualizationDetailDialogBox = QDialog()
        VisualizationDetailDialogBox.setModal(True)
        VisualizationDetailDialogBox.setWindowTitle("Details")
        VisualizationDetailDialogBox.setParent(self)
        VisualizationDetailDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        VisualizationDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width / 3,
                                               self.height / 10)
        VisualizationDetailDialogBox.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == VisualizationItemName.text(0):
                break

        # ************************************** Labels *************************************

        # Data Source Name Label
        DataSourceNameLabel = QLabel(VisualizationDetailDialogBox)
        DataSourceNameLabel.setText("Name:")
        DataSourceNameLabel.setGeometry(VisualizationDetailDialogBox.width() * 0.1,
                                        VisualizationDetailDialogBox.height() * 0.2,
                                        VisualizationDetailDialogBox.width() / 4,
                                        VisualizationDetailDialogBox.height() / 5)
        DataSourceNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNameLabel)

        # Data Source Path Label
        DataSourceNoofVisualizationLabel = QLabel(VisualizationDetailDialogBox)
        DataSourceNoofVisualizationLabel.setText("No of Visualizations:")
        DataSourceNoofVisualizationLabel.setGeometry(VisualizationDetailDialogBox.width() * 0.1,
                                                     VisualizationDetailDialogBox.height() * 0.6,
                                                     VisualizationDetailDialogBox.width() / 4,
                                                     VisualizationDetailDialogBox.height() / 5)
        DataSourceNoofVisualizationLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(DataSourceNoofVisualizationLabel)

        # ************************************** LineEdit *************************************

        # Data Source Name LineEdit
        DataSourceNameLineEdit = QLineEdit(VisualizationDetailDialogBox)
        DataSourceNameLineEdit.setText(VisualizationItemName.text(0))
        DataSourceNameLineEdit.setReadOnly(True)
        DataSourceNameLineEdit.setGeometry(VisualizationDetailDialogBox.width() * 0.35,
                                           VisualizationDetailDialogBox.height() * 0.2,
                                           VisualizationDetailDialogBox.width() * 0.6,
                                           VisualizationDetailDialogBox.height() / 5)
        DataSourceNameLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNameLineEdit)

        # Data Source Path LineEdit
        DataSourceNoofVisualizationLineEdit = QLineEdit(VisualizationDetailDialogBox)
        DataSourceNoofVisualizationLineEdit.setText(str(len(DS.VisualizationList)))
        DataSourceNoofVisualizationLineEdit.setReadOnly(True)
        DataSourceNoofVisualizationLineEdit.setGeometry(VisualizationDetailDialogBox.width() * 0.35,
                                                        VisualizationDetailDialogBox.height() * 0.6,
                                                        VisualizationDetailDialogBox.width() * 0.6,
                                                        VisualizationDetailDialogBox.height() / 5)
        DataSourceNoofVisualizationLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LineEditSizeAdjustment(DataSourceNoofVisualizationLineEdit)

        VisualizationDetailDialogBox.exec_()

    # Visualization Child Remove
    def VisualizationChildRemoveDialog(self, VisualizationItemName):
        VisualizationRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's Visualization?",
                                                        QMessageBox.Yes | QMessageBox.No)

        if VisualizationRemoveChoice == QMessageBox.Yes:
            self.VisualizationChildRemove(VisualizationItemName)
        else:
            pass

    # Visualization Child Remove
    def VisualizationChildRemove(self, VisualizationItemName):
        for tabs in myFile.TabList:
            if tabs.DataSourceName == VisualizationItemName.parent().text(0):
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == tabs.DataSourceName:
                        for visual in DS.VisualizationList:
                            if visual[0] == VisualizationItemName and visual[1] == tabs.tabWidget:
                                myFile.TabList.remove(tabs)
                                DS.VisualizationList.remove(visual)
                                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                                tabs.__del__()
                                break

        if VisualizationItemName.parent().childCount() == 1:
            tempParent = VisualizationItemName.parent()
            tempParent.removeChild(VisualizationItemName)
            self.VisualizationTreeWidget.invisibleRootItem().removeChild(tempParent)
        else:
            VisualizationItemName.parent().removeChild(VisualizationItemName)

    # Preview Visual/Tab on double click
    def VisualizationDoubleClickHandler(self, VisualizationItemName):
        if VisualizationItemName.text(0) == 'Document Clustering':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Document Clustering':
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                    break
        else:
            for tabs in myFile.TabList:
                if tabs.DataSourceName == VisualizationItemName.parent().text(0):
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == tabs.DataSourceName:
                            for visuals in DS.VisualizationList:
                                if visuals[0] == VisualizationItemName and visuals[1] == tabs.tabWidget:
                                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                                    break

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
        myDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        myDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        myDialog.show()

    #Open File
    def OpenFileWindow(self):
        self.dummyWindow = OpenWindow("Open File", "TextWiz File *.tax", 0)

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
        file = open('LICENSE', 'r')
        lic = file.read()
        QMessageBox().about(self, "About TextWiz", lic)

    # ****************************************************************************
    # *************************** Import Features ********************************
    # ****************************************************************************

    # Import DataSource Window
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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                        self.DataSourceDocumentClusteringUpdate()
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0 and not dummyDataSource.DataSourceLoadError:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                            self.DataSourceDocumentClusteringUpdate()
                        else:
                            dummyDataSource.__del__()
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)
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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                        self.DataSourceDocumentClusteringUpdate()

                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                        myFile.setDataSources(dummyDataSource)
                        newNode = QTreeWidgetItem(self.rtfTreeWidget)
                        newNode.setText(0, ntpath.basename(path[0]))
                        self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")

                        if self.rtfTreeWidget.isHidden():
                            self.rtfTreeWidget.setHidden(False)

                        newNode.setToolTip(0, newNode.text(0))
                        dummyDataSource.setNode(newNode)

                        self.DataSourceSimilarityUpdate()
                        self.DataSourceDocumentClusteringUpdate()
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                        self.DataSourceDocumentClusteringUpdate()
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

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
                    if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                        self.DataSourceDocumentClusteringUpdate()
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
                        dummyDataSource.__del__()
                else:
                    dummyDataSource.__del__()
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

                    # Import Tweet Window

    # Import Tweet Window
    def ImportTweetWindow(self):
        TweetDialog = QDialog()
        TweetDialog.setWindowTitle("Import From Twitter")
        TweetDialog.setGeometry(self.width * 0.375, self.height * 0.375, self.width / 4, self.height / 4)
        TweetDialog.setParent(self)
        TweetDialog.setAttribute(Qt.WA_DeleteOnClose)
        TweetDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        TweetDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
                    DataSourceImportNameErrorBox = QMessageBox.information(self, "Import Error",
                                                                        "No Tweet Found with Hashtag : " + Hashtag,
                                                                        QMessageBox.Ok)
            else:
                dummyDataSource.__del__()
                DataSourceImportNameErrorBox = QMessageBox.information(self, "Import Error",
                                                                       "TextWiz is unable to retrive any tweet",
                                                                       QMessageBox.Ok)
        else:
            dummyDataSource.__del__()
            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                   "A Tweet with Similar Hashtag Exist!",
                                                                   QMessageBox.Ok)

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
        URLDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        URLDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
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
                self.DataSourceDocumentClusteringUpdate()
            else:
                if not dummyDataSource.DataSourceLoadError and len(dummyDataSource.DataSourcetext) == 0:
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                        QMessageBox.Ok)

                dummyDataSource.__del__()
        else:
            dummyDataSource.__del__()
            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                   "A Web Source with Similar URL Exist!",
                                                                   QMessageBox.Ok)

    # Import From Youtube Window
    def ImportYoutubeWindow(self):
        YoutubeDialog = QDialog()
        YoutubeDialog.setWindowTitle("Import Youtube Comments")
        YoutubeDialog.setGeometry(self.width * 0.3, self.height * 0.4, self.width * 2 / 5, self.height * 0.20)
        YoutubeDialog.setParent(self)
        YoutubeDialog.setAttribute(Qt.WA_DeleteOnClose)
        YoutubeDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        YoutubeDialog.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

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
            if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.YoutubeData) == 0:
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
                self.DataSourceDocumentClusteringUpdate()
            else:
                if len(dummyDataSource.YoutubeData) == 0:
                    if VideoURLCheck:
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "No Youtube comment Retreive From the URL: " + URL,
                                                                            QMessageBox.Ok)
                    else:
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "No comment Retreive of Key Word: " + KeyWord,
                                                                            QMessageBox.Ok)
                dummyDataSource.__del__()
        else:
            dummyDataSource.__del__()

            if VideoURLCheck:
                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                    "A Youtube Source with Similar URL Exist!",
                                                                    QMessageBox.Ok)
            else:
                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                    "A Youtube Source with Similar KeyWord Exist!",
                                                                    QMessageBox.Ok)

if __name__ == "__main__":
    WindowTitleLogo = "Images/TextWizLogo.png"
    isSaveAs = True
    myFile = File()
    myFile.setCreatedDate(datetime.datetime.now())
    myFile.setCreatedDate(datetime.datetime.now())
    myFile.setCreatedDate(getpass.getuser())

    App = QApplication(sys.argv)

    # TextWizSplash = QSplashScreen()
    # TextWizSplash.resize(200, 100)
    # TextWizSplashPixmap = QPixmap("Images/TextWizSplash.png")
    # TextWizSplash.setPixmap(TextWizSplashPixmap)
    #
    # SplahScreenProgressBar = QProgressBar(TextWizSplash)
    # SplahScreenProgressBar.setGeometry(TextWizSplash.width() / 10, TextWizSplash.height() * 0.9,
    #                         TextWizSplash.width() * 0.8, TextWizSplash.height() * 0.035)
    # SplahScreenProgressBar.setTextVisible(False)
    # SplahScreenProgressBar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}")
    #
    # TextWizSplash.show()
    #
    # for i in range(0, 100):
    #     SplahScreenProgressBar.setValue(i)
    #     t = time.time()
    #     while time.time() < t + 0.05:
    #         App.processEvents()
    #
    # TextWizSplash.close()

    TextWizMainwindow = Window()
    TextWizMainwindow.show()
    sys.exit(App.exec())