from calendar import different_locale

from PyQt5.QtCore import QThread, pyqtSignal
from ProgressInfo import *
from File import *
import queue

ThreadQueue = queue.Queue()

class TaskThread(QThread):
    taskFinished = pyqtSignal()

    def run(self):
        try:
            dummyProgressInfo = ThreadQueue.get()

            # ************************* Importing *************************

            # Importing Data Source
            if dummyProgressInfo.ProcessName == "Importing":
                # Retrieving Tweets
                if dummyProgressInfo.DataSourceName == "Tweet":
                    dummyProgressInfo.DataSource.TweetDataSource(dummyProgressInfo.Hashtag,
                                                                 dummyProgressInfo.Since,
                                                                 dummyProgressInfo.NoofTweet)
                    ThreadQueue.put(dummyProgressInfo.DataSource)

                # Importing CSV
                elif dummyProgressInfo.DataSourceName == "CSV":
                    dummyProgressInfo.DataSource.CSVDataSource(dummyProgressInfo.CSVHeader,
                                                               dummyProgressInfo.CSVPathFlag)
                    ThreadQueue.put(dummyProgressInfo.DataSource)

                # Retrieving Youtube Comments
                elif dummyProgressInfo.DataSourceName == "Youtube":
                    ThreadQueue.put(dummyProgressInfo.DataSource)
                else:
                    dummyDataSource = DataSource(dummyProgressInfo.DataSourcePath,
                                                 dummyProgressInfo.DataSourceExt)
                    ThreadQueue.put(dummyDataSource)

            # ************************** Queries **************************

            # Word Frequency
            elif dummyProgressInfo.ProcessName == "Word Frequency":
                dummyQuery = Query()
                rowList = dummyQuery.FindWordFrequency(dummyProgressInfo.DataSource.DataSourcetext)
                ThreadQueue.put(rowList)

            # Question Generator
            elif dummyProgressInfo.ProcessName == "Generate Question":
                dummyQuery = Query()
                rowList = dummyQuery.GenerateQuestion(dummyProgressInfo.DataSourcetext)
                ThreadQueue.put(rowList)

            # Sentiment Analysis
            elif dummyProgressInfo.ProcessName == "Sentiment Analysis":
                if hasattr(dummyProgressInfo.DataSource, "PositiveSentimentCount"):
                    pass
                else:
                    dummyProgressInfo.DataSource.SentimentAnalysis(dummyProgressInfo.SentimentAnalysisColumnName)
                ThreadQueue.put(dummyProgressInfo.DataSource)

            # Entity Relationship
            elif dummyProgressInfo.ProcessName == "Entity Relationship":
                dummyQuery = Query()
                EntityRelationShip = dummyQuery.EntityRelationShip(dummyProgressInfo.DataSource.DataSourcetext)
                ThreadQueue.put(EntityRelationShip)

            # Part of Speech
            elif dummyProgressInfo.ProcessName == "Part of Speech":
                dummyQuery = Query()
                PartOfSpeech = dummyQuery.PartOfSpeech(dummyProgressInfo.DataSource.DataSourceName,
                                                       dummyProgressInfo.DataSource.DataSourcetext, 3)
                ThreadQueue.put(PartOfSpeech)

            # Topic Modelling
            elif dummyProgressInfo.ProcessName == "Topic Modelling":
                dummyQuery = Query()
                TopicModellingHTML = dummyQuery.TopicModelling(dummyProgressInfo.DataSource.DataSourcetext, 5)
                ThreadQueue.put(TopicModellingHTML)

            # *************************** Cases ***************************

            # ************************* Sentiments ************************

            # *********************** Visualization ***********************

            # Word Cloud
            elif dummyProgressInfo.ProcessName == "Word Cloud":
                dummyQuery = Query()
                WordCloudImage = dummyQuery.CreateWordCloud(dummyProgressInfo.DataSourcetext,
                                                            dummyProgressInfo.WCBGColor,
                                                            dummyProgressInfo.maxword,
                                                            dummyProgressInfo.maskname)
                ThreadQueue.put(WordCloudImage)

            # Word Tree
            elif dummyProgressInfo.ProcessName == "Word Tree":
                WordTreeHTML = dummyProgressInfo.DataSource.CreateWordTree(dummyProgressInfo.WordTreeWidth,
                                                                           dummyProgressInfo.WordTreeHeight)
                ThreadQueue.put(WordTreeHTML)

            # Survey Analysis
            elif dummyProgressInfo.ProcessName == "Survey Analysis":
                pass


            self.taskFinished.emit()

        except Exception as e:
            print(str(e))
