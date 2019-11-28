
class Cases:
    def __init__(self, CaseTopic):
        self.CaseTopic = CaseTopic
        self.TopicCases = []

    def addtoCase(self, TopicText):
        self.TopicCases.append(TopicText)

    def removefromCase(self, TopicText):
        self.TopicCases.remove(TopicText)
