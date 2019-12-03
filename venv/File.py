from builtins import print, dict

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from threading import *
from PIL import Image
from gensim import *
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from wordcloud import WordCloud, STOPWORDS
from anytree import Node, RenderTree, PreOrderIter, exporter
from sklearn.feature_extraction.text import TfidfVectorizer
from stat import *
from PIL import *
from pyglet import *
from Cases import *
from Sentiments import *
from spacy import displacy
from urllib.parse import urlparse
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
from spacy.lang.en import English
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import pickle
import pyLDAvis.gensim
import urllib
import datetime
import requests
import cv2
import pytesseract

import en_core_web_sm
import numpy as np
import matplotlib
import re
import nltk
import ntpath, pyglet
import docx2txt, PyPDF2
import os, time
import spacy
import tweepy
import csv
import pandas as pd

import pyautogui, qstylizer.style

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

class File():
    def __init__(self):
        super().__init__()
        self.DataSourceList = []
        self.TabList = []

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

    #Data Source Similarity
    def FindSimilarityBetweenDataSource(self):
        SimilarityCorpus = []

        for DS in self.DataSourceList:
            SimilarityCorpus.append(DS.DataSourcetext)

        vect = TfidfVectorizer(min_df=1, stop_words="english")
        tfidf = vect.fit_transform(SimilarityCorpus)
        pairwise_similarity = tfidf * tfidf.T

        high = pairwise_similarity.toarray().tolist()

        highlist = []

        for row in range(len(high)):
            for column in range(len(high[row])):
                if row != column and row < column:

                    column2 = round(high[row][column] * 100, 5)

                    for DS in self.DataSourceList:
                        if SimilarityCorpus[column] == DS.DataSourcetext:
                            index = DS.DataSourceName

                    for DS in self.DataSourceList:
                        if SimilarityCorpus[row] == DS.DataSourcetext:
                            index2 = DS.DataSourceName

                    dummylist = [index, index2, column2]
                    highlist.append(dummylist)

        highlist = sorted(highlist, key=lambda l: l[2], reverse=True)

        return highlist

    #Data Source Similar Phrases
    def FindSimilarPhrases(self):
        print("Hello World")

