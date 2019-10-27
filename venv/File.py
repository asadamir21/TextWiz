from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
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


    def CreateWordCloud(self, text):
        currdir = path.dirname(__file__)
        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open(path.join(currdir, "Images/cloud.png")))

        # create set of stopwords
        stopwords = set(STOPWORDS)

        # create wordcloud object
        wc = WordCloud(background_color="white",
                       max_words=200,
                       mask=mask,
                       stopwords=stopwords)

        # generate wordcloud
        wc.generate(text)

        # save wordcloud
        wc.to_file(path.join(currdir, "wc.png"))



class DataSource(File):
    def __init__(self, path, ext):
        super().__init__()
        self.DataSourcePath = path
        self.DataSourceName = ntpath.basename(path)
        self.DataSourceext = ext
        self.DataSourcetext = ""
        self.DataSourceLoadError = False

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

    def __del__(self):
        self.DataSourceDelete = True