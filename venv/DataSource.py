from PyQt5.QtWidgets import *

from Query import *
from pyglet import *

from Cases import *
from Sentiments import *
from stat import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, parse_qs
from textblob import TextBlob
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import urllib
import requests
import cv2
import pytesseract

import re
import ntpath, pyglet
import os, time

#PDF, Word, Twitter
import docx2txt, PyPDF2, tweepy
#Youtube
from Youtube.KeyWord import *
from Youtube.URL import *

import re
import os
import win32com.client as win32
from win32com.client import constants



class DataSource():
    def __init__(self, path, ext, MainWindow):
        super().__init__()
        self.DataSourcePath = path

        if ext == "Image files (*.png *.bmp *.jpeg *.jpg *.webp *.tiff *.tif *.pfm *.jp2 *.hdr *.pic *.exr *.ras *.sr *.pbm *.pgm *.ppm *.pxm *.pnm)":
            self.DataSourceName = ntpath.basename(path[0])
        elif ext == "URL" or ext ==  'Tweet' or ext ==  'Youtube':
            self.DataSourceName = path
        else:
            self.DataSourceName = ntpath.basename(path)

        self.DataSourceext = ext
        self.DataSourcetext = ""
        self.DataSourceLoadError = False
        self.QueryList = []
        self.CasesList = []
        self.SentimentList = []
        self.AutomaticSentimentList = []
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

        self.CreatSentiments()

    # Word File
    def WordDataSource(self):
        try:
            if self.DataSourcePath.endswith('.docx'):
                self.DataSourcetext = docx2txt.process(self.DataSourcePath)
                self.DataSourceLoadError = False
            else:
                word = win32.gencache.EnsureDispatch('Word.Application')
                doc = word.Documents.Open(self.DataSourcePath)

                # Rename path with .docx
                new_file_abs = os.path.abspath(self.DataSourcePath)

                new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

                # Save and Close
                word.ActiveDocument.SaveAs(
                    new_file_abs, FileFormat=constants.wdFormatXMLDocument
                )
                doc.Close(False)

                self.DataSourcetext = docx2txt.process(new_file_abs)
                self.DataSourceLoadError = False

                os.remove(new_file_abs)

        except Exception as e:
            try:
                self.DataSourceLoadError = True
                DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error", "Any Error occurred. There was a Problem, the File " + self.DataSourceName  + " is Unable to load", QMessageBox.Ok)
            except Exception as e2:
                print(str(e2))

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
            DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error",
                                                          "Any Error occurred. There was a Problem, the File " + self.DataSourceName + " is Unable to load",
                                                          QMessageBox.Ok)

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
            self.DataSourceLoadError = True
            DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error",
                                                          "Any Error occurred. There was a Problem, the File " + self.DataSourceName + " is Unable to load",
                                                          QMessageBox.Ok)

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
            DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error", "Any Error occurred. There was a Problem, the File " + self.DataSourceName + " is Unable to load", QMessageBox.Ok)

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
            DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error",
                                                          "Any Error occurred. There was a Problem, the File " + self.DataSourceName + " is Unable to load",
                                                          QMessageBox.Ok)

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
            DataSourceLoadErrorBox = QMessageBox.critical(self.MainWindow, "Load Error",
                                                          "Any Error occurred. There was a Problem, the File " + self.DataSourceName + " is Unable to load",
                                                          QMessageBox.Ok)

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

                self.DataSourcePath.append(imgPth)

                st = os.stat(imgPth)
                self.DataSourceSize.append(st[ST_SIZE])
                self.DataSourceAccessTime.append(time.asctime(time.localtime(st[ST_ATIME])))
                self.DataSourceModifiedTime.append(time.asctime(time.localtime(st[ST_MTIME])))
                self.DataSourceChangeTime.append(time.asctime(time.localtime(st[ST_CTIME])))

    # Web URL
    def WebDataSource(self):
        try:
            response = requests.get(self.DataSourcePath)
            self.DataSourceLoadError = False
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self.DataSourceLoadError = True
                URLErrorBox = QMessageBox.critical(self.MainWindow, "URL Error",
                                                              str(e),
                                                              QMessageBox.Ok)
        except requests.exceptions.ConnectionError as e:
            self.DataSourceLoadError = True
            URLErrorBox = QMessageBox.critical(self.MainWindow, "URL Error",
                                               "Unable to Connect to url: " + self.DataSourcePath,
                                               QMessageBox.Ok)
        except requests.exceptions.MissingSchema as e:
            self.DataSourceLoadError = True
            URLErrorBox = QMessageBox.critical(self.MainWindow, "URL Error",
                                               str(e),
                                               QMessageBox.Ok)

        if not self.DataSourceLoadError:
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

    # Twitter Tweet
    def TweetDataSource(self, Hashtag, Since, Language, NoOfTweet):
        try:
            self.DataSourceHashtag = Hashtag

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

    #Yotube Comments From URL
    def YoutubeURL(self):
        self.YoutubeURLFlag = True
        try:
            video_id = urlparse(self.DataSourcePath)
            q = parse_qs(video_id.query)
            vid = q["v"][0]

            VC = VideoComment(100, vid, 'AIzaSyClLW3rJUSeU5kLrf7njWItFdKdgtoX1pA')
            self.YoutubeData = VC.comments

            self.DataSourcetext = ""
            for row in range(len(self.YoutubeData)):
                self.DataSourcetext = self.DataSourcetext + self.YoutubeData[row][0]

            self.DataSourceLoadError = False
        except Exception as e:
            self.DataSourceLoadError = True
            YoutubeErrorBox = QMessageBox.critical(self.MainWindow, "Youtube Error",
                                                   "Unable to Retrieve Comments from URL: " + self.DataSourcePath,
                                                   QMessageBox.Ok)

    # Yotube Comments From KeyWord
    def YoutubeKeyWord(self):
        self.YoutubeKeyWordFlag = True
        try:
            self.YoutubeData = retreiveComments(self.DataSourcePath)

            self.DataSourcetext = ""
            for row in range(len(self.YoutubeData)):
                self.DataSourcetext = self.DataSourcetext + self.YoutubeData[row][4]

            self.DataSourceLoadError = False

        except Exception as e:
            self.DataSourceLoadError = True
            self.DataSourceLoadError = True
            YoutubeErrorBox = QMessageBox.critical(self.MainWindow, "Youtube Error",
                                               "Unable to Retrieve Comments of Key Word: " + self.DataSourcePath,
                                               QMessageBox.Ok)

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

    # Create Sentiments
    def CreatSentiments(self):
        self.SentimentList.append(Sentiments("Good"))
        self.SentimentList.append(Sentiments("Neutral"))
        self.SentimentList.append(Sentiments("Bad"))

    # Automatic Sentiment Analysis
    def SentimentAnalysis(self):
        DataSourceTextTokenize = tokenize.sent_tokenize(self.DataSourcetext)

        analyzer = SentimentIntensityAnalyzer()

        self.PositiveSentimentCount = 0
        self.NegativeSentimentCount = 0
        self.NeutralSentimentCount = 0

        for line in DataSourceTextTokenize:
            vs = analyzer.polarity_scores(line)

            vs = analyzer.polarity_scores(line)
            if not vs['neg'] > 0.1:
                if vs['pos'] - vs['neg'] > 0:
                    self.AutomaticSentimentList.append([line, 'Positive'])
                    self.PositiveSentimentCount += 1
                else:
                    self.AutomaticSentimentList.append([line, 'Neutral'])
                    self.NeutralSentimentCount += 1

            elif not vs['pos'] > 0.1:
                if vs['pos'] - vs['neg'] <= 0:
                    self.AutomaticSentimentList.append([line, 'Negative'])
                    self.NegativeSentimentCount += 1
                else:
                    self.AutomaticSentimentList.append([line, 'Neutral'])
                    self.NeutralSentimentCount += 1

            else:
                self.AutomaticSentimentList.append([line, 'Neutral'])
                self.NeutralSentimentCount += 1

    # Create Dashboard
    def CreateDashboard(self):
        print("Hello")

    # Set Query
    def setQuery(self, QueryTreeWidgetItem, TabItem):
        self.QueryList.append([QueryTreeWidgetItem, TabItem])

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

    # Delete Object
    def __del__(self):
        self.DataSourceDelete = True

