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
import numpy as np
import matplotlib
import re
import nltk
import ntpath, pyglet
import docx2txt, PyPDF2
import os, time
import spacy

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
        if blob.detect_language() != 'en':
            self.isEnglish = False
        else:
            self.isEnglish = True

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
