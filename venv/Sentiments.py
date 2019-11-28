
class Sentiments:
    def __init__(self, SentimentType):
        self.SentimentType = SentimentType
        self.SentimentTextList = []

    def addSentiment(self, SentimentsText):
        self.SentimentTextList.append(SentimentsText)

    def removeSentiment(self, SentimentsText):
        self.SentimentTextList.remove(SentimentsText)
