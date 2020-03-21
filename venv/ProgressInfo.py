
class ProgressInfo:
    def __init__(self, DataSourceName, ProcessName):
        self.DataSourceName = DataSourceName
        self.ProcessName = ProcessName


    def ImportFile(self, Path, Extension):
        self.DataSourcePath = Path
        self.DataSourceExt = Extension

    def ImportCSVFile(self, CSVHeader, CSVPathFlag, DataSource):
        self.CSVHeader = CSVHeader
        self.CSVPathFlag = CSVPathFlag
        self.DataSource = DataSource

    def ImportTweetFile(self, Hashtag, NoofTweet, Since, DataSource):
        self.Hashtag = Hashtag
        self.NoofTweet = NoofTweet
        self.Since = Since
        self.DataSource = DataSource

    def GenerateWordFrequency(self, DataSource):
        self.DataSource = DataSource

    def SentimentAnalysis(self, DataSource, Column):
        self.DataSource = DataSource
        self.SentimentAnalysisColumnName = Column

    def SentimentAnalysisVisualization(self, DataSource):
        self.DataSource = DataSource

    def CreateWordCloud(self, DataSourcetext, WCBGColor, maxword, maskname):
        self.DataSourcetext = DataSourcetext
        self.WCBGColor = WCBGColor
        self.maxword = maxword
        self.maskname = maskname

    def CreateWordTree(self, width, height, DataSource):
        self.WordTreeWidth = width
        self.WordTreeHeight = height
        self.DataSource = DataSource

    def QuestionGenerator(self, DataSourcetext):
        self.DataSourcetext = DataSourcetext
