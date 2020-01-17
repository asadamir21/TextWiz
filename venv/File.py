from sklearn.feature_extraction.text import TfidfVectorizer

from DataSource import *
from Tab import *

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

        self.high = pairwise_similarity.toarray().tolist()

        highlist = []

        for row in range(len(self.high)):
            for column in range(len(self.high[row])):
                if row != column and row < column:

                    column2 = round(self.high[row][column] * 100, 5)

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

    # Data Source Document Clustering
    def DocumnetClustering(self):
        self.DocumnetClusteringDataSourceError = False

        if len(self.DataSourceList) > 1:
            if hasattr(self, 'high'):
                pass
            else:
                self.FindSimilarityBetweenDataSource()
        else:
            self.DocumnetClusteringDataSourceError = True

    #Data Source Similar Phrases
    def FindSimilarPhrases(self):
        print("Hello World")

















#
#
# class Animation(QObject):
#     finished = pyqtSignal()
#     intReady = pyqtSignal(list)
#
#     def __init__(self, name, MainWindow):
#         super().__init__()
#         self.name = name
#         self.MainWindow = MainWindow
#
#     def run(self):
#         try:
#             self.myLoadingDialog = QDialog()
#
#             loadingGIF = pyglet.image.load_animation("Loading gifs/" + self.name)
#             loadingGIFSprite = pyglet.sprite.Sprite(loadingGIF)
#
#             self.myLoadingDialog.setParent(self.MainWindow)
#             self.myLoadingDialog.setModal(True)
#
#             LoadingGifMovie = QMovie()
#             LoadingGifMovie.setFileName("Loading gifs/" + self.name)
#
#             gifWidth = loadingGIFSprite.width
#             gifheight = loadingGIFSprite.height
#
#             self.myLoadingDialog.setGeometry(pyautogui.size().width / 2 - gifWidth / 2,
#                                              pyautogui.size().height / 2 - gifheight / 2, gifWidth, gifheight)
#             self.myLoadingDialog.setAttribute(Qt.WA_TranslucentBackground)
#             self.myLoadingDialog.setWindowFlags(Qt.FramelessWindowHint)
#
#             movie_screen = QLabel()
#             # Make label fit the gif
#             movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#             movie_screen.setAlignment(Qt.AlignCenter)
#
#             main_layout = QVBoxLayout()
#             main_layout.addWidget(movie_screen)
#
#             css = qstylizer.style.StyleSheet()
#             css.setValues(backgroundColor="transparent")
#             self.myLoadingDialog.setStyleSheet(css.toString())
#             self.myLoadingDialog.setLayout(main_layout)
#
#             # Add the QMovie object to the label
#             LoadingGifMovie.setCacheMode(QMovie.CacheAll)
#             LoadingGifMovie.setSpeed(100)
#             movie_screen.setMovie(LoadingGifMovie)
#             LoadingGifMovie.start()
#             self.myLoadingDialog.exec()
#
#         except Exception as e:
#             print(str(e))
#
#     def stop(self):
#         self.terminate()
