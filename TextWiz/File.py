

import random
from sklearn.cluster import KMeans
import pandas as pd
from scipy.cluster.hierarchy import ward, dendrogram, linkage
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from DataSource import *
from Tab import *

class File():
    def __init__(self):
        super().__init__()
        self.DataSourceList = []
        self.TabList = []
        self.requiredSaved = False

    def setFileName(self, name):
        self.FileName = name

    def setFileLocation(self, path):
        self.FileLocation = path

    def setCreatedDate(self, date):
        self.CreatedDate = date

    def setCreatedBy(self, name):
        self.CreatedBy = name

    def setModifiedDate(self, date):
        self.ModifiedDate = date

    def setModifiedBy(self, name):
        self.ModifiedBy = name

    def setDataSources(self, myDataSource):
        isAvailable = False

        for DataSourceIndex in self.DataSourceList:
            if DataSourceIndex.DataSourcePath == myDataSource.DataSourcePath:
                myDataSource.DataSourceLoadError = True
                isAvailable = True
                break

        if not isAvailable:
            self.DataSourceList.append(myDataSource)
        else:
            DataSourceLoadErrorBox = QMessageBox()
            DataSourceLoadErrorBox.setIcon(QMessageBox.Information)
            DataSourceLoadErrorBox.setWindowTitle("Load Error")
            DataSourceLoadErrorBox.setText(myDataSource.DataSourceName + " is Already Added")
            DataSourceLoadErrorBox.setStandardButtons(QMessageBox.Ok)
            DataSourceLoadErrorBox.exec_()

    #Data Source Similarity
    def FindSimilarityBetweenDataSource(self):
        SimilarityCorpus = []

        for DS in self.DataSourceList:
            SimilarityCorpus.append(DS.DataSourcetext)

        vect = TfidfVectorizer(min_df=1, stop_words="english")
        tfidf = vect.fit_transform(SimilarityCorpus)
        pairwise_similarity = tfidf * tfidf.T

        self.highNumpy = pairwise_similarity.toarray()
        self.high = self.highNumpy.tolist()

        highlist = []

        for row in range(len(self.high)):
            for column in range(len(self.high[row])):
                if row != column and row < column:

                    column2 = round(self.high[row][column] * 100, 5)

                    for DS in self.DataSourceList:
                        if SimilarityCorpus[column] == DS.DataSourcetext:
                            index = DS.DataSourceName

                    for DS in self.DataSourceList:
                        if SimilarityCorpus[row] == DS.DataSourcetext:
                            index2 = DS.DataSourceName

                    dummylist = [index, index2, column2]
                    highlist.append(dummylist)

        highlist = sorted(highlist, key=lambda l: l[2], reverse=True)

        return highlist

    # Data Source Document Clustering
    def DocumnetClustering(self):
        self.DocumnetClusteringDataSourceError = False

        if len(self.DataSourceList) > 3:
            self.FindSimilarityBetweenDataSource()

            #Dendrogram
            self.plot_canvas = MyStaticMplCanvas(width=5, height=4, dpi=100)
            self.plot_canvas.compute_initial_figure(self.high, [DS.DataSourceName for DS in self.DataSourceList])

            # Scatter Plot
            self.ScatterFigure = plt.figure(figsize=(10, 5))
            ax = self.ScatterFigure.add_subplot(111)

            doc_titles = [DS.DataSourceName for DS in self.DataSourceList]

            num_clusters = 4
            km = KMeans(n_clusters=num_clusters)
            km.fit(self.highNumpy)
            clusters = km.labels_.tolist()

            xs, ys = self.highNumpy[:, 0], self.highNumpy[:, 1]

            df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=doc_titles))

            # group by cluster
            groups = df.groupby('label')

            ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling

            for name, group in groups:
                ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
                        mec='none')
                ax.set_aspect('auto')
                ax.tick_params(
                    axis='x',  # changes apply to the x-axis
                    which='both',  # both major and minor ticks are affected
                    bottom='off',  # ticks along the bottom edge are off
                    top='off',  # ticks along the top edge are off
                    labelbottom='off')
                ax.tick_params(
                    axis='y',  # changes apply to the y-axis
                    which='both',  # both major and minor ticks are affected
                    left='off',  # ticks along the bottom edge are off
                    top='off',  # ticks along the top edge are off
                    labelleft='off')

            ax.legend(numpoints=1)  # show legend with only 1 point

            # add label in x,y position with the label as the film title
            for i in range(len(df)):
                ax.text(df.iloc[i]['x'], df.iloc[i]['y'], df.iloc[i]['title'], size=8)

        else:
            self.DocumnetClusteringDataSourceError = True

class MyMplCanvas(FigureCanvas):
    #Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        self.axes = fig.add_subplot(111)
        # We want the axes not to be cleared every time plot() is called
        #self.axes.hold(True)

        FigureCanvas.__init__(self, fig)

        #FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class MyStaticMplCanvas(MyMplCanvas):
    #Simple canvas with dendrogram plot
    def compute_initial_figure(self, X, doc_titles):
        # generate the linkage matrix

        self.fancy_dendrogram(
            ward(X),
            orientation="right",
            labels=doc_titles,
            show_leaf_counts=True,
            leaf_font_size=8., # font size for the x axis labels
            show_contracted=False,
            #annotate_above=10,
            #max_d=cut_off,  # plot a horizontal cut-off line
        )

    def createSampleDate(self):
      # generate two clusters: a with 100 points, b with 50:
      np.random.seed(4711)  # for repeatability of this tutorial
      a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[4,])
      b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[4,])
      self.X = np.concatenate((a, b),)

    def fancy_dendrogram(self, *args, **kwargs):
          kwargs['ax'] = self.axes
          max_d = kwargs.pop('max_d', None)
          if max_d and 'color_threshold' not in kwargs:
              kwargs['color_threshold'] = max_d
          annotate_above = kwargs.pop('annotate_above', 0)

          ddata = dendrogram(*args, **kwargs)

          if not kwargs.get('no_plot', False):
              self.axes.set_title('Document Clustering')
              self.axes.set_xlabel('distance')
              #self.axes.set_ylabel('')
              for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
                  x = 0.5 * sum(i[1:3])
                  y = d[1]
                  if y > annotate_above:
                      self.axes.plot(x, y, 'o', c=c)
                      self.axes.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                                   textcoords='offset points',
                                   va='top', ha='center')
              if max_d:
                  self.axes.axhline(y=max_d, c='k', linestyle='--', color='red')
          return ddata
