
class Tab():
    def __init__(self, tabName, tabWidget, DataSourceName):
        self.TabName = tabName
        self.tabWidget = tabWidget
        self.DataSourceName = DataSourceName
        self.isActive = True

    def setisActive(self, Flag):
        self.isActive = Flag

    def setTabCase(self, TabCase):
        self.tabCase = TabCase

    def setTabSentiment(self, TabSentiment):
        self.tabSentiment = TabSentiment

    def setWordCloud(self, BGColor, MaxWords, Mask):
        self.WordCloudBGColor = BGColor
        self.WordCloudMaxWords = MaxWords
        self.WordCloudMask = Mask

    def setStemWords(self, word):
        self.StemWord = word

    def setTranslateLanguage(self, language):
        self.TranslatedLanguage = language

    def setAutomaticSentimentAnalysis(self, ColumnName):
        self.AutomaticSentimentAnalysisColumnName = ColumnName

    def __del__(self):
        self.TabDelete = True
