
class Sentiments:
    def __init__(self, SentimentType):
        self.SentimentType = SentimentType
        self.SentimentTextList = []
        self.ParentTextlen = 0

    def addSentiment(self, SentimentsText):
        self.ParentTextlen += len(SentimentsText)
        self.SentimentTextList.append([SentimentsText, len(SentimentsText.split()), len(SentimentsText), len(SentimentsText)/self.ParentTextlen])

    def removeSentiment(self, SentimentsText):
        self.SentimentTextList.remove(SentimentsText)
