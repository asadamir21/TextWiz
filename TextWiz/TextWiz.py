import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5 import QtPrintSupport, QtQuickWidgets, QtPositioning
from PyQt5.QtWebEngineWidgets import *
from PIL import Image
from TaskThread import *
from OpenWindow import *
from MarkerModel import *

import humanfriendly, platform
import glob, sys, os, getpass, ntpath, math, csv, datetime, graphviz, threading, queue

from pyparsing import Char

WindowPlatform = False
LinuxPlatform = False
MacPlatform = False

if platform.system() == "Windows":
    WindowPlatform = True
elif platform.system() == "Linux":
    LinuxPlatform = True
elif platform.system() == "Darwin":
    MacPlatform = True

if WindowPlatform:
    from PyQt5 import QAxContainer

class PicButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "TextWiz"

        if WindowPlatform:
            from win32api import GetMonitorInfo, MonitorFromPoint
            Monitor_Resolution_Info = GetMonitorInfo(MonitorFromPoint((0, 0)))
            self.width = Monitor_Resolution_Info.get("Work")[2]
            self.height = Monitor_Resolution_Info.get("Work")[3]

        elif LinuxPlatform:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('Gtk', '3.0')

            from gi.repository import Gdk, Gtk, GdkX11

            display = Gdk.Display().get_default()
            for i in range(display.get_n_monitors()):
                monitor = display.get_monitor(i)
                w_area = monitor.get_workarea()

                self.width = w_area.width
                self.height = w_area.height

        self.settings = QSettings('TextWiz', 'TextWiz')

        # Retrieving Theme from settings
        self.theme = self.settings.value('theme', '')

        # setting theme from setting
        if self.theme == '' or self.theme == 'Light':
           self.setStyleSheet(open('Styles/Light.css', 'r').read())
        elif self.theme == 'Dark':
           self.setStyleSheet(open('Styles/Dark.css', 'r').read())
        elif self.theme == 'DarkOrange':
           self.setStyleSheet(open('Styles/DarkOrange.css', 'r').read())


        self.languages = open('Languages.txt', 'r').read().split("\n")

        self.stopwordspath = self.settings.value('stopwords', '')

        if not self.stopwordspath == '':
            try:
                self.stopwords = open(self.stopwordspath, 'r').read().split("\n")
            except IOError:
                pass

        for fileRow in self.languages:
            self.languages[self.languages.index(fileRow)] = fileRow.split(',')

        coordinatecsvreader = csv.reader(open('Coordinates.csv'))

        self.Coordinates = []

        for row in coordinatecsvreader:
            self.Coordinates.append([row[0], row[1], row[2]])

        self.initWindows()

    # Initiate Windows
    def initWindows(self):
        self.setWindowIcon(QIcon(WindowTitleLogo))
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)
        self.setMinimumSize(self.width/2, self.height/2)
        self.showMaximized()

        # *****************************  ToolBar ******************************************

        self.toolbar = self.addToolBar("Show Toolbar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon | Qt.AlignLeading)  # <= Toolbuttonstyle
        self.toolbar.setMovable(False)

        WordAct = QAction(QIcon('Images/Word.png'), 'Word', self)
        WordAct.triggered.connect(lambda: self.ImportFileWindow("Word"))
        self.toolbar.addAction(WordAct)

        PDFAct = QAction(QIcon('Images/PDF.png'), 'PDF', self)
        PDFAct.triggered.connect(lambda: self.ImportFileWindow("PDF"))
        self.toolbar.addAction(PDFAct)

        NotepadAct = QAction(QIcon('Images/Notepad.png'), 'txt', self)
        NotepadAct.triggered.connect(lambda: self.ImportFileWindow("Txt"))
        self.toolbar.addAction(NotepadAct)

        RTFAct = QAction(QIcon('Images/rtf.png'), 'RTF', self)
        RTFAct.triggered.connect(lambda: self.ImportFileWindow("RTF"))
        self.toolbar.addAction(RTFAct)

        SoundAct = QAction(QIcon('Images/Sound.png'), 'Audio', self)
        SoundAct.triggered.connect(lambda: self.ImportFileWindow("Sound"))
        self.toolbar.addAction(SoundAct)

        ImageAct = QAction(QIcon('Images/ImageDataSource.png'), 'Image', self)
        ImageAct.triggered.connect(lambda: self.ImportFileWindow("Image"))
        self.toolbar.addAction(ImageAct)

        CSVAct = QAction(QIcon('Images/CSV.png'), 'csv', self)
        CSVAct.triggered.connect(lambda: self.ImportCSVWindowDialog())
        self.toolbar.addAction(CSVAct)

        TwitterAct = QAction(QIcon('Images/Twitter.png'), 'Twitter', self)
        TwitterAct.triggered.connect(lambda: self.ImportTweetWindow())
        self.toolbar.addAction(TwitterAct)

        WebAct = QAction(QIcon('Images/Web.png'), 'URL', self)
        WebAct.triggered.connect(lambda: self.ImportURLWindow())
        self.toolbar.addAction(WebAct)

        YoutubeAct = QAction(QIcon('Images/Youtube.png'), 'Youtube', self)
        YoutubeAct.triggered.connect(lambda: self.ImportYoutubeWindow())
        self.toolbar.addAction(YoutubeAct)

        self.toolbar.addSeparator()
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

        # ***********************************************************************************
        # *****************************  Menu Item ******************************************
        # ***********************************************************************************

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        viewMenu = mainMenu.addMenu('View')
        importMenu = mainMenu.addMenu('Import')
        ToolMenu = mainMenu.addMenu('Tools')
        VisualizationMenu = mainMenu.addMenu('Visualization')
        helpMenu = mainMenu.addMenu('Help')

        # *****************************  FileMenuItem ***************************************

        # New File Button
        newFileButton = QAction('New File', self)
        newFileButton.setShortcut('Ctrl+N')
        newFileButton.setStatusTip('New File')
        newFileButton.triggered.connect(self.NewFileWindow)
        fileMenu.addAction(newFileButton)

        # Open File Button
        OpenFileButton = QAction('Open File', self)
        OpenFileButton.setShortcut('Ctrl+O')
        OpenFileButton.setStatusTip('Open File')
        OpenFileButton.triggered.connect(self.OpenFileWindow)
        fileMenu.addAction(OpenFileButton)

        # Save File Button
        SaveButton = QAction(QIcon("Images/Save.png"), 'Save', self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('File Saved')
        SaveButton.triggered.connect(self.SaveWindow)
        fileMenu.addAction(SaveButton)

        # SaveAS File Button
        SaveASButton = QAction(QIcon("Images/Save.png"), 'Save As', self)
        SaveASButton.setStatusTip('File Saved')
        SaveASButton.triggered.connect(self.SaveASWindow)
        fileMenu.addAction(SaveASButton)

        # print Button
        printButton = QAction(QIcon("Images/Printer.png"), 'Print', self)
        printButton.setShortcut('Ctrl+P')
        printButton.setStatusTip('Print')
        printButton.triggered.connect(self.printWindow)
        fileMenu.addAction(printButton)

        # Add Stopword File
        self.AddStopWordFileButton = QAction('Add Stopword File', self)
        self.AddStopWordFileButton.setStatusTip('Add Stopword File')
        self.AddStopWordFileButton.triggered.connect(self.AddStopWordFile)
        fileMenu.addAction(self.AddStopWordFileButton)

        # Remove Stopword File
        self.RemoveStopWordFileButton = QAction('Remove Stopword File', self)
        self.RemoveStopWordFileButton.setStatusTip('Remove Stopword File')
        self.RemoveStopWordFileButton.triggered.connect(self.RemoveStopWordFile)

        if self.stopwordspath == '':
            self.RemoveStopWordFileButton.setDisabled(True)

        fileMenu.addAction(self.RemoveStopWordFileButton)

        printButton = QAction(QIcon("Images/Printer.png"), 'Print', self)
        printButton.setShortcut('Ctrl+P')
        printButton.setStatusTip('Print')
        printButton.triggered.connect(self.printWindow)
        fileMenu.addAction(printButton)

        # exit Button
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
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

        ChangeThemeButton = QAction('Change Theme', self)
        ChangeThemeButton.triggered.connect(lambda: self.ChangeThemeDialog())
        viewMenu.addAction(ChangeThemeButton)

        # *****************************  ImportMenuItem *************************************

        WordFileButton = QAction(QIcon("Images/Word.png"),'Word File', self)
        WordFileButton.setStatusTip('Word File')
        WordFileButton.triggered.connect(lambda: self.ImportFileWindow("Word"))
        importMenu.addAction(WordFileButton)

        PDFFileButton = QAction(QIcon("Images/PDF.png"), 'PDF File', self)
        PDFFileButton.setStatusTip('PDF File')
        PDFFileButton.triggered.connect(lambda: self.ImportFileWindow("PDF"))
        importMenu.addAction(PDFFileButton)

        TXTFileButton = QAction(QIcon("Images/Notepad.png"), 'Notepad File', self)
        TXTFileButton.setStatusTip('Notepad File')
        TXTFileButton.triggered.connect(lambda: self.ImportFileWindow("Txt"))
        importMenu.addAction(TXTFileButton)

        RTFFileButton = QAction(QIcon("Images/rtf.png"), 'RTF File', self)
        RTFFileButton.setStatusTip('RTF File')
        RTFFileButton.triggered.connect(lambda: self.ImportFileWindow("RTF"))
        importMenu.addAction(RTFFileButton)

        SoundFileButton = QAction(QIcon("Images/Sound.png"), 'Audio File', self)
        SoundFileButton.setStatusTip('Audio File')
        SoundFileButton.triggered.connect(lambda: self.ImportFileWindow("Sound"))
        importMenu.addAction(SoundFileButton)

        ImageFileButton = QAction(QIcon("Images\ImageDataSource.png"), 'Image File', self)
        ImageFileButton.setStatusTip('Image File')
        ImageFileButton.triggered.connect(lambda: self.ImportFileWindow("Image"))
        importMenu.addAction(ImageFileButton)

        CSVFileButton = QAction(QIcon("Images\CSV.png"), 'CSV File', self)
        CSVFileButton.setStatusTip('CSV File')
        CSVFileButton.triggered.connect(lambda: self.ImportCSVWindowDialog())
        importMenu.addAction(CSVFileButton)

        TwitterButton = QAction(QIcon("Images\Twitter.png"), 'Twitter Tweets', self)
        TwitterButton.setStatusTip('Tweets')
        TwitterButton.triggered.connect(lambda checked: self.ImportTweetWindow())
        importMenu.addAction(TwitterButton)

        URLButton = QAction(QIcon("Images\Web.png"), 'Web', self)
        URLButton.setStatusTip('Get Data From URL')
        URLButton.triggered.connect(lambda checked: self.ImportURLWindow())
        importMenu.addAction(URLButton)

        YoutubeButton = QAction(QIcon("Images\Youtube.png"), 'Youtube Comments', self)
        YoutubeButton.setStatusTip('Youtube Comments')
        YoutubeButton.triggered.connect(lambda checked: self.ImportYoutubeWindow())
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

        # Create Word Cloud Tool
        CreateWordCloudTool = QAction('Create Word Cloud', self)
        CreateWordCloudTool.setStatusTip('Create Word Cloud')
        CreateWordCloudTool.triggered.connect(lambda: self.DataSourceCreateCloud())
        VisualizationMenu.addAction(CreateWordCloudTool)

        # Word Tree Tool
        WordTreeTool = QAction('Word Tree', self)
        WordTreeTool.setStatusTip('Word Tree')
        WordTreeTool.triggered.connect(lambda: self.DataSourceWordTreeDialog())
        VisualizationMenu.addAction(WordTreeTool)

        # Survey Analysis Tool
        SurveyAnalysisTool = QAction('Survey Analysis', self)
        SurveyAnalysisTool.setStatusTip('Survey Analysis')
        SurveyAnalysisTool.triggered.connect(lambda: self.DataSourceSurveyAnalysisDialog())
        VisualizationMenu.addAction(SurveyAnalysisTool)

        # Tweet Analysis
        TweetAnalysisTool = QAction('Tweet Analysis', self)
        TweetAnalysisTool.setStatusTip('Tweet Analysis')
        TweetAnalysisTool.triggered.connect(lambda: self.DataSourceTweetAnalysisDialog())
        VisualizationMenu.addAction(TweetAnalysisTool)

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
        
        LicenseButton = QAction('License', self)
        LicenseButton.setStatusTip('License')
        LicenseButton.triggered.connect(lambda: self.LicenseWindow())
        helpMenu.addAction(LicenseButton)

        AboutButton = QAction('About Us', self)        
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

        self.CSVTreeWidget = QTreeWidgetItem(self.DataSourceTreeWidget)
        self.CSVTreeWidget.setText(0, "CSV" + "(" + str(self.CSVTreeWidget.childCount()) + ")")
        self.CSVTreeWidget.setHidden(True)

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

        # ********************************** Right Tab Widget *******************************

        # Windows Title Bar Size
        if WindowPlatform:
            import win32gui
            rect = win32gui.GetWindowRect(self.winId())
            clientRect = win32gui.GetClientRect(self.winId())
            windowOffset = math.floor(((rect[2] - rect[0]) - clientRect[2]) / 2)
            titleOffset = ((rect[3] - rect[1]) - clientRect[3]) - windowOffset
        elif LinuxPlatform:
            titleOffset = 0
        elif MacPlatform:
            self.setUnifiedTitleAndToolBarOnMac(True)
            titleOffset = 0

        self.verticalLayoutWidget.setGeometry(0, 0,
                                              self.width / 8,
                                              self.height - titleOffset - self.menuBar().height() - self.toolbar.height() - self.statusBar().height())

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setSizePolicy(self.sizePolicy)

        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(self.sizePolicy)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setElideMode(Qt.ElideRight)
        self.tabWidget.tabBar().setExpanding(True)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.tabCloseRequested.connect(self.tabCloseHandler)

        self.horizontalLayoutWidget.setGeometry(self.verticalLayoutWidget.width(),
                                                0,
                                                self.width - self.verticalLayoutWidget.width(),
                                                self.verticalLayoutWidget.height())

        self.horizontalLayout.addWidget(self.tabWidget)
        self.tabBoxHeight = self.tabWidget.tabBar().geometry().height()
        self.setCentralWidget(self.centralwidget)

    # StopWord File Doesnot Exist
    def StopWordFileExistence(self):
        if not self.stopwordspath == '':
            if os.path.exists(self.stopwordspath):
                if os.path.isfile(self.stopwordspath) and self.stopwordspath.endswith('.txt'):
                    pass
                else:
                    QMessageBox.warning(self, 'Stopword File',
                                        'Stopword File is not a valid txt File!',
                                        QMessageBox.Ok)

                    self.RemoveStopWordFileButton.setDisabled(True)
                    self.settings.setValue('stopwords', '')
                    if hasattr(self, 'stopwordspath'):
                        del self.stopwordspath

                    if hasattr(self, 'stopwords'):
                        del self.stopwords
            else:
                QMessageBox.warning(self, 'Stopword File',
                                    'Stopword File Path doesnot exist!',
                                    QMessageBox.Ok)

                self.RemoveStopWordFileButton.setDisabled(True)
                self.settings.setValue('stopwords', '')
                if hasattr(self, 'stopwordspath'):
                    del self.stopwordspath

                if hasattr(self, 'stopwords'):
                    del self.stopwords

    # Add Stopword File
    def AddStopWordFile(self):
        try:
            path = QFileDialog.getOpenFileName(self, 'Open Stopword File', '', 'TXT(*.txt)')

            if all(path):
                self.stopwords = open(path[0], 'r').read().split("\n")

                self.RemoveStopWordFileButton.setDisabled(False)

                self.settings.setValue('stopwords', path[0])
                self.statusBar().showMessage('Stopword File successfully added')
                QMessageBox.information(self, "Stopword File",
                                        "Stopword File successfully added!", QMessageBox.Ok)


        except PermissionError:
            QMessageBox.critical(self, "Saving Error", "Permission Denied!", QMessageBox.Ok)

    # Remove Stopword File
    def RemoveStopWordFile(self):
        self.RemoveStopWordFileButton.setDisabled(True)
        self.settings.setValue('stopwords', '')
        self.statusBar().showMessage('Stopword File successfully removed')
        QMessageBox.information(self, "Stopword File",
                                "Stopword File successfully Removed!", QMessageBox.Ok)

        if hasattr(self, 'stopwordspath'):
            del self.stopwordspath

        if hasattr(self, 'stopwords'):
            del self.stopwords

    # Change Theme Dialog
    def ChangeThemeDialog(self):
        ChangeThemeDialog = QDialog()
        ChangeThemeDialog.setWindowTitle("Change Theme Dialog")
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

        # Change Theme Button Box
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
        for tabs in myFile.TabList:
            if tabs.tabWidget == self.tabWidget.widget(index):
                tabs.setisActive(False)
                break
        self.tabWidget.removeTab(index)
        myFile.requiredSaved = True

    #Find Similarity Between Data Sources
    def DataSourcesSimilarity(self):
        DataSourceSimilarityTabFlag = False
        DataSourceSimilarityTabFlag2 = False
        DataSourceSimilarityTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == len(myFile.DataSourceList) and tabs.TabName == 'Data Sources Similarity' and tabs.tabWidget != None:
                if self.tabWidget.currentWidget() != tabs.tabWidget:
                    self.tabWidget.setCurrentWidget(tabs.tabWidget)
                DataSourceSimilarityTabFlag = True
                break
            elif tabs.TabName == 'Data Sources Similarity' and tabs.tabWidget != None:
                DataSourceSimilarityTabFlag2 = True
                break
            elif tabs.TabName == 'Data Sources Similarity' and tabs.tabWidget == None:
                DataSourceSimilarityTabFlag3 = True

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
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(DataSourcesSimilarityTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)
                    tabs.tabWidget = DataSourcesSimilarityTab
                    tabs.setisActive(True)
                    myFile.requiredSaved = True

                elif DataSourceSimilarityTabFlag3:
                    tabs.tabWidget = DataSourcesSimilarityTab
                    if tabs.isActive:
                        self.tabWidget.addTab(DataSourcesSimilarityTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)
                else:
                    # Adding Data Source Similarity Tab to QTabWidget
                    myFile.TabList.append(Tab("Data Sources Similarity", DataSourcesSimilarityTab, len(myFile.DataSourceList)))

                    # Adding Data Sources Similarity Query
                    ItemsWidget = self.QueryTreeWidget.findItems("Data Sources Similarity", Qt.MatchExactly, 0)

                    if len(ItemsWidget) == 0:
                        DSVisualWidget = QTreeWidgetItem(self.QueryTreeWidget)
                        DSVisualWidget.setText(0, "Data Sources Similarity")
                        DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))

                    self.tabWidget.addTab(DataSourcesSimilarityTab, "Data Sources Similarity")
                    self.tabWidget.setCurrentWidget(DataSourcesSimilarityTab)
                    myFile.requiredSaved = True

            else:
                DataSourceLoadErrorBox = QMessageBox.critical(self, "Data Sources Similarity Error",
                                                              "An Error Occured! Similarity can only be found if Data Sources are more than one",
                                                              QMessageBox.Ok)

        elif tabs.tabWidget != None:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            myFile.requiredSaved = True

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
        DataSourceDocumentClusteringTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == len(myFile.DataSourceList) and tabs.TabName == 'Document Clustering' and tabs.tabWidget != None:
                if self.tabWidget.currentWidget() != tabs.tabWidget:
                    self.tabWidget.setCurrentWidget(tabs.tabWidget)
                DataSourceDocumentClusteringTabFlag = True
                break
            elif tabs.TabName == 'Document Clustering' and tabs.tabWidget != None:
                DataSourceDocumentClusteringTabFlag2 = True
                break
            elif tabs.TabName == 'Document Clustering' and tabs.tabWidget == None:
                DataSourceDocumentClusteringTabFlag3 = True

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
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(DataSourceDocumentClusteringTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)
                    tabs.tabWidget = DataSourceDocumentClusteringTab
                    tabs.setisActive(True)
                    myFile.requiredSaved = True

                elif DataSourceDocumentClusteringTabFlag3:
                    tabs.tabWidget = DataSourceDocumentClusteringTab
                    if tabs.isActive:
                        self.tabWidget.addTab(DataSourceDocumentClusteringTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)

                else:
                    # Adding Document Clustering Tab to QTabWidget
                    myFile.TabList.append(Tab("Document Clustering", DataSourceDocumentClusteringTab, len(myFile.DataSourceList)))

                    # Adding Document Clustering Query
                    ItemsWidget = self.VisualizationTreeWidget.findItems("Document Clustering", Qt.MatchExactly, 0)

                    if len(ItemsWidget) == 0:
                        DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                        DSVisualWidget.setText(0, "Document Clustering")
                        DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))

                    self.tabWidget.addTab(DataSourceDocumentClusteringTab, "Document Clustering")
                    self.tabWidget.setCurrentWidget(DataSourceDocumentClusteringTab)
                    myFile.requiredSaved = True
            else:
                DataSourceDocumnetClusteringErrorBox = QMessageBox.critical(self, "Data Sources Documnet Clustering",
                                                                           "An Error Occured! Clustering can only be done if Data Sources are more than three",
                                                                            QMessageBox.Ok)
        elif tabs.tabWidget != None:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            myFile.requiredSaved = True

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
        #Parent Data Source
        if DataSourceWidgetItemName.parent() == None:
            DataSourceRightClickMenu = QMenu(self.DataSourceTreeWidget)

            DataSourceExpand = QAction('Expand', self.DataSourceTreeWidget)
            DataSourceExpand.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(DataSourceWidgetItemName))

            if(DataSourceWidgetItemName.childCount() == 0 or DataSourceWidgetItemName.isExpanded() == True):
                DataSourceExpand.setDisabled(True)
            else:
                DataSourceExpand.setDisabled(False)

            DataSourceCollapse = QAction('Collapse', self.DataSourceTreeWidget)
            DataSourceCollapse.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(DataSourceWidgetItemName))

            if (DataSourceWidgetItemName.childCount() == 0 or DataSourceWidgetItemName.isExpanded() == False):
                DataSourceCollapse.setDisabled(True)
            else:
                DataSourceCollapse.setDisabled(False)

            DataSourceDetail = QAction('Details', self.DataSourceTreeWidget)
            DataSourceDetail.triggered.connect(lambda: self.DataSourceWidgetItemDetail(DataSourceWidgetItemName))

            DataSourceRightClickMenu.addAction(DataSourceExpand)
            DataSourceRightClickMenu.addAction(DataSourceCollapse)
            DataSourceRightClickMenu.addAction(DataSourceDetail)
            DataSourceRightClickMenu.popup(DataSourceWidgetPos)

        #Child DataSource
        else:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    break

            DataSourceRightClickMenu = QMenu(self.DataSourceTreeWidget)

            # Data Source Preview Web Page
            if hasattr(DS, 'DataSourceHTML'):
                DataSourcePreviewWeb = QAction('Preview Web', self.DataSourceTreeWidget)
                DataSourcePreviewWeb.triggered.connect(lambda: self.DataSourcePreviewWeb(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourcePreviewWeb)

            # Data Source Show Tweet Data
            if hasattr(DS, 'TweetData'):
                DataSourceShowTweetData = QAction('Show Tweet Data', self.DataSourceTreeWidget)
                DataSourceShowTweetData.triggered.connect(lambda: self.DataSourceShowTweetData(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceShowTweetData)

            # Youtube Show Video
            DataSourceYoutubeShowVideo = QAction('Show Video', self.DataSourceTreeWidget)

            if DS.DataSourceext == "Youtube" and hasattr(DS, 'YoutubeURLFlag'):
                DataSourceYoutubeShowVideo.triggered.connect(lambda: self.DataSourceYoutubeShowVideo(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceYoutubeShowVideo)

            # Data Source Show Youtube Comments
            DataSourceShowYoutubeComments = QAction('Show Youtube Data', self.DataSourceTreeWidget)
            if hasattr(DS, 'YoutubeURLFlag'):
                DataSourceShowYoutubeComments.triggered.connect(lambda: self.DataSourceShowYoutubeCommentsURL(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)

            if hasattr(DS, 'YoutubeKeyWordFlag'):
                DataSourceShowYoutubeComments.triggered.connect(lambda: self.DataSourceShowYoutubeCommentsKeyWord(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceShowYoutubeComments)

            # Data Source View Images
            if hasattr(DS, 'DataSourceImage'):
                DataSourceViewImages = QAction('View Image', self.DataSourceTreeWidget)
                DataSourceViewImages.triggered.connect(lambda: self.DataSourceViewImage(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceViewImages)

            # Data Source View CSV Data
            if hasattr(DS, 'CSVData'):
                DataSourceViewCSVData = QAction('View Data', self.DataSourceTreeWidget)
                DataSourceViewCSVData.triggered.connect(lambda: self.DataSourceViewCSVData(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceViewCSVData)

            # Data Sources Preview
            DataSourcePreviewText = QAction('Preview Text', self.DataSourceTreeWidget)

            if DS.DataSourceext == "Pdf files (*.pdf)":
                DataSourcePreviewText.triggered.connect(lambda: self.DataSourcePDFPreview(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)
            elif DS.DataSourceext == "Doc files (*.doc *.docx)":
                DataSourcePreviewText.triggered.connect(lambda: self.DataSourceWordPreview(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)
            elif DS.DataSourceext == 'Notepad files (*.txt)' or DS.DataSourceext == 'Rich Text Format files (*.rtf)':
                DataSourcePreviewText.triggered.connect(lambda: self.DataSourcePreview(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourcePreviewText)

            # Data Source Add Image
            if hasattr(DS, 'DataSourceImage'):
                DataSourceAddImage = QAction('Add Image', self.DataSourceTreeWidget)
                DataSourceAddImage.triggered.connect(lambda: self.DataSourceAddImage(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceAddImage)

            if DS.DataSourceext != "URL" and DS.DataSourceext !=  'Tweet' and DS.DataSourceext !=  'Youtube' and DS.DataSourcetext != "CSV files (*.csv)" :
                # Data Source Create Cases
                DataSourceCreateCases = QAction('Create Cases...', self.DataSourceTreeWidget)
                DataSourceCreateCases.triggered.connect(lambda: self.DataSourceCreateCases(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceCreateCases)

                # Data Source Create Sentiments
                DataSourceCreateSentiments = QAction('Create Sentiments...', self.DataSourceTreeWidget)
                DataSourceCreateSentiments.triggered.connect(lambda: self.DataSourceCreateSentiments(DataSourceWidgetItemName))
                DataSourceRightClickMenu.addAction(DataSourceCreateSentiments)

            # Data Source Rename
            DataSourceRename = QAction('Rename', self.DataSourceTreeWidget)
            DataSourceRename.triggered.connect(lambda: self.DataSourceRename(DataSourceWidgetItemName))
            DataSourceRightClickMenu.addAction(DataSourceRename)

            # Data Source Remove
            DataSourceRemove = QAction('Remove', self.DataSourceTreeWidget)
            DataSourceRemove.triggered.connect(lambda: self.DataSourceRemoveDialog(DataSourceWidgetItemName))
            DataSourceRightClickMenu.addAction(DataSourceRemove)

            # Data Source Child Detail
            DataSourceChildDetail = QAction('Details', self.DataSourceTreeWidget)
            DataSourceChildDetail.triggered.connect(lambda: self.DataSourceChildDetail(DataSourceWidgetItemName))
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
        DataSourcePreviewWebTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Web Preview':
                if tabs.tabWidget != None:
                    DataSourcePreviewWebTabFlag = True
                    break
                else:
                    DataSourcePreviewWebTabFlag2 = True
                    break

        if not DataSourcePreviewWebTabFlag:
            # Creating New Tab for Preview Tab
            PreviewWebTab = QWidget()

            # LayoutWidget For within Preview Tab
            PreviewWebTabVerticalLayoutWidget = QWidget(PreviewWebTab)
            PreviewWebTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Preview Tab
            PreviewWebTabVerticalLayout = QHBoxLayout(PreviewWebTabVerticalLayoutWidget)
            PreviewWebTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            PreviewHTMLWebPage = QWebEngineView()
            PreviewHTMLWebPage.setContextMenuPolicy(Qt.PreventContextMenu)
            PreviewWebTabVerticalLayout.addWidget(PreviewHTMLWebPage)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    try:
                        PreviewHTMLWebPage.setHtml(DS.DataSourceHTML.decode("utf-8"))
                    except UnicodeDecodeError:
                        try:
                            PreviewHTMLWebPage.setHtml(DS.DataSourceHTML.decode("ISO-8859-1"))
                        except UnicodeDecodeError:
                            PreviewHTMLWebPage.setHtml(DS.DataSourceHTML.decode("ISO-8859-4"))
                    break

            if DataSourcePreviewWebTabFlag2:
                tabs.tabWidget = PreviewWebTab
                if tabs.isActive:
                    self.tabWidget.addTab(PreviewWebTab, "Web Preview")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(PreviewWebTab)
            else:
                # Adding Preview Tab to TabList
                myFile.TabList.append(Tab("Web Preview", PreviewWebTab, DataSourceWidgetItemName.text(0)))

                # Adding Preview Tab to QTabWidget
                self.tabWidget.addTab(PreviewWebTab, "Web Preview")
                self.tabWidget.setCurrentWidget(PreviewWebTab)
                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Show Tweet Data
    def DataSourceShowTweetData(self, DataSourceWidgetItemName):
        DataSourceShowTweetDataTabFlag = False
        DataSourceShowTweetDataTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Tweet Data':
                if tabs.tabWidget != None:
                    DataSourceShowTweetDataTabFlag = True
                    break
                else:
                    DataSourceShowTweetDataTabFlag2 = True
                    break

        if not DataSourceShowTweetDataTabFlag:
            ShowTweetDataTab = QWidget()
            ShowTweetDataTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
                             self.horizontalLayoutWidget.height()))
            ShowTweetDataTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Show Tweet Data Tab
            ShowTweetDataTabverticalLayoutWidget = QWidget(ShowTweetDataTab)
            ShowTweetDataTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            ShowTweetDataTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

            # Box Layout for Show Tweet Data Tab
            ShowTweetDataTabverticalLayout = QVBoxLayout(ShowTweetDataTabverticalLayoutWidget)
            ShowTweetDataTabverticalLayout.setContentsMargins(0, 0, 0, 0)

            # Table for Show Tweet Data
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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    rowList = DS.TweetData
                    break

            for row in rowList:
                ShowTweetDataTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 6 or row.index(item) == 9:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(int(item)))
                    else:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))

                    ShowTweetDataTable.setItem(rowList.index(row), row.index(item), intItem)
                    if row.index(item) != 3:
                        ShowTweetDataTable.item(rowList.index(row), row.index(item)).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    ShowTweetDataTable.item(rowList.index(row), row.index(item)).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            ShowTweetDataTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            ShowTweetDataTable.resizeColumnsToContents()
            ShowTweetDataTable.resizeRowsToContents()

            ShowTweetDataTable.setSortingEnabled(True)
            # ShowTweetDataTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            # for i in range(ShowTweetDataTable.columnCount()):
            #     ShowTweetDataTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if DataSourceShowTweetDataTabFlag2:
                tabs.tabWidget = ShowTweetDataTab
                if tabs.isActive:
                    self.tabWidget.addTab(ShowTweetDataTab, "Show Tweet Data")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(ShowTweetDataTab)
            else:
                # Adding Show Tweet Data Tab to TabList
                myFile.TabList.append(Tab("Show Tweet Data", ShowTweetDataTab, DataSourceWidgetItemName.text(0)))

                # Adding Show Tweet Data Tab to QTabWidget
                self.tabWidget.addTab(ShowTweetDataTab, "Show Tweet Data")
                self.tabWidget.setCurrentWidget(ShowTweetDataTab)

                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Youtube Show Video
    def DataSourceYoutubeShowVideo(self, DataSourceWidgetItemName):
        DataSourceYoutubeShowVideoTabFlag = False
        DataSourceYoutubeShowVideoTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Video':
                if tabs.tabWidget != None:
                    DataSourceYoutubeShowVideoTabFlag = True
                    break
                else:
                    DataSourceYoutubeShowVideoTabFlag2 = True
                    break

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                break

        if not DataSourceYoutubeShowVideoTabFlag:
            # Creating New Tab for Video Tab
            VideoTab = QWidget()

            # LayoutWidget For within Video Tab
            VideoTabVerticalLayoutWidget = QWidget(VideoTab)
            VideoTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Video Tab
            VideoTabVerticalLayout = QHBoxLayout(VideoTabVerticalLayoutWidget)
            VideoTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            VideoTabWebPage = QWebEngineView()
            VideoTabWebPage.setContextMenuPolicy(Qt.PreventContextMenu)
            VideoTabWebPage.setUrl(QUrl(DS.DataSourcePath))
            VideoTabVerticalLayout.addWidget(VideoTabWebPage)

            if DataSourceYoutubeShowVideoTabFlag2:
                tabs.tabWidget = VideoTabWebPage
                if tabs.isActive:
                    self.tabWidget.addTab(VideoTab, "Show Video")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(VideoTab)

            else:
                # Adding Preview Tab to TabList
                myFile.TabList.append(Tab("Show Video", VideoTab, DataSourceWidgetItemName.text(0)))

                # Adding Preview Tab to QTabWidget
                self.tabWidget.addTab(VideoTab, "Show Video")
                self.tabWidget.setCurrentWidget(VideoTab)
                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsURL(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False
        DataSourceShowYoutubeCommentsTabFlag2 = False
        
        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                if tabs.tabWidget != None:
                    DataSourceShowYoutubeCommentsTabFlag = True
                    break
                else:
                    DataSourceShowYoutubeCommentsTabFlag2 = True
                    break

        if not DataSourceShowYoutubeCommentsTabFlag:
            ShowYoutubeCommentsTab = QWidget()
            ShowYoutubeCommentsTab.setGeometry(QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
                             self.horizontalLayoutWidget.height()))
            ShowYoutubeCommentsTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Show Youtube Comments Tab
            ShowYoutubeCommentsTabverticalLayoutWidget = QWidget(ShowYoutubeCommentsTab)
            ShowYoutubeCommentsTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            ShowYoutubeCommentsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

            # Box Layout for Show Youtube Comments Tab
            ShowYoutubeCommentsTabverticalLayout = QVBoxLayout(ShowYoutubeCommentsTabverticalLayoutWidget)
            ShowYoutubeCommentsTabverticalLayout.setContentsMargins(0, 0, 0, 0)

            # Table for Show Youtube Comments
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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    rowList = DS.YoutubeData
                    break

            for row in rowList:
                ShowYoutubeCommentsTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 0:
                        ptext = QPlainTextEdit()
                        ptext.setReadOnly(True)
                        ptext.setPlainText(item);
                        ptext.setFixedHeight(self.tabWidget.height() / 15)
                        ShowYoutubeCommentsTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                    else:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        ShowYoutubeCommentsTable.setItem(rowList.index(row), row.index(item), intItem)
                        ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        ShowYoutubeCommentsTable.item(rowList.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            ShowYoutubeCommentsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            ShowYoutubeCommentsTable.resizeColumnsToContents()
            ShowYoutubeCommentsTable.resizeRowsToContents()

            ShowYoutubeCommentsTable.setSortingEnabled(True)
            row_width = 0

            for i in range(ShowYoutubeCommentsTable.columnCount()):
                 ShowYoutubeCommentsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            
            if DataSourceShowYoutubeCommentsTabFlag2:
                tabs.tabWidget = ShowYoutubeCommentsTab
                if tabs.isActive:
                    self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
            else:
                # Adding Show Youtube Comments Tab to TabList
                myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))
    
                # Adding Show Youtube Comments Tab to QTabWidget
                self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
                self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
                myFile.requiredSaved = True

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Show Youtube Comments URL
    def DataSourceShowYoutubeCommentsKeyWord(self, DataSourceWidgetItemName):
        DataSourceShowYoutubeCommentsTabFlag = False
        DataSourceShowYoutubeCommentsTabFlag2 = False
        
        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Show Youtube Data':
                if tabs.tabWidget != None:
                    DataSourceShowYoutubeCommentsTabFlag = True
                    break
                else:
                    DataSourceShowYoutubeCommentsTabFlag2 = True
                    break
                    
        if not DataSourceShowYoutubeCommentsTabFlag:
            ShowYoutubeCommentsTab = QWidget()
            ShowYoutubeCommentsTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
                             self.horizontalLayoutWidget.height()))
            ShowYoutubeCommentsTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Show Youtube Comments Tab
            ShowYoutubeCommentsTabverticalLayoutWidget = QWidget(ShowYoutubeCommentsTab)
            ShowYoutubeCommentsTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            ShowYoutubeCommentsTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

            # Box Layout for Show Youtube Comments Tab
            ShowYoutubeCommentsTabverticalLayout = QVBoxLayout(ShowYoutubeCommentsTabverticalLayoutWidget)
            ShowYoutubeCommentsTabverticalLayout.setContentsMargins(0, 0, 0, 0)

            # Table for Show Youtube Comments
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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    rowList = DS.YoutubeData
                    break

            for row in rowList:
                ShowYoutubeCommentsTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 0:
                        ptext = QPlainTextEdit()
                        ptext.setReadOnly(True)
                        ptext.setPlainText(item);
                        ptext.setFixedHeight(self.tabWidget.height() / 15)
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

            ShowYoutubeCommentsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            ShowYoutubeCommentsTable.resizeColumnsToContents()
            ShowYoutubeCommentsTable.resizeRowsToContents()

            ShowYoutubeCommentsTable.setSortingEnabled(True)
            row_width = 0

            for i in range(ShowYoutubeCommentsTable.columnCount()):
                ShowYoutubeCommentsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            
            if DataSourceShowYoutubeCommentsTabFlag2:
                tabs.tabWidget = ShowYoutubeCommentsTab
                if tabs.isActive:
                    self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
            else:
                # Adding Show Youtube Comments Tab to TabList
                myFile.TabList.append(Tab("Show Youtube Data", ShowYoutubeCommentsTab, DataSourceWidgetItemName.text(0)))
    
                # Adding Show Youtube Comments Tab to QTabWidget
                self.tabWidget.addTab(ShowYoutubeCommentsTab, "Show Youtube Data")
                self.tabWidget.setCurrentWidget(ShowYoutubeCommentsTab)
                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True
    
    # Data Source View Images
    def DataSourceViewImage(self, DataSourceWidgetItemName):
        DataSourceShowImagesTabFlag = False
        DataSourceShowImagesTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'View Image':
                if tabs.tabWidget != None:
                    DataSourceShowImagesTabFlag = True
                    break
                else:
                    DataSourceShowImagesTabFlag2 = True
                    break
                    
        if not DataSourceShowImagesTabFlag:
            ViewImageTab = QWidget()
            ViewImageTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
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

            # Box Layout for View Image Tab
            ViewImageTabverticalLayout = QVBoxLayout(ViewImageTabverticalLayoutWidget)
            ViewImageTabverticalLayout.setContentsMargins(0, 0, 0, 0)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
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

            if DataSourceShowImagesTabFlag2:
                tabs.tabWidget = ViewImageTab
                if tabs.isActive:
                    self.tabWidget.addTab(ViewImageTab, "View Image")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(ViewImageTab)
            else:
                myFile.TabList.append(Tab("View Image", ViewImageTab, DataSourceWidgetItemName.text(0)))
    
                # Adding View Image Tab to QTabWidget
                self.tabWidget.addTab(ViewImageTab, "View Image")
                self.tabWidget.setCurrentWidget(ViewImageTab)
                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source View CSV Data
    def DataSourceViewCSVData(self, DataSourceWidgetItemName):
        DataSourceViewCSVDataTabFlag = False
        DataSourceViewCSVDataTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'CSV Data':
                if tabs.tabWidget != None:
                    DataSourceViewCSVDataTabFlag = True
                    break
                else:
                    DataSourceViewCSVDataTabFlag2 = True
                    break

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                CSVdf = DS.CSVData
                break

        if not DataSourceViewCSVDataTabFlag:
            ViewCSVDataTab = QWidget()
            ViewCSVDataTab.setGeometry(QRect(self.verticalLayoutWidget.width(), 0,
                                                     self.width - self.verticalLayoutWidget.width(),self.horizontalLayoutWidget.height()))
            ViewCSVDataTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within View CSV Data Tab
            ViewCSVDataTabverticalLayoutWidget = QWidget(ViewCSVDataTab)
            ViewCSVDataTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(),
                                                                   self.tabWidget.height())
            ViewCSVDataTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

            # Box Layout for View CSV Data Tab
            ViewCSVDataTabverticalLayout = QVBoxLayout(ViewCSVDataTabverticalLayoutWidget)
            ViewCSVDataTabverticalLayout.setContentsMargins(0, 0, 0, 0)

            # Table for View CSV Data
            ViewCSVDataTable = QTableWidget(ViewCSVDataTabverticalLayoutWidget)
            ViewCSVDataTable.setColumnCount(len(DS.CSVHeaderLabel))
            ViewCSVDataTable.setGeometry(0, 0, ViewCSVDataTabverticalLayoutWidget.width(),
                                                 ViewCSVDataTabverticalLayoutWidget.height())
            ViewCSVDataTable.setSizePolicy(self.sizePolicy)

            ViewCSVDataTable.setWindowFlags(ViewCSVDataTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)


            ViewCSVDataTable.setHorizontalHeaderLabels(DS.CSVHeaderLabel)
            ViewCSVDataTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

            for i in range(ViewCSVDataTable.columnCount()):
                ViewCSVDataTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
                ViewCSVDataTable.horizontalHeaderItem(i).setFont(
                    QFont(ViewCSVDataTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))

            count = 0

            for i in range(len(CSVdf.index)):
                ViewCSVDataTable.insertRow(i)
                for j in range(len(CSVdf.columns)):
                    newitem = CSVdf.iloc[i, j]

                    if isinstance(newitem, (int, np.integer)):
                        newitem = int(newitem)
                    elif isinstance(newitem, (float, np.float)):
                        newitem = float(newitem)
                    elif isinstance(newitem, (float, pd.datetime)):
                        newitem = newitem.to_pydatetime().strftime("%m/%d/%Y, %H:%M:%S")


                    intItem = QTableWidgetItem()
                    intItem.setData(Qt.EditRole, QVariant(newitem))
                    ViewCSVDataTable.setItem(i, j, intItem)
                    ViewCSVDataTable.item(i, j).setTextAlignment(Qt.AlignVCenter)
                    ViewCSVDataTable.item(i, j).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            ViewCSVDataTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            ViewCSVDataTable.resizeColumnsToContents()
            ViewCSVDataTable.resizeRowsToContents()
            ViewCSVDataTable.setSortingEnabled(True)

            # for i in range(ViewCSVDataTable.columnCount()):
            #     ViewCSVDataTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if DataSourceViewCSVDataTabFlag2:
                tabs.tabWidget = ViewCSVDataTab
                if tabs.isActive:
                    self.tabWidget.addTab(ViewCSVDataTab, "CSV Data")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(ViewCSVDataTab)
            else:
                # Adding View CSV Data Tab to TabList
                myFile.TabList.append(Tab("CSV Data", ViewCSVDataTab, DataSourceWidgetItemName.text(0)))
    
                # Adding View CSV Data Tab to QTabWidget
                self.tabWidget.addTab(ViewCSVDataTab, "CSV Data")
                self.tabWidget.setCurrentWidget(ViewCSVDataTab)
                myFile.requiredSaved = True
        else:
            # Adding View CSV Data Tab to QTabWidget
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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

    # Data Source PDF Preview
    def DataSourcePDFPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTabFlag = False
        DataSourcePreviewTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                if tabs.tabWidget != None:
                    DataSourcePreviewTabFlag = True
                    break
                else:
                    DataSourcePreviewTabFlag2 = True
                    break
                    
        if not DataSourcePreviewTabFlag:
            DataSourcePreviewTab = QWidget()

            # LayoutWidget For within DataSource Preview Tab
            DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
            DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
            DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())



            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    if os.path.exists(DS.DataSourcePath):
                        # Box Layout for Data SourceTab
                        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
                        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

                        PDFPreviewWeb = QWebEngineView()
                        DataSourceverticalLayout.addWidget(PDFPreviewWeb)
                        PDFPreviewWeb.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
                        PDFPreviewWeb.setUrl(QUrl(DS.DataSourcePath))
                        break
                    else:
                        DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
                        DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
                        DataSourcePreview.setReadOnly(True)
                        DataSourcePreview.setText(DS.DataSourcetext)
                        break

            if DataSourcePreviewTabFlag2:
                tabs.tabWidget = DataSourcePreviewTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
            else:
                # Adding Preview Tab to TabList
                myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

                # Adding Preview Tab to QTabWidget
                self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
                myFile.requiredSaved = True
        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Word Preview
    def DataSourceWordPreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTabFlag = False
        DataSourcePreviewTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                if tabs.tabWidget != None:
                    DataSourcePreviewTabFlag = True
                    break
                else:
                    DataSourcePreviewTabFlag2 = True
                    break

        if not DataSourcePreviewTabFlag:
            DataSourcePreviewTab = QWidget()
            # LayoutWidget For within DataSource Preview Tab
            DataSourcePreviewTabverticalLayoutWidget = QWidget(DataSourcePreviewTab)
            DataSourcePreviewTabverticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
            DataSourcePreviewTabverticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())



            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    if os.path.exists(DS.DataSourcePath) and WindowPlatform:
                        # Box Layout for Data SourceTab
                        DataSourceverticalLayout = QVBoxLayout(DataSourcePreviewTabverticalLayoutWidget)
                        DataSourceverticalLayout.setContentsMargins(0, 0, 0, 0)

                        WordActivex = QAxContainer.QAxWidget()
                        WordActivex.setFocusPolicy(Qt.StrongFocus)
                        WordActivex.setProperty("DisplayScrollBars", True);
                        WordActivex.setControl(DS.DataSourcePath)

                        DataSourceverticalLayout.addWidget(WordActivex)
                        break
                    else:
                        DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
                        DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
                        DataSourcePreview.setReadOnly(True)
                        DataSourcePreview.setText(DS.DataSourcetext)
                        break

            if DataSourcePreviewTabFlag:
                tabs.tabWidget = DataSourcePreviewTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
            else:
                # Adding Preview Tab to TabList
                myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

                # Adding Preview Tab to QTabWidget
                self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
                myFile.requiredSaved = True

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Data Source Preview
    def DataSourcePreview(self, DataSourceWidgetItemName):
        DataSourcePreviewTabFlag = False
        DataSourcePreviewTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Preview':
                if tabs.tabWidget != None:
                    DataSourcePreviewTabFlag = True
                    break
                else:
                    DataSourcePreviewTabFlag2 = True
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

            DataSourcePreview = QTextEdit(DataSourcePreviewTabverticalLayoutWidget)
            DataSourcePreview.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())
            DataSourcePreview.setReadOnly(True)

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DataSourcePreview.setText(DS.DataSourcetext)
                    break

            if DataSourcePreviewTabFlag2:
                tabs.tabWidget = DataSourcePreviewTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
            else:
                # Adding Preview Tab to TabList
                myFile.TabList.append(Tab("Preview", DataSourcePreviewTab, DataSourceWidgetItemName.text(0)))

                # Adding Preview Tab to QTabWidget
                self.tabWidget.addTab(DataSourcePreviewTab, "Preview")
                self.tabWidget.setCurrentWidget(DataSourcePreviewTab)
                myFile.requiredSaved = True
        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)

    # Data Source Add Image
    def DataSourceAddImage(self, DataSourceWidgetItemName):
        dummyWindow = OpenWindow("Open Image File",
                                 "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)",
                                 2)
        path = dummyWindow.filepath
        del dummyWindow

        if all(path):
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    DS.AddImage(path[0])
                    break

            if len(DS.AddImagePathDoublingError) == 0:
                QMessageBox.information(self, "Add Image",  "Images Added Successfully", QMessageBox.Ok)
                myFile.requiredSaved = True
                self.DataSourceSimilarityUpdate()
                self.DataSourceDocumentClusteringUpdate()
            else:
                if len(path[0]) == len(DS.AddImagePathDouble):
                    myFile.requiredSaved = False
                else:
                    myFile.requiredSaved = True

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

                QMessageBox.critical(self, "Add Image",
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

        self.QDialogAddProperties(DataSourceShowFrequencyTableDialog)


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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Show Word Frequency Button Box
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
        DataSourceShowFrequencyTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Word Frequency':
                if tabs.tabWidget != None:
                    DataSourceShowFrequencyTabFlag = True
                    break
                else:
                    DataSourceShowFrequencyTabFlag2 = True
                    break

        if not DataSourceShowFrequencyTabFlag:
            WordFrequencyTab = QWidget()
            WordFrequencyTab.setGeometry(
                             QRect(self.verticalLayoutWidget.width(),
                                   self.tabWidget.tabBar().geometry().height(),
                                   self.width - self.verticalLayoutWidget.width(),
                                   self.horizontalLayoutWidget.height() - self.tabWidget.tabBar().geometry().height()))
            WordFrequencyTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within Word Freuency Tab
            WordFrequencyTabVerticalLayoutWidget2 = QWidget(WordFrequencyTab)
            WordFrequencyTabVerticalLayoutWidget2.setGeometry(WordFrequencyTab.width() / 4,
                                                              0,
                                                              WordFrequencyTab.width() / 2,
                                                              WordFrequencyTab.height() / 10)

            # Box Layout for Word Freuency Tab
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
            WordFrequencyTabverticalLayoutWidget.setGeometry(0, WordFrequencyTab.height() / 10, WordFrequencyTab.width(),
                                                             WordFrequencyTab.height() - WordFrequencyTab.height() / 10)
            WordFrequencyTabverticalLayoutWidget.setSizePolicy(self.sizePolicy)

            # Box Layout for Word Frequency Tab
            WordFrequencyverticalLayout = QVBoxLayout(WordFrequencyTabverticalLayoutWidget)
            WordFrequencyverticalLayout.setContentsMargins(0, 0, 0, 0)

            # Table for Word Frequency
            WordFrequencyTable = QTableWidget(WordFrequencyTabverticalLayoutWidget)
            WordFrequencyTable.setColumnCount(7)
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



            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Word Frequency")
                    dummyProgressInfo.GenerateWordFrequency(DS)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Word Frequency Table")

                    del dummyProgressInfo

                    rowList = ThreadQueue.get()
                    break

            DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(WordFrequencyTable))


            for row in rowList:
                WordFrequencyTable.insertRow(rowList.index(row))
                for item in row:
                    if row.index(item) == 4:
                        ptext = QPlainTextEdit()
                        ptext.setReadOnly(True)
                        ptext.setPlainText(item);
                        ptext.setFixedHeight(self.tabWidget.height() / 15)
                        WordFrequencyTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                    else:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        WordFrequencyTable.setItem(rowList.index(row), row.index(item), intItem)
                        WordFrequencyTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        WordFrequencyTable.item(rowList.index(row), row.index(item)).setFlags(
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            WordFrequencyTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            WordFrequencyTable.resizeColumnsToContents()
            WordFrequencyTable.resizeRowsToContents()

            WordFrequencyTable.setSortingEnabled(True)
            WordFrequencyTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            row_width = 0

            for i in range(WordFrequencyTable.columnCount()):
                WordFrequencyTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            if DataSourceShowFrequencyTabFlag2:
                tabs.tabWidget = WordFrequencyTab
                if tabs.isActive:
                    self.tabWidget.addTab(WordFrequencyTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(WordFrequencyTab)

            else:
                # Adding Word Frequency Tab to TabList
                myFile.TabList.append(Tab("Word Frequency", WordFrequencyTab, DataSourceName))
                # Adding Word Frequency Tab to QTabWidget
                self.tabWidget.addTab(WordFrequencyTab, "Word Frequency")
                self.tabWidget.setCurrentWidget(WordFrequencyTab)
                myFile.requiredSaved = True

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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
        self.QDialogAddProperties(GenerateQuestionsDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Generate Questio Button Box
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
        GenerateQuestionsTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Generate Questions':
                if tabs.tabWidget != None:
                    GenerateQuestionsTabFlag = True
                    break
                else:
                    GenerateQuestionsTabFlag2 = True
                    break

        if not GenerateQuestionsTabFlag:
            #Generate Question Tab
            GenerateQuestionsTab = QWidget()
            GenerateQuestionsTab.setGeometry(
                QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
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



            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:


                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Generate Question")
                    dummyProgressInfo.QuestionGenerator(DS.DataSourcetext)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Questions")

                    del dummyProgressInfo

                    rowList = ThreadQueue.get()

                    break

            DownloadAsCSVButton.clicked.connect(lambda: self.SaveTableAsCSV(GenerateQuestionsTable))

            if len(rowList) != 0:
                for row in rowList:
                    GenerateQuestionsTable.insertRow(rowList.index(row))

                    ptext = QPlainTextEdit()
                    ptext.setReadOnly(True)
                    ptext.setPlainText(row)
                    ptext.adjustSize()
                    ptext.setFixedHeight(self.tabWidget.height() / 15)
                    GenerateQuestionsTable.setCellWidget(rowList.index(row), 0, ptext)

                GenerateQuestionsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                GenerateQuestionsTable.resizeColumnsToContents()
                GenerateQuestionsTable.resizeRowsToContents()

                GenerateQuestionsTable.setSortingEnabled(True)
                GenerateQuestionsTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                row_width = 0

                for i in range(GenerateQuestionsTable.columnCount()):
                    GenerateQuestionsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

                if GenerateQuestionsTabFlag2:
                    tabs.tabWidget = GenerateQuestionsTab
                    if tabs.isActive:
                        self.tabWidget.addTab(GenerateQuestionsTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(GenerateQuestionsTab)
                else:
                    # Adding Generate Question Tab to TabList
                    myFile.TabList.append(Tab("Generate Questions", GenerateQuestionsTab, DataSourceName))

                    # Adding Generate Questions Tab to QTabWidget
                    self.tabWidget.addTab(GenerateQuestionsTab, "Generate Questions")
                    self.tabWidget.setCurrentWidget(GenerateQuestionsTab)
                    myFile.requiredSaved = True

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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # ****************************************************************************
    # ********************* Data Sources Sentiment Analysis **********************
    # ****************************************************************************

    # Data Source Sentiment Analysis
    def DataSourcesSentimentAnalysis(self):
        SentimentAnalysisDialog = QDialog()
        SentimentAnalysisDialog.setWindowTitle("Sentiment Analysis")
        SentimentAnalysisDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                            self.height / 5)
        SentimentAnalysisDialog.setParent(self)
        self.QDialogAddProperties(SentimentAnalysisDialog)

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
            if DS.DataSourceext == "Youtube" or DS.DataSourceext == "Tweet" or DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Data Source Label
        DataSourceColumnLabel = QLabel(SentimentAnalysisDialog)
        DataSourceColumnLabel.setGeometry(SentimentAnalysisDialog.width() * 0.125,
                                          SentimentAnalysisDialog.height() * 0.45,
                                          SentimentAnalysisDialog.width() / 4,
                                          SentimentAnalysisDialog.height() * 0.1)

        DataSourceColumnLabel.setText("Column")
        DataSourceColumnLabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourceColumnLabel)

        # Data Source ComboBox
        ColumnComboBox = QComboBox(SentimentAnalysisDialog)
        ColumnComboBox.setGeometry(SentimentAnalysisDialog.width() * 0.4,
                                   SentimentAnalysisDialog.height() * 0.45,
                                   SentimentAnalysisDialog.width() / 2,
                                   SentimentAnalysisDialog.height() / 10)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DSComboBox.currentText():
                if DS.DataSourceext == "Youtube":
                    ColumnComboBox.addItem("Youtube Comments")
                    ColumnComboBox.setDisabled(True)
                elif DS.DataSourceext == "Tweet":
                    ColumnComboBox.addItem("Tweet Text")
                    ColumnComboBox.setDisabled(True)
                elif DS.DataSourceext == "CSV files (*.csv)":
                    for rows in DS.CSVHeaderLabel:
                        ColumnComboBox.addItem(rows)

        self.LineEditSizeAdjustment(ColumnComboBox)

        # Sentiment Analysis Button Box
        SentimentAnalysisbuttonBox = QDialogButtonBox(SentimentAnalysisDialog)
        SentimentAnalysisbuttonBox.setGeometry(SentimentAnalysisDialog.width() * 0.125,
                                               SentimentAnalysisDialog.height() * 0.8,
                                               SentimentAnalysisDialog.width() * 3 / 4,
                                               SentimentAnalysisDialog.height() / 5)
        SentimentAnalysisbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        SentimentAnalysisbuttonBox.button(QDialogButtonBox.Ok).setText('Generate')

        if len(DSComboBox.currentText()) == 0:
            SentimentAnalysisbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(SentimentAnalysisbuttonBox)

        DSComboBox.currentTextChanged.connect(lambda: self.SentimentAnalysisDSColumnChange(ColumnComboBox))

        SentimentAnalysisbuttonBox.accepted.connect(SentimentAnalysisDialog.accept)
        SentimentAnalysisbuttonBox.rejected.connect(SentimentAnalysisDialog.reject)

        SentimentAnalysisbuttonBox.accepted.connect(
            lambda: self.SentimentAnalysisTable(DSComboBox.currentText(), ColumnComboBox.currentText()))

        SentimentAnalysisDialog.exec()

    # Sentiment Analysis DS Column Changer
    def SentimentAnalysisDSColumnChange(self, ColumnComboBox):
        DSComboBox = self.sender()

        while ColumnComboBox.count() > 0:
            ColumnComboBox.removeItem(0)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DSComboBox.currentText():
                if DS.DataSourceext == "Youtube":
                    ColumnComboBox.addItem("Youtube Comments")
                    ColumnComboBox.setDisabled(True)
                elif DS.DataSourceext == "Tweet":
                    ColumnComboBox.addItem("Tweet Text")
                    ColumnComboBox.setDisabled(True)
                elif DS.DataSourceext == "CSV files (*.csv)":
                    for rows in DS.CSVHeaderLabel:
                        ColumnComboBox.addItem(rows)
                    ColumnComboBox.setDisabled(False)

    # Sentiment Analysis Table
    def SentimentAnalysisTable(self, DataSourceName, ColumnName):
        DataSourceSentimentAnalysisFlag = False
        DataSourceSentimentAnalysisFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Automatic Sentiment Analysis':
                if tabs.tabWidget != None:
                    DataSourceSentimentAnalysisFlag = True
                    break
                else:
                    DataSourceSentimentAnalysisFlag2 = True
                    break

        if not DataSourceSentimentAnalysisFlag:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Sentiment Analysis")
                    dummyProgressInfo.SentimentAnalysis(DS, ColumnName)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Performing Sentiment Analysis")

                    del dummyProgressInfo

                    DS = ThreadQueue.get()

                    rowList = DS.AutomaticSentimentList

                    DS.SentimentAnalysisVisualization()
                    break

            SentimentAnalysisTab = QWidget()
            SentimentAnalysisTab.setGeometry(QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(),
                                                          self.horizontalLayoutWidget.height() - self.tabWidget.tabBar().geometry().height()))
            SentimentAnalysisTab.setSizePolicy(self.sizePolicy)

            # LayoutWidget For within SentimentAnalysis Tab
            SentimentAnalysisTabVerticalLayoutWidget = QWidget(SentimentAnalysisTab)
            SentimentAnalysisTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(),
                                                                  self.tabWidget.height() / 10)
            # Box Layout for SentimentAnalysis Tab
            SentimentAnalysisTabVerticalLayout = QHBoxLayout(SentimentAnalysisTabVerticalLayoutWidget)
            SentimentAnalysisTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Positive_Count Label
            PositiveCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget)
            PositiveCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget.width() * 0.05,
                                           SentimentAnalysisTabVerticalLayoutWidget.height() * 0.142,
                                           SentimentAnalysisTabVerticalLayoutWidget.width() / 20,
                                           SentimentAnalysisTabVerticalLayoutWidget.height() / 7)
            PositiveCountLabel.setText("Positive: " + str(DS.PositiveSentimentCount))
            PositiveCountLabel.setAlignment(Qt.AlignVCenter)
            PositiveCountLabel.adjustSize()

            # Neutral_Count Label
            NeutralCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget)
            NeutralCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget.width() * 0.05,
                                          SentimentAnalysisTabVerticalLayoutWidget.height() * 0.428,
                                          SentimentAnalysisTabVerticalLayoutWidget.width() / 20,
                                          SentimentAnalysisTabVerticalLayoutWidget.height() / 7)
            NeutralCountLabel.setText("Neutral: " + str(DS.NeutralSentimentCount))
            NeutralCountLabel.setAlignment(Qt.AlignVCenter)
            NeutralCountLabel.adjustSize()

            # Negative_Count Label
            NegativeCountLabel = QLabel(SentimentAnalysisTabVerticalLayoutWidget)
            NegativeCountLabel.setGeometry(SentimentAnalysisTabVerticalLayoutWidget.width() * 0.05,
                                           SentimentAnalysisTabVerticalLayoutWidget.height() * 0.714,
                                           SentimentAnalysisTabVerticalLayoutWidget.width() / 20,
                                           SentimentAnalysisTabVerticalLayoutWidget.height() / 7)
            NegativeCountLabel.setText("Negative: " + str(DS.NegativeSentimentCount))
            NegativeCountLabel.setAlignment(Qt.AlignVCenter)
            NegativeCountLabel.adjustSize()

            # Download Button For Sentiment Analysis Table
            DownloadAsCSVButton = QPushButton(SentimentAnalysisTabVerticalLayoutWidget)
            DownloadAsCSVButton.setGeometry(SentimentAnalysisTabVerticalLayoutWidget.width() * 0.6,
                                            SentimentAnalysisTabVerticalLayoutWidget.height() * 0.4,
                                            SentimentAnalysisTabVerticalLayoutWidget.width() * 0.15,
                                            SentimentAnalysisTabVerticalLayoutWidget.height() * 0.2)
            DownloadAsCSVButton.setText("Download")
            DownloadAsCSVButton.setIcon(QIcon("Images/Download Button.png"))
            DownloadAsCSVButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

            DownloadAsCSVButtonFont = QFont("sans-serif")
            DownloadAsCSVButtonFont.setPixelSize(14)
            DownloadAsCSVButtonFont.setBold(True)
            DownloadAsCSVButton.setFont(DownloadAsCSVButtonFont)

            self.LineEditSizeAdjustment(DownloadAsCSVButton)

            # Data Source Label
            DataSourceLabel = QLabel()
            DataSourceLabel.setText("Sentiment Analysis of " + DS.DataSourceName)
            DataSourceLabel.setStyleSheet("font-size: 20px;font-weight: bold; background: transparent;")
            DataSourceLabel.setAlignment(Qt.AlignVCenter)
            DataSourceLabel.hide()
            SentimentAnalysisTabVerticalLayout.addWidget(DataSourceLabel)

            # Data Source Sentiment Analysis  ComboBox
            DSSAComboBox = QComboBox(SentimentAnalysisTabVerticalLayoutWidget)
            DSSAComboBox.setGeometry(SentimentAnalysisTabVerticalLayoutWidget.width() * 0.8,
                                     SentimentAnalysisTabVerticalLayoutWidget.height() * 0.4,
                                     SentimentAnalysisTabVerticalLayoutWidget.width() * 0.15,
                                     SentimentAnalysisTabVerticalLayoutWidget.height() * 0.2)
            DSSAComboBox.addItem("Show Table")
            DSSAComboBox.addItem("Show Chart")
            self.LineEditSizeAdjustment(DSSAComboBox)

            # LayoutWidget For within Sentiment Analysis Tab
            SentimentAnalysisTabverticalLayoutWidget2 = QWidget(SentimentAnalysisTab)
            SentimentAnalysisTabverticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                                    self.tabWidget.height() - self.tabWidget.height() / 10)
            SentimentAnalysisTabverticalLayoutWidget2.setSizePolicy(self.sizePolicy)

            # Box Layout for Sentiment Analysis Tab
            SentimentAnalysisverticalLayout2 = QVBoxLayout(SentimentAnalysisTabverticalLayoutWidget2)
            SentimentAnalysisverticalLayout2.setContentsMargins(0, 0, 0, 0)

            # Table for Sentiment Analysis
            SentimentAnalysisTable = QTableWidget(SentimentAnalysisTabverticalLayoutWidget2)
            SentimentAnalysisTable.setColumnCount(2)
            SentimentAnalysisTable.setGeometry(0, 0, SentimentAnalysisTabverticalLayoutWidget2.width(),
                                                     SentimentAnalysisTabverticalLayoutWidget2.height())
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
                            ptext.setFixedHeight(self.tabWidget.height()/15)
                            SentimentAnalysisTable.setCellWidget(rowList.index(row), row.index(item), ptext)

                        else:
                            intItem = QTableWidgetItem()
                            intItem.setData(Qt.EditRole, QVariant(item))
                            SentimentAnalysisTable.setItem(rowList.index(row), row.index(item), intItem)
                            SentimentAnalysisTable.item(rowList.index(row), row.index(item)).setTextAlignment(
                                Qt.AlignHCenter | Qt.AlignVCenter)
                            SentimentAnalysisTable.item(rowList.index(row), row.index(item)).setFlags(
                                Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                SentimentAnalysisTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                SentimentAnalysisTable.resizeColumnsToContents()
                SentimentAnalysisTable.resizeRowsToContents()

                SentimentAnalysisTable.setSortingEnabled(True)
                SentimentAnalysisTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

                for i in range(SentimentAnalysisTable.columnCount()):
                    SentimentAnalysisTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

                # Sentiment Analysis Chart

                # LayoutWidget For within Sentiment Analysis Tab
                SentimentAnalysisTabverticalLayoutWidget3 = QWidget(SentimentAnalysisTab)
                SentimentAnalysisTabverticalLayoutWidget3.setGeometry(0, self.tabWidget.height() / 10,
                                                                      self.tabWidget.width()/2,
                                                                      self.tabWidget.height() - self.tabWidget.height() / 10)
                SentimentAnalysisTabverticalLayoutWidget3.setSizePolicy(self.sizePolicy)

                # Box Layout for Sentiment Analysis Tab
                SentimentAnalysisverticalLayout3 = QVBoxLayout(SentimentAnalysisTabverticalLayoutWidget3)
                SentimentAnalysisverticalLayout3.setContentsMargins(0, 0, 0, 0)

                canvas = FigureCanvas(DS.BarSentimentFigure)
                SentimentAnalysisverticalLayout3.addWidget(canvas)
                SentimentAnalysisTabverticalLayoutWidget3.hide()


                SentimentAnalysisTabverticalLayoutWidget4 = QWidget(SentimentAnalysisTab)
                SentimentAnalysisTabverticalLayoutWidget4.setGeometry(self.tabWidget.width()/2, self.tabWidget.height() / 10,
                                                                      self.tabWidget.width()/2,
                                                                      self.tabWidget.height() - self.tabWidget.height() / 10)
                SentimentAnalysisTabverticalLayoutWidget4.setSizePolicy(self.sizePolicy)

                # Box Layout for Sentiment Analysis Tab
                SentimentAnalysisverticalLayout4 = QVBoxLayout(SentimentAnalysisTabverticalLayoutWidget4)
                SentimentAnalysisverticalLayout4.setContentsMargins(0, 0, 0, 0)

                canvas2 = FigureCanvas(DS.PieSentimentFigure)
                SentimentAnalysisverticalLayout4.addWidget(canvas2)
                SentimentAnalysisTabverticalLayoutWidget4.hide()

                DSSAComboBox.currentTextChanged.connect(lambda: self.SentimentAnalysisComboBox(DataSourceLabel,
                                                                                               PositiveCountLabel,
                                                                                               NegativeCountLabel,
                                                                                               NeutralCountLabel,
                                                                                               DownloadAsCSVButton,
                                                                                               SentimentAnalysisTabverticalLayoutWidget2,
                                                                                               SentimentAnalysisTabverticalLayoutWidget3,
                                                                                               SentimentAnalysisTabverticalLayoutWidget4))

                if DataSourceSentimentAnalysisFlag2:
                    tabs.tabWidget = SentimentAnalysisTab
                    if tabs.isActive:
                        self.tabWidget.addTab(SentimentAnalysisTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(SentimentAnalysisTab)

                else:
                    # Adding Automatic Sentiment Analysis Tab to TabList
                    dummyTab = Tab("Automatic Sentiment Analysis", SentimentAnalysisTab, DataSourceName)
                    dummyTab.setAutomaticSentimentAnalysis(ColumnName)
                    myFile.TabList.append(dummyTab)

                    # Adding Sentiment Analysis Tab to QTabWidget
                    self.tabWidget.addTab(SentimentAnalysisTab, "Automatic Sentiment Analysis")
                    self.tabWidget.setCurrentWidget(SentimentAnalysisTab)
                    myFile.requiredSaved = True

                # Adding Sentiment Query
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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Sentiment Analysis ComboBox
    def SentimentAnalysisComboBox(self, DataSourceLabel, PositiveCountLabel, NegativeCountLabel, NeutralCountLabel, DownloadASCSVButton, Layout1, Layout2, Layout3):
        DSSAComboBox = self.sender()

        if DSSAComboBox.currentText() == "Show Table":
            DataSourceLabel.hide()
            PositiveCountLabel.show(),
            NegativeCountLabel.show(),
            NeutralCountLabel.show(),
            DownloadASCSVButton.show()
            Layout1.show()
            Layout2.hide()
            Layout3.hide()
        else:
            DataSourceLabel.show()
            PositiveCountLabel.hide(),
            NegativeCountLabel.hide(),
            NeutralCountLabel.hide(),
            DownloadASCSVButton.hide()
            Layout1.hide()
            Layout2.show()
            Layout3.show()


    # ****************************************************************************
    # ************************** Data Sources Rename *****************************
    # ****************************************************************************

    # Data Source Rename
    def DataSourceRename(self, DataSourceWidgetItemName):
        DataSourceRename = QDialog()
        DataSourceRename.setWindowTitle("Rename")
        DataSourceRename.setGeometry(self.width * 0.375, self.height * 0.425, self.width/4, self.height*0.15)
        DataSourceRename.setParent(self)
        self.QDialogAddProperties(DataSourceRename)

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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    for tab in myFile.TabList:
                        if tab.DataSourceName == DS.DataSourceName:
                            tab.DataSourceName = name

                    # ************** updating queries *****************
                    for widgets in self.QueryTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0):
                        widgets.setText(0, name)
                        widgets.setToolTip(0, widgets.text(0))

                    # ************** updating cases *****************
                    for widgets in self.CasesTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0):
                        widgets.setText(0, name)
                        widgets.setToolTip(0, widgets.text(0))

                    # *********** updating sentiments ***************
                    for widgets in self.SentimentTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0):
                        widgets.setText(0, name)
                        widgets.setToolTip(0, widgets.text(0))

                    # ********* updating Visualizations *************
                    for widgets in self.VisualizationTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0):
                        widgets.setText(0, name)
                        widgets.setToolTip(0, widgets.text(0))

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

            myFile.requiredSaved = True
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
        self.QDialogAddProperties(DataSourceStemWord)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
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
        DataSourceStemWordTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Stem Word':
                if tabs.tabWidget != None:
                    DataSourceStemWordTabFlag = True
                    break
                else:
                    DataSourceStemWordTabFlag2 = True
                    break

        if not DataSourceStemWordTabFlag:
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

                if DataSourceStemWordTabFlag2:
                    tabs.tabWidget = StemWordTab
                    if tabs.isActive:
                        self.tabWidget.addTab(StemWordTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(StemWordTab)

                else:
                    # Adding Stem Word Tab to QTabWidget
                    dummyTab = Tab("Stem Word", StemWordTab, DataSourceName)
                    dummyTab.setStemWords(word)
                    myFile.TabList.append(dummyTab)

                    # Adding Stem Word Tab to QTabWidget
                    self.tabWidget.addTab(StemWordTab, "Stem Word")
                    self.tabWidget.setCurrentWidget(StemWordTab)
                    myFile.requiredSaved = True

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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
        self.QDialogAddProperties(PartOfSpeechDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Part Of Speech Button Box
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
        DataSourcePOSTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Parts of Speech':
                if tabs.tabWidget != None:
                    DataSourcePOSTabFlag = True
                    break
                else:
                    DataSourcePOSTabFlag2 = True
                    break

        if not DataSourcePOSTabFlag:
            dummyQuery = Query()
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Part of Speech")
                    dummyProgressInfo.PartOfSpeech(DS)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Part of Speech Table")

                    del dummyProgressInfo

                    POSGraph, rowList, noun_count, verb_count, adj_count = ThreadQueue.get()
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

            # 2nd LayoutWidget For within Part Of Speech Tab
            POSTabVerticalLayoutWidget2 = QWidget(POSTab)
            POSTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                    self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Part Of Speech Tab
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

                POSTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                POSTable.resizeColumnsToContents()
                POSTable.resizeRowsToContents()

                POSTable.setSortingEnabled(True)
                POSTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                row_width = 0

                for i in range(POSTable.columnCount()):
                    POSTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            # Label for POSGraph Image
            POSGraphLabel = QLabel(POSTabVerticalLayoutWidget2)

            # Resizing label to Layout
            POSGraphLabel.resize(POSTabVerticalLayoutWidget2.width(), POSTabVerticalLayoutWidget2.height())


            # Settinh Scaled Converted Pixmap Image on Label
            POSGraphLabel.setPixmap(POSGraph.toqpixmap().scaled(POSTabVerticalLayoutWidget2.width(),
                                                                POSTabVerticalLayoutWidget2.height(),
                                                                Qt.KeepAspectRatio))
            POSGraphLabel.setGeometry((POSTabVerticalLayoutWidget2.width() - POSGraphLabel.pixmap().width()) / 2,
                                      (POSTabVerticalLayoutWidget2.height() - POSGraphLabel.pixmap().height()) / 2,
                                      POSGraphLabel.pixmap().width(), POSGraphLabel.pixmap().height())
            POSGraphLabel.hide()

            POSComboBox.currentTextChanged.connect(lambda: self.togglePOSView(POSTable, POSGraphLabel))

            if DataSourcePOSTabFlag2:
                tabs.tabWidget = POSTab
                if tabs.isActive:
                    self.tabWidget.addTab(POSTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(POSTab)
            else:
                # Adding Part of Speech Tab to QTabWidget
                myFile.TabList.append(Tab("Parts of Speech", POSTab, DataSourceName))
                # Adding Part of Speech Tab to QTabWidget
                self.tabWidget.addTab(POSTab, "Parts of Speech")
                self.tabWidget.setCurrentWidget(POSTab)
                myFile.requiredSaved = True

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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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

        self.QDialogAddProperties(EntityRelationShipDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Entity RelationShip Button Box
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
        DataSourceERTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Entity Relationship':
                if tabs.tabWidget != None:
                    DataSourceERTabFlag = True
                    break
                else:
                    DataSourceERTabFlag2 = True
                    break

        if not DataSourceERTabFlag:

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Entity Relationship")
                    dummyProgressInfo.EntityRelationShip(DS)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Entity Relationship ")

                    del dummyProgressInfo

                    Entity_List, EntityHTML, DependencyHTML = ThreadQueue.get()
                    break

            # Creating New Tab for Entity Relationship
            DSERTab = QWidget()

            # LayoutWidget For within Entity Relationship Tab
            DSERTabVerticalLayoutWidget = QWidget(DSERTab)
            DSERTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

            # Box Layout for Entity RelationShip Tab
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

            # 2nd Box Layout for Entity RelationShip Tab
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

                DSERTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
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

            if DataSourceERTabFlag2:
                tabs.tabWidget = DSERTab
                if tabs.isActive:
                    self.tabWidget.addTab(DSERTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DSERTab)
            else:
                # Adding Entity Relationship Tab to QTabWidget
                myFile.TabList.append(Tab("Entity Relationship", DSERTab, DataSourceName))
                # Adding Entity Relationship Tab to QTabWidget
                self.tabWidget.addTab(DSERTab, "Entity Relationship")
                self.tabWidget.setCurrentWidget(DSERTab)
                myFile.requiredSaved = True

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
        else:
            # Adding Entity Relationship Tab to QTabWidget
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
        TopicModellingDialog.setWindowTitle("Topic Modelling")
        TopicModellingDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                             self.height / 10)
        TopicModellingDialog.setParent(self)

        self.QDialogAddProperties(TopicModellingDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Topic Modelling Button Box
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
        DataSourceTotalModellingTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Topic Modelling':
                if tabs.tabWidget != None:
                    DataSourceTotalModellingTabFlag = True
                    break
                else:
                    DataSourceTotalModellingTabFlag = True
                    break

        if not DataSourceTotalModellingTabFlag:
            TopicModellingTab = QWidget()
            TopicModellingTab.setGeometry(QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(), self.horizontalLayoutWidget.height()))
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
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Topic Modelling")
                    dummyProgressInfo.PartOfSpeech(DS)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Topic")

                    del dummyProgressInfo

                    TopicModellingHTML = ThreadQueue.get()
                    break

            # Topic Modelling HTML Viewer
            TopicModellingHTMLWeb = QWebEngineView()
            TopicModellingTabVerticalLayout2.addWidget(TopicModellingHTMLWeb)
            TopicModellingHTMLWeb.setHtml(TopicModellingHTML)

            if DataSourceTotalModellingTabFlag2:
                tabs.tabWidget = TopicModellingTab
                if tabs.isActive:
                    self.tabWidget.addTab(TopicModellingTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(TopicModellingTab)
            else:
                # Adding Topic Modelling Tab to TabList
                myFile.TabList.append(Tab("Topic Modelling", TopicModellingTab, DataSourceName))
                # Adding Topic Modelling Tab to QTabWidget
                self.tabWidget.addTab(TopicModellingTab, "Topic Modelling")
                self.tabWidget.setCurrentWidget(TopicModellingTab)
                myFile.requiredSaved = True

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

        else:
            # Adding Topic Modelling Tab to QTabWidget
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # ****************************************************************************
    # ************************ Data Sources Create Cases *************************
    # ****************************************************************************

    # Data Source Create Cases
    def DataSourceCreateCases(self, DataSourceWidgetItemName):
        DataSourceCreateCasesTabFlag = False
        DataSourceCreateCasesTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == 'Create Cases':
                if tabs.tabWidget != None:
                    DataSourceCreateCasesTabFlag = True
                    break
                else:
                    DataSourceCreateCasesTabFlag2 = True
                    break

        if not DataSourceCreateCasesTabFlag:
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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    CreateCasesPreview.setText(DS.DataSourcetext)
                    break

            if DataSourceCreateCasesTabFlag2:
                tabs.tabWidget = DataSourceCreateCasesTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourceCreateCasesTab, "Create Cases")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceCreateCasesTab)
            else:
                # Adding Word Cloud Tab to QTabWidget
                myFile.TabList.append(Tab("Create Cases", DataSourceCreateCasesTab, DataSourceWidgetItemName.text(0)))
                self.tabWidget.addTab(DataSourceCreateCasesTab, "Create Cases")
                self.tabWidget.setCurrentWidget(DataSourceCreateCasesTab)
                myFile.requiredSaved = True
        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
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
        self.QDialogAddProperties(CreateCaseDialogBox)

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
        if CaseTopic != DataSourceWidgetItemName.text(0):
            CasesNameConflict = False

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    break

            for cases in DS.CasesList:
                if cases.CaseTopic == CaseTopic:
                    CasesNameConflict = True
                    break

            if not CasesNameConflict:
                DS.CreateCase(CaseTopic, selectedText)
                if (len(DS.CasesList) == 1):
                    DSCaseWidget = QTreeWidgetItem(self.CasesTreeWidget)
                    DSCaseWidget.setText(0, DS.DataSourceName)
                    DSCaseWidget.setExpanded(True)

                ItemsWidget = self.CasesTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly, 0)

                for widgets in ItemsWidget:
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, CaseTopic)
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                self.statusBar().showMessage('New Case Added')
                self.CasesParentCoverageUpdate(DSNewCaseNode.parent())
                self.CasesStructureUpdate(DSNewCaseNode.parent())
            else:
                QMessageBox.information(self, "Creation Error",
                                        "A Case with that Topic is already created",
                                        QMessageBox.Ok)
        else:
            QMessageBox.critical(self, "Case Name Error",
                                "Case cannot have the same Name as its Data Source",
                                 QMessageBox.Ok)

    # Add to Case onClick
    def AddtoCaseDialog(self, selectedText, DataSourceWidgetItemName):
        AddtoCaseDialogBox = QDialog()
        AddtoCaseDialogBox.setModal(True)
        AddtoCaseDialogBox.setWindowTitle("Add to Case")
        AddtoCaseDialogBox.setParent(self)
        AddtoCaseDialogBox.setWindowFlags(Qt.WindowCloseButtonHint)
        AddtoCaseDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width * 0.3,
                                       self.height / 10)
        self.QDialogAddProperties(AddtoCaseDialogBox)

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
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                for cases in DS.CasesList:
                    if not cases.MergedCase:
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
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                for cases in DS.CasesList:
                    if cases.CaseTopic == CaseTopic:
                        cases.addtoCase(selectedText)

                        # Updating Cases Parent Coverage
                        ItemsWidget = self.CasesTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly,0)
                        for widgets in ItemsWidget:
                            self.statusBar().showMessage('Component Added to Case')
                            self.CasesParentCoverageUpdate(widgets)
                            self.CasesStructureUpdate(widgets)

                        # Updating Show Component Table
                        for childCount in range(widgets.childCount()):
                            ItemsWidget2 = widgets.child(childCount)

                            if ItemsWidget2.text(0) == CaseTopic:
                                self.CasesShowTopicComponentUpdate(ItemsWidget2)
                                break

                        break

    # ****************************************************************************
    # ********************* Data Sources Create Sentiments ***********************
    # ****************************************************************************

    # Data Source Create Sentiments
    def DataSourceCreateSentiments(self, DataSourceWidgetItemName):
        DataSourceCreateSentimentsTabFlag = False
        DataSourceCreateSentimentsTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceWidgetItemName.text(0) and tabs.TabName == "Create Sentiments":
                if tabs.tabWidget != None:
                    DataSourceCreateSentimentsTabFlag = True
                    break
                else:
                    DataSourceCreateSentimentsTabFlag2 = True
                    break

        if not DataSourceCreateSentimentsTabFlag:
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
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                    CreateSentimentsPreview.setText(DS.DataSourcetext)
                    break

            if DataSourceCreateSentimentsTabFlag2:
                tabs.tabWidget = DataSourceCreateSentimentsTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourceCreateSentimentsTab, "Create Sentiments")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceCreateSentimentsTab)
            else:
                # Adding Word Cloud Tab to QTabWidget
                myFile.TabList.append(Tab("Create Sentiments", DataSourceCreateSentimentsTab, DataSourceWidgetItemName.text(0)))
                self.tabWidget.addTab(DataSourceCreateSentimentsTab, "Create Sentiments")
                self.tabWidget.setCurrentWidget(DataSourceCreateSentimentsTab)
        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
        self.QDialogAddProperties(AddtoSentimentsDialogBox)

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
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
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
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                for sentiments in DS.SentimentList:
                    if len(sentiments.SentimentTextList) == 0:
                        NewWidgetAddFlagList.append(True)
                    else:
                        NewWidgetAddFlagList.append(False)

        ItemsWidget = self.SentimentTreeWidget.findItems(DataSourceWidgetItemName.text(0), Qt.MatchExactly, 0)

        if all([ v for v in NewWidgetAddFlagList]) and len(ItemsWidget) == 0:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceWidgetItemName.text(0):
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
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
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
        self.QDialogAddProperties(SummarizeDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
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
        DataSourceSummaryPreviewTabFlag2 = False
        DataSourceSummaryPreviewTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Summary':
                if tabs.tabWidget != None:
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == DataSourceName:
                            if tabs.SummarizeLengthText == len(DS.DataSourceTextSummary.split()):
                                DataSourceSummaryPreviewTabFlag = True
                                break
                            else:
                                DataSourceSummaryPreviewTabFlag2 = True
                                break
                else:
                    DataSourceSummaryPreviewTabFlag3 = True
                    break

        if not DataSourceSummaryPreviewTabFlag or DataSourceSummaryPreviewTabFlag2:
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

            if DataSourceSummaryPreviewTabFlag3:
                tabs.tabWidget = DataSourceSummaryPreviewTab
                if tabs.isActive:
                    # Adding Preview Tab to QTabWidget
                    self.tabWidget.addTab(DataSourceSummaryPreviewTab, "Summary")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceSummaryPreviewTab)

            else:
                if DataSourceSummaryPreviewTabFlag2:
                    tabs.setSummarizeTextLength(len(DataSourceSummaryPreview.toPlainText().split()))
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(DataSourceSummaryPreviewTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(DataSourceSummaryPreviewTab)
                    tabs.tabWidget = DataSourceSummaryPreviewTab
                    tabs.setisActive(True)
                else:
                    # Adding Preview Tab to TabList
                    dummyTab = Tab("Summary", DataSourceSummaryPreviewTab, DataSourceName)
                    dummyTab.setSummarizeTextLength(len(DataSourceSummaryPreview.toPlainText().split()))
                    myFile.TabList.append(dummyTab)

                    # Adding Preview Tab to QTabWidget
                    self.tabWidget.addTab(DataSourceSummaryPreviewTab, "Summary")
                    self.tabWidget.setCurrentWidget(DataSourceSummaryPreviewTab)
                    myFile.requiredSaved = True

            # Adding Summary Preview Query
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
                    SummaryWidget = self.QueryTreeWidget.findItems("Summary", Qt.MatchRecursive, 0)

                    SummaryFlag = False

                    if len(SummaryWidget) > 0:
                        for SWidgets in SummaryWidget:
                            if SWidgets.parent().text(0) == DataSourceName:
                                SummaryFlag = True
                                break

                    if not SummaryFlag:
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Summary')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

        else:
            # updating tab
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

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
        self.QDialogAddProperties(DataSourceTranslateDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
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
                if DS.TranslationError:
                    QMessageBox.critical(self, "Translation Error",
                                         "An Error occurred. The language is undetectable", QMessageBox.Ok)
                elif DS.isTranslated:
                    QMessageBox.information(self, "Translation Success",
                                            DS.DataSourceName + " is Translated Successfully!", QMessageBox.Ok)


        if not DS.TranslationError:
            DataSourceShowTranslationTabFlag = False
            DataSourceShowTranslationTabFlag2 = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Translated Text':
                    if tabs.tabWidget != None:
                        DataSourceShowTranslationTabFlag = True
                        break
                    else:
                        DataSourceShowTranslationTabFlag2 = True
                        break

            if not DataSourceShowTranslationTabFlag:
                DataSourceShowTranslationTab = QWidget()
                DataSourceShowTranslationTab.setGeometry(QRect(self.verticalLayoutWidget.width(), 0, self.width - self.verticalLayoutWidget.width(), self.horizontalLayoutWidget.height()))
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

                if DataSourceShowTranslationTabFlag2:
                    tabs.tabWidget = DataSourceShowTranslationTab
                    if tabs.isActive:
                        self.tabWidget.addTab(DataSourceShowTranslationTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(DataSourceShowTranslationTab)
                else:
                    # Adding Translation Tab to TabList
                    dummyTab = Tab("Translated Text", DataSourceShowTranslationTab, DataSourceName)
                    dummyTab.setTranslateLanguage(TranslateTo)
                    myFile.TabList.append(dummyTab)
                    # Adding Translation Tab to QTabWidget
                    self.tabWidget.addTab(DataSourceShowTranslationTab, "Translated Text")
                    self.tabWidget.setCurrentWidget(DataSourceShowTranslationTab)
                    myFile.requiredSaved = True

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

            else:
                self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                self.tabWidget.setCurrentWidget(tabs.TabName)
                tabs.setisActive(True)
                myFile.requiredSaved = True

    # ****************************************************************************
    # *************************** Data Source Remove *****************************
    # ****************************************************************************

    #Data Source Remove Dialog
    def DataSourceRemoveDialog(self, DataSourceWidgetItemName):
        DataSourceRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this file? Doing this will remove all task related to " + DataSourceWidgetItemName.text(0),
                                                      QMessageBox.Yes | QMessageBox.No)

        if DataSourceRemoveChoice == QMessageBox.Yes:
            self.DataSourceRemove(DataSourceWidgetItemName)
        else:
            pass

    # Data Source Remove
    def DataSourceRemove(self, DataSourceWidgetItemName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                if DataSourceWidgetItemName.parent().childCount() == 1:
                    DataSourceWidgetItemName.parent().setHidden(True)

                DataSourceWidgetItemName.parent().setText(0, DataSourceWidgetItemName.parent().text(0).replace(
                    ''.join(x for x in DataSourceWidgetItemName.parent().text(0) if x.isdigit()),
                    str(DataSourceWidgetItemName.parent().childCount() - 1)
                ))

                DataSourceWidgetItemName.parent().removeChild(DataSourceWidgetItemName)

                # Removing Queries
                for QueryTreeItems in self.QueryTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0):
                    self.QueryParentRemove(QueryTreeItems)

                # Removing Cases
                for CasesTreeItems in self.CasesTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0):
                    self.CasesParentRemove(CasesTreeItems)

                # Removing sentiments
                for SentimentTreeItems in self.SentimentTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0):
                    self.SentimentsRemove(SentimentTreeItems)

                # Removing Visualization
                for VisualTreeItems in self.VisualizationTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0):
                    self.VisualizationParentRemove(VisualTreeItems)

                # Removing all tabs related to Data Source
                for tabs in myFile.TabList:
                    if DS.DataSourceName == tabs.DataSourceName:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))

                myFile.TabList = [tabs for tabs in myFile.TabList if not tabs.DataSourceName == DS.DataSourceName]

                myFile.DataSourceList.remove(DS)
                del DS
                break

        self.DataSourceSimilarityUpdate()
        self.DataSourceDocumentClusteringUpdate()
        myFile.requiredSaved = True

    # ****************************************************************************
    # ************************* Data Source Child Detail *************************
    # ****************************************************************************

    # Data Source Child Detail
    def DataSourceChildDetail(self, DataSourceWidgetItemName):
        DataSourceWidgetDetailDialogBox = QDialog()
        DataSourceWidgetDetailDialogBox.setModal(True)
        DataSourceWidgetDetailDialogBox.setWindowTitle("Details")
        DataSourceWidgetDetailDialogBox.setParent(self)
        self.QDialogAddProperties(DataSourceWidgetDetailDialogBox)

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceWidgetItemName.text(0):
                break

        if DS.DataSourceext == "Doc files (*.doc *.docx)" or DS.DataSourceext == "Pdf files (*.pdf)" or DS.DataSourceext == "Notepad files (*.txt)" or DS.DataSourceext == "Rich Text Format files (*.rtf)" or DS.DataSourceext == "Audio files (*.wav *.mp3)":
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width/3,
                                                        self.height*2/5)

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
            DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext.split())))
            DataSourceWordCountLineEdit.setReadOnly(True)
            DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                    DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                    DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                    DataSourceWidgetDetailDialogBox.height() / 20)
            DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)

            DataSourceWidgetDetailDialogBox.exec_()

        elif DS.DataSourceext == "CSV files (*.csv)":
            if DS.CSVPathFlag:
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width/3,
                                                            self.height*2/5)

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
                DataSourceRowsCount = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceRowsCount.setText("Total Rows:")
                DataSourceRowsCount.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                DataSourceWidgetDetailDialogBox.width() / 4,
                                                DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceRowsCount.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceRowsCount)

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
                DataSourceRowCountLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceRowCountLineEdit.setText(str(len(DS.CSVData.index)))
                DataSourceRowCountLineEdit.setReadOnly(True)
                DataSourceRowCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                       DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                       DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                       DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceRowCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceRowCountLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()

            else:
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)

                # Data Source Label
                DataSourceLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceLabel.setText("Name:")
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
                DataSourceRowCountLabel = QLabel(DataSourceWidgetDetailDialogBox)
                DataSourceRowCountLabel.setText("Total Rows:")
                DataSourceRowCountLabel.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.1,
                                                    DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                    DataSourceWidgetDetailDialogBox.width() / 4,
                                                    DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceRowCountLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LabelSizeAdjustment(DataSourceRowCountLabel)

                # ************************************** LineEdit *************************************

                # Data Source Name LineEdit
                DataSourceLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceLineEdit.setText(DS.DataSourceName)
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
                DataSourceRowCountLineEdit = QLineEdit(DataSourceWidgetDetailDialogBox)
                DataSourceRowCountLineEdit.setText(str(len(DS.CSVData.index)))
                DataSourceRowCountLineEdit.setReadOnly(True)
                DataSourceRowCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                       DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                       DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                       DataSourceWidgetDetailDialogBox.height() / 10)
                DataSourceRowCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceRowCountLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()

        elif DS.DataSourceext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":
            if len(DS.DataSourceImage) == 1:
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width / 3,
                                                            self.height * 2 / 5)

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
                DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext.split())))
                DataSourceWordCountLineEdit.setReadOnly(True)
                DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                        DataSourceWidgetDetailDialogBox.height() * 0.8,
                                                        DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                        DataSourceWidgetDetailDialogBox.height() / 20)
                DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)

                DataSourceWidgetDetailDialogBox.exec_()

            else:
                DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                            self.height / 5)

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
                DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext.split())))
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
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                        self.height / 5)

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
            DataSourceWordCountLineEdit.setText(str(len(DS.DataSourcetext.split())))
            DataSourceWordCountLineEdit.setReadOnly(True)
            DataSourceWordCountLineEdit.setGeometry(DataSourceWidgetDetailDialogBox.width() * 0.35,
                                                    DataSourceWidgetDetailDialogBox.height() * 0.6,
                                                    DataSourceWidgetDetailDialogBox.width() * 0.6,
                                                    DataSourceWidgetDetailDialogBox.height() / 10)
            DataSourceWordCountLineEdit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LineEditSizeAdjustment(DataSourceWordCountLineEdit)

            DataSourceWidgetDetailDialogBox.exec_()

        elif DS.DataSourceext == "Tweet":
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                        self.height / 5)

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
            DataSourceWidgetDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                                        self.height / 5)

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

        DataSourceShowImagesDetailsBox.setGeometry(self.width * 0.35, self.height * 0.3, self.width / 3,
                                                    self.height * 2 / 5)
        self.QDialogAddProperties(DataSourceShowImagesDetailsBox)

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
    # ************************ Data Sources Word Cloud ***************************
    # ****************************************************************************

    # Data Source Create World Cloud
    def DataSourceCreateCloud(self):
        CreateWordCloudDialog = QDialog()
        CreateWordCloudDialog.setWindowTitle("Create Word Cloud")
        CreateWordCloudDialog.setGeometry(self.width * 0.35, self.height*0.35, self.width/3, self.height/3)
        CreateWordCloudDialog.setParent(self)
        CreateWordCloudDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.QDialogAddProperties(CreateWordCloudDialog)

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
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
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

    # map WordCloud on Tab
    def mapWordCloudonTab(self, WCDSName, WCBGColor, maxword, maskname):
        DataSourceWordCloudTabFlag = False
        DataSourceWordCloudTabFlag2 = False
        DataSourceWordCloudTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == WCDSName and tabs.TabName == 'Word Cloud':
                if tabs.tabWidget != None:
                    if tabs.WordCloudBGColor == WCBGColor and tabs.WordCloudMaxWords == maxword and tabs.WordCloudMask == maskname:
                        DataSourceWordCloudTabFlag = True
                        break
                    else:
                        DataSourceWordCloudTabFlag2 = True
                        break
                else:
                    DataSourceWordCloudTabFlag3 = True
                    break

        if not DataSourceWordCloudTabFlag or DataSourceWordCloudTabFlag2:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == WCDSName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(WCDSName, "Word Cloud")
                    dummyProgressInfo.CreateWordCloud(DS.DataSourcetext, WCBGColor, maxword, maskname)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Word Cloud")

                    del dummyProgressInfo

                    WordCloudImage = ThreadQueue.get()
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

            # Setting Scaled Converted Word Cloud Pixamp image on Word Cloud label
            WordCloudLabel.setPixmap(WordCloudImage.toqpixmap().scaled(WordCloudTabverticalLayoutWidget.width(),
                                                                       WordCloudTabverticalLayoutWidget.height(),
                                                                       Qt.KeepAspectRatio))
            WordCloudLabel.setGeometry((WordCloudTabverticalLayoutWidget.width() - WordCloudLabel.pixmap().width()) / 2,
                                       (WordCloudTabverticalLayoutWidget.height() - WordCloudLabel.pixmap().height()) / 2,
                                       WordCloudLabel.pixmap().width(), WordCloudLabel.pixmap().height())

            # Setting ContextMenu Policies on Label
            WordCloudLabel.setContextMenuPolicy(Qt.CustomContextMenu)
            WordCloudLabel.customContextMenuRequested.connect(lambda index=QContextMenuEvent: self.WordCloudContextMenu(index,
                                                                                                                        WordCloudLabel.pixmap(),
                                                                                                                        WordCloudLabel))
            if DataSourceWordCloudTabFlag3:
                tabs.tabWidget = WordCloudTab
                if tabs.isActive:
                    self.tabWidget.addTab(WordCloudTab, "Word Cloud")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(WordCloudTab)
            else:
                if DataSourceWordCloudTabFlag2:
                    tabs.setWordCloud(WCBGColor, maxword, maskname)
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(WordCloudTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(WordCloudTab)
                    tabs.tabWidget = WordCloudTab
                    tabs.setisActive(True)

                else:
                    # Adding Word Cloud Tab to QTabWidget
                    dummyTab = Tab("Word Cloud", WordCloudTab, WCDSName)
                    dummyTab.setWordCloud(WCBGColor, maxword, maskname)
                    myFile.TabList.append(dummyTab)

                    # Adding Preview Tab to QTabWidget
                    self.tabWidget.addTab(WordCloudTab, "Word Cloud")
                    self.tabWidget.setCurrentWidget(WordCloudTab)
                    myFile.requiredSaved = True

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
                    WordCloudWidget = self.VisualizationTreeWidget.findItems("Word Cloud", Qt.MatchRecursive, 0)

                    WordCloudWidgetFlag = False

                    if len(WordCloudWidget) > 0:
                        for WCWidgets in WordCloudWidget:
                            if WCWidgets.parent().text(0) == WCDSName:
                                WordCloudWidgetFlag = True
                                break

                    if not WordCloudWidgetFlag:
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Word Cloud')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Word Cloud ContextMenu
    def WordCloudContextMenu(self, WordCloudClickEvent, dummypixmap, WordCloudLabel):
        WordCloudClickMenu = QMenu()

        WordCloudImageDownload = QAction('Download Image')
        WordCloudImageDownload.triggered.connect(lambda: self.WordCloudDownload(dummypixmap))
        WordCloudClickMenu.addAction(WordCloudImageDownload)

        WordCloudClickMenu.exec(WordCloudClickEvent)

    # WordCloud Download
    def WordCloudDownload(self, dummypixmap):
        dummyWindow = OpenWindow("Save Word Cloud", ".png", 1)
        path = dummyWindow.filepath

        if all(path):
            dummypixmap.save(path[0] + ".png", "PNG")

    # ****************************************************************************
    # ************************* Data Sources Tree Word ***************************
    # ****************************************************************************

    # Data Source Word Tree Dialog
    def DataSourceWordTreeDialog(self):
        DataSourceWordTreeDialog = QDialog()
        DataSourceWordTreeDialog.setWindowTitle("Word Tree")
        DataSourceWordTreeDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                  self.height / 10)
        DataSourceWordTreeDialog.setParent(self)
        self.QDialogAddProperties(DataSourceWordTreeDialog)

        # Data Source Label
        DataSourcelabel = QLabel(DataSourceWordTreeDialog)
        DataSourcelabel.setGeometry(DataSourceWordTreeDialog.width() * 0.125,
                                    DataSourceWordTreeDialog.height() * 0.2,
                                    DataSourceWordTreeDialog.width() / 4,
                                    DataSourceWordTreeDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourceWordTreeDialog)
        DSComboBox.setGeometry(DataSourceWordTreeDialog.width() * 0.4,
                               DataSourceWordTreeDialog.height() * 0.2,
                               DataSourceWordTreeDialog.width() / 2,
                               DataSourceWordTreeDialog.height() / 10)

        for DS in myFile.DataSourceList:
            if not DS.DataSourceext == "Tweet" and not DS.DataSourceext == "Youtube" and not DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Word Tree Button Box
        DataSourceWordTreebuttonBox = QDialogButtonBox(DataSourceWordTreeDialog)
        DataSourceWordTreebuttonBox.setGeometry(DataSourceWordTreeDialog.width() * 0.125,
                                                      DataSourceWordTreeDialog.height() * 0.7,
                                                      DataSourceWordTreeDialog.width() * 3 / 4,
                                                      DataSourceWordTreeDialog.height() / 5)
        DataSourceWordTreebuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourceWordTreebuttonBox.button(QDialogButtonBox.Ok).setText('Show')

        if DSComboBox.count() == 0:
            DataSourceWordTreebuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(DataSourceWordTreebuttonBox)

        DataSourceWordTreebuttonBox.accepted.connect(DataSourceWordTreeDialog.accept)
        DataSourceWordTreebuttonBox.rejected.connect(DataSourceWordTreeDialog.reject)

        DataSourceWordTreebuttonBox.accepted.connect(
            lambda: self.DataSourceWordTree(DSComboBox.currentText()))

        DataSourceWordTreeDialog.exec()

    # Data Source Word Tree
    def DataSourceWordTree(self, DataSourceName):
        DataSourceWordTreeTabFlag = False
        DataSourceWordTreeTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Word Tree':
                if tabs.tabWidget != None:
                    DataSourceWordTreeTabFlag = True
                    break
                else:
                    DataSourceWordTreeTabFlag2 = True
                    break

        if not DataSourceWordTreeTabFlag:

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DataSourceName:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(DataSourceName, "Word Tree")
                    dummyProgressInfo.CreateWordTree(self.tabWidget.width(), self.tabWidget.height(), DS)

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Generating Word Tree")

                    del dummyProgressInfo

                    WordTreeHTML = ThreadQueue.get()
                    break

            # Creating New Tab for Word Tree
            DataSourceWordTreeTab = QWidget()

            # LayoutWidget For within Word Tree Tab
            DataSourceWordTreeTabVerticalLayoutWidget = QWidget(DataSourceWordTreeTab)
            DataSourceWordTreeTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height())

            # Box Layout for Word Tree Tab
            DataSourceWordTreeTabVerticalLayout = QHBoxLayout(DataSourceWordTreeTabVerticalLayoutWidget)
            DataSourceWordTreeTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            WordTreeWeb = QWebEngineView()
            WordTreeWeb.setContextMenuPolicy(Qt.PreventContextMenu)
            DataSourceWordTreeTabVerticalLayout.addWidget(WordTreeWeb)
            WordTreeWeb.setHtml(WordTreeHTML)

            if DataSourceWordTreeTabFlag2:
                tabs.tabWidget = DataSourceWordTreeTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourceWordTreeTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceWordTreeTab)
            else:
                # Adding Word Tree Tab to QTabWidget
                myFile.TabList.append(Tab("Word Tree", DataSourceWordTreeTab, DataSourceName))
                # Adding Word Tree Tab to QTabWidget
                self.tabWidget.addTab(DataSourceWordTreeTab, "Word Tree")
                self.tabWidget.setCurrentWidget(DataSourceWordTreeTab)
                myFile.requiredSaved = True

            ItemsWidget = self.VisualizationTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:  # if no Parent Widget
                # Adding Parent Query
                DSQueryWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                DSQueryWidget.setText(0, DataSourceName)
                DSQueryWidget.setToolTip(0, DSQueryWidget.text(0))
                DSQueryWidget.setExpanded(True)

                # Adding Word Tree Query
                DSNewCaseNode = QTreeWidgetItem(DSQueryWidget)
                DSNewCaseNode.setText(0, 'Word Tree')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    # Adding Word Tree Query
                    DSNewCaseNode = QTreeWidgetItem(widgets)
                    DSNewCaseNode.setText(0, 'Word Tree')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # ****************************************************************************
    # ********************** Data Sources Survey Analysis ************************
    # ****************************************************************************

    # Data Source Survey Analysis Dialog
    def DataSourceSurveyAnalysisDialog(self):
        self.ChartType = ["Bar Chart", "Donut Chart", "Pie Chart", "Time Series"]
        self.ChartListCount = 0

        # Data Source Survey Analysis Dialog

        DataSourceSurveyAnalysisDialog = QDialog()
        DataSourceSurveyAnalysisDialog.setWindowTitle("Survey Analysis")
        DataSourceSurveyAnalysisDialog.setGeometry(self.width * 0.3,
                                                   self.height * 0.2,
                                                   self.width * 0.4,
                                                   self.height * 0.6)
        DataSourceSurveyAnalysisDialog.setParent(self)
        self.QDialogAddProperties(DataSourceSurveyAnalysisDialog)

        # ************************* Survey Analysis First Layout *************************

        # LayoutWidget For within Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayoutWidget = QWidget(DataSourceSurveyAnalysisDialog)
        DataSourceSurveyAnalysisVerticalLayoutWidget.setGeometry(0, 0,
                                                                 DataSourceSurveyAnalysisDialog.width(),
                                                                 DataSourceSurveyAnalysisDialog.height()*0.2)

        # Box Layout for Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayout = QHBoxLayout(DataSourceSurveyAnalysisVerticalLayoutWidget)
        DataSourceSurveyAnalysisVerticalLayout.setContentsMargins(0, 0, 0, 0)

        # Data Source Label
        DataSourcelabel = QLabel(DataSourceSurveyAnalysisDialog)
        DataSourcelabel.setGeometry(DataSourceSurveyAnalysisVerticalLayoutWidget.width() * 0.125,
                                    DataSourceSurveyAnalysisVerticalLayoutWidget.height() * 0.2,
                                    DataSourceSurveyAnalysisVerticalLayoutWidget.width() / 4,
                                    DataSourceSurveyAnalysisVerticalLayoutWidget.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourceSurveyAnalysisVerticalLayoutWidget)
        DSComboBox.setGeometry(DataSourceSurveyAnalysisVerticalLayoutWidget.width() * 0.4,
                               DataSourceSurveyAnalysisVerticalLayoutWidget.height() * 0.2,
                               DataSourceSurveyAnalysisVerticalLayoutWidget.width() / 2,
                               DataSourceSurveyAnalysisVerticalLayoutWidget.height() / 10)
        for DS in myFile.DataSourceList:
            if DS.DataSourceext == "CSV files (*.csv)":
                DSComboBox.addItem(DS.DataSourceName)
        self.LineEditSizeAdjustment(DSComboBox)

        # ************************* Survey Analysis Second Layout *************************

        # LayoutWidget For within Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayoutWidget2 = QWidget(DataSourceSurveyAnalysisDialog)
        DataSourceSurveyAnalysisVerticalLayoutWidget2.setGeometry(0, DataSourceSurveyAnalysisDialog.height() * 0.2,
                                                                 DataSourceSurveyAnalysisDialog.width(),
                                                                 DataSourceSurveyAnalysisDialog.height() * 0.6)
        # Box Layout for Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayout2 = QHBoxLayout(DataSourceSurveyAnalysisVerticalLayoutWidget2)
        DataSourceSurveyAnalysisVerticalLayout2.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        DataSourceSurveyAnalysisScrollArea = QScrollArea(DataSourceSurveyAnalysisVerticalLayoutWidget2)
        DataSourceSurveyAnalysisScrollArea.setGeometry(DataSourceSurveyAnalysisVerticalLayoutWidget2.width() * 0.1,
                                                       0,
                                                       DataSourceSurveyAnalysisVerticalLayoutWidget2.width() * 0.8,
                                                       DataSourceSurveyAnalysisVerticalLayoutWidget2.height())

        DataSourceSurveyAnalysisScrollArea.setFixedWidth(DataSourceSurveyAnalysisVerticalLayoutWidget2.width() * 0.8)
        DataSourceSurveyAnalysisScrollArea.setFixedHeight(DataSourceSurveyAnalysisVerticalLayoutWidget2.height())

        DataSourceSurveyAnalysisScrollArea.setWidgetResizable(True)
        DataSourceSurveyAnalysisVerticalLayout2.addWidget(DataSourceSurveyAnalysisScrollArea)

        # # Scroll Area Widget
        DataSourceSurveyAnalysisScrollWidget = QWidget(DataSourceSurveyAnalysisVerticalLayoutWidget2)
        DataSourceSurveyAnalysisScrollWidget.setGeometry(DataSourceSurveyAnalysisScrollArea.width() * 0.1,
                                                         0,
                                                         DataSourceSurveyAnalysisScrollArea.width() * 0.8,
                                                         DataSourceSurveyAnalysisScrollArea.height())
        DataSourceSurveyAnalysisScrollArea.setWidget(DataSourceSurveyAnalysisScrollWidget)

        # Scroll Area Layout
        DataSourceSurveyAnalysisScrollLayout = QVBoxLayout(DataSourceSurveyAnalysisScrollWidget)
        DataSourceSurveyAnalysisScrollLayout.setContentsMargins(0, 0, 0, 0)


        # ************************* Survey Analysis Third Layout *************************

        # LayoutWidget For within Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayoutWidget3 = QWidget(DataSourceSurveyAnalysisDialog)
        DataSourceSurveyAnalysisVerticalLayoutWidget3.setGeometry(0, DataSourceSurveyAnalysisDialog.height() * 0.8,
                                                                  DataSourceSurveyAnalysisDialog.width(),
                                                                  DataSourceSurveyAnalysisDialog.height() * 0.1)
        # Box Layout for Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayout3 = QHBoxLayout(DataSourceSurveyAnalysisVerticalLayoutWidget3)
        DataSourceSurveyAnalysisVerticalLayout3.setContentsMargins(0, 0, 0, 0)

        AddChartButton = QPushButton(DataSourceSurveyAnalysisVerticalLayoutWidget3)
        AddChartButton.setGeometry(DataSourceSurveyAnalysisVerticalLayoutWidget3.width() * 0.75,
                                   DataSourceSurveyAnalysisVerticalLayoutWidget3.height() * 0.2,
                                   DataSourceSurveyAnalysisVerticalLayoutWidget3.width() * 0.2,
                                   DataSourceSurveyAnalysisVerticalLayoutWidget3.height() * 0.8)
        AddChartButton.setText("Add Chart")
        AddChartButton.setStyleSheet("Text-align:left");
        self.LabelSizeAdjustment(AddChartButton)

        AddChartButton.clicked.connect(lambda: self.DataSourceSurveyAnalysisAddChartButtonClicked(DSComboBox, DataSourceSurveyAnalysisScrollLayout, DataSourceSurveyAnalysisScrollWidget))

        if DSComboBox.count() == 0:
            AddChartButton.setDisabled(True)

        if self.ChartListCount < 6 and DSComboBox.count() > 0:
            self.DataSourceSurveyAnalysissetInitialState(DataSourceSurveyAnalysisScrollLayout, AddChartButton,
                                                         DataSourceSurveyAnalysisScrollWidget, DSComboBox)

        # ************************* Survey Analysis Fourth Layout *************************

        # LayoutWidget For within Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayoutWidget4 = QWidget(DataSourceSurveyAnalysisDialog)
        DataSourceSurveyAnalysisVerticalLayoutWidget4.setGeometry(0, DataSourceSurveyAnalysisDialog.height() * 0.9,
                                                                  DataSourceSurveyAnalysisDialog.width(),
                                                                  DataSourceSurveyAnalysisDialog.height() * 0.2)
        # Box Layout for Survey Analysis Tab
        DataSourceSurveyAnalysisVerticalLayout4 = QHBoxLayout(DataSourceSurveyAnalysisVerticalLayoutWidget4)
        DataSourceSurveyAnalysisVerticalLayout4.setContentsMargins(0, 0, 0, 0)

        # Survey Analysis Button Box
        DataSourceSurveyAnalysisbuttonBox = QDialogButtonBox(DataSourceSurveyAnalysisVerticalLayoutWidget4)
        DataSourceSurveyAnalysisbuttonBox.setGeometry(DataSourceSurveyAnalysisVerticalLayoutWidget4.width() * 0.5,
                                                      0,
                                                      DataSourceSurveyAnalysisVerticalLayoutWidget4.width() * 0.45,
                                                      DataSourceSurveyAnalysisVerticalLayoutWidget4.height())
        DataSourceSurveyAnalysisbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourceSurveyAnalysisbuttonBox.button(QDialogButtonBox.Ok).setText('Analyze')

        if DSComboBox.count() == 0:
            DataSourceSurveyAnalysisbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(DataSourceSurveyAnalysisbuttonBox)

        DSComboBox.currentTextChanged.connect(lambda: self.DataSourceSurveyAnalysisDSComboBoxTextChanged(DataSourceSurveyAnalysisScrollLayout, AddChartButton, DataSourceSurveyAnalysisScrollWidget, DSComboBox))

        DataSourceSurveyAnalysisbuttonBox.accepted.connect(DataSourceSurveyAnalysisDialog.accept)
        DataSourceSurveyAnalysisbuttonBox.rejected.connect(DataSourceSurveyAnalysisDialog.reject)

        DataSourceSurveyAnalysisbuttonBox.accepted.connect(
            lambda: self.DataSourceSurveyAnalysis(DSComboBox.currentText(), None, DataSourceSurveyAnalysisScrollLayout))

        DataSourceSurveyAnalysisDialog.exec()

    # Data Source Survey Analysis Data Source Combo Box Text Changed
    def DataSourceSurveyAnalysisDSComboBoxTextChanged(self, DataSourceSurveyAnalysisScrollLayout, AddChartButton, DataSourceSurveyAnalysisScrollWidget, DSComboBox):
        # Removing All Widgets
        while DataSourceSurveyAnalysisScrollLayout.count() > 0:
            WidgetItem = DataSourceSurveyAnalysisScrollLayout.takeAt(0)
            if not WidgetItem:
                continue

            widget = WidgetItem.widget()
            if widget:
                widget.deleteLater()

        # Restoring Counter and Button to Default
        self.ChartListCount = 0
        AddChartButton.setDisabled(False)

        self.DataSourceSurveyAnalysissetInitialState(DataSourceSurveyAnalysisScrollLayout, AddChartButton, DataSourceSurveyAnalysisScrollWidget, DSComboBox)

    # Data Source Survey Analysis set Initial State
    def DataSourceSurveyAnalysissetInitialState(self, DataSourceSurveyAnalysisScrollLayout, AddChartButton, DataSourceSurveyAnalysisScrollWidget, DSComboBox):
        ChartGroupBox = QGroupBox("Chart No. {}".format(self.ChartListCount + 1),
                                  DataSourceSurveyAnalysisScrollWidget)
        HorizontalBoxLayout = QHBoxLayout(ChartGroupBox)

        # ***********************************************
        # **************** Chart ComboBox ***************
        # ***********************************************

        # ComboBox Layout
        ChartComboBoxLayout = QVBoxLayout()

        # Chart Label
        ChartLabel = QLabel()
        ChartLabel.setText("Chart Type")
        self.LabelSizeAdjustment(ChartLabel)
        ChartComboBoxLayout.addWidget(ChartLabel)
        ChartComboBoxLayout.addStretch(1)

        # Chart ComboBox
        ChartTypeCombBox = QComboBox()
        for Chart in self.ChartType:
            ChartTypeCombBox.addItem(Chart)

        ChartComboBoxLayout.addWidget(ChartTypeCombBox)
        ChartComboBoxLayout.addStretch(2)

        HorizontalBoxLayout.addLayout(ChartComboBoxLayout)
        HorizontalBoxLayout.addStretch(1)

        # ***********************************************
        # ************ First Column ComboBox ************
        # ***********************************************

        # First Column ComboBox Layout
        FirstComboBoxLayout = QVBoxLayout()

        # Chart Label
        FirstLabel = QLabel()
        FirstLabel.setText("First Quantity")
        self.LabelSizeAdjustment(FirstLabel)
        FirstComboBoxLayout.addWidget(FirstLabel)
        FirstComboBoxLayout.addStretch(1)

        # First Column ComboBox
        FirstComboBox = QComboBox()
        self.LineEditSizeAdjustment(FirstComboBox)

        FirstComboBoxLayout.addWidget(FirstComboBox)
        FirstComboBoxLayout.addStretch(2)

        HorizontalBoxLayout.addLayout(FirstComboBoxLayout)
        HorizontalBoxLayout.addStretch(2)

        # ***********************************************
        # ************ Second Column ComboBox ***********
        # ***********************************************

        # Second Column ComboBox Layout
        SecondComboBoxLayout = QVBoxLayout()

        # Second Column Label
        SecondLabel = QLabel()
        SecondLabel.setText("Second Quantity")
        SecondLabel.hide()
        self.LabelSizeAdjustment(SecondLabel)
        SecondComboBoxLayout.addWidget(SecondLabel)
        SecondComboBoxLayout.addStretch(1)

        # Second Column ComboBox
        SecondComboBox = QComboBox()
        self.LineEditSizeAdjustment(SecondComboBox)

        SecondComboBoxLayout.addWidget(SecondComboBox)
        SecondComboBoxLayout.addStretch(2)

        HorizontalBoxLayout.addLayout(SecondComboBoxLayout)
        HorizontalBoxLayout.addStretch(3)

        self.setItemsinComboBox(ChartTypeCombBox, DSComboBox, FirstComboBox, SecondComboBox, SecondLabel)
        ChartTypeCombBox.currentTextChanged.connect(
            lambda: self.DataSourceSurveyAnalysisChartComboBoxTextChanged(DSComboBox, FirstComboBox, SecondComboBox,
                                                                          SecondLabel))

        self.ChartListCount += 1

        DataSourceSurveyAnalysisScrollLayout.addWidget(ChartGroupBox)
        DataSourceSurveyAnalysisScrollLayout.addStretch(1)

    # Data Source Survey Analysis Chart Combo Box Text Changed
    def DataSourceSurveyAnalysisChartComboBoxTextChanged(self, DSComboBox, FirstComboBox, SecondComboBox, SecondLabel):
        ChartTypeCombBox = self.sender()

        # Clearing First ComboBox
        while FirstComboBox.count() > 0:
            FirstComboBox.removeItem(0)

        # Clearing Second ComboBox
        while SecondComboBox.count() > 0:
            SecondComboBox.removeItem(0)

        # Setting Items in ComboBox
        self.setItemsinComboBox(ChartTypeCombBox, DSComboBox, FirstComboBox, SecondComboBox, SecondLabel)

    # Data Source Survey Analysis Chart set Items in ComboBox
    def setItemsinComboBox(self, ChartTypeCombBox, DSComboBox, FirstComboBox, SecondComboBox, SecondLabel):
        # Data Source ComboBox
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DSComboBox.currentText():
                for HeaderLabel in DS.CSVHeaderLabel:
                    # Time Series
                    if ChartTypeCombBox.currentText() == "Time Series":
                        if DS.CSVHeader:
                            if not str(DS.CSVData.dtypes[HeaderLabel]) == "datetime64[ns, UTC]" and not str(
                                    DS.CSVData.dtypes[HeaderLabel]) == "datetime64[ns]":
                                FirstComboBox.addItem(HeaderLabel)
                        else:
                            if not str(DS.CSVData.iloc[:, DS.CSVHeaderLabel.index(
                                    HeaderLabel)].dtype) == "datetime64[ns, UTC]" and not str(
                                    DS.CSVData.iloc[:, DS.CSVHeaderLabel.index(HeaderLabel)].dtype) == "datetime64[ns]":
                                FirstComboBox.addItem(HeaderLabel)

                    # Bar Chart | Donut Chart |  Pie Chart | Word Cloud
                    elif ChartTypeCombBox.currentText() == "Bar Chart" or ChartTypeCombBox.currentText() == "Donut Chart" or ChartTypeCombBox.currentText() == "Pie Chart":
                        if DS.CSVHeader:
                            if str(DS.CSVData.dtypes[HeaderLabel]) == "object":
                                FirstComboBox.addItem(HeaderLabel)
                        else:
                            if str(DS.CSVData.iloc[:, DS.CSVHeaderLabel.index(HeaderLabel)].dtype) == "object":
                                FirstComboBox.addItem(HeaderLabel)


        if ChartTypeCombBox.currentText() == "Time Series":
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == DSComboBox.currentText():
                    for HeaderLabel in DS.CSVHeaderLabel:
                        # Time Series
                        if ChartTypeCombBox.currentText() == "Time Series":
                            if DS.CSVHeader:
                                if str(DS.CSVData.dtypes[HeaderLabel]) == "datetime64[ns, UTC]" or str(DS.CSVData.dtypes[HeaderLabel]) == "datetime64[ns]":
                                    SecondComboBox.addItem(HeaderLabel)
                            else:
                                if str(DS.CSVData.iloc[:, DS.CSVHeaderLabel.index(HeaderLabel)].dtype) == "datetime64[ns, UTC]" or str(DS.CSVData.iloc[:, DS.CSVHeaderLabel.index(HeaderLabel)].dtype) == "datetime64[ns]":
                                    SecondComboBox.addItem(HeaderLabel)

            SecondLabel.show()
            SecondComboBox.show()
        else:
            SecondLabel.hide()
            SecondComboBox.hide()

    # Data Source Survey Analysis Add Chart Button Clicked
    def DataSourceSurveyAnalysisAddChartButtonClicked(self, DSComboBox, DataSourceSurveyAnalysisScrollLayout, DataSourceSurveyAnalysisScrollWidget):
        if self.ChartListCount < 6 and DSComboBox.count() > 0:
            self.DataSourceSurveyAnalysissetInitialState(DataSourceSurveyAnalysisScrollLayout, self.sender(), DataSourceSurveyAnalysisScrollWidget, DSComboBox)

        if self.ChartListCount == 6:
            self.sender().setDisabled(True)

    # Validate Chart List
    def ValidateChartList(self, ChartList):
        ValidatedChartList = []

        for Chart in ChartList:
            if Chart[0] == "Time Series":
                if Chart[2] == '':
                    pass
                else:
                    ValidatedChartList.append(Chart)
            else:
                if Chart[1] == '':
                    pass
                else:
                    ValidatedChartList.append(Chart)

        #[ValidatedChartList.remove(i) for i in [ValidatedChartList[i] for i in [i for i, x in enumerate([i[0] for i in ValidatedChartList]) if x == "Word Cloud"]][1:]]

        return ValidatedChartList

    # Data Source Survey Analysis
    def DataSourceSurveyAnalysis(self, DataSourceName, ArgChartList, DataSourceSurveyAnalysisScrollLayout):
        if ArgChartList is None and DataSourceSurveyAnalysisScrollLayout is not None:
            # Collecting Data to create a ChartList
            ChartList = []
            GroupBoxItemsList = (DataSourceSurveyAnalysisScrollLayout.itemAt(i).widget() for i in range(DataSourceSurveyAnalysisScrollLayout.count()))

            for GroupBox in GroupBoxItemsList:
                if isinstance(GroupBox, QGroupBox):
                    Chart = []
                    for HBoxLayout in (GroupBox.findChildren(QHBoxLayout)):
                        for VBoxLayout in (HBoxLayout.findChildren(QVBoxLayout)):
                            if isinstance(VBoxLayout, QVBoxLayout):
                                ComboBoxlist = [VBoxLayout.itemAt(i).widget() for i in range(VBoxLayout.count())]
                                for ComboBox in ComboBoxlist:
                                    if isinstance(ComboBox, QComboBox):
                                        Chart.append(ComboBox.currentText())
                    ChartList.append(Chart)
        else:
            ChartList = ArgChartList

        CharListlength = len(ChartList)
        # Validate ChartList
        ChartList = self.ValidateChartList(ChartList)

        if len(ChartList) > 0 and len(ChartList) <=  CharListlength:
            # Data Source Survey Analysis
            DataSourceSurveyAnalysisTabFlag = False
            DataSourceSurveyAnalysisTabFlag2 = False
            DataSourceSurveyAnalysisTabFlag3 = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Survey Analysis':
                    if tabs.tabWidget != None:
                        if sorted(tabs.SurveyAnalysisChartList) == sorted(ChartList):
                            DataSourceSurveyAnalysisTabFlag = True
                            break

                        else:
                            DataSourceSurveyAnalysisTabFlag2 = True
                            break
                    else:
                        DataSourceSurveyAnalysisTabFlag3 = True
                        break

            if not DataSourceSurveyAnalysisTabFlag or DataSourceSurveyAnalysisTabFlag2:
                # Creating New Tab for Survey Analysis
                DataSourceSurveyAnalysisTab = QWidget()

                # **********************************************************************************************
                # ************************ Data Source Survey Analysis Setting Widget **************************
                # **********************************************************************************************

                # LayoutWidget For within Survey Analysis Tab
                DataSourceSurveyAnalysisTabverticalLayoutWidget = QWidget(DataSourceSurveyAnalysisTab)
                DataSourceSurveyAnalysisTabverticalLayoutWidget.setGeometry(self.tabWidget.width()*0.2,
                                                                            0,
                                                                            self.tabWidget.width()*0.6,
                                                                            self.tabWidget.height()/20)

                # Box Layout for Survey Analysis Tab
                DataSourceSurveyAnalysisTabverticalLayout = QHBoxLayout(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                DataSourceSurveyAnalysisTabverticalLayout.setContentsMargins(0, 0, 0, 0)

                # ********************* Theme *********************
                # Theme Label
                ThemeLabel = QLabel(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                ThemeLabel.setText("Theme:")
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(ThemeLabel)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(1)

                # Theme Combo Box
                ThemeComboBox = QComboBox(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(ThemeComboBox)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(2)

                # Adding Items to ComboBox
                ThemeComboBox.addItem("Light")
                ThemeComboBox.addItem("Blue Cerulean")
                ThemeComboBox.addItem("Blue Icy")
                ThemeComboBox.addItem("Blue Ncs")
                ThemeComboBox.addItem("Brown Sand")
                ThemeComboBox.addItem("High Contrast")
                ThemeComboBox.addItem("Theme Dark")

                # ******************* Animation *******************

                # Animation Label
                AnimationLabel = QLabel()
                AnimationLabel.setText("Animation:")
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(AnimationLabel)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(3)

                # Animation Combo Box
                AnimationComboBox = QComboBox(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(AnimationComboBox)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(4)

                # Adding Items to ComboBox
                AnimationComboBox.addItem("All Animations")
                AnimationComboBox.addItem("Series Animation")
                AnimationComboBox.addItem("Grid Axis Animation")
                AnimationComboBox.addItem("No Animation")

                # ********************* Legend ********************
                # Legend Label
                LegendLabel = QLabel(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                LegendLabel.setText("Legend:")
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(LegendLabel)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(5)


                # Legend ComboBox
                LegendComboBox = QComboBox(DataSourceSurveyAnalysisTabverticalLayoutWidget)
                DataSourceSurveyAnalysisTabverticalLayout.addWidget(LegendComboBox)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(6)

                # Adding Items to ComboBox
                LegendComboBox.addItem("Bottom")
                LegendComboBox.addItem("Top")
                LegendComboBox.addItem("Left")
                LegendComboBox.addItem("Right")
                LegendComboBox.addItem("Hide")

                self.LineEditSizeAdjustment(LegendComboBox)


                # Download Button
                DownloadDashboardButton = QPushButton('Download ')
                DownloadDashboardButton.setIcon(QIcon("Images/Download Button.png"))
                DownloadDashboardButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

                DownloadDashboardButtonFont = QFont("sans-serif")
                DownloadDashboardButtonFont.setPixelSize(14)
                DownloadDashboardButtonFont.setBold(True)
                DownloadDashboardButton.setFont(DownloadDashboardButtonFont)

                DataSourceSurveyAnalysisTabverticalLayout.addWidget(DownloadDashboardButton)
                DataSourceSurveyAnalysisTabverticalLayout.addStretch(8)

                self.LineEditSizeAdjustment(DownloadDashboardButton)

                # *********************************************************************************************
                # ************************ Data Source Survey Analysis Chart Widgets **************************
                # *********************************************************************************************

                chartWidget = []

                for Chart in ChartList:
                    # Bar Chart
                    if Chart[0] == "Bar Chart":
                        chartWidget.append(self.DataSourceSurveyAnalysisBarChart(Chart, DataSourceName))

                    # Donut Chart
                    elif Chart[0] == "Donut Chart":
                        chartWidget.append(self.DataSourceSurveyAnalysisDonutChart(Chart, DataSourceName))

                    # Pie Chart
                    elif Chart[0] == "Pie Chart":
                        chartWidget.append(self.DataSourceSurveyAnalysisPieChart(Chart, DataSourceName))

                    # Time Series
                    elif Chart[0] == "Time Series":
                        chartWidget.append(self.DataSourceSurveyAnalysisLineChart(Chart, DataSourceName))


                # Group Widget For within Survey Analysis Tab
                DashBoardWidget = QGroupBox(DataSourceSurveyAnalysisTab)
                DashBoardWidget.setGeometry(0, self.tabWidget.height() * 0.05, self.tabWidget.width(), self.tabWidget.height() * 0.95)


                # Box Layout for Survey Analysis Tab
                DashBoardWidgetLayout = QGridLayout(DashBoardWidget)
                DashBoardWidgetLayout.setContentsMargins(0, 0, 0, 0)

                colWid = 0
                if len(chartWidget) >= 5:
                    colWid = 3
                elif len(chartWidget) > 2  and len(chartWidget) < 5:
                    colWid = 2

                colcounter = 0
                rowcounter = 0

                for chartWid in chartWidget:
                    if colcounter < colWid:
                        pass
                    else:
                        colcounter = 0
                        rowcounter += 1

                    DashBoardWidgetLayout.addWidget(chartWid, rowcounter, colcounter)
                    colcounter += 1


                ThemeComboBox.currentTextChanged.connect(lambda: self.ThemeComboBoxTextChanged(chartWidget, DashBoardWidget.palette()))
                AnimationComboBox.currentTextChanged.connect(lambda: self.AnimationComboBoxTextChanged(chartWidget))
                LegendComboBox.currentTextChanged.connect(lambda: self.LegendComboBoxTextChanged(chartWidget))

                # Push Button Clicked
                DownloadDashboardButton.clicked.connect(lambda : self.DataSourceSurveyAnalysisDownloadDashboard(DashBoardWidget))

                # Tab Management
                if DataSourceSurveyAnalysisTabFlag3:
                    tabs.tabWidget = DataSourceSurveyAnalysisTab
                    if tabs.isActive:
                        self.tabWidget.addTab(DataSourceSurveyAnalysisTab, "Survey Analysis")
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(DataSourceSurveyAnalysisTab)
                else:
                    if DataSourceSurveyAnalysisTabFlag2:
                        tabs.setSurveryAnalysisChartList(ChartList)
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        self.tabWidget.addTab(DataSourceSurveyAnalysisTab, tabs.TabName)
                        self.tabWidget.setCurrentWidget(DataSourceSurveyAnalysisTab)
                        tabs.tabWidget = DataSourceSurveyAnalysisTab
                        tabs.setisActive(True)

                    else:
                        # Adding Survey Analysis Tab to QTabWidget
                        dummyTab = Tab("Survey Analysis", DataSourceSurveyAnalysisTab, DataSourceName)
                        dummyTab.setSurveryAnalysisChartList(ChartList)

                        myFile.TabList.append(dummyTab)

                        # Adding Preview Tab to QTabWidget
                        self.tabWidget.addTab(DataSourceSurveyAnalysisTab, "Survey Analysis")
                        self.tabWidget.setCurrentWidget(DataSourceSurveyAnalysisTab)
                        myFile.requiredSaved = True

                ItemsWidget = self.VisualizationTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

                if len(ItemsWidget) == 0:
                    DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                    DSVisualWidget.setText(0, DataSourceName)
                    DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                    DSVisualWidget.setExpanded(True)

                    DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                    DSNewCaseNode.setText(0, 'Survey Analysis')
                    DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

                else:
                    for widgets in ItemsWidget:
                        SurveyAnalysisWidget = self.VisualizationTreeWidget.findItems('Survey Analysis', Qt.MatchRecursive, 0)

                        SurveyAnalysisWidgetFlag = False

                        if len(SurveyAnalysisWidget) > 0:
                            for SAWidgets in SurveyAnalysisWidget:
                                if SAWidgets.parent().text(0) == DataSourceName:
                                    SurveyAnalysisWidgetFlag = True
                                    break

                        if not SurveyAnalysisWidgetFlag:
                            DSNewCaseNode = QTreeWidgetItem(widgets)
                            DSNewCaseNode.setText(0, 'Survey Analysis')
                            DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                self.tabWidget.setCurrentWidget(tabs.tabWidget)
                tabs.setisActive(True)
                myFile.requiredSaved = True

        else:
            QMessageBox.critical(self, "Survey Analysis Error",
                                 "There were some errors in selecting Chart Type!", QMessageBox.Ok)

    # Data Source Survey Analysis Line Chart
    def DataSourceSurveyAnalysisLineChart(self, Chart, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName and DS.DataSourceext == "CSV files (*.csv)":
                df = DS.CSVData
                break
            elif DS.DataSourceName == DataSourceName and DS.DataSourceext == "Tweet":
                df = DS.TweetDataFrame
                break

        # Creating a Line Chart
        chart = QChart()
        chart.setTitle(Chart[1])

        DateFlag = False
        TimeFlag = False

        # **************************************************
        # ***** Storing data from Pandas CSV to Series *****
        # **************************************************

        if DS.DataSourceext == "CSV files (*.csv)":
            # Column Type Integer
            if df.dtypes[Chart[1]] == 'float64' or df.dtypes[Chart[1]] == 'int64':

                # Line Series
                series = QLineSeries(self)
                series.setName("Date wise " + Chart[1])
                series.setPointsVisible(True)
                series.setPointLabelsClipping(True)
                series.setPointLabelsVisible(True)
                series.setPointLabelsFormat("@yPoint");

                data = df.groupby(Chart[2])[Chart[1]].sum().reset_index().values.tolist()

                # Creating Series
                for date, value in data:
                    xValue = QDateTime()
                    if not date.date() == datetime.date(1900, 1, 1):
                        DateFlag = True
                        xValue.setDate(QDate(date.date().year, date.date().month, date.date().day));

                    if not date.time() == datetime.time(0, 0):
                        TimeFlag = True
                        xValue.setTime(QTime(date.time().hour, date.time().minute, date.time().second));

                    series.append(xValue.toMSecsSinceEpoch(), value);

                chart.addSeries(series)

            # Column Type Object
            elif df.dtypes[Chart[1]] == 'object':
                LineSeriesList = df.groupby([Chart[1], Chart[2]]).size()

                GroupList = LineSeriesList.keys().tolist()

                UpdatedList = []

                for city, date in GroupList:
                    if any(city in sublist for sublist in UpdatedList):
                        for sublist in UpdatedList:
                            if sublist[0] == city:
                                sublist[1].append([date, LineSeriesList[GroupList.index((city, date))]])
                                break

                    else:
                        sublist = [city, []]
                        sublist[1].append([date, LineSeriesList[GroupList.index((city, date))]])
                        UpdatedList.append(sublist)

                # Creating Series
                for labelX, data in UpdatedList:
                    series = QLineSeries(self)
                    series.setName(labelX)
                    series.setPointsVisible(True)
                    series.setPointLabelsClipping(True)

                    DateFlag = False
                    TimeFlag = False

                    for date, value in data:
                        xValue = QDateTime()

                        if not date.date() == datetime.date(1900, 1, 1):
                            DateFlag = True
                            xValue.setDate(QDate(date.date().year, date.date().month, date.date().day));

                        if not date.time() == datetime.time(0, 0):
                            TimeFlag = True
                            xValue.setTime(QTime(date.time().hour, date.time().minute, date.time().second));

                        series.append(xValue.toMSecsSinceEpoch(), value);

                    # Adding Series
                    chart.addSeries(series)

        elif DS.DataSourceext == "Tweet":
            # Line Series
            series = QLineSeries(self)
            series.setName("Date wise " + Chart[1])
            series.setPointsVisible(True)
            series.setPointLabelsClipping(True)
            series.setPointLabelsVisible(True)
            series.setPointLabelsFormat("@yPoint");

            data = df.groupby([pd.Grouper(key=Chart[1], freq='H')]).size().reset_index(name='count').values.tolist()
            DateFlag = False
            TimeFlag = False
            for Time, value in data:
                xValue = QDateTime()

                if not Time.date() == datetime.date(1900, 1, 1):
                    DateFlag = True
                    xValue.setDate(QDate(Time.date().year, Time.date().month, Time.date().day));

                if not Time.time() == datetime.time(0, 0):
                    TimeFlag = True
                    xValue.setTime(QTime(Time.time().hour, Time.time().minute, Time.time().second));

                series.append(xValue.toMSecsSinceEpoch(), value);

            chart.addSeries(series)

        # Chart Default Animation
        chart.setAnimationOptions(QChart.AllAnimations)

        # Chart Default Theme
        chart.setTheme(QChart.ChartThemeQt)

        # chart Title Font
        chart.setTitleFont(QFont("Times", 12, QFont.Bold))

        # Chart Axis
        axisX = QDateTimeAxis()
        axisX.setTitleText(Chart[2])
        axisX.setTickCount(5);

        if DateFlag and TimeFlag:
            axisX.setFormat("dd-MM-yy hh:mm");
        elif DateFlag:
            axisX.setFormat("dd-MM-yy");
        elif TimeFlag:
            axisX.setFormat("hh:mm:ss");

        chart.createDefaultAxes()
        chart.setAxisX(axisX, series);

        if DS.DataSourceext == "CSV files (*.csv)":
            chart.axisY(series).setTitleText(Chart[1])
        elif DS.DataSourceext == "Tweet":
            chart.axisY(series).setTitleText("No. of Tweets per hour")

        # Default legends
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # creating chartview for line chart
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview

    # Data Source Survey Analysis Donut Chart
    def DataSourceSurveyAnalysisDonutChart(self, Chart, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName and DS.DataSourceext == "CSV files (*.csv)":
                df = DS.CSVData
                break
            elif DS.DataSourceName == DataSourceName and DS.DataSourceext == "Tweet":
                df = DS.TweetDataFrame
                break

        # Storing data from Pandas CSV to Series
        LabelList = df[Chart[1]].value_counts().index.tolist()
        ValueList = df[Chart[1]].value_counts(normalize=True).tolist()

        data = [[LabelList[i], ValueList[i]] for i in range(0, len(LabelList))]

        # Pie Series and Pie Slice
        series = QPieSeries()
        series.setHoleSize(0.35)

        for d in data:
            slice = QPieSlice()
            slice = series.append(d[0] + " " + str("%0.3f" % (d[1] * 100)) + "%", d[1])
            slice.setLabelVisible()
            if data.index(d) == 0:
                slice.setExploded()

        # Creating a Donut Chart
        chart = QChart()
        chart.setTitle(Chart[1])
        chart.addSeries(series)

        # Chart Default Animation
        chart.setAnimationOptions(QChart.AllAnimations)

        # Chart Default Theme
        chart.setTheme(QChart.ChartThemeQt)

        # chart Title Font
        chart.setTitleFont(QFont("Times", 12, QFont.Bold))

        # Default legends
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # creating chartview for line chart
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview

    # Data Source Survey Analysis Pie Chart
    def DataSourceSurveyAnalysisPieChart(self, Chart, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName and DS.DataSourceext == "CSV files (*.csv)":
                df = DS.CSVData
                break
            elif DS.DataSourceName == DataSourceName and DS.DataSourceext == "Tweet":
                df = DS.TweetDataFrame
                break

        # Storing data from Pandas CSV to Series
        LabelList = df[Chart[1]].value_counts().index.tolist()
        ValueList = df[Chart[1]].value_counts(normalize=True).tolist()

        data = [[LabelList[i], ValueList[i]] for i in range(0, len(LabelList))]

        series = QPieSeries()
        series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
        series.setLabelsVisible(True)

        for name, value in data:
            slice = series.append(name + " " + str("%0.3f" % (value * 100)) + "%", value)
            slice.setLabelVisible(True)
            slice.setLabelPosition(QPieSlice.LabelOutside)
            slice.setLabelFont(QFont("Times", 8, QFont.Bold))

        chart = QChart()
        chart.setTitle(Chart[1])
        chart.setAnimationOptions(QChart.AllAnimations)
        chart.addSeries(series)

        # Chart Default Animation
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Chart Default Theme
        chart.setTheme(QChart.ChartThemeQt)

        # chart Title Font
        chart.setTitleFont(QFont("Times", 12, QFont.Bold))

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Times", 10))

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview

    # Data Source Survey Analysis Bar Chart
    def DataSourceSurveyAnalysisBarChart(self, Chart, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName and DS.DataSourceext == "CSV files (*.csv)":
                df = DS.CSVData
                break
            elif DS.DataSourceName == DataSourceName and DS.DataSourceext == "Tweet":
                df = DS.TweetDataFrame
                break

        LabelList = df[Chart[1]].value_counts().index.tolist()
        ValueList = df[Chart[1]].value_counts().tolist()

        # Creating Bar Series
        set0 = QBarSet(Chart[1])
        set0.append(ValueList)

        series = QBarSeries()
        series.append(set0)
        series.setLabelsVisible(True)
        series.setLabelsAngle(-30.0)

        # Creating a Bar Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(Chart[1])

        # Chart Default Animation
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Chart Default Theme
        chart.setTheme(QChart.ChartThemeQt)

        # chart Title Font
        chart.setTitleFont(QFont("Times", 12, QFont.Bold))

        # Chart Axis
        axisX = QBarCategoryAxis()
        axisX.setTitleText(Chart[1])
        axisX.append(LabelList)
        axisX.setLabelsAngle(-30)

        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Frequency")
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        axisY.applyNiceNumbers()

        # Chart legends
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # creating chartview for Bar chart
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        return chartView

    # Data Source Survey Analysis Word Cloud
    def DataSourceSurveyAnalysisWordCloud(self, Chart, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName and DS.DataSourceext == "CSV files (*.csv)":
                df = DS.CSVData
                break
            elif DS.DataSourceName == DataSourceName and DS.DataSourceext == "Tweet":
                df = DS.TweetDataFrame
                break

        # Storing data from Pandas CSV to Series
        LabelList = df[Chart[1]].value_counts().index.tolist()

        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open("Word Cloud Maskes/" + random.choice(os.listdir("Word Cloud Maskes/"))))

        # create wordcloud object
        WordCloudImage = WordCloud(background_color="white", max_words=200, mask=mask, stopwords=set(STOPWORDS), collocations=False)

        # generate wordcloud
        WordCloudImage.generate(" ".join(LabelList))

        return WordCloudImage.to_image()

    # Word Cloud Combo Box Text Change
    def WorldCloudComboBoxTextChanged(self, DashboardWidget, WordCloudWidget):
        WordCloudComboBox = self.sender()

        if WordCloudComboBox.currentText() == "Dashboard":
            DashboardWidget.show()
            WordCloudWidget.hide()
        else:
            DashboardWidget.hide()
            WordCloudWidget.show()

    # Theme Combo Box Text Change
    def ThemeComboBoxTextChanged(self, chartWidget, pal):
        ThemeComboBox = self.sender()

        # Standard
        if ThemeComboBox.currentText() == "Light":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeQt)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0xf0f0f0))
                    pal.setColor(QPalette.WindowText, QColor(0x404044))

        # Blue Cerulean
        elif ThemeComboBox.currentText() == "Blue Cerulean":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeBlueCerulean)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0x40434a))
                    pal.setColor(QPalette.WindowText, QColor(0xd6d6d6))

        # Blue Icy
        elif ThemeComboBox.currentText() == "Blue Icy":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeBlueIcy)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0xcee7f0))
                    pal.setColor(QPalette.WindowText, QColor(0x404044))

        # Blue Ncs
        elif ThemeComboBox.currentText() == "Blue Ncs":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeBlueNcs)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0x018bba))
                    pal.setColor(QPalette.WindowText, QColor(0x404044))

        # Brown Sand
        elif ThemeComboBox.currentText() == "Brown Sand":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeBrownSand)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0x9e8965))
                    pal.setColor(QPalette.WindowText, QColor(0x404044))

        # High Contrast
        elif ThemeComboBox.currentText() == "High Contrast":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeHighContrast)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0xffab03))
                    pal.setColor(QPalette.WindowText, QColor(0x181818))

        # Theme Dark
        elif ThemeComboBox.currentText() == "Theme Dark":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setTheme(QChart.ChartThemeDark)
                    chartview.chart().setTitleFont(QFont("Times", 12, QFont.Bold))
                    pal.setColor(QPalette.Window, QColor(0x121218))
                    pal.setColor(QPalette.WindowText, QColor(0xd6d6d6))

    # Animation Combo Box Text Change
    def AnimationComboBoxTextChanged(self, chartWidget):
        AnimationComboBox = self.sender()

        # All Animations
        if AnimationComboBox.currentText() == "All Animations":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setAnimationOptions(QChart.AllAnimations)

        # Series Animation
        elif AnimationComboBox.currentText() == "Series Animation":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setAnimationOptions(QChart.SeriesAnimations)

        # Grid Axis Animation
        elif AnimationComboBox.currentText() == "Grid Axis Animation":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setAnimationOptions(QChart.GridAxisAnimations)

        # No Animation
        elif AnimationComboBox.currentText() == "No Animation":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().setAnimationOptions(QChart.NoAnimation)

    # Legend Combo Box Text Change
    def LegendComboBoxTextChanged(self, chartWidget):
        LegendComboBox = self.sender()

        # Bottom
        if LegendComboBox.currentText() == "Bottom":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().legend().setVisible(True)
                    chartview.chart().legend().setAlignment(Qt.AlignBottom)

        # Top
        elif LegendComboBox.currentText() == "Top":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().legend().setVisible(True)
                    chartview.chart().legend().setAlignment(Qt.AlignTop)

        # Right
        elif LegendComboBox.currentText() == "Right":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().legend().setVisible(True)
                    chartview.chart().legend().setAlignment(Qt.AlignRight)

        # left
        elif LegendComboBox.currentText() == "Left":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().legend().setVisible(True)
                    chartview.chart().legend().setAlignment(Qt.AlignLeft)

        # Hide
        elif LegendComboBox.currentText() == "Hide":
            for chartview in chartWidget:
                if not isinstance(chartview, Image.Image):
                    chartview.chart().legend().setVisible(False)

    # Download Dashboard
    def DataSourceSurveyAnalysisDownloadDashboard(self, Widget):
        path = QFileDialog.getSaveFileName(self, 'Save File', '', 'PNG(*.png)')

        if all(path):
            pixmap = QPixmap(Widget.size())
            Widget.render(pixmap)
            pixmap.save(path[0])

            self.statusBar().showMessage('Saved Successfully')

            SaveSuccessBox = QMessageBox(self)
            SaveSuccessBox.setIcon(QMessageBox.Information)
            SaveSuccessBox.setText('Image successfully Saved in ' + path[0])
            SaveSuccessBox.setStandardButtons(QMessageBox.Open | QMessageBox.Ok)
            SaveSuccessBox.button(QMessageBox.Open).clicked.connect(lambda: os.startfile(path[0]))
            SaveSuccessBox.show()

    # ****************************************************************************
    # ********************** Data Source Tweet Analysis **************************
    # ****************************************************************************

    # Data Source Tweet Analysis Dialog
    def DataSourceTweetAnalysisDialog(self):
        DataSourceTweetAnalysisDialog = QDialog()
        DataSourceTweetAnalysisDialog.setWindowTitle("Tweet Analysis")
        DataSourceTweetAnalysisDialog.setGeometry(self.width * 0.375, self.height * 0.45, self.width / 4,
                                                  self.height / 10)
        DataSourceTweetAnalysisDialog.setParent(self)
        self.QDialogAddProperties(DataSourceTweetAnalysisDialog)

        # Data Source Label
        DataSourcelabel = QLabel(DataSourceTweetAnalysisDialog)
        DataSourcelabel.setGeometry(DataSourceTweetAnalysisDialog.width() * 0.125,
                                    DataSourceTweetAnalysisDialog.height() * 0.2,
                                    DataSourceTweetAnalysisDialog.width() / 4,
                                    DataSourceTweetAnalysisDialog.height() * 0.1)

        DataSourcelabel.setText("Data Source")
        DataSourcelabel.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.LabelSizeAdjustment(DataSourcelabel)

        # Data Source ComboBox
        DSComboBox = QComboBox(DataSourceTweetAnalysisDialog)
        DSComboBox.setGeometry(DataSourceTweetAnalysisDialog.width() * 0.4,
                               DataSourceTweetAnalysisDialog.height() * 0.2,
                               DataSourceTweetAnalysisDialog.width() / 2,
                               DataSourceTweetAnalysisDialog.height() / 10)

        for DS in myFile.DataSourceList:
            if DS.DataSourceext == 'Tweet':
                DSComboBox.addItem(DS.DataSourceName)

        self.LineEditSizeAdjustment(DSComboBox)

        # Tweet Analysis Button Box
        DataSourceTweetAnalysisbuttonBox = QDialogButtonBox(DataSourceTweetAnalysisDialog)
        DataSourceTweetAnalysisbuttonBox.setGeometry(DataSourceTweetAnalysisDialog.width() * 0.125,
                                                     DataSourceTweetAnalysisDialog.height() * 0.7,
                                                     DataSourceTweetAnalysisDialog.width() * 3 / 4,
                                                     DataSourceTweetAnalysisDialog.height() / 5)
        DataSourceTweetAnalysisbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        DataSourceTweetAnalysisbuttonBox.button(QDialogButtonBox.Ok).setText('Show')

        if DSComboBox.count() == 0:
            DataSourceTweetAnalysisbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.LineEditSizeAdjustment(DataSourceTweetAnalysisbuttonBox)

        DataSourceTweetAnalysisbuttonBox.accepted.connect(DataSourceTweetAnalysisDialog.accept)
        DataSourceTweetAnalysisbuttonBox.rejected.connect(DataSourceTweetAnalysisDialog.reject)

        DataSourceTweetAnalysisbuttonBox.accepted.connect(lambda: self.DataSourceTweetAnalysis(DSComboBox.currentText()))

        DataSourceTweetAnalysisDialog.exec()

    # Data Source Tweet Analysis
    def DataSourceTweetAnalysis(self, DataSourceName):
        DataSourceTweetAnalysisTabFlag = False
        DataSourceTweetAnalysisTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Tweet Analysis':
                if tabs.tabWidget != None:
                    DataSourceTweetAnalysisTabFlag = True
                    break
                else:
                    DataSourceTweetAnalysisTabFlag2 = True
                    break

        if not DataSourceTweetAnalysisTabFlag:
            # Creating New Tab for Survey Analysis
            DataSourceTweetAnalysisTab = QWidget()

            # **********************************************************************************************
            # ************************ Data Source Survey Analysis Setting Widget **************************
            # **********************************************************************************************

            # LayoutWidget For within Survey Analysis Tab
            OptionWidget = QWidget(DataSourceTweetAnalysisTab)
            OptionWidget.setGeometry(self.tabWidget.width() * 0.2, 0, self.tabWidget.width() * 0.6,self.tabWidget.height() / 20)

            # Box Layout for Survey Analysis Tab
            OptionWidgetLayout = QHBoxLayout(OptionWidget)
            OptionWidgetLayout.setContentsMargins(0, 0, 0, 0)

            # ********************* Theme *********************

            # Theme Label
            ThemeLabel = QLabel(OptionWidget)
            ThemeLabel.setText("Theme:")
            OptionWidgetLayout.addWidget(ThemeLabel)
            OptionWidgetLayout.addStretch(1)

            # Theme Combo Box
            ThemeComboBox = QComboBox(OptionWidget)
            OptionWidgetLayout.addWidget(ThemeComboBox)
            OptionWidgetLayout.addStretch(2)

            # Adding Items to ComboBox
            ThemeComboBox.addItem("Standard")
            ThemeComboBox.addItem("Blue Cerulean")
            ThemeComboBox.addItem("Blue Icy")
            ThemeComboBox.addItem("Blue Ncs")
            ThemeComboBox.addItem("Brown Sand")
            ThemeComboBox.addItem("High Contrast")
            ThemeComboBox.addItem("Theme Dark")

            # ******************* Animation *******************

            # Animation Label
            AnimationLabel = QLabel()
            AnimationLabel.setText("Animation:")
            OptionWidgetLayout.addWidget(AnimationLabel)
            OptionWidgetLayout.addStretch(3)

            # Animation Combo Box
            AnimationComboBox = QComboBox(OptionWidget)
            OptionWidgetLayout.addWidget(AnimationComboBox)
            OptionWidgetLayout.addStretch(4)

            # Adding Items to ComboBox
            AnimationComboBox.addItem("All Animations")
            AnimationComboBox.addItem("Series Animation")
            AnimationComboBox.addItem("Grid Axis Animation")
            AnimationComboBox.addItem("No Animation")

            # ********************* Legend ********************
            # Legend Label
            LegendLabel = QLabel(OptionWidget)
            LegendLabel.setText("Legend:")
            OptionWidgetLayout.addWidget(LegendLabel)
            OptionWidgetLayout.addStretch(5)

            # Legend ComboBox
            LegendComboBox = QComboBox(OptionWidget)
            OptionWidgetLayout.addWidget(LegendComboBox)
            OptionWidgetLayout.addStretch(6)

            # Adding Items to ComboBox
            LegendComboBox.addItem("Bottom")
            LegendComboBox.addItem("Top")
            LegendComboBox.addItem("Left")
            LegendComboBox.addItem("Right")
            LegendComboBox.addItem("Hide")

            self.LineEditSizeAdjustment(LegendComboBox)

            # Word Cloud ComboBox
            WordCloudComboBox = QComboBox()
            OptionWidgetLayout.addWidget(WordCloudComboBox)
            OptionWidgetLayout.addStretch(7)

            WordCloudComboBox.addItem("Dashboard")
            WordCloudComboBox.addItem("Word Cloud")

            self.LineEditSizeAdjustment(WordCloudComboBox)

            # Download Button
            DownloadDashboardButton = QPushButton('Download ')
            DownloadDashboardButton.setIcon(QIcon("Images/Download Button.png"))
            DownloadDashboardButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

            DownloadDashboardButtonFont = QFont("sans-serif")
            DownloadDashboardButtonFont.setPixelSize(14)
            DownloadDashboardButtonFont.setBold(True)
            DownloadDashboardButton.setFont(DownloadDashboardButtonFont)

            OptionWidgetLayout.addWidget(DownloadDashboardButton)
            OptionWidgetLayout.addStretch(7)

            self.LineEditSizeAdjustment(DownloadDashboardButton)

            # *********************************************************************************************
            # ************************ Data Source Survey Analysis Chart Widgets **************************
            # *********************************************************************************************

            # ********************* Dashboard *********************

            chartWidget = []

            chartWidget.append(self.DataSourceSurveyAnalysisBarChart(['Bar Chart', 'Phone Type', ''], DataSourceName))
            chartWidget.append(self.DataSourceSurveyAnalysisDonutChart(['Pie Chart', 'Retweeted', ''], DataSourceName))
            chartWidget.append(self.SentimentAnalysisPieChart(DataSourceName))
            chartWidget.append(self.DataSourceSurveyAnalysisLineChart(['LineChart', 'Tweet Created At', ''], DataSourceName))

            # Group Widget For within Survey Analysis Tab
            DashboardWidget = QGroupBox(DataSourceTweetAnalysisTab)
            DashboardWidget.setGeometry(0, self.tabWidget.height() * 0.05, self.tabWidget.width(), self.tabWidget.height() * 0.95)

            # Box Layout for Survey Analysis Tab
            DashboardWidgetLayout = QGridLayout(DashboardWidget)
            DashboardWidgetLayout.setContentsMargins(0, 0, 0, 0)

            colWid = 2

            colcounter = 0
            rowcounter = 0

            for chartWid in chartWidget:
                if colcounter < colWid:
                    pass
                else:
                    colcounter = 0
                    rowcounter += 1

                DashboardWidgetLayout.addWidget(chartWid, rowcounter, colcounter)
                colcounter += 1

            # ******************************************************
            # ********************* Word Cloud *********************
            # ******************************************************

            WordCloudWidget = QGroupBox(DataSourceTweetAnalysisTab)
            WordCloudWidget.setGeometry(0, self.tabWidget.height() * 0.05, self.tabWidget.width(), self.tabWidget.height() * 0.95)

            # Box Layout for Survey Analysis Tab
            WordCloudWidgetLayout = QGridLayout(WordCloudWidget)
            WordCloudWidgetLayout.setContentsMargins(0, 0, 0, 0)

            WordCloudLabel = QLabel(WordCloudWidget)

            # Resizing label to Layout
            WordCloudLabel.resize(WordCloudWidget.width(), WordCloudWidget.height())

            # Setting and Scaling Pixmap image on Label
            WordCloudLabel.setPixmap(self.DataSourceSurveyAnalysisWordCloud(['Word Cloud', 'Tweet Text', ''], DataSourceName).toqpixmap().scaled(WordCloudWidget.width(), WordCloudWidget.height(), Qt.KeepAspectRatio))

            WordCloudLabel.setGeometry((WordCloudWidget.width() - WordCloudLabel.pixmap().width()) / 2,
                                       (WordCloudWidget.height() - WordCloudLabel.pixmap().height()) / 2,
                                       WordCloudLabel.pixmap().width(), WordCloudLabel.pixmap().height())
            WordCloudWidget.hide()

            # ******************************************************
            # ************** ComboBox Text Changed *****************
            # ******************************************************

            WordCloudComboBox.currentTextChanged.connect(lambda: self.WordCloudComboBoxTextChanged(DashboardWidget, WordCloudWidget))
            ThemeComboBox.currentTextChanged.connect(lambda: self.ThemeComboBoxTextChanged(chartWidget, DashboardWidget.palette()))
            AnimationComboBox.currentTextChanged.connect(lambda: self.AnimationComboBoxTextChanged(chartWidget))
            LegendComboBox.currentTextChanged.connect(lambda: self.LegendComboBoxTextChanged(chartWidget))

            # *************** Push Button Clicked ******************

            DownloadDashboardButton.clicked.connect(lambda: self.DataSourceSurveyAnalysisDownloadDashboard(DashboardWidget) if WordCloudWidget.isHidden() else self.DataSourceSurveyAnalysisDownloadDashboard(WordCloudWidget))

            # *********************************************************************************************
            # ************************************ Tab Management *****************************************
            # *********************************************************************************************

            if DataSourceTweetAnalysisTabFlag2:
                tabs.tabWidget = DataSourceTweetAnalysisTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourceTweetAnalysisTab, "Tweet Analysis")
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceTweetAnalysisTab)
            else:
                # ************ Adding Survey Analysis Tab to QTabWidget *************

                myFile.TabList.append(Tab("Tweet Analysis", DataSourceTweetAnalysisTab, DataSourceName))

                # ***************** Adding Preview Tab to QTabWidget ****************

                self.tabWidget.addTab(DataSourceTweetAnalysisTab, "Tweet Analysis")
                self.tabWidget.setCurrentWidget(DataSourceTweetAnalysisTab)
                myFile.requiredSaved = True

            ItemsWidget = self.VisualizationTreeWidget.findItems(DataSourceName, Qt.MatchExactly, 0)

            if len(ItemsWidget) == 0:
                DSVisualWidget = QTreeWidgetItem(self.VisualizationTreeWidget)
                DSVisualWidget.setText(0, DataSourceName)
                DSVisualWidget.setToolTip(0, DSVisualWidget.text(0))
                DSVisualWidget.setExpanded(True)

                DSNewCaseNode = QTreeWidgetItem(DSVisualWidget)
                DSNewCaseNode.setText(0, 'Tweet Analysis')
                DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

            else:
                for widgets in ItemsWidget:
                    SurveyAnalysisWidget = self.VisualizationTreeWidget.findItems('Tweet Analysis', Qt.MatchRecursive, 0)

                    SurveyAnalysisWidgetFlag = False

                    if len(SurveyAnalysisWidget) > 0:
                        for SAWidgets in SurveyAnalysisWidget:
                            if SAWidgets.parent().text(0) == DataSourceName:
                                SurveyAnalysisWidgetFlag = True
                                break

                    if not SurveyAnalysisWidgetFlag:
                        DSNewCaseNode = QTreeWidgetItem(widgets)
                        DSNewCaseNode.setText(0, 'Tweet Analysis')
                        DSNewCaseNode.setToolTip(0, DSNewCaseNode.text(0))

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Sentiment Analysis Pie Chart
    def SentimentAnalysisPieChart(self, DataSourceName):
        for DS in myFile.DataSourceList:
            if DS.DataSourceName == DataSourceName:
                if hasattr(DS, "PositiveSentimentCount"):
                    pass
                else:
                    DS.SentimentAnalysis("Tweet Text")
                break


        series = QPieSeries()
        series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
        series.setLabelsVisible(True)

        # Setting Data in Pie Series
        # Positive
        slice = series.append("Positive " + str("%0.3f" % (DS.PositiveSentimentCount * 100/len(DS.AutomaticSentimentList))) + "%", DS.PositiveSentimentCount)
        slice.setLabelVisible(True)
        slice.setLabelPosition(QPieSlice.LabelOutside)
        slice.setLabelFont(QFont("Times", 8, QFont.Bold))

        # Negative
        slice = series.append("Negative " + str("%0.3f" % (DS.NegativeSentimentCount * 100/len(DS.AutomaticSentimentList))) + "%", DS.NegativeSentimentCount)
        slice.setLabelVisible(True)
        slice.setLabelPosition(QPieSlice.LabelOutside)
        slice.setLabelFont(QFont("Times", 8, QFont.Bold))

        # Neutral
        slice = series.append("Neutral " + str("%0.3f" % (DS.NeutralSentimentCount * 100/len(DS.AutomaticSentimentList))) + "%", DS.NeutralSentimentCount)
        slice.setLabelVisible(True)
        slice.setLabelPosition(QPieSlice.LabelOutside)
        slice.setLabelFont(QFont("Times", 8, QFont.Bold))

        # Creating Chart For Pie Series
        chart = QChart()
        chart.setTitle("Sentiment Analysis")
        chart.setAnimationOptions(QChart.AllAnimations)
        chart.addSeries(series)

        # Chart Default Animation
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Chart Default Theme
        chart.setTheme(QChart.ChartThemeQt)

        # chart Title Font
        chart.setTitleFont(QFont("Times", 12, QFont.Bold))

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Times", 10))

        # Creating Chartview for Pie Chart
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview

    # Word CLoud Combo Box Text Change
    def WordCloudComboBoxTextChanged(self, DashboardWidget, WordCloudWidget):
        WordCloudComboBox = self.sender()

        if WordCloudComboBox.currentText() == "Word Cloud":
            DashboardWidget.hide()
            WordCloudWidget.show()
        else:
            DashboardWidget.show()
            WordCloudWidget.hide()

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
        self.QDialogAddProperties(DataSourceCoordinateMapDialog)

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

        # Coordinate Map Button Box
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
        DataSourceCoordinateMapTabFlag2 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == DataSourceName and tabs.TabName == 'Coordinate Map':
                if tabs.tabWidget != None:
                    DataSourceCoordinateMapTabFlag = True
                    break
                else:
                    DataSourceCoordinateMapTabFlag2 = True
                    break

        if not DataSourceCoordinateMapTabFlag:
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
                tabs.tabWidget = DataSourceCoordinateMapTab
                if tabs.isActive:
                    self.tabWidget.addTab(DataSourceCoordinateMapTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(DataSourceCoordinateMapTab)
            else:
                # Adding Word Cloud Tab to QTabWidget
                myFile.TabList.append(Tab("Coordinate Map", DataSourceCoordinateMapTab, DataSourceName))
                self.tabWidget.addTab(DataSourceCoordinateMapTab, "Coordinate Map")
                self.tabWidget.setCurrentWidget(DataSourceCoordinateMapTab)
                myFile.requiredSaved = True

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

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # ****************************************************************************
    # ********************** Enable/Disable/Reusable Function ********************
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
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        elif RadioButton.isChecked():
            FirstLineEdit.setEnabled(False)
            SecondLineEdit.setEnabled(True)

            if (len(SecondLineEdit.text()) > 0):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    # Ok Button Enable on Youtube Radio Button Toggling
    def EnableOkonCSVRadioButtonToggle(self, RadioButton, FirstLineEdit, SecondLineEdit, BrowseButton, ButtonBox):
        Button = self.sender()
        if Button.isChecked():
            if Button.text() == "Computer":
                FirstLineEdit.setEnabled(True)
                BrowseButton.setEnabled(True)
                SecondLineEdit.setEnabled(False)
            else:
                FirstLineEdit.setEnabled(True)
                BrowseButton.setEnabled(False)
                SecondLineEdit.setEnabled(False)

            if (len(FirstLineEdit.text()) > 0):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        elif RadioButton.isChecked():
            if RadioButton.text() == "Computer":
                FirstLineEdit.setEnabled(True)
                BrowseButton.setEnabled(True)
                SecondLineEdit.setEnabled(False)
            else:
                FirstLineEdit.setEnabled(True)
                BrowseButton.setEnabled(False)
                SecondLineEdit.setEnabled(False)

            if (len(FirstLineEdit.text()) > 0):
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                ButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

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
                            item2 = Table.cellWidget(row, column)
                            if item is not None:
                                rowdata.append(item.text())
                            elif item2 is not None:
                                rowdata.append(item2.toPlainText())
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)

                    self.statusBar().showMessage('Table successfully Saved')

                    SaveSuccessBox = QMessageBox(self)
                    SaveSuccessBox.setIcon(QMessageBox.Information)
                    SaveSuccessBox.setText('Table successfully Saved in ' + path[0])
                    SaveSuccessBox.setStandardButtons(QMessageBox.Open | QMessageBox.Ok)
                    SaveSuccessBox.button(QMessageBox.Open).clicked.connect(lambda: os.startfile(path[0]))
                    SaveSuccessBox.show()

                    #self, "Saving Error", "Permission Denied!", QMessageBox.Ok)

        except PermissionError:
            QMessageBox.critical(self, "Saving Error", "Permission Denied!", QMessageBox.Ok)

    # Save Structure as PDF
    def SaveStructureAsPDF(self, graph):
        try:
            path = QFileDialog.getSaveFileName(
                self, 'Save File', '', 'PDF Files(*.pdf)')

            if all(path):
                graph.format = "pdf"
                self.statusBar().showMessage('Structure successfully Saved')
                SaveSuccessBox = QMessageBox(self)
                SaveSuccessBox.setIcon(QMessageBox.Information)
                SaveSuccessBox.setText('Table successfully Saved in ' + path[0])
                SaveSuccessBox.setStandardButtons(QMessageBox.Open | QMessageBox.Ok)
                SaveSuccessBox.button(QMessageBox.Open).clicked.connect(lambda: graph.render(ntpath.basename(path[0]), os.path.dirname(path[0]), view=True, cleanup=True))
                SaveSuccessBox.button(QMessageBox.Ok).clicked.connect(lambda: graph.render(ntpath.basename(path[0]), os.path.dirname(path[0]), view=False, cleanup=True))
                SaveSuccessBox.show()

        except PermissionError:
            QMessageBox.critical(self, "Saving Error", "Permission Denied!", QMessageBox.Ok)

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
                QueryRemove.triggered.connect(lambda: self.QueryParentRemoveDialog(QueryItemName))
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
                QueryRemove.triggered.connect(lambda: self.QueryParentRemoveDialog(QueryItemName))

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

    # Remove Parent Query (Tab) Dialog
    def QueryParentRemoveDialog(self, QueryItemName):
        QueryRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's all Queries?",
                                                         QMessageBox.Yes | QMessageBox.No)

        if QueryRemoveChoice == QMessageBox.Yes:
            self.QueryParentRemove(QueryItemName)
        else:
            pass

    # Remove Parent Query (Tab)
    def QueryParentRemove(self, QueryItemName):
        if QueryItemName.text(0) == 'Data Sources Similarity':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Data Sources Similarity':
                    myFile.TabList.remove(tabs)
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    del tabs

            self.QueryTreeWidget.invisibleRootItem().removeChild(QueryItemName)

        else:
            # Removing Tabs From TabWidget
            for tabs in myFile.TabList:
                if tabs.DataSourceName == QueryItemName.text(0):
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    del tabs

            # Removing Tabs From TabList
            myFile.TabList = [tabs for tabs in myFile.TabList if
                              not tabs.DataSourceName == QueryItemName.text(0)]

            self.QueryTreeWidget.invisibleRootItem().removeChild(QueryItemName)

        myFile.requiredSaved = True

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
            if tabs.DataSourceName == QueryItemName.parent().text(0) and tabs.TabName == QueryItemName.text(0):
                myFile.TabList.remove(tabs)
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                del tabs
                break

        if QueryItemName.parent().childCount() == 1:
            tempParent = QueryItemName.parent()
            tempParent.removeChild(QueryItemName)
            self.QueryTreeWidget.invisibleRootItem().removeChild(tempParent)
        else:
            QueryItemName.parent().removeChild(QueryItemName)

        myFile.requiredSaved = True

    # Preview Query/Tab on double click
    def QueryDoubleClickHandler(self, QueryItemName):
        if QueryItemName.text(0) == 'Data Sources Similarity':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Data Sources Similarity':
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                        tabs.setisActive(True)
                    break
        else:
            for tabs in myFile.TabList:
                if tabs.DataSourceName == QueryItemName.parent().text(0) and tabs.TabName == QueryItemName.text(0):
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                        tabs.setisActive(True)
                        break

        myFile.requiredSaved = True

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
            CasesExpand.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(CasesItemName))
            if (CasesItemName.childCount() == 0 or CasesItemName.isExpanded() == True):
                CasesExpand.setDisabled(True)
            else:
                CasesExpand.setDisabled(False)
            CasesRightClickMenu.addAction(CasesExpand)

            # Cases Collapse
            CasesCollapse = QAction('Collapse', self.CasesTreeWidget)
            CasesCollapse.triggered.connect(lambda: self.DataSourceWidgetItemExpandCollapse(CasesItemName))
            if (CasesItemName.childCount() == 0 or CasesItemName.isExpanded() == False):
                CasesCollapse.setDisabled(True)
            else:
                CasesCollapse.setDisabled(False)
            CasesRightClickMenu.addAction(CasesCollapse)

            # Cases Structure
            CasesStructure = QAction('Show Structure', self.CasesTreeWidget)
            CasesStructure.triggered.connect(lambda: self.CasesStructure(CasesItemName))
            CasesRightClickMenu.addAction(CasesStructure)

            # Cases Coverage
            CasesCoverage = QAction('Show Cases Coverage', self.CasesTreeWidget)
            CasesCoverage.triggered.connect(lambda: self.CasesParentCoverage(CasesItemName))
            CasesRightClickMenu.addAction(CasesCoverage)

            # Merge Cases
            MergeCases = QAction("Merge Cases", self.CasesTreeWidget)
            MergeCases.triggered.connect(lambda: self.MergeCasesDialog(CasesItemName))

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.text(0):
                    if len(DS.CasesList) > 1:
                        MergeCases.setDisabled(False)
                    else:
                        MergeCases.setDisabled(True)

            CasesRightClickMenu.addAction(MergeCases)

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
            MergeCaseFlag = False
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.parent().text(0):
                    for cases in DS.CasesList:
                        if cases.CaseTopic == CasesItemName.text(0):
                            if cases.MergedCase:
                                MergeCaseFlag = True

            if MergeCaseFlag:
                CasesRightClickMenu = QMenu(self.CasesTreeWidget)

                # Case UnMerge
                CasesUnMerge = QAction('Unmerge', self.CasesTreeWidget)
                CasesUnMerge.triggered.connect(lambda: self.CasesUnMerge(CasesItemName))
                CasesRightClickMenu.addAction(CasesUnMerge)

                # Case Rename
                CasesRename = QAction('Rename', self.CasesTreeWidget)
                CasesRename.triggered.connect(lambda: self.CasesRename(CasesItemName))
                CasesRightClickMenu.addAction(CasesRename)
                # Case Rename

                CasesDetail = QAction('Detail', self.CasesTreeWidget)
                CasesDetail.triggered.connect(lambda: self.CasesChildDetail(CasesItemName))
                CasesRightClickMenu.addAction(CasesDetail)

                CasesRightClickMenu.popup(CasesWidgetPos)

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

    # Cases Structure
    def CasesStructure(self, CasesItemName):
        CasesStructureTabFlag = False
        CasesStructureTabFlag2 = False
        CasesStructureTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == CasesItemName.text(0) and tabs.TabName == 'Cases Structure':
                if tabs.tabWidget != None:
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == CasesItemName.text(0):
                            if len(DS.CasesList) == tabs.CasesLength:
                                CasesStructureTabFlag = True
                            else:
                                CasesStructureTabFlag2 = True
                    break
                else:
                    CasesStructureTabFlag3 = True
                    break

        if not CasesStructureTabFlag or CasesStructureTabFlag2:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.text(0):
                    break

            # Creating New Tab for Case Structure Tab
            CasesStructureTab = QWidget()

            # ******************************* LayoutWidget For within Case Structure Tab ************************************
            CasesStructureTabVerticalLayoutWidget = QWidget(CasesStructureTab)
            CasesStructureTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(),
                                                                    self.tabWidget.height() / 10)

            # Box Layout for Case Structure Tab
            CasesStructureTabVerticalLayout = QHBoxLayout(CasesStructureTabVerticalLayoutWidget)
            CasesStructureTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            DownloadAsPDFButton = QPushButton(CasesStructureTabVerticalLayoutWidget)
            DownloadAsPDFButton.setText("Download")
            DownloadAsPDFButton.setGeometry(CasesStructureTabVerticalLayoutWidget.width() * 0.8,
                                            CasesStructureTabVerticalLayoutWidget.height() * 0.4,
                                            CasesStructureTabVerticalLayoutWidget.width() * 0.1,
                                            CasesStructureTabVerticalLayoutWidget.height() * 0.2)
            DownloadAsPDFButton.setIcon(QIcon("Images/Download Button.png"))
            DownloadAsPDFButton.setStyleSheet('QPushButton {background-color: #0080FF; color: white;}')

            DownloadAsPDFButtonFont = QFont("sans-serif")
            DownloadAsPDFButtonFont.setPixelSize(14)
            DownloadAsPDFButtonFont.setBold(True)
            DownloadAsPDFButton.setFont(DownloadAsPDFButtonFont)
            self.LineEditSizeAdjustment(DownloadAsPDFButton)


            # *************************** 2nd LayoutWidget For within Case Structure Tab *************************************
            CasesStructureTabVerticalLayoutWidget2 = QWidget(CasesStructureTab)
            CasesStructureTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10,
                                                               self.tabWidget.width(),
                                                               self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Case Structure Tab
            CasesStructureTabVerticalLayout2 = QVBoxLayout(CasesStructureTabVerticalLayoutWidget2)

            os.environ["PATH"] += os.pathsep + 'Graphviz2.38/bin/'


            graph = graphviz.Digraph(name="Cases")
            graph.edge_attr.update(arrowhead="vee", arrowsize="1")
            graph.node_attr.update(shape="box")
            graph.graph_attr['rankdir'] = 'LR'

            cases_list = []

            for cases in DS.CasesList:
                ItemWidget = self.CasesTreeWidget.findItems(cases.CaseTopic, Qt.MatchRecursive, 0)
                if len(ItemWidget) > 1:
                    ItemPresentFlag = False
                    for widget in ItemWidget:
                        tempWidget = widget
                        while tempWidget.parent() != None:
                            tempWidget = tempWidget.parent()

                        if tempWidget.text(0) == CasesItemName.text(0):
                            ItemPresentFlag = True
                            break

                    if ItemPresentFlag:
                        cases_list.append([widget, widget.parent()])

                elif len(ItemWidget) > 0:
                    for widget in ItemWidget:
                        cases_list.append([widget, widget.parent()])

            parent_child_list = []

            for i in range(len(cases_list)):
                graph.node(cases_list[i][0].text(0))
                if cases_list[i][1] != None:
                    parent_child_list.append([cases_list[i][1].text(0), cases_list[i][0].text(0)])

            for i in range(len(parent_child_list)):
                graph.edge(parent_child_list[i][0], parent_child_list[i][1])

            graph.format = "png"
            graph.render("Cases", cleanup=True)
            CasesStructureImage = Image.open("Cases.png")
            ImageArray = np.array(CasesStructureImage)
            CasesStructureImage = Image.fromarray(ImageArray)
            os.remove("Cases.png")

            # Label for Word Cloud Image
            CasesStructureLabel = QLabel(CasesStructureTabVerticalLayoutWidget2)

            # Resizing label to Layout
            CasesStructureLabel.resize(CasesStructureTabVerticalLayoutWidget2.width(), CasesStructureTabVerticalLayoutWidget2.height())

            # Converting WordCloud Image to Pixmap
            CasesStructurePixmap = CasesStructureImage.toqpixmap()

            # Scaling Pixmap image
            dummypixmap = CasesStructurePixmap.scaled(CasesStructureTabVerticalLayoutWidget2.width(),
                                                      CasesStructureTabVerticalLayoutWidget2.height(),
                                                      Qt.KeepAspectRatio)
            CasesStructureLabel.setPixmap(dummypixmap)
            CasesStructureLabel.setGeometry((CasesStructureTabVerticalLayoutWidget2.width() - dummypixmap.width()) / 2,
                                            (CasesStructureTabVerticalLayoutWidget2.height() - dummypixmap.height()) / 2,
                                            dummypixmap.width(), dummypixmap.height())

            DownloadAsPDFButton.clicked.connect(lambda: self.SaveStructureAsPDF(graph))

            if CasesStructureTabFlag3:
                tabs.tabWidget = CasesStructureTab
                if tabs.isActive:
                    self.tabWidget.addTab(CasesStructureTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(CasesStructureTab)

            else:
                if CasesStructureTabFlag2:
                    tabs.setCasesLength(len(DS.CasesList))
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(CasesStructureTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(CasesStructureTab)
                    tabs.tabWidget = CasesStructureTab
                    tabs.setisActive(True)
                    myFile.requiredSaved = True
                else:
                    # Adding Word Cloud Tab to QTabWidget
                    dummyTab = Tab("Cases Structure", CasesStructureTab, CasesItemName.text(0))
                    dummyTab.setCasesLength(len(DS.CasesList))
                    myFile.TabList.append(dummyTab)
                    self.tabWidget.addTab(CasesStructureTab, "Cases Structure")
                    self.tabWidget.setCurrentWidget(CasesStructureTab)
                    myFile.requiredSaved = True
        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Cases Structure Update
    def CasesStructureUpdate(self, CasesItemName):
        for tabs in myFile.TabList:
            if tabs.TabName == "Cases Structure" and tabs.DataSourceName == CasesItemName.text(0) :
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == CasesItemName.text(0):
                        break

                if self.tabWidget.indexOf(tabs.tabWidget) >= 0:
                    currentTab = self.tabWidget.currentWidget()
                    if len(DS.CasesList) > 0:
                        self.CasesStructure(CasesItemName)
                        self.tabWidget.setCurrentWidget(currentTab)
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                    break

    # Merge Cases Dailog
    def MergeCasesDialog(self, CasesItemName):
        MergeCasesDialog = QDialog()
        MergeCasesDialog.setWindowTitle("Merge Cases")
        MergeCasesDialog.setGeometry(self.width * 0.35, self.height * 0.35, self.width / 3, self.height / 3)
        MergeCasesDialog.setParent(self)
        MergeCasesDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.QDialogAddProperties(MergeCasesDialog)

        # Case Name Label
        CaseNameLabel = QLabel(MergeCasesDialog)
        CaseNameLabel.setGeometry(MergeCasesDialog.width() * 0.2,
                                  MergeCasesDialog.height() * 0.1,
                                  MergeCasesDialog.width() / 5,
                                  MergeCasesDialog.height() / 15)
        CaseNameLabel.setText("Case Name")
        self.LabelSizeAdjustment(CaseNameLabel)

        # Case Name LineEdit
        CaseNameLineEdit = QLineEdit(MergeCasesDialog)
        CaseNameLineEdit.setGeometry(MergeCasesDialog.width() * 0.5,
                                     MergeCasesDialog.height() * 0.1,
                                     MergeCasesDialog.width() * 0.3,
                                     MergeCasesDialog.height() / 15)
        self.LineEditSizeAdjustment(CaseNameLineEdit)

        # Cases List View
        ListModel = QStandardItemModel()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == CasesItemName.text(0):
                for cases in DS.CasesList:
                    if cases.ParentCase == None:
                        item = QStandardItem(cases.CaseTopic)
                        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                        item.setData(QVariant(Qt.Unchecked), Qt.CheckStateRole)
                        ListModel.appendRow(item)

        CasesListView = QListView(MergeCasesDialog)
        CasesListView.setGeometry(MergeCasesDialog.width() * 0.2,
                                  MergeCasesDialog.height() * 0.2,
                                  MergeCasesDialog.width() * 0.6,
                                  MergeCasesDialog.height() / 2)
        CasesListView.setModel(ListModel)


        MergeCasesbuttonBox = QDialogButtonBox(MergeCasesDialog)
        MergeCasesbuttonBox.setGeometry(MergeCasesDialog.width() * 0.5,
                                        MergeCasesDialog.height() * 0.8,
                                        MergeCasesDialog.width() / 3,
                                        MergeCasesDialog.height() / 15)
        MergeCasesbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        MergeCasesbuttonBox.button(QDialogButtonBox.Ok).setText('Merge')
        MergeCasesbuttonBox.button(QDialogButtonBox.Ok).setDisabled(True)
        self.LineEditSizeAdjustment(MergeCasesbuttonBox)

        CaseNameLineEdit.textChanged.connect(lambda: self.OkButtonEnable(MergeCasesbuttonBox, True))

        MergeCasesbuttonBox.accepted.connect(MergeCasesDialog.accept)
        MergeCasesbuttonBox.rejected.connect(MergeCasesDialog.reject)

        MergeCasesbuttonBox.accepted.connect(lambda: self.MergeCases(CasesItemName, CaseNameLineEdit.text(), ListModel))

        MergeCasesDialog.exec_()

    # Merge Cases
    def MergeCases(self, CasesItemName, MergeCaseName, ListModel):
        # Check Selection in List
        SingleSelectionInListError = False

        CheckedCasesList = []

        for listRow in range(ListModel.rowCount()):
            dummyList = ListModel.findItems(ListModel.data(ListModel.index(listRow, 0)), Qt.MatchExactly)

            for object in dummyList:
                if object.checkState() == 2:
                    CheckedCasesList.append(object.text())

        if len(CheckedCasesList) < 2:
            SingleSelectionInListError = True

        if not SingleSelectionInListError:
            # Check Merge Case Name
            MergeCaseNameDuplicateError = False

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.text(0):
                    break

            for cases in DS.CasesList:
                if cases.CaseTopic == MergeCaseName:
                    MergeCaseNameDuplicateError = True
                    break

            if not MergeCaseNameDuplicateError:
                if  MergeCaseName != CasesItemName.text(0):
                    # Creating New Case (MergeCase)
                    NewCase = Cases(MergeCaseName, 0)
                    NewCase.setMergeCaseFlag()

                    DS.CasesList.append(NewCase)
                    # Setting Parent of Cases
                    for CheckedCases in CheckedCasesList:
                        for cases in DS.CasesList:
                            if cases.CaseTopic == CheckedCases:
                                cases.setParentCase(NewCase)
                                break

                    # Removing All Child
                    while CasesItemName.childCount() != 0:
                        CasesItemName.removeChild(CasesItemName.child(0))

                    self.statusBar().showMessage('Cases successfully Merged')

                    # Setting All Child
                    self.SetCasesWidget(DS, CasesItemName)

                    myFile.requiredSaved = True

                else:
                    QMessageBox.critical(self, "Case Name Error",
                                         "Case cannot have the same Name as its Data Source",
                                         QMessageBox.Ok)

            else:
                QMessageBox.critical(self, "Case Name Error",
                                     "A Case with a similar Name Exists! Please Try a different Name",
                                     QMessageBox.Ok)
        else:
            QMessageBox.critical(self, "Selection Error",
                                 "Please Select More than one cases from the list to merge",
                                 QMessageBox.Ok)

    # UnMerge Cases
    def CasesUnMerge(self, CasesItemName):
        tempWidget = CasesItemName
        while tempWidget.parent() != None:
            tempWidget = tempWidget.parent()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == tempWidget.text(0):
                for cases in DS.CasesList:
                    if cases.ParentCase != None:
                        if cases.ParentCase.CaseTopic == CasesItemName.text(0):
                            for cases2 in DS.CasesList:
                                if cases2.CaseTopic == cases.ParentCase.CaseTopic:
                                    cases.ParentCase = cases2.ParentCase

                            ItemWidget = self.CasesTreeWidget.findItems(cases.CaseTopic, Qt.MatchRecursive, 0)
                            if len(ItemWidget) > 1:
                                ItemPresentFlag = False
                                for widget in ItemWidget:
                                    tempWidget2 = widget
                                    while tempWidget2.parent() != None:
                                        tempWidget2 = tempWidget2.parent()

                                    if tempWidget2.text(0) == tempWidget2.text(0):
                                        ItemPresentFlag = True
                                        break

                                if ItemPresentFlag:
                                    tempChild = CasesItemName.takeChild(CasesItemName.indexOfChild(widget))
                                    CasesItemName.parent().addChild(tempChild)

                            elif len(ItemWidget) == 1:
                                for widget in ItemWidget:
                                    tempChild = CasesItemName.takeChild(CasesItemName.indexOfChild(widget))
                                    CasesItemName.parent().addChild(tempChild)


                for cases in DS.CasesList:
                    if cases.CaseTopic == CasesItemName.text(0):
                        DS.CasesList.remove(cases)
                        del cases

                CasesItemName.parent().removeChild(CasesItemName)

        self.statusBar().showMessage('Case Unmerge Successfully')
        self.CasesParentCoverageUpdate(tempWidget)
        self.CasesStructureUpdate(tempWidget)
        myFile.requiredSaved = True

    # Set Cases Widget
    def SetCasesWidget(self, DS, CasesItemName):
        counter = 0
        while (counter < len(DS.CasesList)):
            for cases in DS.CasesList:
                if cases.ParentCase == None:
                    ItemWidget = self.CasesTreeWidget.findItems(cases.CaseTopic, Qt.MatchRecursive, 0)
                    if len(ItemWidget) == 0:
                        DSMergeCaseWidget = QTreeWidgetItem(CasesItemName)
                        DSMergeCaseWidget.setText(0, cases.CaseTopic)
                        DSMergeCaseWidget.setToolTip(0, DSMergeCaseWidget.text(0))
                        DSMergeCaseWidget.setExpanded(True)
                        counter += 1

                    elif len(ItemWidget) > 0:
                        ItemPresentFlag = False
                        for items in ItemWidget:
                            tempWidget = items
                            while tempWidget.parent() != None:
                                tempWidget = tempWidget.parent()

                            if tempWidget.text(0) == CasesItemName.text(0):
                                ItemPresentFlag = True
                                break

                        if not ItemPresentFlag:
                            DSMergeCaseWidget = QTreeWidgetItem(CasesItemName)
                            DSMergeCaseWidget.setText(0, cases.CaseTopic)
                            DSMergeCaseWidget.setToolTip(0, DSMergeCaseWidget.text(0))
                            DSMergeCaseWidget.setExpanded(True)
                            counter += 1

                else:
                    SelfItemWidget = self.CasesTreeWidget.findItems(cases.CaseTopic, Qt.MatchRecursive, 0)

                    if len(SelfItemWidget) == 0:
                        ItemWidget = self.CasesTreeWidget.findItems(cases.ParentCase.CaseTopic, Qt.MatchRecursive, 0)
                        if len(ItemWidget) > 0:
                            for items in ItemWidget:
                                tempWidget = items
                                while tempWidget.parent() != None:
                                    tempWidget = tempWidget.parent()

                                if tempWidget.text(0) == CasesItemName.text(0):
                                    DSMergeCaseWidget = QTreeWidgetItem(items)
                                    DSMergeCaseWidget.setText(0, cases.CaseTopic)
                                    DSMergeCaseWidget.setToolTip(0, DSMergeCaseWidget.text(0))
                                    DSMergeCaseWidget.setExpanded(True)

                                    counter += 1

                    elif len(SelfItemWidget) > 0:
                        ItemPresentFlag = False
                        for items in SelfItemWidget:
                            tempWidget2 = items
                            while tempWidget2.parent() != None:
                                tempWidget2 = tempWidget2.parent()

                            if tempWidget2.text(0) == CasesItemName.text(0):
                                ItemPresentFlag = True
                                break

                        if not ItemPresentFlag:

                            for items in SelfItemWidget:
                                ItemWidget = self.CasesTreeWidget.findItems(cases.ParentCase.CaseTopic,
                                                                            Qt.MatchRecursive, 0)
                                if len(ItemWidget) > 0:
                                    for items in ItemWidget:
                                        tempWidget = items
                                        while tempWidget.parent() != None:
                                            tempWidget = tempWidget.parent()

                                        if tempWidget.text(0) == CasesItemName.text(0):
                                            DSMergeCaseWidget = QTreeWidgetItem(items)
                                            DSMergeCaseWidget.setText(0, cases.CaseTopic)
                                            DSMergeCaseWidget.setToolTip(0, DSMergeCaseWidget.text(0))
                                            DSMergeCaseWidget.setExpanded(True)

                                            counter += 1

        self.CasesParentCoverageUpdate(CasesItemName)
        self.CasesStructureUpdate(CasesItemName)

    # Cases Coverage
    def CasesParentCoverage(self, CasesItemName):
        CasesParentCoverageTabFlag = False
        CasesParentCoverageTabFlag2 = False
        CasesParentCoverageTabFlag3 = False

        for tabs in myFile.TabList:
            if tabs.DataSourceName == CasesItemName.text(0) and tabs.TabName == 'Cases Coverage':
                if tabs.tabWidget != None:
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == CasesItemName.text(0):
                            if len(DS.CasesList) == tabs.CasesLength:
                                CasesParentCoverageTabFlag = True
                            else:
                                CasesParentCoverageTabFlag2 = True
                    break
                else:
                    CasesParentCoverageTabFlag3 = True
                    break

        if not CasesParentCoverageTabFlag or CasesParentCoverageTabFlag2:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == CasesItemName.text(0):
                    DS.allCasesCoverage()
                    break


            # Creating New Tab for Case Parent Coverage Tab
            CasesParentCoverageTab = QWidget()

            # ******************************* LayoutWidget For within Case Parent Coverage Tab ************************************
            CasesParentCoverageTabVerticalLayoutWidget = QWidget(CasesParentCoverageTab)
            CasesParentCoverageTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

            # Box Layout for Case Parent Coverage Tab
            CasesParentCoverageTabVerticalLayout = QHBoxLayout(CasesParentCoverageTabVerticalLayoutWidget)
            CasesParentCoverageTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Data Source Label
            DataSourceLabel = QLabel()
            DataSourceLabel.setText(CasesItemName.text(0))
            DataSourceLabel.setStyleSheet("font-size: 20px;font-weight: bold; background: transparent;")
            DataSourceLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            CasesParentCoverageTabVerticalLayout.addWidget(DataSourceLabel)


            # *************************** 2nd LayoutWidget For within Case Parent Coverage Tab *************************************
            CasesParentCoverageTabVerticalLayoutWidget2 = QWidget(CasesParentCoverageTab)
            CasesParentCoverageTabVerticalLayoutWidget2.setGeometry(0,
                                                                    self.tabWidget.height() / 10,
                                                                    self.tabWidget.width()/4,
                                                                    self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Case Parent Coverage Tab
            CasesParentCoverageTabVerticalLayout2 = QVBoxLayout(CasesParentCoverageTabVerticalLayoutWidget2)

            CasesList = QListWidget(CasesParentCoverageTabVerticalLayoutWidget2)
            CasesList.setGeometry(0, 0,
                                  self.tabWidget.width()/4,
                                  self.tabWidget.height() - self.tabWidget.height() / 10)


            for cases in DS.CasesList:
                if not cases.MergedCase:
                    CasesList.addItem(cases.CaseTopic)

            # *************************** 3rd LayoutWidget For within Case Parent Coverage Tab *************************************
            CasesParentCoverageTabVerticalLayoutWidget3 = QWidget(CasesParentCoverageTab)
            CasesParentCoverageTabVerticalLayoutWidget3.setGeometry(self.tabWidget.width()*0.25,
                                                                    self.tabWidget.height()*0.1,
                                                                    self.tabWidget.width()*0.75,
                                                                    self.tabWidget.height()*0.45)
            # 3rd Box Layout for Case Parent Coverage Tab
            CasesParentCoverageTabVerticalLayout3 = QVBoxLayout(CasesParentCoverageTabVerticalLayoutWidget3)

            dummyQuery = Query()
            TempText = ""
            for cases in DS.CasesList:
                for caseText in cases.TopicCases:
                    TempText += caseText[0]

            rowList = dummyQuery.FindSimpleFrequency(TempText)

            # Table for Cases Parent Coverage
            CasesParentCoverageTable = QTableWidget(CasesParentCoverageTabVerticalLayoutWidget3)
            CasesParentCoverageTable.setColumnCount(4)
            CasesParentCoverageTable.setGeometry(0, 0,
                                                 CasesParentCoverageTabVerticalLayoutWidget3.width(),
                                                 CasesParentCoverageTabVerticalLayoutWidget3.height())
            CasesParentCoverageTable.setSizePolicy(self.sizePolicy)
            CasesParentCoverageTable.setWindowFlags(CasesParentCoverageTable.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
            CasesParentCoverageTable.setHorizontalHeaderLabels(["Word", "Length", "Frequency", "Weighted Average"])
            CasesParentCoverageTable.horizontalHeader().setStyleSheet("::section {""background-color: grey;  color: white;}")

            for i in range(CasesParentCoverageTable.columnCount()):
                CasesParentCoverageTable.horizontalHeaderItem(i).setFont(QFont("Ariel Black", 11))
                CasesParentCoverageTable.horizontalHeaderItem(i).setFont(QFont(CasesParentCoverageTable.horizontalHeaderItem(i).text(), weight=QFont.Bold))


            if len(rowList) != 0:
                for row in rowList:
                    CasesParentCoverageTable.insertRow(rowList.index(row))
                    for item in row:
                        intItem = QTableWidgetItem()
                        intItem.setData(Qt.EditRole, QVariant(item))
                        CasesParentCoverageTable.setItem(rowList.index(row), row.index(item), intItem)
                        CasesParentCoverageTable.item(rowList.index(row), row.index(item)).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        CasesParentCoverageTable.item(rowList.index(row), row.index(item)).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                CasesParentCoverageTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                CasesParentCoverageTable.resizeColumnsToContents()
                CasesParentCoverageTable.resizeRowsToContents()

                CasesParentCoverageTable.setSortingEnabled(True)
                CasesParentCoverageTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

                for i in range(CasesParentCoverageTable.columnCount()):
                    CasesParentCoverageTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

            # *************************** 4th LayoutWidget For within Case Parent Coverage Tab *************************************
            CasesParentCoverageTabVerticalLayoutWidget4 = QWidget(CasesParentCoverageTab)
            CasesParentCoverageTabVerticalLayoutWidget4.setGeometry(self.tabWidget.width()*0.25,
                                                                    self.tabWidget.height()*0.55,
                                                                    self.tabWidget.width()*0.75,
                                                                    self.tabWidget.height()*0.45)
            # 4th Box Layout for Case Parent Coverage Tab
            CasesParentCoverageTabVerticalLayout4 = QVBoxLayout(CasesParentCoverageTabVerticalLayoutWidget4)

            canvas = FigureCanvas(DS.BarCasesCoverageFigure)
            CasesParentCoverageTabVerticalLayout4.addWidget(canvas)

            if CasesParentCoverageTabFlag3:
                tabs.tabWidget = CasesParentCoverageTab
                if tabs.isActive:
                    self.tabWidget.addTab(CasesParentCoverageTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(CasesParentCoverageTab)
            else:
                if CasesParentCoverageTabFlag2:
                    tabs.setCasesLength(len(DS.CasesList))
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    self.tabWidget.addTab(CasesParentCoverageTab, tabs.TabName)
                    self.tabWidget.setCurrentWidget(CasesParentCoverageTab)
                    tabs.tabWidget = CasesParentCoverageTab
                    tabs.setisActive(True)
                else:
                    # Adding Word Cloud Tab to QTabWidget
                    dummyTab = Tab("Cases Coverage", CasesParentCoverageTab, CasesItemName.text(0))
                    dummyTab.setCasesLength(len(DS.CasesList))
                    myFile.TabList.append(dummyTab)
                    self.tabWidget.addTab(CasesParentCoverageTab, "Cases Coverage")
                    self.tabWidget.setCurrentWidget(CasesParentCoverageTab)
        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)

    # Cases Coverage Update
    def CasesParentCoverageUpdate(self, CasesItemName):
        for tabs in myFile.TabList:
            if tabs.TabName == "Cases Coverage" and tabs.DataSourceName == CasesItemName.text(0) :
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == CasesItemName.text(0):
                        break

                if self.tabWidget.indexOf(tabs.tabWidget) >= 0:
                    currentTab = self.tabWidget.currentWidget()
                    if len(DS.CasesList) > 0:
                        self.CasesParentCoverage(CasesItemName)
                        self.tabWidget.setCurrentWidget(currentTab)
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                    break

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
                for cases in DS.CasesList:
                    del cases

                DS.CasesList.clear()
                self.statusBar().showMessage('Data Source Cases Removed Successfully')
                break

        myFile.requiredSaved = True

    # Cases Parent Detail
    def CasesParentDetail(self, CasesItemName):
        CasesParentDetailDialogBox = QDialog()
        CasesParentDetailDialogBox.setModal(True)
        CasesParentDetailDialogBox.setWindowTitle("Details")
        CasesParentDetailDialogBox.setParent(self)
        CasesParentDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width / 3,
                                                    self.height / 10)
        self.QDialogAddProperties(CasesParentDetailDialogBox)

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

    # Cases Show Topic Component
    def CasesShowTopicComponent(self, CasesItemName):
        CaseShowComponentTabFlag = False
        CaseShowComponentTabFlag2 = False

        dummyParent = CasesItemName.parent()

        while dummyParent != None:
            tempParent = dummyParent
            dummyParent = dummyParent.parent()

        for tabs in myFile.TabList:
            if tabs.DataSourceName == tempParent.text(0) and tabs.TabName == 'Case Component' and tabs.tabCase == CasesItemName.text(0):
                if tabs.tabWidget != None:
                    CaseShowComponentTabFlag = True
                    break
                else:
                    CaseShowComponentTabFlag2 = True
                    break

        if not CaseShowComponentTabFlag:
            # Creating New Tab for Case Show Component
            CaseShowComponentTab = QWidget()

            # LayoutWidget For within Case Show Component Tab
            CaseShowComponentTabVerticalLayoutWidget = QWidget(CaseShowComponentTab)
            CaseShowComponentTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

            # Box Layout for Case Show Component Tab
            CaseShowComponentTabVerticalLayout = QHBoxLayout(CaseShowComponentTabVerticalLayoutWidget)
            CaseShowComponentTabVerticalLayout.setContentsMargins(0, 0, 0, 0)

            # Case Name label
            CaseNameLabel = QLabel(CaseShowComponentTabVerticalLayoutWidget)
            CaseNameLabel.setGeometry(0, 0,
                                      CaseShowComponentTabVerticalLayoutWidget.width(),
                                      CaseShowComponentTabVerticalLayoutWidget.height())
            CaseNameLabel.setText(CasesItemName.text(0))
            CaseNameLabel.setStyleSheet("font-size: 16px;font-weight: bold; background: transparent;")
            CaseNameLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

            # 2nd LayoutWidget For within Case Show Component Tab
            CaseShowComponentTabVerticalLayoutWidget2 = QWidget(CaseShowComponentTab)
            CaseShowComponentTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                                  self.tabWidget.height() - self.tabWidget.height() / 10)

            # 2nd Box Layout for Case Show Component Tab
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
                if DS.DataSourceName == tempParent.text(0):
                    for cases in DS.CasesList:
                        if cases.CaseTopic == CasesItemName.text(0):
                            Case_List = cases.TopicCases
                            break

            if len(Case_List) != 0:
                for row in Case_List:
                    CaseShowComponentTable.insertRow(Case_List.index(row))
                    for item in row:
                        if row.index(item) == 0:
                            ptext = QPlainTextEdit()
                            ptext.setReadOnly(True)
                            ptext.setPlainText(item);
                            ptext.setFixedHeight(self.tabWidget.height() / 10)
                            CaseShowComponentTable.setCellWidget(Case_List.index(row), row.index(item), ptext)
                        else:
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

            if CaseShowComponentTabFlag2:
                tabs.tabWidget = CaseShowComponentTab
                if tabs.isActive:
                    self.tabWidget.addTab(CaseShowComponentTab, tabs.TabName)
                    if tabs.isCurrentWidget:
                        self.tabWidget.setCurrentWidget(CaseShowComponentTab)
            else:
                # Adding Word Cloud Tab to QTabWidget
                dummyTab = Tab("Case Component", CaseShowComponentTab, tempParent.text(0))
                dummyTab.setTabCase(CasesItemName.text(0))
                myFile.TabList.append(dummyTab)

                self.tabWidget.addTab(CaseShowComponentTab, "Case Component")
                self.tabWidget.setCurrentWidget(CaseShowComponentTab)
                myFile.requiredSaved = True

        else:
            self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
            self.tabWidget.setCurrentWidget(tabs.tabWidget)
            tabs.setisActive(True)
            myFile.requiredSaved = True

    # Cases Show Topic Component Update
    def CasesShowTopicComponentUpdate(self, CasesItemName):
        for tabs in myFile.TabList:
            if tabs.TabName == 'Case Show Topic Component' and tabs.DataSourceName == CasesItemName.parent().text(0) and tabs.tabCase == CasesItemName.text(0):
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == CasesItemName.text(0):
                        break

                if self.tabWidget.indexOf(tabs.tabWidget) >= 0:
                    currentTab = self.tabWidget.currentWidget()
                    if len(DS.CasesList) > 0:
                        self.CasesShowTopicComponent(CasesItemName)
                        self.tabWidget.setCurrentWidget(currentTab)
                    else:
                        self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                        myFile.TabList.remove(tabs)
                    break

    # Cases Remove Component Row
    def deleteCaseComponentRow(self, CasesItemName, Table):
        button = self.sender()
        if button:
            row = Table.indexAt(button.pos()).row()
            temp = Table.cellWidget(row, 0)

            tempWidget = CasesItemName
            while tempWidget.parent() != None:
                tempWidget = tempWidget.parent()

            for DS in myFile.DataSourceList:
                if DS.DataSourceName == tempWidget.text(0):
                    for case in DS.CasesList:
                        if case.CaseTopic == CasesItemName.text(0):
                            regex = re.compile(r'[\n\r\t]')
                            for topicComponents in case.TopicCases:
                                if (regex.sub("", temp.toPlainText()) == topicComponents[0] or len(temp.toPlainText()) == len(topicComponents[0])) and row == case.TopicCases.index(topicComponents):
                                    case.TopicCases.remove(topicComponents)
                                    break

            Table.removeRow(row)

        self.CasesParentCoverageUpdate(CasesItemName)
        self.CasesStructureUpdate(CasesItemName)

        myFile.requiredSaved = True

    # Cases Rename
    def CasesRename(self, CasesItemName):
        CaseRenameDialog = QDialog()
        CaseRenameDialog.setWindowTitle("Rename")
        CaseRenameDialog.setGeometry(self.width * 0.375, self.height * 0.425, self.width / 4, self.height * 0.15)
        CaseRenameDialog.setParent(self)
        self.QDialogAddProperties(CaseRenameDialog)

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

        dummyParent = CasesItemName.parent()

        while dummyParent != None:
            tempParent = dummyParent
            dummyParent = dummyParent.parent()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == tempParent.text(0):
                for case in DS.CasesList:
                    if case.CaseTopic == CaseName:
                        CaseRenameCheck = True
                        break

        if not CaseRenameCheck:
            for DS in myFile.DataSourceList:
                if DS.DataSourceName == tempParent.text(0):
                    for case in DS.CasesList:
                        if case.CaseTopic == CasesItemName.text(0):
                            case.CaseTopic = CaseName
                            break

            CasesItemName.setText(0, CaseName)
            CasesItemName.setToolTip(0, CasesItemName.text(0))

            myFile.requiredSaved = True

            QMessageBox.information(self, "Rename Success",
                                    "Case Rename Successfully!",
                                    QMessageBox.Ok)
        else:
            QMessageBox.critical(self, "Rename Error",
                                 "A Case with Similar Name Exist!",
                                 QMessageBox.Ok)

    # Cases Remove Dialog
    def CasesChildRemoveDialog(self, CasesItemName):
        CasesRemoveChoice = QMessageBox.critical(self, 'Remove', "Are you sure you want to remove this Case?",
                                                 QMessageBox.Yes | QMessageBox.No)

        if CasesRemoveChoice == QMessageBox.Yes:
            TempParent = CasesItemName.parent()
            self.CasesChildRemove(CasesItemName)
            self.CasesParentCoverageUpdate(TempParent)
            self.CasesStructureUpdate(TempParent)
        else:
            pass

    # Cases Remove Dialog
    def CasesChildRemove(self, CasesItemName):
        tempWidget = CasesItemName
        while tempWidget.parent() != None:
            tempWidget = tempWidget.parent()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == tempWidget.text(0):
                if CasesItemName.parent().childCount() == 1:
                    TempParent = CasesItemName.parent()
                    TempParent.removeChild(CasesItemName)
                    if TempParent == tempWidget:
                        self.CasesTreeWidget.invisibleRootItem().removeChild(TempParent)
                    else:
                        TempParent.parent().removeChild(TempParent)
                else:
                    CasesItemName.parent().removeChild(CasesItemName)

                for cases in DS.CasesList:
                    if cases.CaseTopic == CasesItemName.text(0):
                        DS.CasesList.remove(cases)
                        del cases
                        break

                self.statusBar().showMessage('Case Removed Successfully')
                break

        myFile.requiredSaved = True

    # Cases Child Detail
    def CasesChildDetail(self, CasesItemName):
        CasesChildDetailDialogBox = QDialog()
        CasesChildDetailDialogBox.setModal(True)
        CasesChildDetailDialogBox.setWindowTitle("Details")
        CasesChildDetailDialogBox.setParent(self)
        CasesChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                               self.height / 5)
        self.QDialogAddProperties(CasesChildDetailDialogBox)

        tempWidget = CasesItemName

        while tempWidget.parent() != None:
            tempWidget = tempWidget.parent()

        for DS in myFile.DataSourceList:
            if DS.DataSourceName == tempWidget.text(0):
                break

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

        if case.MergedCase:
            TotalComponent = 0
            for cases2 in DS.CasesList:
                if cases2.ParentCase == case:
                    TotalComponent += len(cases2.TopicCases)
            NoofCasesLineEdit.setText(str(TotalComponent))
        else:
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
            SentimentsShowComponentTabFlag = False

            for tabs in myFile.TabList:
                if tabs.DataSourceName == SentimentsItemName.parent().text(0) and tabs.TabName == 'Sentiments Component' and tabs.tabSentiment == SentimentsItemName.text(0):
                    if tabs.tabWidget != None:
                        SentimentsShowComponentTabFlag = True
                        break
                    else:
                        SentimentsShowComponentTabFlag2 = True
                        break

            if not SentimentsShowComponentTabFlag2:
                for DS in myFile.DataSourceList:
                    if DS.DataSourceName == SentimentsItemName.parent().text(0):
                        for sentiments in DS.SentimentList:
                            if sentiments.SentimentType == SentimentsItemName.text(0):
                                Sentiments_List = sentiments.SentimentTextList
                                break

                # Creating New Tab for Sentiment Show Component
                SentimentsShowComponentTab = QWidget()

                # LayoutWidget For within Sentiments Show Component Tab
                SentimentsShowComponentTabVerticalLayoutWidget = QWidget(SentimentsShowComponentTab)
                SentimentsShowComponentTabVerticalLayoutWidget.setGeometry(0, 0, self.tabWidget.width(), self.tabWidget.height() / 10)

                # Box Layout for Sentiments Show Component Tab
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

                # 2nd LayoutWidget For within Sentiments Show Component Tab
                SentimentsShowComponentTabVerticalLayoutWidget2 = QWidget(SentimentsShowComponentTab)
                SentimentsShowComponentTabVerticalLayoutWidget2.setGeometry(0, self.tabWidget.height() / 10, self.tabWidget.width(),
                                                                      self.tabWidget.height() - self.tabWidget.height() / 10)

                # 2nd Box Layout for Sentiments Show Component Tab
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

                if SentimentsShowComponentTabFlag2:
                    tabs.tabWidget = SentimentsShowComponentTab
                    if tabs.isActive:
                        self.tabWidget.addTab(SentimentsShowComponentTab, tabs.TabName)
                        if tabs.isCurrentWidget:
                            self.tabWidget.setCurrentWidget(SentimentsShowComponentTab)
                else:
                    # Adding Word Cloud Tab to QTabWidget
                    dummyTab = Tab("Sentiments Component", SentimentsShowComponentTab, SentimentsItemName.parent().text(0))
                    dummyTab.setTabSentiment(SentimentsItemName.text(0))
                    myFile.TabList.append(dummyTab)
                    self.tabWidget.addTab(SentimentsShowComponentTab, "Sentiments Component")
                    self.tabWidget.setCurrentWidget(SentimentsShowComponentTab)
                    myFile.requiredSaved = True
            else:
                self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                self.tabWidget.setCurrentWidget(tabs.tabWidget)
                tabs.setisActive(True)
                myFile.requiredSaved = True

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

        myFile.requiredSaved = True

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

        myFile.requiredSaved = True

    # Sentiment Child Detail
    def SentimentsChildDetail(self, SentimentsItemName):
        SentimentsChildDetailDialogBox = QDialog()
        SentimentsChildDetailDialogBox.setModal(True)
        SentimentsChildDetailDialogBox.setWindowTitle("Details")
        SentimentsChildDetailDialogBox.setParent(self)
        SentimentsChildDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.4, self.width / 3,
                                              self.height / 5)
        self.QDialogAddProperties(SentimentsChildDetailDialogBox)

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
                    lambda: self.VisualizationParentRemoveDialog(VisualizationItemName))
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
                VisualizationRemove.triggered.connect(lambda: self.VisualizationParentRemoveDialog(VisualizationItemName))
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

    # Visualization Parent Remove Dialog
    def VisualizationParentRemoveDialog(self, VisualizationItemName):
        VisualizationRemoveChoice = QMessageBox.critical(self, 'Remove',
                                                        "Are you sure you want to remove this Data Source's all Visualization?",
                                                        QMessageBox.Yes | QMessageBox.No)

        if VisualizationRemoveChoice == QMessageBox.Yes:
            self.VisualizationParentRemove(VisualizationItemName)
        else:
            pass

    # Visualization Parent Remove
    def VisualizationParentRemove(self, VisualizationItemName):
        if VisualizationItemName.text(0) == 'Document Clustering':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Document Clustering':
                    myFile.TabList.remove(tabs)
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    del tabs

            self.VisualizationTreeWidget.invisibleRootItem().removeChild(VisualizationItemName)
        else:
            # Removing Tabs From TabWidget
            for tabs in myFile.TabList:
                if tabs.DataSourceName == VisualizationItemName.text(0):
                    self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                    del tabs

            # Removing Tabs From TabList
            myFile.TabList = [tabs for tabs in myFile.TabList if
                              not tabs.DataSourceName == VisualizationItemName.text(0)]

            self.VisualizationTreeWidget.invisibleRootItem().removeChild(VisualizationItemName)

        myFile.requiredSaved = True

    # Visualization Parent Detail
    def VisualizationDetail(self, VisualizationItemName):
        VisualizationDetailDialogBox = QDialog()
        VisualizationDetailDialogBox.setModal(True)
        VisualizationDetailDialogBox.setWindowTitle("Details")
        VisualizationDetailDialogBox.setParent(self)
        VisualizationDetailDialogBox.setGeometry(self.width * 0.35, self.height * 0.45, self.width / 3,
                                               self.height / 10)
        self.QDialogAddProperties(VisualizationDetailDialogBox)

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

        for VisualTreeItems in self.VisualizationTreeWidget.findItems(DS.DataSourceName, Qt.MatchExactly, 0):
            DataSourceNoofVisualizationLineEdit.setText(str(VisualTreeItems.childCount()))

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
            if tabs.DataSourceName == VisualizationItemName.parent().text(0) and tabs.TabName == VisualizationItemName.text(0):
                myFile.TabList.remove(tabs)
                self.tabWidget.removeTab(self.tabWidget.indexOf(tabs.tabWidget))
                del tabs
                break

        if VisualizationItemName.parent().childCount() == 1:
            tempParent = VisualizationItemName.parent()
            tempParent.removeChild(VisualizationItemName)
            self.VisualizationTreeWidget.invisibleRootItem().removeChild(tempParent)
        else:
            VisualizationItemName.parent().removeChild(VisualizationItemName)

        myFile.requiredSaved = True

    # Preview Visual/Tab on double click
    def VisualizationDoubleClickHandler(self, VisualizationItemName):
        if VisualizationItemName.text(0) == 'Document Clustering':
            for tabs in myFile.TabList:
                if tabs.TabName == 'Document Clustering':
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                        tabs.setisActive(True)
                    break
        else:
            for tabs in myFile.TabList:
                if tabs.DataSourceName == VisualizationItemName.parent().text(0) and tabs.TabName == VisualizationItemName.text(0):
                    if self.tabWidget.currentWidget() != tabs.tabWidget:
                        self.tabWidget.addTab(tabs.tabWidget, tabs.TabName)
                        self.tabWidget.setCurrentWidget(tabs.tabWidget)
                        tabs.setisActive(True)
                        break

        myFile.requiredSaved = True

    # ****************************************************************************
    # *********************** Application Basic Features *************************
    # ****************************************************************************

    # Close Application / Exit
    def closeEvent(self, event):
        if myFile.requiredSaved:
            SaveBeforeNewWindowOpenchoice = QMessageBox.question(self, 'Exit', "Are you Sure you want to exit without Saving?", QMessageBox.No | QMessageBox.Yes | QMessageBox.Cancel)
            if SaveBeforeNewWindowOpenchoice == QMessageBox.No:
                self.SaveASWindow()
                if not myFile.requiredSaved:
                    event.accept()
                else:
                    self.closeEvent(event)
            elif SaveBeforeNewWindowOpenchoice == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # Open New File
    def NewFileWindow(self):
        if myFile.requiredSaved:
            SaveBeforeNewWindowOpenchoice = QMessageBox.question(self, 'Save', "You have made changes. Do you want to discard or save them?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if SaveBeforeNewWindowOpenchoice == QMessageBox.Save:
                self.SaveASWindow()
                if not myFile.requiredSaved:
                    self.EmptyWindowForNewFile()
                else:
                    self.NewFileWindow()
            elif SaveBeforeNewWindowOpenchoice == QMessageBox.Discard:
                self.EmptyWindowForNewFile()
            else:
                pass

    # Empty Window For New File
    def EmptyWindowForNewFile(self):
        global myFile
        DataSourceNameList = [DS.DataSourceName for DS in myFile.DataSourceList]

        for DataSourceName in DataSourceNameList:
            for widgets in self.DataSourceTreeWidget.findItems(DataSourceName, Qt.MatchRecursive, 0):
                self.DataSourceRemove(widgets)

        myFile = File()
        myFile.setCreatedDate(datetime.datetime.now())
        myFile.setCreatedBy(getpass.getuser())

    # Open File
    def OpenFileWindow(self):
        dummyWindow = OpenWindow("Open File", "TextWiz File *.twiz", -1)
        path = dummyWindow.filepath
        del dummyWindow

        if all(path):
            global myFile

            if not myFile.requiredSaved:
                if hasattr(myFile, "FileLocation") and hasattr(myFile, "FileName"):
                    self.EmptyWindowForNewFile()
                else:
                    pass
            else:
                SaveBeforeOpenWindowchoice = QMessageBox.question(self, 'Open File',
                                                                  "You have made changes. Do you want to discard or save them?",
                                                                  QMessageBox.Save | QMessageBox.Discard)
                if SaveBeforeOpenWindowchoice == QMessageBox.Save:
                    self.SaveASWindow()
                    if not myFile.requiredSaved:
                        self.EmptyWindowForNewFile()
                    else:
                        return

                elif SaveBeforeOpenWindowchoice == QMessageBox.Discard:
                    pass

                self.EmptyWindowForNewFile()

            myFile = pickle.load(open(path[0], "rb"))
            myFile.setFileLocation(path[0])

            # Setting Data Sources
            for DS in myFile.DataSourceList:
                if DS.DataSourceext == "Doc files (*.doc *.docx)" or DS.DataSourceext == "Pdf files (*.pdf)" or DS.DataSourceext == "Notepad files (*.txt)" or DS.DataSourceext == "Rich Text Format files (*.rtf)" or DS.DataSourceext == "Audio files (*.wav *.mp3)" or DS.DataSourceext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":
                    # Adding Node to Data Source Tree Widget

                    # Word File
                    if DS.DataSourceext == "Doc files (*.doc *.docx)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.wordTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")
                        if self.wordTreeWidget.isHidden():
                            self.wordTreeWidget.setHidden(False)
                            self.wordTreeWidget.setExpanded(True)
                        newNode.setToolTip(0, newNode.text(0))

                    # PDF File
                    elif DS.DataSourceext == "Pdf files (*.pdf)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.pdfTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")
                        if self.pdfTreeWidget.isHidden():
                            self.pdfTreeWidget.setHidden(False)
                            self.pdfTreeWidget.setExpanded(True)
                        newNode.setToolTip(0, newNode.text(0))

                    # Text File
                    elif DS.DataSourceext == "Notepad files (*.txt)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.txtTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")
                        if self.txtTreeWidget.isHidden():
                            self.txtTreeWidget.setHidden(False)
                            self.txtTreeWidget.setExpanded(True)
                        newNode.setToolTip(0, newNode.text(0))

                    # RTF File
                    elif DS.DataSourceext == "Rich Text Format files (*.rtf)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.rtfTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")

                        if self.rtfTreeWidget.isHidden():
                            self.rtfTreeWidget.setHidden(False)

                        newNode.setToolTip(0, newNode.text(0))

                    # Audio File
                    elif DS.DataSourceext == "Audio files (*.wav *.mp3)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.audioSTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")

                        if self.audioSTreeWidget.isHidden():
                            self.audioSTreeWidget.setHidden(False)
                            self.audioSTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))

                    # Image File
                    elif DS.DataSourceext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":

                        # Adding Node to Data Source Tree Widget
                        newNode = QTreeWidgetItem(self.ImageSTreeWidget)
                        newNode.setText(0, DS.DataSourceName)
                        self.ImageSTreeWidget.setText(0, "Image" + "(" + str(self.ImageSTreeWidget.childCount()) + ")")

                        if self.ImageSTreeWidget.isHidden():
                            self.ImageSTreeWidget.setHidden(False)
                            self.ImageSTreeWidget.setExpanded(True)

                        newNode.setToolTip(0, newNode.text(0))

                    # Adding Cases
                    if (len(DS.CasesList) > 0):
                        DSCaseWidget = QTreeWidgetItem(self.CasesTreeWidget)
                        DSCaseWidget.setText(0, DS.DataSourceName)
                        DSCaseWidget.setExpanded(True)

                        self.SetCasesWidget(DS, DSCaseWidget)

                    # Adding Sentiments
                    NewWidgetAddFlagList = []

                    for sentiments in DS.SentimentList:
                        if len(sentiments.SentimentTextList) == 0:
                            NewWidgetAddFlagList.append(True)
                        else:
                            NewWidgetAddFlagList.append(False)

                    if not all([v for v in NewWidgetAddFlagList]):
                        # Adding Sentiments
                        DSSentimentWidget = QTreeWidgetItem(self.SentimentTreeWidget)
                        DSSentimentWidget.setText(0, DS.DataSourceName)
                        DSSentimentWidget.setToolTip(0, DSSentimentWidget.text(0))
                        DSSentimentWidget.setExpanded(True)

                        for sentiments in DS.SentimentList:
                            DSNewSentimentNode = QTreeWidgetItem(DSSentimentWidget)
                            DSNewSentimentNode.setText(0, sentiments.SentimentType)

                # CSV File
                elif DS.DataSourceext == "CSV files (*.csv)":

                    # Adding Node to Data Source Tree Widget
                    newNode = QTreeWidgetItem(self.CSVTreeWidget)
                    newNode.setText(0, DS.DataSourceName)
                    self.CSVTreeWidget.setText(0, "CSV" + "(" + str(self.CSVTreeWidget.childCount()) + ")")

                    if self.CSVTreeWidget.isHidden():
                        self.CSVTreeWidget.setHidden(False)
                        self.CSVTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

                # URL
                elif DS.DataSourceext == "URL":

                    # Adding Node to Data Source Tree Widget
                    newNode = QTreeWidgetItem(self.WebTreeWidget)
                    newNode.setText(0, DS.DataSourceName)
                    self.WebTreeWidget.setText(0, "Web" + "(" + str(self.WebTreeWidget.childCount()) + ")")

                    if self.WebTreeWidget.isHidden():
                        self.WebTreeWidget.setHidden(False)
                        self.WebTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

                # Tweet
                elif DS.DataSourceext == "Tweet":

                    # Adding Node to Data Source Tree Widget
                    newNode = QTreeWidgetItem(self.TweetTreeWidget)
                    newNode.setText(0, DS.DataSourceName)
                    self.TweetTreeWidget.setText(0, "Tweet" + "(" + str(self.TweetTreeWidget.childCount()) + ")")

                    if self.TweetTreeWidget.isHidden():
                        self.TweetTreeWidget.setHidden(False)
                        self.TweetTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

                # Youtube
                elif DS.DataSourceext == "Youtube":

                    # Adding Node to Data Source Tree Widget
                    newNode = QTreeWidgetItem(self.YoutubeTreeWidget)
                    newNode.setText(0, DS.DataSourceName)
                    self.YoutubeTreeWidget.setText(0, "Youtube" + "(" + str(self.YoutubeTreeWidget.childCount()) + ")")

                    if self.YoutubeTreeWidget.isHidden():
                        self.YoutubeTreeWidget.setHidden(False)
                        self.YoutubeTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

            # Setting tabs
            for tabs in myFile.TabList:
                # Data Sources Similarity
                if tabs.TabName == "Data Sources Similarity":
                    self.DataSourcesSimilarity()

                # Document Clustering
                elif tabs.TabName == "Document Clustering":
                    self.DataSourceDocumentClustering()

                # Web Preview
                elif tabs.TabName == "Web Preview":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourcePreviewWeb(widgets)

                # Show Tweet Data
                elif tabs.TabName == "Show Tweet Data":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourceShowTweetData(widgets)

                # Show Video
                elif tabs.TabName == "Show Video":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        for DS in myFile.DataSourceList:
                            if DS.DataSourceName == tabs.DataSourceName:
                                if DS.YoutubeURLFlag:
                                    self.DataSourceYoutubeShowVideo(widgets)

                # Show Youtube Data
                elif tabs.TabName == "Show Youtube Data":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        for DS in myFile.DataSourceList:
                            if DS.DataSourceName == tabs.DataSourceName:
                                if DS.YoutubeURLFlag:
                                    self.DataSourceShowYoutubeCommentsURL(widgets)
                                else:
                                    self.DataSourceShowYoutubeCommentsKeyWord(widgets)
                                break

                # View Image
                elif tabs.TabName == "View Image":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourceViewImage(widgets)

                # CSV Data
                elif tabs.TabName == "CSV Data":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourceViewCSVData(widgets)

                # Preview
                elif tabs.TabName == "Preview":
                    for DS in myFile.DataSourceList:
                        if DS.DataSourceName == tabs.DataSourceName:
                            break

                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        if DS.DataSourceext == "Pdf files (*.pdf)":
                            self.DataSourcePDFPreview(widgets)

                        elif DS.DataSourceext == "Doc files (*.doc *.docx)":
                            self.DataSourceWordPreview(widgets)

                        elif DS.DataSourceext == 'Notepad files (*.txt)' or DS.DataSourceext == 'Rich Text Format files (*.rtf)':
                            self.DataSourcePreview(widgets)

                # Word Frequency
                elif tabs.TabName == "Word Frequency":
                    self.DataSourceShowFrequencyTable(tabs.DataSourceName)

                # Generate Questions
                elif tabs.TabName == "Generate Questions":
                    self.DataSourcesGenerateQuestions(tabs.DataSourceName)

                # Automatic Sentiment Analysis
                elif tabs.TabName == "Automatic Sentiment Analysis":
                    self.SentimentAnalysisTable(tabs.DataSourceName, tabs.AutomaticSentimentAnalysisColumnName)

                # Stem Word
                elif tabs.TabName == "Stem Word":
                    self.mapStemWordonTab(tabs.DataSourceName, tabs.StemWord)

                # Parts of Speech
                elif tabs.TabName == "Parts of Speech":
                    self.DataSourcePOS(tabs.DataSourceName)

                # Entity Relationship
                elif tabs.TabName == "Entity Relationship":
                    self.DataSourceEntityRelationShip(tabs.DataSourceName)

                # Topic Modelling
                elif tabs.TabName == "Topic Modelling":
                    self.DataSourceTopicModelling(tabs.DataSourceName)

                # Create Cases
                elif tabs.TabName == "Create Cases":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourceCreateCases(widgets)

                # Create Sentiments
                elif tabs.TabName == "Create Sentiments":
                    for widgets in self.DataSourceTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.DataSourceCreateSentiments(widgets)

                # Translated Text
                elif tabs.TabName == "Translated Text":
                    self.DataSourceTranslate(tabs.DataSourceName, tabs.TranslatedLanguage)

                # Word Cloud
                elif tabs.TabName == "Word Cloud":
                    self.mapWordCloudonTab(tabs.DataSourceName, tabs.WordCloudBGColor, tabs.WordCloudMaxWords, tabs.WordCloudMask)

                # Word Tree
                elif tabs.TabName == "Word Tree":
                    self.DataSourceWordTree(tabs.DataSourceName)

                # Survey Analysis
                elif tabs.TabName == "Survey Analysis":
                    self.DataSourceSurveyAnalysis(tabs.DataSourceName, tabs.SurveyAnalysisChartList, None)

                # Tweet Analysis
                elif tabs.TabName == "Tweet Analysis":
                    self.DataSourceTweetAnalysis(tabs.DataSourceName)

                # Coordinate Map
                elif tabs.TabName == "Coordinate Map":
                    self.DataSourceCoordinateMap(tabs.DataSourceName)

                # Cases Structure
                elif tabs.TabName == "Cases Structure":
                    for widgets in self.CasesTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.CasesStructure(widgets)

                # Cases Coverage
                elif tabs.TabName == "Cases Coverage":
                    for widgets in self.CasesTreeWidget.findItems(tabs.DataSourceName, Qt.MatchRecursive, 0):
                        self.CasesParentCoverage(widgets)

                # Case Component
                elif tabs.TabName == "Case Component":
                    CasesItemWidgets = self.CasesTreeWidget.findItems(tabs.tabCase, Qt.MatchRecursive, 0)

                    if len(CasesItemWidgets) > 0:
                        ItemPresentFlag = False
                        for items in CasesItemWidgets:
                            tempWidget = items
                            while tempWidget.parent() != None:
                                tempWidget = tempWidget.parent()

                            if tempWidget.text(0) == tabs.DataSourceName:
                                ItemPresetFlag = True
                                break

                        if ItemPresentFlag:
                            self.CasesShowTopicComponent(items)

                # Sentiments Component
                elif tabs.TabName == "Sentiments Component":
                    SentimentItemWidgets = self.SentimentTreeWidget.findItems(tabs.tabSentiment, Qt.MatchRecursive, 0)

                    if len(SentimentItemWidgets) > 0:
                        ItemPresentFlag = False
                        for items in SentimentItemWidgets:
                            tempWidget = items
                            while tempWidget.parent() != None:
                                tempWidget = tempWidget.parent()

                            if tempWidget.text(0) == tabs.DataSourceName:
                                ItemPresetFlag = True
                                break

                        if ItemPresentFlag:
                            self.SentimentsShowComponent(items)

    # Save File Window
    def SaveWindow(self):
        if hasattr(myFile, "FileLocation") and hasattr(myFile, "FileName"):
            self.Save()
        else:
            self.SaveASWindow()

    # SaveASWindow
    def SaveASWindow(self):
        dummyWindow = OpenWindow("Open File", "TextWiz File *.twiz", 1)
        path = dummyWindow.filepath
        del dummyWindow

        if all(path):
            myFile.setFileLocation(path[0])
            myFile.setFileName(ntpath.basename(path[0]))
            self.Save()

    # Save
    def Save(self):
        myFile.setModifiedDate(datetime.datetime.now())
        myFile.setModifiedBy(getpass.getuser())
        myFile.requiredSaved = False

        SaveFile = open(myFile.FileLocation, 'wb')

        for tabs in myFile.TabList:
            if self.tabWidget.currentWidget() == tabs.tabWidget:
                tabs.setCurrentWidget(True)
            else:
                tabs.setCurrentWidget(False)

        dummyTabList = []

        for i in range(len(myFile.TabList)):
            dummyTabList.append(myFile.TabList[i].tabWidget)

        for tabs in myFile.TabList:
            tabs.tabWidget = None

        pickle.dump(myFile, SaveFile)

        for i in range(len(myFile.TabList)):
            myFile.TabList[i].tabWidget = dummyTabList[i]

        self.statusBar().showMessage("File Saved...")

    # ProgressBar
    def ProgressBar(self, ProgressBarWidget, progressBar, ProgressBarLabel):
        # ProgressBar Widget
        if ProgressBarLabel == "Importing" or ProgressBarLabel == "Retrieving Tweets":
            ProgressBarWidget.setGeometry(self.width * 0.375, self.height * 0.4875,
                                          self.width * 0.25, self.height * 0.025)
        else:
            ProgressBarWidget.setGeometry((self.width - self.tabWidget.width()) +  self.tabWidget.width()* 0.375,
                                          (self.height - self.horizontalLayoutWidget.height()) + self.tabWidget.height()*0.4875,
                                          self.tabWidget.width() * 0.25,
                                          self.tabWidget.height() * 0.025)

        ProgressBarWidget.setParent(self)
        ProgressBarWidget.setAttribute(Qt.WA_DeleteOnClose)
        self.QDialogAddProperties(ProgressBarWidget)
        ProgressBarWidget.setWindowFlags(ProgressBarWidget.windowFlags() | Qt.FramelessWindowHint)

        # ProgressBar
        progressBar.setGeometry(0, 0, ProgressBarWidget.width(), ProgressBarWidget.height())
        progressBar.setMaximum(0)
        progressBar.setMinimum(0)

        # ProgressBarLabel
        progressBarLabel = QLabel(ProgressBarWidget)
        progressBarLabel.setGeometry(0, 0, ProgressBarWidget.width(), ProgressBarWidget.height())
        progressBarLabel.setStyleSheet("background-color: rgba(0,0,0,0%)");
        progressBarLabel.setText(ProgressBarLabel + "...")
        progressBarLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.LabelSizeAdjustment(progressBarLabel)

        ProgressBarWidget.exec_()

    # Print Window
    def printWindow(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        self.Printdialog = QtPrintSupport.QPrintDialog(printer, self)
        self.Printdialog.setWindowTitle('Print')
        self.Printdialog.setGeometry(self.width * 0.25, self.height * 0.25, self.width/2, self.height/2)

        if self.Printdialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            if self.tabWidget.currentWidget() is not None:
                pixmap = QPixmap(self.tabWidget.currentWidget().size())
                self.tabWidget.currentWidget().render(pixmap)
                pixmap.print_(printer)

    # Hide ToolBar
    def toolbarHide(self):
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    # Hide Left Sources
    def LeftPaneHide(self, label, TreeWidget):
        if label.isHidden() and TreeWidget.isHidden():
            label.show()
            TreeWidget.show()
        else:
            label.hide()
            TreeWidget.hide()

    # QDialogAddProperties
    def QDialogAddProperties(self, Dialog):
        if WindowPlatform:
            Dialog.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        elif LinuxPlatform:
            Dialog.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.Tool)
            Dialog.setFixedSize(Dialog.width(), Dialog.height())

    # License Window
    def LicenseWindow(self):
        file = open('LICENSE', 'r')
        lic = file.read()
        QMessageBox().about(self, "License", lic)

    # License Window
    def AboutWindow(self):
        QMessageBox().about(self,
                            "About TextWiz",
                            '''
                            <h2 style="text-align:center">TextWiz For Windows</h2>
                            <br>
                            <p style="text-align:center;font-size:40px">Version 1.0.0 (32 Bit)</p>
                            <br>
                            <p style="text-align:center;font-size:20px">Edition: Community</p>
                            <br>
                            <p style="text-align:center;font-size:40px">Copyright @ 1999-2015 QRS International</p>
                            <br>
                            <p style="text-align:center;font-size:40px">Ptv Ltd. All rights reserved</p>
                            <a href='https://www.google.com/'>TextWiz</a>
                            '''
                            );

    # ****************************************************************************
    # *************************** Import Features ********************************
    # ****************************************************************************

    # Import DataSource Window
    def ImportFileWindow(self, check):
        if check == "Word":
            dummyWindow = OpenWindow("Open Word File", "Doc files (*.doc *.docx)", 0)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                for pth in path[0]:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(ntpath.basename(pth), "Importing")
                    dummyProgressInfo.ImportFile(pth, path[1])

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                    del dummyProgressInfo

                    dummyDataSource = ThreadQueue.get()

                    DataSourceNameCheck = False

                    for DS in myFile.DataSourceList:
                        if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                            DataSourceNameCheck = True

                    if not DataSourceNameCheck:
                        if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                            myFile.setDataSources(dummyDataSource)
                            newNode = QTreeWidgetItem(self.wordTreeWidget)
                            newNode.setText(0, ntpath.basename(pth))
                            self.wordTreeWidget.setText(0, "Word" + "(" + str(self.wordTreeWidget.childCount()) + ")")

                            if self.wordTreeWidget.isHidden():
                                self.wordTreeWidget.setHidden(False)
                                self.wordTreeWidget.setExpanded(True)

                            newNode.setToolTip(0, newNode.text(0))

                            self.statusBar().showMessage('Word File Uploaded')

                            self.DataSourceSimilarityUpdate()
                            self.DataSourceDocumentClusteringUpdate()

                            myFile.requiredSaved = True
                        else:
                            if len(dummyDataSource.DataSourcetext) == 0 and not dummyDataSource.DataSourceLoadError:
                                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                    dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                    QMessageBox.Ok)
                            elif dummyDataSource.DataSourceLoadError:
                                QMessageBox.critical(self, "Load Error",
                                                    "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                     QMessageBox.Ok)
                            del dummyDataSource
                    else:
                        del dummyDataSource
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                            QMessageBox.Ok)

        elif check == "PDF":
            dummyWindow = OpenWindow("Open PDF File", "Pdf files (*.pdf)", 0)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                for pth in path[0]:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(ntpath.basename(pth), "Importing")
                    dummyProgressInfo.ImportFile(pth, path[1])

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                    del dummyProgressInfo

                    dummyDataSource = ThreadQueue.get()

                    DataSourceNameCheck = False

                    for DS in myFile.DataSourceList:
                        if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                            DataSourceNameCheck = True

                    if not DataSourceNameCheck:
                        if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                            myFile.setDataSources(dummyDataSource)
                            if not dummyDataSource.DataSourceLoadError:
                                newNode = QTreeWidgetItem(self.pdfTreeWidget)
                                newNode.setText(0, ntpath.basename(pth))
                                self.pdfTreeWidget.setText(0, "PDF" + "(" + str(self.pdfTreeWidget.childCount()) + ")")

                                if self.pdfTreeWidget.isHidden():
                                    self.pdfTreeWidget.setHidden(False)
                                    self.pdfTreeWidget.setExpanded(True)

                                newNode.setToolTip(0, newNode.text(0))
                                self.statusBar().showMessage('PDF File Uploaded')
                                self.DataSourceSimilarityUpdate()
                                self.DataSourceDocumentClusteringUpdate()

                                myFile.requiredSaved = True
                            else:
                                del dummyDataSource
                        else:
                            if len(dummyDataSource.DataSourcetext) == 0:
                                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                    dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                    QMessageBox.Ok)
                            elif dummyDataSource.DataSourceLoadError:
                                QMessageBox.critical(self, "Load Error",
                                                    "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                     QMessageBox.Ok)
                            del dummyDataSource
                    else:
                        del dummyDataSource
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                            QMessageBox.Ok)

        elif check == "Txt":
            dummyWindow = OpenWindow("Open Notepad File", "Notepad files (*.txt)", 0)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                for pth in path[0]:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(ntpath.basename(pth), "Importing")
                    dummyProgressInfo.ImportFile(pth, path[1])

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                    del dummyProgressInfo

                    dummyDataSource = ThreadQueue.get()

                    DataSourceNameCheck = False

                    for DS in myFile.DataSourceList:
                        if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                            DataSourceNameCheck = True

                    if not DataSourceNameCheck:
                        if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                            myFile.setDataSources(dummyDataSource)
                            newNode = QTreeWidgetItem(self.txtTreeWidget)
                            newNode.setText(0, ntpath.basename(pth))
                            self.txtTreeWidget.setText(0, "Text" + "(" + str(self.txtTreeWidget.childCount()) + ")")

                            if self.txtTreeWidget.isHidden():
                                self.txtTreeWidget.setHidden(False)
                                self.txtTreeWidget.setExpanded(True)

                            newNode.setToolTip(0, newNode.text(0))

                            self.statusBar().showMessage('Text File Uploaded')

                            self.DataSourceSimilarityUpdate()
                            self.DataSourceDocumentClusteringUpdate()

                            myFile.requiredSaved = True
                        else:
                            if len(dummyDataSource.DataSourcetext) == 0:
                                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                QMessageBox.Ok)
                            elif dummyDataSource.DataSourceLoadError:
                                QMessageBox.critical(self, "Load Error",
                                                    "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                     QMessageBox.Ok)
                            del dummyDataSource
                    else:
                        del dummyDataSource
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                            QMessageBox.Ok)

        elif check == "RTF":
            dummyWindow = OpenWindow("Open Rich Text Format File", "Rich Text Format files (*.rtf)", 0)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                for pth in path[0]:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(ntpath.basename(pth), "Importing")
                    dummyProgressInfo.ImportFile(pth, path[1])

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                    del dummyProgressInfo

                    dummyDataSource = ThreadQueue.get()

                    DataSourceNameCheck = False

                    for DS in myFile.DataSourceList:
                        if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                            DataSourceNameCheck = True

                    if not DataSourceNameCheck:
                        if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                            myFile.setDataSources(dummyDataSource)
                            newNode = QTreeWidgetItem(self.rtfTreeWidget)
                            newNode.setText(0, ntpath.basename(pth))
                            self.rtfTreeWidget.setText(0, "RTF" + "(" + str(self.rtfTreeWidget.childCount()) + ")")

                            if self.rtfTreeWidget.isHidden():
                                self.rtfTreeWidget.setHidden(False)

                            newNode.setToolTip(0, newNode.text(0))

                            self.statusBar().showMessage('RTF File Uploaded')

                            self.DataSourceSimilarityUpdate()
                            self.DataSourceDocumentClusteringUpdate()

                            myFile.requiredSaved = True
                        else:
                            if len(dummyDataSource.DataSourcetext) == 0:
                                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                QMessageBox.Ok)
                            elif dummyDataSource.DataSourceLoadError:
                                QMessageBox.critical(self, "Load Error",
                                                     "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                     QMessageBox.Ok)
                            del dummyDataSource
                    else:
                        del dummyDataSource
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                            QMessageBox.Ok)

        elif check == "Sound":
            dummyWindow = OpenWindow("Open Audio File", "Audio files (*.wav *.mp3)", 0)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                for pth in path[0]:
                    ProgressBarWidget = QDialog()
                    progressBar = QProgressBar(ProgressBarWidget)

                    dummyProgressInfo = ProgressInfo(ntpath.basename(pth), "Importing")
                    dummyProgressInfo.ImportFile(pth, path[1])

                    ThreadQueue.put(dummyProgressInfo)

                    self.myLongTask = TaskThread()
                    self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                    self.myLongTask.start()

                    self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                    del dummyProgressInfo

                    dummyDataSource = ThreadQueue.get()

                    DataSourceNameCheck = False

                    for DS in myFile.DataSourceList:
                        if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                            DataSourceNameCheck = True

                    if not DataSourceNameCheck:
                        if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                            myFile.setDataSources(dummyDataSource)
                            newNode = QTreeWidgetItem(self.audioSTreeWidget)
                            newNode.setText(0, ntpath.basename(pth))
                            self.audioSTreeWidget.setText(0, "Audio" + "(" + str(self.audioSTreeWidget.childCount()) + ")")

                            if self.audioSTreeWidget.isHidden():
                                self.audioSTreeWidget.setHidden(False)
                                self.audioSTreeWidget.setExpanded(True)

                            newNode.setToolTip(0, newNode.text(0))

                            self.statusBar().showMessage('Audio File Uploaded')

                            self.DataSourceSimilarityUpdate()
                            self.DataSourceDocumentClusteringUpdate()

                            myFile.requiredSaved = True
                        else:
                            if len(dummyDataSource.DataSourcetext) == 0:
                                DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                                dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                                QMessageBox.Ok)
                            elif dummyDataSource.DataSourceLoadError:
                                QMessageBox.critical(self, "Load Error",
                                                     "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                     QMessageBox.Ok)
                            del dummyDataSource
                    else:
                        del dummyDataSource
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                            QMessageBox.Ok)

        elif check == "Image":
            dummyWindow = OpenWindow("Open Image File",
                                     "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)",
                                     2)
            path = dummyWindow.filepath
            del dummyWindow

            if all(path):
                ProgressBarWidget = QDialog()
                progressBar = QProgressBar(ProgressBarWidget)

                dummyProgressInfo = ProgressInfo(ntpath.basename(path[0][0]), "Importing")
                dummyProgressInfo.ImportFile(path[0], path[1])

                ThreadQueue.put(dummyProgressInfo)

                self.myLongTask = TaskThread()
                self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
                self.myLongTask.start()

                self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

                del dummyProgressInfo

                dummyDataSource = ThreadQueue.get()

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
                        self.statusBar().showMessage('Image File Uploaded')

                        self.DataSourceSimilarityUpdate()
                        self.DataSourceDocumentClusteringUpdate()

                        myFile.requiredSaved = True
                    else:
                        if len(dummyDataSource.DataSourcetext) == 0:
                            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
                        elif dummyDataSource.DataSourceLoadError:
                            QMessageBox.critical(self, "Load Error",
                                                 "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                                 QMessageBox.Ok)
                        del dummyDataSource
                else:
                    del dummyDataSource
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                        QMessageBox.Ok)

    # Import CSV Window
    def ImportCSVWindowDialog(self):
        CSVDialog = QDialog()
        CSVDialog.setWindowTitle("Import CSV File")
        CSVDialog.setGeometry(self.width * 0.375, self.height * 0.3, self.width / 3, self.height *0.4)
        CSVDialog.setParent(self)
        CSVDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.QDialogAddProperties(CSVDialog)

        # CSV Path Radio Button
        PathRadioButton = QRadioButton(CSVDialog)
        PathRadioButton.setGeometry(CSVDialog.width() * 0.1, CSVDialog.height() * 0.1,
                                    CSVDialog.width() / 5, CSVDialog.height() / 10)
        PathRadioButton.setText("Computer")
        PathRadioButton.adjustSize()

        # CSV Path LineEdit
        CSVPathLineEdit = QLineEdit(CSVDialog)
        CSVPathLineEdit.setGeometry(CSVDialog.width() * 0.15, CSVDialog.height() * 0.2,
                                    CSVDialog.width() * 0.5, CSVDialog.height() / 10)
        CSVPathLineEdit.setReadOnly(True)
        CSVPathLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(CSVPathLineEdit)

        # CSV Browse Button
        CSVBrowseButton = QPushButton(CSVDialog)
        CSVBrowseButton.setText("Browse")
        CSVBrowseButton.setGeometry(CSVDialog.width() * 0.8, CSVDialog.height() * 0.2,
                                    CSVDialog.width() / 10, CSVDialog.height() / 10)
        CSVBrowseButton.setEnabled(False)
        self.LineEditSizeAdjustment(CSVBrowseButton)

        # CSV URL Radio Button
        URLPathRadioButton = QRadioButton(CSVDialog)
        URLPathRadioButton.setGeometry(CSVDialog.width() * 0.1, CSVDialog.height() * 0.3,
                                       CSVDialog.width() / 5, CSVDialog.height() / 10)
        URLPathRadioButton.setText("URL")
        URLPathRadioButton.adjustSize()

        # CSV URL Path LineEdit
        CSVURLPathLineEdit = QLineEdit(CSVDialog)
        CSVURLPathLineEdit.setGeometry(CSVDialog.width() * 0.15, CSVDialog.height() * 0.4,
                                       CSVDialog.width() * 0.7, CSVDialog.height() / 10)
        CSVURLPathLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(CSVURLPathLineEdit)

        # CSV Header CheckBox
        CSVHeaderCheckBox = QCheckBox(CSVDialog)
        CSVHeaderCheckBox.setChecked(True)
        CSVHeaderCheckBox.setText("Contains Header")
        CSVHeaderCheckBox.setGeometry(CSVDialog.width() * 0.1, CSVDialog.height() * 0.6,
                                      CSVDialog.width() / 10, CSVDialog.height() / 10)
        CSVHeaderCheckBox.adjustSize()

        # CSV ButtonBox
        CSVbuttonBox = QDialogButtonBox(CSVDialog)
        CSVbuttonBox.setGeometry(CSVDialog.width() * 0.6, CSVDialog.height() * 0.75,
                                 CSVDialog.width() / 3, CSVDialog.height() / 10)
        CSVbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        CSVbuttonBox.button(QDialogButtonBox.Ok).setText('Import')
        CSVbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(CSVbuttonBox)

        CSVBrowseButton.clicked.connect(lambda: self.CSVBrowseButtonAction(CSVPathLineEdit))
        CSVPathLineEdit.textChanged.connect(lambda: self.OkButtonEnable(CSVbuttonBox, True))
        CSVURLPathLineEdit.textChanged.connect(lambda: self.OkButtonEnable(CSVbuttonBox, True))

        PathRadioButton.toggled.connect(lambda: self.EnableOkonCSVRadioButtonToggle(URLPathRadioButton, CSVPathLineEdit, CSVURLPathLineEdit, CSVBrowseButton, CSVbuttonBox))
        URLPathRadioButton.toggled.connect(lambda: self.EnableOkonCSVRadioButtonToggle(PathRadioButton, CSVURLPathLineEdit, CSVPathLineEdit, CSVBrowseButton, CSVbuttonBox))

        CSVbuttonBox.accepted.connect(CSVDialog.accept)
        CSVbuttonBox.rejected.connect(CSVDialog.reject)

        CSVbuttonBox.accepted.connect(lambda: self.ImportFromCSV(CSVPathLineEdit.text(), CSVURLPathLineEdit.text(), PathRadioButton.isChecked(), CSVHeaderCheckBox.isChecked()))

        CSVDialog.exec_()

    # CSV Browse
    def CSVBrowseButtonAction(self, LineEdit):
        dummyWindow = OpenWindow("Open CSV File", "CSV files (*.csv)", -1)
        LineEdit.setText(dummyWindow.filepath[0])
        del dummyWindow

    # Import From CSV
    def ImportFromCSV(self, CSVPath, CSVURLPath, CSVPathFlag, CSVHeader):
        if CSVPathFlag:
            dummyDataSource = DataSource(CSVPath, "CSV files (*.csv)")
        else:
            dummyDataSource = DataSource(CSVURLPath, "CSV files (*.csv)")
        DataSourceNameCheck = False

        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            ProgressBarWidget = QDialog()
            progressBar = QProgressBar(ProgressBarWidget)

            dummyProgressInfo = ProgressInfo("CSV", "Importing")
            dummyProgressInfo.ImportCSVFile(CSVHeader, CSVPathFlag, dummyDataSource)

            ThreadQueue.put(dummyProgressInfo)

            self.myLongTask = TaskThread()
            self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
            self.myLongTask.start()

            self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

            del dummyProgressInfo

            dummyDataSource = ThreadQueue.get()

            if not dummyDataSource.DataSourceLoadError and not len(dummyDataSource.CSVData.index) == 0:
                myFile.setDataSources(dummyDataSource)
                newNode = QTreeWidgetItem(self.CSVTreeWidget)
                if CSVPathFlag:
                    newNode.setText(0, ntpath.basename(CSVPath))
                else:
                    newNode.setText(0, ntpath.basename(CSVURLPath))

                self.statusBar().showMessage('CSV File Uploaded')
                self.CSVTreeWidget.setText(0, "CSV" + "(" + str(self.CSVTreeWidget.childCount()) + ")")

                if self.CSVTreeWidget.isHidden():
                    self.CSVTreeWidget.setHidden(False)
                    self.CSVTreeWidget.setExpanded(True)

                newNode.setToolTip(0, newNode.text(0))

                self.DataSourceSimilarityUpdate()
                self.DataSourceDocumentClusteringUpdate()
                myFile.requiredSaved = True
            else:
                if len(dummyDataSource.CSVData.index) == 0 and not dummyDataSource.DataSourceLoadError:
                    DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                        dummyDataSource.DataSourceName + " doesnot contains any row",
                                                                        QMessageBox.Ok)
                elif dummyDataSource.DataSourceHTTPError:
                    QMessageBox.critical(self, "Load Error",
                                         "Error 404: \n CSV URL Not found!",
                                         QMessageBox.Ok)

                elif dummyDataSource.DataSourceLoadError:
                    QMessageBox.critical(self, "Load Error",
                                         "Any Error occurred. There was a Problem, the File " + dummyDataSource.DataSourceName + " is Unable to load",
                                         QMessageBox.Ok)


                del dummyDataSource
        else:
            del dummyDataSource
            DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                "A Data Source with Similar Name Exist! Please Rename the File then try Again",
                                                                QMessageBox.Ok)

    # Import Tweet Window
    def ImportTweetWindow(self):
        TweetDialog = QDialog()
        TweetDialog.setWindowTitle("Import From Twitter")
        TweetDialog.setGeometry(self.width * 0.35, self.height * 0.35, self.width * 0.3, self.height * 0.3)
        TweetDialog.setParent(self)
        TweetDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.QDialogAddProperties(TweetDialog)

        # Tweet HashTag Label
        TweetHashtagLabel = QLabel(TweetDialog)
        TweetHashtagLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.1,
                                      TweetDialog.width() / 5, TweetDialog.height() / 10)
        TweetHashtagLabel.setText("Hastag")
        self.LabelSizeAdjustment(TweetHashtagLabel)

        # Tweet Date Label
        DateLabel = QLabel(TweetDialog)
        DateLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.3,
                              TweetDialog.width() / 5, TweetDialog.height() / 10)
        DateLabel.setText("Since")
        self.LabelSizeAdjustment(DateLabel)

        # No. of Tweets Label
        NTweetLabel = QLabel(TweetDialog)
        NTweetLabel.setGeometry(TweetDialog.width() * 0.2, TweetDialog.height() * 0.5,
                                TweetDialog.width() / 5, TweetDialog.height() / 10)
        NTweetLabel.setText("No of Tweets")
        self.LabelSizeAdjustment(NTweetLabel)

        # Twitter HashTag LineEdit
        TweetHashtagLineEdit = QLineEdit(TweetDialog)
        TweetHashtagLineEdit.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.1,
                                         TweetDialog.width() * 0.3, TweetDialog.height() / 10)
        TweetHashtagLineEdit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.LineEditSizeAdjustment(TweetHashtagLineEdit)

        # Tweet Since Date
        DateCalendar = QDateEdit(TweetDialog)
        DateCalendar.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.3,
                                 TweetDialog.width() * 0.3, TweetDialog.height() / 10)
        DateCalendar.setCalendarPopup(True)
        DateCalendar.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        DateCalendar.setMaximumDate(QDate(datetime.datetime.today()))
        DateCalendar.setMinimumDate(datetime.datetime.now() - datetime.timedelta(days=365))
        DateCalendar.setDate(datetime.datetime.today())
        self.LineEditSizeAdjustment(DateCalendar)

        # Tweet No Label
        NTweetLineEdit = QDoubleSpinBox(TweetDialog)
        NTweetLineEdit.setGeometry(TweetDialog.width() * 0.5, TweetDialog.height() * 0.5,
                                   TweetDialog.width() * 0.3, TweetDialog.height() / 10)
        NTweetLineEdit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        NTweetLineEdit.setDecimals(0)
        NTweetLineEdit.setMinimum(10)
        NTweetLineEdit.setMaximum(1000)
        self.LineEditSizeAdjustment(NTweetLineEdit)

        # TweetDialog ButtonBox
        TweetbuttonBox = QDialogButtonBox(TweetDialog)
        TweetbuttonBox.setGeometry(TweetDialog.width() * 0.4, TweetDialog.height() * 0.75,
                                   TweetDialog.width() * 0.4, TweetDialog.height() / 10)
        TweetbuttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        TweetbuttonBox.button(QDialogButtonBox.Ok).setText('Get')
        TweetbuttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.LineEditSizeAdjustment(TweetbuttonBox)

        TweetHashtagLineEdit.textChanged.connect(lambda: self.GetButtonEnableTweet(TweetbuttonBox))

        TweetbuttonBox.accepted.connect(TweetDialog.accept)
        TweetbuttonBox.rejected.connect(TweetDialog.reject)

        TweetbuttonBox.accepted.connect(
            lambda: self.ImportFromTweet(str(TweetHashtagLineEdit.text()),
                                         str(DateCalendar.text()),
                                         NTweetLineEdit.text()))

        TweetDialog.exec_()

    # Import From Tweet
    def ImportFromTweet(self, Hashtag, Since, NoOfTweet):
        dummyDataSource = DataSource(Hashtag, "Tweet")
        DataSourceNameCheck = False

        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            ProgressBarWidget = QDialog()
            progressBar = QProgressBar(ProgressBarWidget)

            dummyProgressInfo = ProgressInfo("Tweet", "Importing")
            dummyProgressInfo.ImportTweetFile(Hashtag, Since, NoOfTweet, dummyDataSource)

            ThreadQueue.put(dummyProgressInfo)

            self.myLongTask = TaskThread()
            self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
            self.myLongTask.start()

            self.ProgressBar(ProgressBarWidget, progressBar, "Retrieving Tweets")

            del dummyProgressInfo

            dummyDataSource = ThreadQueue.get()

            if not dummyDataSource.DataSourceLoadError:
                if not dummyDataSource.DataSourceRetrieveZeroError:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.TweetTreeWidget)
                    newNode.setText(0, Hashtag)
                    self.statusBar().showMessage('Tweet with Hashtag Imported')
                    self.TweetTreeWidget.setText(0, "Tweet" + "(" + str(self.TweetTreeWidget.childCount()) + ")")

                    if self.TweetTreeWidget.isHidden():
                        self.TweetTreeWidget.setHidden(False)
                        self.TweetTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))
                    self.DataSourceSimilarityUpdate()
                    myFile.requiredSaved = True
                else:
                    del dummyDataSource
                    DataSourceImportNameErrorBox = QMessageBox.information(self, "Import Error",
                                                                        "No Tweet Found with Hashtag : " + Hashtag,
                                                                        QMessageBox.Ok)
            else:
                del dummyDataSource
                DataSourceImportNameErrorBox = QMessageBox.information(self, "Import Error",
                                                                       "TextWiz is unable to retrive any tweet",
                                                                       QMessageBox.Ok)
        else:
            del dummyDataSource
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
        self.QDialogAddProperties(URLDialog)

        # URL Label
        URLLabel = QLabel(URLDialog)
        URLLabel.setGeometry(URLDialog.width() * 0.1, URLDialog.height() * 0.3,
                             URLDialog.width()/10 , URLDialog.height() / 10)
        URLLabel.setText("URL")
        self.LabelSizeAdjustment(URLLabel)

        # URL LineEdit
        URLLineEdit = QLineEdit(URLDialog)
        URLLineEdit.setGeometry(URLDialog.width() * 0.25, URLDialog.height() * 0.3,
                                URLDialog.width() * 0.7, URLDialog.height() /10)
        URLLineEdit.setAlignment(Qt.AlignVCenter)
        self.LineEditSizeAdjustment(URLLineEdit)

        # URL ButtonBox
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
        ProgressBarWidget = QDialog()
        progressBar = QProgressBar(ProgressBarWidget)

        dummyProgressInfo = ProgressInfo(URL, "Importing")
        dummyProgressInfo.ImportFile(URL, "URL")

        ThreadQueue.put(dummyProgressInfo)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(lambda: ProgressBarWidget.close())
        self.myLongTask.start()

        self.ProgressBar(ProgressBarWidget, progressBar, "Importing")

        del dummyProgressInfo

        dummyDataSource = ThreadQueue.get()
        DataSourceNameCheck = False

        for DS in myFile.DataSourceList:
            if DS != dummyDataSource and DS.DataSourceName == dummyDataSource.DataSourceName:
                DataSourceNameCheck = True

        if not DataSourceNameCheck:
            if not dummyDataSource.DataSourceLoadError:
                if not dummyDataSource.DataSourceForbiddenLoadError and not len(dummyDataSource.DataSourcetext) == 0:
                    myFile.setDataSources(dummyDataSource)
                    newNode = QTreeWidgetItem(self.WebTreeWidget)
                    newNode.setText(0, URL)
                    self.WebTreeWidget.setText(0, "Web" + "(" + str(self.WebTreeWidget.childCount()) + ")")

                    if self.WebTreeWidget.isHidden():
                        self.WebTreeWidget.setHidden(False)
                        self.WebTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

                    self.DataSourceSimilarityUpdate()
                    self.DataSourceDocumentClusteringUpdate()
                    myFile.requiredSaved = True
                else:
                    if dummyDataSource.DataSourceForbiddenLoadError:
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            "HTTP Error 403: Forbidden\n" +
                                                                            dummyDataSource.DataSourceName + " is not accessible",
                                                                            QMessageBox.Ok)

                    elif dummyDataSource.DataSourcetext == 0:
                        DataSourceImportNameErrorBox = QMessageBox.critical(self, "Import Error",
                                                                            dummyDataSource.DataSourceName + " doesnot contains any text",
                                                                            QMessageBox.Ok)
            elif dummyDataSource.DataSourceLoadError:
                if hasattr(dummyDataSource, "DataSourceURLHTTPError") or hasattr(dummyDataSource, "DataSourceURLConnectionError") or hasattr(dummyDataSource, "DataSourceURLMissingSchema"):
                    QMessageBox.critical(self, "URL Error",
                                         dummyDataSource.DataSoureURLErrorMessage,
                                         QMessageBox.Ok)
                del dummyDataSource
        else:
            del dummyDataSource
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
        self.QDialogAddProperties(YoutubeDialog)

        # Youtube URL Radio Button
        VideoURLRadioButton = QRadioButton(YoutubeDialog)
        VideoURLRadioButton.setGeometry(YoutubeDialog.width() * 0.1, YoutubeDialog.height() * 0.2,
                                       YoutubeDialog.width() / 5, YoutubeDialog.height() / 10)
        VideoURLRadioButton.setText("Video URL")

        # Youtube URL LineEdit
        URLLineEdit = QLineEdit(YoutubeDialog)
        URLLineEdit.setGeometry(YoutubeDialog.width() * 0.3, YoutubeDialog.height() * 0.2,
                                YoutubeDialog.width() * 0.6, YoutubeDialog.height() / 10)
        URLLineEdit.setAlignment(Qt.AlignVCenter)
        URLLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(URLLineEdit)

        # Youtube Keyword Radio Button
        KeyWordRadioButton = QRadioButton(YoutubeDialog)
        KeyWordRadioButton.setGeometry(YoutubeDialog.width() * 0.1, YoutubeDialog.height() * 0.4,
                                       YoutubeDialog.width() / 5, YoutubeDialog.height() / 10)
        KeyWordRadioButton.setText("Key Word")
        KeyWordRadioButton.adjustSize()

        # Twitter KeyWord LineEdit
        KeyWordLineEdit = QLineEdit(YoutubeDialog)
        KeyWordLineEdit.setGeometry(YoutubeDialog.width() * 0.6, YoutubeDialog.height() * 0.4,
                                    YoutubeDialog.width() * 0.3, YoutubeDialog.height() / 10)
        KeyWordLineEdit.setAlignment(Qt.AlignVCenter)
        KeyWordLineEdit.setEnabled(False)
        self.LineEditSizeAdjustment(KeyWordLineEdit)

        # Youtube ButtonBox
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
            dummyDataSource = DataSource(URL, "Youtube")
            dummyDataSource.YoutubeURL()
            DataSourceNameCheck = False

        elif KeyWordCheck:
            dummyDataSource = DataSource(KeyWord, "Youtube")
            dummyDataSource.YoutubeKeyWord()
            DataSourceNameCheck = False

        if VideoURLCheck or (KeyWordCheck and not dummyDataSource.YoutubeServerNotFoundError):

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

                    self.statusBar().showMessage('Youtube Comments Imported')

                    self.YoutubeTreeWidget.setText(0, "Youtube" + "(" + str(self.YoutubeTreeWidget.childCount()) + ")")

                    if self.YoutubeTreeWidget.isHidden():
                        self.YoutubeTreeWidget.setHidden(False)
                        self.YoutubeTreeWidget.setExpanded(True)

                    newNode.setToolTip(0, newNode.text(0))

                    self.DataSourceSimilarityUpdate()
                    self.DataSourceDocumentClusteringUpdate()
                    myFile.requiredSaved = True

                elif dummyDataSource.DataSourceLoadError:
                    if VideoURLCheck:
                        QMessageBox.critical(self, "Youtube Error",
                                            "Unable to Retrieve Comments from URL: " + dummyDataSource.DataSourcePath,
                                             QMessageBox.Ok)
                    else:
                        QMessageBox.critical(self, "Youtube Error",
                                             "Unable to Retrieve Comments of Key Word: " + dummyDataSource.DataSourcePath,
                                             QMessageBox.Ok)

                elif len(dummyDataSource.YoutubeData) == 0:
                    if VideoURLCheck:
                        QMessageBox.critical(self, "Import Error",
                                             "No Youtube comment Retreive From the URL: " + URL,
                                             QMessageBox.Ok)
                    else:
                        QMessageBox.critical(self, "Import Error",
                                             "No comment Retreive of Key Word: " + KeyWord,
                                             QMessageBox.Ok)
                    del dummyDataSource

            else:
                del dummyDataSource

                if VideoURLCheck:
                    QMessageBox.critical(self, "Import Error",
                                         "A Youtube Source with Similar URL Exist!",
                                         QMessageBox.Ok)
                else:
                    QMessageBox.critical(self, "Import Error",
                                         "A Youtube Source with Similar KeyWord Exist!",
                                         QMessageBox.Ok)

        else:
            QMessageBox.critical(self, "Import Error",
                                 "When the application started you were not connected to the internet. Please Restart the application and make sure you are connected to the internet",
                                 QMessageBox.Ok)

if __name__ == "__main__":
    WindowTitleLogo = "Images/TextWizLogo.png"
    myFile = File()
    myFile.setCreatedDate(datetime.datetime.now())
    myFile.setCreatedBy(getpass.getuser())

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
    TextWizMainwindow.StopWordFileExistence()

    sys.exit(App.exec())