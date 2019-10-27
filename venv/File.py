from PyQt5.QtWidgets import *
import numpy as np
import ntpath
from PIL import  Image
from wordcloud import WordCloud, STOPWORDS
import docx2txt
import PyPDF2
import os
import time
from stat import *


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
        self.DataSourceList.append(myDataSource)

    def CreateWordCloud(self, text):
        currdir = path.dirname(__file__)
        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open(path.join(currdir, "cloud.png")))

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
            self.WordDataSource(path)
        elif(ext == "Pdf files (*.pdf)"):
            self.PDFDataSource(path)
        elif (ext == "Notepad files (*.txt)"):
            self.TxtDataSource(path)
        elif (ext == "Rich Text Format files (*.rtf)"):
            self.rtfDataSource(path)
        elif (ext == "Audio files (*.wav *.mp3)"):
            self.AudioDataSource(path)



    def WordDataSource(self, path):
        try:
            self.DataSourceText = docx2txt.process(path)
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
            st = os.stat(path)
            self.DataSourceSize = st[ST_SIZE]
            self.DataSourceAccessTime = time.asctime(time.localtime(st[ST_ATIME]))
            self.DataSourceModifiedTime = time.asctime(time.localtime(st[ST_MTIME]))
            self.DataSourceChangeTime = time.asctime(time.localtime(st[ST_CTIME]))




    def PDFDataSource(self, path):
        print("Hello World")

    def TxtDataSource(self, path):
        print("Hello World")

    def rtfDataSource(self, path):
        print("Hello World")

    def AudioDataSource(self, path):
        print("Hello World")

    def __del__(self):
        self.DataSourceDelete = True