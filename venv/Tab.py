
class Tab():
    def __init__(self, tabName, tabWidget, DataSourceName):
        self.TabName = tabName
        self.tabWidget = tabWidget
        self.DataSourceName = DataSourceName
        self.isActive = True

    def setisActive(self, Flag):
        self.isActive = Flag

    def setCurrentWidget(self, Flag):
        self.isCurrentWidget = Flag

    def setTabCase(self, TabCase):
        self.tabCase = TabCase

    def setCasesLength(self, length):
        self.CasesLength = length

    def setTabSentiment(self, TabSentiment):
        self.tabSentiment = TabSentiment

    def setSummarizeTextLength(self, length):
        self.SummarizeLengthText = length

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

    def setSurveryAnalysisChartList(self, ChartList):
        self.SurveyAnalysisChartList = ChartList

