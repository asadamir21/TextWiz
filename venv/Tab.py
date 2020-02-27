
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

    def __del__(self):
        self.TabDelete = True
