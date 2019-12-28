
class Tab():
    def __init__(self, tabName, tabWidget, DataSourceName):
        self.TabName = tabName
        self.tabWidget = tabWidget
        self.DataSourceName = DataSourceName

    def __del__(self):
        self.TabDelete = True
