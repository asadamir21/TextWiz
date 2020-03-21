
class Cases:
    def __init__(self, CaseTopic, ParentTextlen):
        self.CaseTopic = CaseTopic
        self.TopicCases = []
        self.ParentTextlen = ParentTextlen
        self.ParentCase = None
        self.MergedCase = False

    def addtoCase(self, TopicText):
        self.ParentTextlen += len(TopicText)
        self.TopicCases.append([TopicText, len(TopicText.split()), len(TopicText), len(TopicText)/self.ParentTextlen])

    def setParentCase(self, ParentCaseName):
        self.ParentCase = ParentCaseName

    def setMergeCaseFlag(self):
        self.MergedCase = True

    def removefromCase(self, TopicText):
        self.TopicCases.remove(TopicText)
