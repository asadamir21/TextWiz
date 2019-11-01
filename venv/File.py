from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib
import threading
import ntpath
from PIL import  Image
from wordcloud import WordCloud, STOPWORDS
import pyglet
from pyglet import *
import docx2txt
import PyPDF2
import os
import time
from stat import *
import pyautogui
import qstylizer.style

class File():
    def __init__(self):
        super().__init__()
        self.DataSourceList = []
        self.WordCloudBackgroundList = []
        self.TabList = []
        self.setBackGroundList()

    def setFileName(self, name):
        self.FileName = name

    def setFileLocation(self, path):
        self.FileLocation = path

    def setCreatedDate(self, date):
        self.CreatedDate = date

    def setModifiedDate(self, date):
        self.ModifiedDate = date

    def setModifiedBy(self, name):
        self.ModifiedBy = name

    def setDataSources(self, myDataSource):
        isAvailable = False

        try:
            for DataSourceIndex in self.DataSourceList:
                if DataSourceIndex.DataSourcePath == myDataSource.DataSourcePath:
                    myDataSource.DataSourceLoadError = True
                    isAvailable = True
                    break

        except Exception as e:
            print(str(e))

        if not isAvailable:
            self.DataSourceList.append(myDataSource)
        else:
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Information)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText(myDataSource.DataSourceName + " is Already Added")
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

    def setBackGroundList(self):
        for colorname,colorhex in matplotlib.colors.cnames.items():
            self.WordCloudBackgroundList.append(colorname)


    def CreateWordCloud(self, WCDSName, WCBGColor, maxword, maskname):
        for WCDS in self.DataSourceList:
            if WCDS.DataSourceName == WCDSName:
                tempDS = WCDS
                break

        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open("Word Cloud Maskes/" + maskname + ".png"))

        # create wordcloud object
        wc = WordCloud(background_color=WCBGColor, max_words=int(maxword), mask=mask, stopwords=set(STOPWORDS))

        # generate wordcloud
        wc.generate(WCDS.DataSourcetext)

        return wc.to_image()


class DataSource(File):
    def __init__(self, path, ext, MainWindow):
        super().__init__()
        self.DataSourcePath = path
        self.DataSourceName = ntpath.basename(path)
        self.DataSourceext = ext
        self.DataSourcetext = ""
        self.DataSourceLoadError = False
        self.QueryList = []
        try:
            self.MainWindow = MainWindow
        except Exception as e:
            print(str(e))


        if(ext == "Doc files (*.doc *.docx)"):
            self.WordDataSource()
        elif(ext == "Pdf files (*.pdf)"):
            self.PDFDataSource()
        elif (ext == "Notepad files (*.txt)"):
            self.TxtDataSource()
        elif (ext == "Rich Text Format files (*.rtf)"):
            self.rtfDataSource()
        elif (ext == "Audio files (*.wav *.mp3)"):
            self.AudioDataSource()

    def WordDataSource(self):
        try:
            # try:
            #     AnimationEvent = threading.Event()
            #     Animationthread = threading.Thread(name='blocking', target=self.Animation, args=(AnimationEvent,))
            #     Animationthread.run()
            #
            #
            # except Exception as e:
            #     print(str(e))

            self.DataSourcetext = docx2txt.process(self.DataSourcePath)
            self.DataSourceLoadError = False

            #AnimationEvent.set()

        except Exception as e:
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Critical)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText("Any Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load")
            DataSourceLoadErrorBox.setDetailedText(str(e))
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

        if not self.DataSourceLoadError:
            st = os.stat(self.DataSourcePath)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))

    def PDFDataSource(self):
        try:
            pdfReader = PyPDF2.PdfFileReader(self.DataSourcePath)
            for page in range(pdfReader.getNumPages()):
                curr_page = pdfReader.getPage(page)
                self.DataSourcetext = self.DataSourcetext + curr_page.extractText()

            self.DataSourceLoadError = False
        except Exception as e:
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Critical)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText("An Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load")
            DataSourceLoadErrorBox.setDetailedText(str(e))
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

        if not self.DataSourceLoadError:
            st = os.stat(self.DataSourcePath)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))


    def TxtDataSource(self):
        try:
            file = open(self.DataSourcePath, 'r')
            self.DataSourcetext = file.read();
            self.DataSourceLoadError = False
        except Exception as e:
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Critical)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText("Any Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load")
            DataSourceLoadErrorBox.setDetailedText(str(e))
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

        if not self.DataSourceLoadError:
            st = os.stat(self.DataSourcePath)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))


    def rtfDataSource(self):
        try:
            file = open(self.DataSourcePath, 'r')
            self.DataSourcetext = file.read();
            print(self.DataSourcetext)
            self.DataSourceLoadError = False
        except Exception as e:
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Critical)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText("Any Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load")
            DataSourceLoadErrorBox.setDetailedText(str(e))
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

        if not self.DataSourceLoadError:
            st = os.stat(self.DataSourcePath)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))


    def AudioDataSource(self):
        try:
            self.DataSourceLoadError = False
        except Exception as e:
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Critical)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText("Any Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load")
            DataSourceLoadErrorBox.setDetailedText(str(e))
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

        if not self.DataSourceLoadError:
            st = os.stat(self.DataSourcePath)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))

    def setNode(self, WidgetItemNode):
        self.DataSourceTreeWidgetItemNode = WidgetItemNode

    def Animation(self, AnimationEvent):
        loadingGIF = pyglet.image.load_animation("Loading gifs/Loading.gif")
        loadingGIFSprite = pyglet.sprite.Sprite(loadingGIF)

        myLoadingDialog = QDialog()
        myLoadingDialog.setParent(self.MainWindow)
        myLoadingDialog.setModal(True)

        LoadingGifMovie = QMovie()
        LoadingGifMovie.setFileName("Loading gifs/Loading.gif")

        gifWidth = loadingGIFSprite.width
        gifheight = loadingGIFSprite.height

        myLoadingDialog.setGeometry(pyautogui.size().width / 2 - gifWidth / 2,
                                    pyautogui.size().height / 2 - gifheight / 2, gifWidth, gifheight)
        myLoadingDialog.setAttribute(Qt.WA_TranslucentBackground)
        myLoadingDialog.setWindowFlags(Qt.FramelessWindowHint)

        movie_screen = QLabel()
        # Make label fit the gif
        movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        movie_screen.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(movie_screen)

        css = qstylizer.style.StyleSheet()
        css.setValues(backgroundColor="transparent")
        myLoadingDialog.setStyleSheet(css.toString())
        myLoadingDialog.setLayout(main_layout)

        # Add the QMovie object to the label
        LoadingGifMovie.setCacheMode(QMovie.CacheAll)
        LoadingGifMovie.setSpeed(100)
        movie_screen.setMovie(LoadingGifMovie)
        LoadingGifMovie.start()

        myLoadingDialog.exec_()

    def setQuery(self):
        print("Hello World")


    def __del__(self):
        self.DataSourceDelete = True





class Tab(File):
    def __init__(self, tabName, tabWidget):
        self.TabName = tabName
        self.tabWidget = tabWidget


    def __del__(self):
        self.TabDelete = True
