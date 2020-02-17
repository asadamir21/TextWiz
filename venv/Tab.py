
class Tab():
    def __init__(self, tabName, tabWidget, DataSourceName):
        self.TabName = tabName
        self.tabWidget = tabWidget
        self.DataSourceName = DataSourceName

    def setTabCase(self, TabCase):
        self.tabCase = TabCase

    def setTabSentiment(self, TabSentiment):
        self.tabSentiment = TabSentiment

    def __del__(self):
        self.TabDelete = True
