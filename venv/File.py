from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from threading import *
from PIL import  Image
from wordcloud import WordCloud, STOPWORDS
from stat import *
from pyglet import *

import numpy as np
import matplotlib
import re
import nltk
import ntpath, pyglet
import docx2txt, PyPDF2
import os, time

import pyautogui, qstylizer.style


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

        for DataSourceIndex in self.DataSourceList:
            if DataSourceIndex.DataSourcePath == myDataSource.DataSourcePath:
                myDataSource.DataSourceLoadError = True
                isAvailable = True
                break



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
        wc.generate(tempDS.DataSourcetext)

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

        self.MainWindow = MainWindow

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
            self.DataSourcetext = docx2txt.process(self.DataSourcePath)
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

    def onIntReady(self, availablecc):  # This method receives the list from the worker
        print('availablecc', availablecc)  # This is for debugging reasons to verify that I receive the list with the correct content
        self.availablecc = availablecc

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

    def Animation(self, name):
        try:
            loadingGIF = pyglet.image.load_animation("Loading gifs/"+ name)
            loadingGIFSprite = pyglet.sprite.Sprite(loadingGIF)

            self.myLoadingDialog = QDialog()
            self.myLoadingDialog.setModal(True)
            self.myLoadingDialog.setParent(self.MainWindow)

            LoadingGifMovie = QMovie()
            LoadingGifMovie.setFileName("Loading gifs/" + name)

            gifWidth = loadingGIFSprite.width
            gifheight = loadingGIFSprite.height

            self.myLoadingDialog.setGeometry(pyautogui.size().width / 2 - gifWidth / 2,
                                             pyautogui.size().height / 2 - gifheight / 2, gifWidth, gifheight)
            self.myLoadingDialog.setAttribute(Qt.WA_TranslucentBackground)
            self.myLoadingDialog.setWindowFlags(Qt.FramelessWindowHint)

            movie_screen = QLabel()

            # Make label fit the gif
            movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            movie_screen.setAlignment(Qt.AlignCenter)

            main_layout = QVBoxLayout()
            main_layout.addWidget(movie_screen)

            css = qstylizer.style.StyleSheet()
            css.setValues(backgroundColor="transparent")
            self.myLoadingDialog.setStyleSheet(css.toString())
            self.myLoadingDialog.setLayout(main_layout)

            # Add the QMovie object to the label
            LoadingGifMovie.setCacheMode(QMovie.CacheAll)
            LoadingGifMovie.setSpeed(100)
            movie_screen.setMovie(LoadingGifMovie)
            LoadingGifMovie.start()

            self.myLoadingDialog.exec_()

        except Exception as e:
            print(str(e))

    def setQuery(self, QueryTreeWidgetItem, TabItem):
        self.QueryList.append([QueryTreeWidgetItem, TabItem])

    def __del__(self):
        self.DataSourceDelete = True


class Tab(File):
    def __init__(self, tabName, tabWidget, DataSourceName):
        self.TabName = tabName
        self.tabWidget = tabWidget
        self.DataSourceName = DataSourceName

    def __del__(self):
        self.TabDelete = True


class Query():
    def GenerateFrequencyList(self, match_pattern):
            frequency = {}

            for word in match_pattern:
                count = frequency.get(word, 0)
                frequency[word] = count + 1


            frequency_list = frequency.keys()

            return frequency_list,frequency

    def find_exact_word(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list,frequency = self.GenerateFrequencyList(match_pattern)


        count = 0;
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def FindWordFrequency(self, DataSourceText):
        WordFrequencyRow = []

        DataSourceTextLower = DataSourceText

        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)

        total_count = 0;

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            weighted_percentage = round((frequency[words]/total_count)*100,2)
            WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage])


        return WordFrequencyRow

    def FindStemmedWords(self, StemWord, DataSourceText):
        StemWordList = []

        DataSourceTextLower = DataSourceText.lower()

        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)

        porter = PorterStemmer()

        stem_word = porter.stem(StemWord)

        count = 0;
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                StemWordList.append([words, count])

        return StemWordList

    def GetDistinctWords(self, DataSourceText):
        DataSourceTextLower = DataSourceText.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)
        return frequency_list



class Animation(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(list)

    def __init__(self, name, MainWindow):
        super().__init__()
        self.name = name
        self.MainWindow = MainWindow

    def run(self):
        try:
            self.myLoadingDialog = QDialog()

            loadingGIF = pyglet.image.load_animation("Loading gifs/" + self.name)
            loadingGIFSprite = pyglet.sprite.Sprite(loadingGIF)

            self.myLoadingDialog.setParent(self.MainWindow)
            self.myLoadingDialog.setModal(True)

            LoadingGifMovie = QMovie()
            LoadingGifMovie.setFileName("Loading gifs/" + self.name)

            gifWidth = loadingGIFSprite.width
            gifheight = loadingGIFSprite.height

            self.myLoadingDialog.setGeometry(pyautogui.size().width / 2 - gifWidth / 2,
                                             pyautogui.size().height / 2 - gifheight / 2, gifWidth, gifheight)
            self.myLoadingDialog.setAttribute(Qt.WA_TranslucentBackground)
            self.myLoadingDialog.setWindowFlags(Qt.FramelessWindowHint)

            movie_screen = QLabel()
            # Make label fit the gif
            movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            movie_screen.setAlignment(Qt.AlignCenter)

            main_layout = QVBoxLayout()
            main_layout.addWidget(movie_screen)

            css = qstylizer.style.StyleSheet()
            css.setValues(backgroundColor="transparent")
            self.myLoadingDialog.setStyleSheet(css.toString())
            self.myLoadingDialog.setLayout(main_layout)

            # Add the QMovie object to the label
            LoadingGifMovie.setCacheMode(QMovie.CacheAll)
            LoadingGifMovie.setSpeed(100)
            movie_screen.setMovie(LoadingGifMovie)
            LoadingGifMovie.start()
            self.myLoadingDialog.exec()

        except Exception as e:
            print(str(e))

    def stop(self):
        self.terminate()