class DataSource(File):
    def __init__(self, path, ext, MainWindow):
        super().__init__()
        self.DataSourcePath = path

        if ext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":
            self.DataSourceName = ntpath.basename(path[0])
        elif ext == "URL" or ext ==  'Tweet':
            self.DataSourceName = path
        else:
            self.DataSourceName = ntpath.basename(path)

        self.DataSourceext = ext
        self.DataSourcetext = ""
        self.DataSourceLoadError = False
        self.QueryList = []
        self.CasesList = []
        self.SentimentList = []
        self.MainWindow = MainWindow

        if(ext == "Doc files (*.doc *.docx)"):
            self.WordDataSource()
        elif(ext == "Pdf files (*.pdf)"):
            self.PDFDataSource()
        elif(ext == "Notepad files (*.txt)"):
            self.TxtDataSource()
        elif(ext == "Rich Text Format files (*.rtf)"):
            self.rtfDataSource()
        elif(ext == "Audio files (*.wav *.mp3)"):
            self.AudioDataSource()
        elif(ext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)"):
            self.ImageDataSource()
        elif(ext == 'URL'):
            self.WebDataSource()

    # Word File
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

    # PDF File
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

    # TXT File
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

    # RTF File
    def rtfDataSource(self):
        try:
            file = open(self.DataSourcePath, 'r')
            self.DataSourcetext = self.RTFtoPlainText(file.read())
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

    # RTFtoPlainText
    def RTFtoPlainText(self, text):
        pattern = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
        # control words which specify a "destionation".
        destinations = frozenset((
            'aftncn', 'aftnsep', 'aftnsepc', 'annotation', 'atnauthor', 'atndate', 'atnicn', 'atnid',
            'atnparent', 'atnref', 'atntime', 'atrfend', 'atrfstart', 'author', 'background',
            'bkmkend', 'bkmkstart', 'blipuid', 'buptim', 'category', 'colorschememapping',
            'colortbl', 'comment', 'company', 'creatim', 'datafield', 'datastore', 'defchp', 'defpap',
            'do', 'doccomm', 'docvar', 'dptxbxtext', 'ebcend', 'ebcstart', 'factoidname', 'falt',
            'fchars', 'ffdeftext', 'ffentrymcr', 'ffexitmcr', 'ffformat', 'ffhelptext', 'ffl',
            'ffname', 'ffstattext', 'field', 'file', 'filetbl', 'fldinst', 'fldrslt', 'fldtype',
            'fname', 'fontemb', 'fontfile', 'fonttbl', 'footer', 'footerf', 'footerl', 'footerr',
            'footnote', 'formfield', 'ftncn', 'ftnsep', 'ftnsepc', 'g', 'generator', 'gridtbl',
            'header', 'headerf', 'headerl', 'headerr', 'hl', 'hlfr', 'hlinkbase', 'hlloc', 'hlsrc',
            'hsv', 'htmltag', 'info', 'keycode', 'keywords', 'latentstyles', 'lchars', 'levelnumbers',
            'leveltext', 'lfolevel', 'linkval', 'list', 'listlevel', 'listname', 'listoverride',
            'listoverridetable', 'listpicture', 'liststylename', 'listtable', 'listtext',
            'lsdlockedexcept', 'macc', 'maccPr', 'mailmerge', 'maln', 'malnScr', 'manager', 'margPr',
            'mbar', 'mbarPr', 'mbaseJc', 'mbegChr', 'mborderBox', 'mborderBoxPr', 'mbox', 'mboxPr',
            'mchr', 'mcount', 'mctrlPr', 'md', 'mdeg', 'mdegHide', 'mden', 'mdiff', 'mdPr', 'me',
            'mendChr', 'meqArr', 'meqArrPr', 'mf', 'mfName', 'mfPr', 'mfunc', 'mfuncPr', 'mgroupChr',
            'mgroupChrPr', 'mgrow', 'mhideBot', 'mhideLeft', 'mhideRight', 'mhideTop', 'mhtmltag',
            'mlim', 'mlimloc', 'mlimlow', 'mlimlowPr', 'mlimupp', 'mlimuppPr', 'mm', 'mmaddfieldname',
            'mmath', 'mmathPict', 'mmathPr', 'mmaxdist', 'mmc', 'mmcJc', 'mmconnectstr',
            'mmconnectstrdata', 'mmcPr', 'mmcs', 'mmdatasource', 'mmheadersource', 'mmmailsubject',
            'mmodso', 'mmodsofilter', 'mmodsofldmpdata', 'mmodsomappedname', 'mmodsoname',
            'mmodsorecipdata', 'mmodsosort', 'mmodsosrc', 'mmodsotable', 'mmodsoudl',
            'mmodsoudldata', 'mmodsouniquetag', 'mmPr', 'mmquery', 'mmr', 'mnary', 'mnaryPr',
            'mnoBreak', 'mnum', 'mobjDist', 'moMath', 'moMathPara', 'moMathParaPr', 'mopEmu',
            'mphant', 'mphantPr', 'mplcHide', 'mpos', 'mr', 'mrad', 'mradPr', 'mrPr', 'msepChr',
            'mshow', 'mshp', 'msPre', 'msPrePr', 'msSub', 'msSubPr', 'msSubSup', 'msSubSupPr', 'msSup',
            'msSupPr', 'mstrikeBLTR', 'mstrikeH', 'mstrikeTLBR', 'mstrikeV', 'msub', 'msubHide',
            'msup', 'msupHide', 'mtransp', 'mtype', 'mvertJc', 'mvfmf', 'mvfml', 'mvtof', 'mvtol',
            'mzeroAsc', 'mzeroDesc', 'mzeroWid', 'nesttableprops', 'nextfile', 'nonesttables',
            'objalias', 'objclass', 'objdata', 'object', 'objname', 'objsect', 'objtime', 'oldcprops',
            'oldpprops', 'oldsprops', 'oldtprops', 'oleclsid', 'operator', 'panose', 'password',
            'passwordhash', 'pgp', 'pgptbl', 'picprop', 'pict', 'pn', 'pnseclvl', 'pntext', 'pntxta',
            'pntxtb', 'printim', 'private', 'propname', 'protend', 'protstart', 'protusertbl', 'pxe',
            'result', 'revtbl', 'revtim', 'rsidtbl', 'rxe', 'shp', 'shpgrp', 'shpinst',
            'shppict', 'shprslt', 'shptxt', 'sn', 'sp', 'staticval', 'stylesheet', 'subject', 'sv',
            'svb', 'tc', 'template', 'themedata', 'title', 'txe', 'ud', 'upr', 'userprops',
            'wgrffmtfilter', 'windowcaption', 'writereservation', 'writereservhash', 'xe', 'xform',
            'xmlattrname', 'xmlattrvalue', 'xmlclose', 'xmlname', 'xmlnstbl',
            'xmlopen',
        ))
        # Translation of some special characters.
        specialchars = {
            'par': '\n',
            'sect': '\n\n',
            'page': '\n\n',
            'line': '\n',
            'tab': '\t',
            'emdash': '\u2014',
            'endash': '\u2013',
            'emspace': '\u2003',
            'enspace': '\u2002',
            'qmspace': '\u2005',
            'bullet': '\u2022',
            'lquote': '\u2018',
            'rquote': '\u2019',
            'ldblquote': '\201C',
            'rdblquote': '\u201D',
        }
        stack = []
        ignorable = False  # Whether this group (and all inside it) are "ignorable".
        ucskip = 1  # Number of ASCII characters to skip after a unicode character.
        curskip = 0  # Number of ASCII characters left to skip
        out = []  # Output buffer.
        for match in pattern.finditer(text):
            word, arg, hex, char, brace, tchar = match.groups()
            if brace:
                curskip = 0
                if brace == '{':
                    # Push state
                    stack.append((ucskip, ignorable))
                elif brace == '}':
                    # Pop state
                    ucskip, ignorable = stack.pop()
            elif char:  # \x (not a letter)
                curskip = 0
                if char == '~':
                    if not ignorable:
                        out.append('\xA0')
                elif char in '{}\\':
                    if not ignorable:
                        out.append(char)
                elif char == '*':
                    ignorable = True
            elif word:  # \foo
                curskip = 0
                if word in destinations:
                    ignorable = True
                elif ignorable:
                    pass
                elif word in specialchars:
                    out.append(specialchars[word])
                elif word == 'uc':
                    ucskip = int(arg)
                elif word == 'u':
                    c = int(arg)
                    if c < 0: c += 0x10000
                    if c > 127:
                        out.append(chr(c))  # NOQA
                    else:
                        out.append(chr(c))
                    curskip = ucskip
            elif hex:  # \'xx
                if curskip > 0:
                    curskip -= 1
                elif not ignorable:
                    c = int(hex, 16)
                    if c > 127:
                        out.append(chr(c))  # NOQA
                    else:
                        out.append(chr(c))
            elif tchar:
                if curskip > 0:
                    curskip -= 1
                elif not ignorable:
                    out.append(tchar)
        return ''.join(out)

    # Audio File
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

    # Image File
    def ImageDataSource(self):
        try:
            pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'
            self.DataSourceImage = []
            self.DataSourcetext = ""

            for paths in self.DataSourcePath:
                dummyImage = cv2.imread(paths)
                self.DataSourceImage.append(dummyImage)
                self.DataSourcetext += pytesseract.image_to_string(dummyImage)

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
            self.DataSourceSize = []
            self.DataSourceAccessTime = []
            self.DataSourceModifiedTime = []
            self.DataSourceChangeTime = []

            for paths in self.DataSourcePath:
                st = os.stat(paths)
                self.DataSourceSize.append(st[ST_SIZE])
                self.DataSourceAccessTime.append(time.asctime(time.localtime(st[ST_ATIME])))
                self.DataSourceModifiedTime.append(time.asctime(time.localtime(st[ST_MTIME])))
                self.DataSourceChangeTime.append(time.asctime(time.localtime(st[ST_CTIME])))

    # Add Image
    def AddImage(self, ImagePaths):
        self.AddImagePathDoublingError = []
        self.AddImagePathDouble = []

        pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'


        for imgPth in ImagePaths:
            imgPthError = False

            for pth in self.DataSourcePath:
                if imgPth == pth:
                    self.AddImagePathDoublingError.append(True)
                    self.AddImagePathDouble.append(pth)
                    imgPthError = True
                    break

            if not imgPthError:
                dummyImage = cv2.imread(imgPth)
                self.DataSourceImage.append(dummyImage)
                self.DataSourcetext += pytesseract.image_to_string(dummyImage)


    # Web URL
    def WebDataSource(self):
        try:
            response = requests.get(self.DataSourcePath)
            self.DataSourceLoadError = False
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self.DataSourceLoadError = True
                URLErrorBox = QMessageBox()
                URLErrorBox.setIcon(QMessageBox.Critical)
                URLErrorBox.setWindowTitle("URL Error")
                URLErrorBox.setText(str(e))
                URLErrorBox.setStandardButtons(QMessageBox.Ok)
                URLErrorBox.exec_()
        except requests.exceptions.ConnectionError as e:
            self.DataSourceLoadError = True
            URLErrorBox = QMessageBox()
            URLErrorBox.setIcon(QMessageBox.Critical)
            URLErrorBox.setWindowTitle("URL Error")
            URLErrorBox.setText("Unable to Connect to url: " + self.DataSourcePath)
            URLErrorBox.setStandardButtons(QMessageBox.Ok)
            URLErrorBox.exec_()
        except requests.exceptions.MissingSchema as e:
            self.DataSourceLoadError = True
            URLErrorBox = QMessageBox()
            URLErrorBox.setIcon(QMessageBox.Critical)
            URLErrorBox.setWindowTitle("URL Error")
            URLErrorBox.setText(str(e))
            URLErrorBox.setStandardButtons(QMessageBox.Ok)
            URLErrorBox.exec_()

        if not self.DataSourceLoadError:
            try:
                self.DataSourceHTML = urllib.request.urlopen(self.DataSourcePath).read()

                soup = BeautifulSoup(self.DataSourceHTML, features="lxml")

                # kill all script and style elements
                for script in soup(["script", "style"]):
                    script.extract()  # rip it out

                # get text
                text = soup.get_text()

                # break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)

                self.DataSourcetext = text
            except Exception as e:
                print(str(e))

    # Twitter Tweet
    def TweetDataSource(self, Hashtag, Since, Language, NoOfTweet):
        try:
            consumer_key = 's3MT03IsWkMrTj41HxH6InNzr'
            consumer_secret = 'jaqHc7GLjmxaM8xITLHWdcHC10nhzPXfG6RTwtUOmAJo673nRg'
            access_token = '1115595365380550659-1q2eKGnzYESKSujOTKQ16fhWbHRWAk'
            access_token_secret = 'le5JNnMhFM3iLbbRODsJyLblIZCltKwwjIXsdVokxsG20'

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)

            self.TweetData = []

            for tweet in tweepy.Cursor(api.search, q=Hashtag, count=NoOfTweet, lang="en", since=Since).items():
                self.DataSourcetext = self.DataSourcetext + tweet.text

                eachtweet = [tweet.user.screen_name,
                             tweet.user.name,
                             str(tweet.created_at),
                             tweet.text,
                             str(tweet.user.location),
                             str(tweet.coordinates),
                             str(tweet.retweet_count),
                             str(tweet.retweeted),
                             str(tweet.source),
                             str(tweet.favorite_count),
                             str(tweet.favorited),
                             str(tweet.in_reply_to_status_id_str)]

                self.TweetData.append(eachtweet)

            if len(self.TweetData) == 0:
                self.DataSourceRetrieveZeroError = True
            else:
                self.DataSourceRetrieveZeroError = False

        except Exception as e:
            self.DataSourceLoadError = True

    # Set Node
    def setNode(self, WidgetItemNode):
        self.DataSourceTreeWidgetItemNode = WidgetItemNode

    # Summary
    def Summarize(self, Default, Criteria, Value):
        if Default:
            self.DataSourceTextSummary = summarization.summarizer.summarize(self.DataSourcetext)
        else:
            if Criteria == "Ratio":
                self.DataSourceTextSummary = summarization.summarizer.summarize(self.DataSourcetext, ratio=Value)
            elif Criteria == "Total Word Count":
                self.DataSourceTextSummary = summarization.summarizer.summarize(self.DataSourcetext, word_count=Value)

    #detection
    def detect(self):
        blob = TextBlob(self.DataSourcetext)
        try:
            if blob.detect_language() != 'en':
                self.isEnglish = False
            else:
                self.isEnglish = True
        except:
            self.LanguageDetectionError = True

    #translation
    def translate(self):
        if not self.isEnglish and not hasattr(self, 'DataSourceTranslatedText'):
            blob = TextBlob(self.DataSourcetext)
            try:
                self.DataSourceTranslatedText = blob.translate(to='en')

                TranslationSuccessBox = QMessageBox()
                TranslationSuccessBox.setIcon(QMessageBox.Information)
                TranslationSuccessBox.setWindowTitle("Translation Success")
                TranslationSuccessBox.setText(self.DataSourceName + " is Translated Successfully!")
                TranslationSuccessBox.setStandardButtons(QMessageBox.Ok)
                TranslationSuccessBox.exec_()

                self.isTranslated = True
            except Exception as e:
                TranslationErrorBox = QMessageBox()
                TranslationErrorBox.setIcon(QMessageBox.Critical)
                TranslationErrorBox.setWindowTitle("Translation Error")
                TranslationErrorBox.setText("An Error occurred. The language is undetectable")
                TranslationErrorBox.setDetailedText(str(e))
                TranslationErrorBox.setStandardButtons(QMessageBox.Ok)
                TranslationErrorBox.exec_()

        elif hasattr(self, 'DataSourceTranslatedText'):
            TranslationErrorBox = QMessageBox()
            TranslationErrorBox.setIcon(QMessageBox.Information)
            TranslationErrorBox.setWindowTitle("Translation Error")
            TranslationErrorBox.setText(self.DataSourceName + " is already Translated!")
            TranslationErrorBox.setStandardButtons(QMessageBox.Ok)
            TranslationErrorBox.exec_()

    # Create Case
    def CreateCase(self, CaseTopic, selectedText):
        self.CasesNameConflict = False

        for cases in self.CasesList:
            if cases.CaseTopic == CaseTopic:
                self.CasesNameConflict = True

        if not self.CasesNameConflict:
            self.CasesList.append(Cases(CaseTopic, len(self.DataSourcetext)))
            self.AddtoCase(CaseTopic, selectedText)
        else:
            CasesCreationErrorBox = QMessageBox()
            CasesCreationErrorBox.setIcon(QMessageBox.Information)
            CasesCreationErrorBox.setWindowTitle("Creation Error")
            CasesCreationErrorBox.setText("A Case with that Topic is already created")
            CasesCreationErrorBox.setStandardButtons(QMessageBox.Ok)
            CasesCreationErrorBox.exec_()

    # Add to Case
    def AddtoCase(self, CaseTopic, SelectedText):
        for cases in self.CasesList:
            if cases.CaseTopic == CaseTopic:
                cases.addtoCase(SelectedText)
                break

    # Set Animation
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

    # Set Query
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

    # Word Cloud
    def CreateWordCloud(self, DataSourceText, WCBGColor, maxword, maskname):
        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open("Word Cloud Maskes/" + maskname + ".png"))

        # create wordcloud object
        wc = WordCloud(background_color=WCBGColor, max_words=int(maxword), mask=mask, stopwords=set(STOPWORDS))

        # generate wordcloud
        wc.generate(DataSourceText)

        return wc.to_image()

    def text_preprocessing(self,document_text):
        # convert all text to lowercase
        doc_text = document_text.lower()

        # remove numbers
        doc_text = re.sub(r'\d+', '', doc_text)

        # remove punctuation, characters and whitespaces
        doc_text = re.sub('\W+', ' ', doc_text)

        # remove stopwords and tokenize
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(doc_text)
        result = [i for i in tokens if not i in stop_words]

        result2 = []

        for word in result:
            if len(word) > 2:
                result2.append(word)

        return result2

    def GenerateFrequencyList(self, match_pattern):
        frequency = {}

        for word in match_pattern:
            count = frequency.get(word, 0)
            frequency[word] = count + 1

        frequency_list = frequency.keys()
        return frequency_list,frequency

    def find_exact_word(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\w+', doc_text)
        frequency_list,frequency = self.GenerateFrequencyList(match_pattern)

        count = 0
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def FindWordFrequency(self, DataSourceText):
        WordFrequencyRow = []
        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)

        total_count = 0
        # stop_words = set(stopwords.words('english'))

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            weighted_percentage = round((frequency[words]/total_count)*100,2)
            WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage])

        return WordFrequencyRow

    def FindStemmedWords(self, StemWord, DataSourceText):
        StemWordList = []

        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)

        porter = PorterStemmer()

        stem_word = porter.stem(StemWord)

        count = 0
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                StemWordList.append([words, count])

        return StemWordList

    def GetDistinctWords(self, DataSourceText):
        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)
        return frequency_list

    def PartOfSpeech(self, DataSourceName, DataSourceText, limit):
        os.environ["PATH"] += os.pathsep + 'Graphviz2.38/bin/'

        WordFrequencyTable = self.FindWordFrequency(DataSourceText)

        word_list = [i[0] for i in WordFrequencyTable]

        freq_list = [i[2] for i in WordFrequencyTable]

        stra = " "
        list_to_string = stra.join(word_list)

        nlp = spacy.load("en_core_web_sm")

        doc = nlp(list_to_string)

        pos_list = []
        i = 0
        for token in doc:
            pos_list.append([token.text, token.pos_, freq_list[i]])
            i += 1

        # print(pos_list)
        pos_list = sorted(pos_list, key=lambda l: l[2], reverse=True)

        root = Node(DataSourceName)
        noun_node = Node("Noun", parent=root)
        verb_node = Node("Verb", parent=root)
        adj_node = Node("Adj", parent=root)

        noun_limit = 0
        verb_limit = 0
        adj_limit = 0

        for word, tag, freq in pos_list:
            if (tag == "NOUN") and (noun_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=noun_node)
                noun_limit += 1

            elif (tag == "VERB") and (verb_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=verb_node)
                verb_limit += 1

            elif (tag == "ADJ") and (adj_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=adj_node)
                adj_limit += 1

        # png image of tree
        exporter.DotExporter(root).to_picture("tree.png")
        POSTreeImage = Image.open("tree.png")
        ImageArray = np.array(POSTreeImage)
        POSTreeImage = Image.fromarray(ImageArray)
        os.remove('tree.png')

        noun_count = 0
        verb_count = 0
        adj_count = 0

        blob2 = TextBlob(DataSourceText)

        for word, tag, freq in pos_list:
            if tag == "NOUN":
                noun_count += 1
            elif tag == "VERB":
                verb_count += 1
            elif tag == "ADJ":
                adj_count += 1

        return ([POSTreeImage, pos_list, noun_count, verb_count, adj_count])

    #Entity RelationShip
    def EntityRelationShip(self, DataSourceText):
        nlp = en_core_web_sm.load()
        DataSourceTextER = nlp(DataSourceText)

        Entity_List = [(X.text, X.label_) for X in DataSourceTextER.ents]

        Entity_Labels = [x.label_ for x in DataSourceTextER.ents]

        return [Entity_List, Entity_Labels, displacy.render(nlp(str(DataSourceTextER)), jupyter=False, style='ent'), displacy.render(nlp(str(DataSourceTextER)), jupyter=False, style='dep')]

    #  *********************************** Topic Modelling **********************************

    def tokenize(self, DataSourceText):
        parser = English()
        lda_tokens = []
        tokens = parser(DataSourceText)
        for token in tokens:
            if token.orth_.isspace():
                continue
            elif token.like_url:
                lda_tokens.append('URL')
            elif token.orth_.startswith('@'):
                lda_tokens.append('SCREEN_NAME')
            else:
                lda_tokens.append(token.lower_)
        return lda_tokens

    def get_lemma(self, word):
        lemma = wn.morphy(word)
        if lemma is None:
            return word
        else:
            return lemma

    def get_lemma2(self, word):
        return WordNetLemmatizer().lemmatize(word)

    def prepare_text_for_lda(self, text):
        en_stop = set(nltk.corpus.stopwords.words('english'))
        tokens = self.tokenize(text)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [token for token in tokens if token not in en_stop]
        tokens = [self.get_lemma(token) for token in tokens]
        return tokens

    def TopicModelling(self, DataSourceText, Topic_NUM):
        spacy.load('en_core_web_sm')

        text_data = []

        tokens = self.prepare_text_for_lda(DataSourceText)

        text_data.append(tokens)

        dictionary = corpora.Dictionary(text_data)
        corpus = [dictionary.doc2bow(text) for text in text_data]
        pickle.dump(corpus, open('Topic Modelling Files/corpus.pkl', 'wb'))
        dictionary.save('Topic Modelling Files/dictionary.gensim')

        ldamodel = models.ldamodel.LdaModel(corpus, num_topics=Topic_NUM, id2word=dictionary, passes=15)
        ldamodel.save('Topic Modelling Files/model5.gensim')
        topics = ldamodel.print_topics(num_words=4)

        new_doc = 'Practical Bayesian Optimization of Machine Learning Algorithms'
        new_doc = self.prepare_text_for_lda(new_doc)
        new_doc_bow = dictionary.doc2bow(new_doc)

        dictionary = corpora.Dictionary.load('Topic Modelling Files/dictionary.gensim')
        corpus = pickle.load(open('Topic Modelling Files/corpus.pkl', 'rb'))
        lda = models.ldamodel.LdaModel.load('Topic Modelling Files/model5.gensim')

        lda_display = pyLDAvis.gensim.prepare(lda, corpus, dictionary, sort_topics=True)

        return pyLDAvis.prepared_data_to_html(lda_display)




























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
