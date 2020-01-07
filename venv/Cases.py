
class Cases:
    def __init__(self, CaseTopic, ParentTextlen):
        self.CaseTopic = CaseTopic
        self.TopicCases = []
        self.ParentTextlen = ParentTextlen

    def addtoCase(self, TopicText):
        self.ParentTextlen += len(TopicText)
        self.TopicCases.append([TopicText, len(TopicText.split()), len(TopicText), len(TopicText)/self.ParentTextlen])

    def removefromCase(self, TopicText):
        self.TopicCases.remove(TopicText)
