import sys
from os import *
import numpy as np
from PIL import  Image
from wordcloud import WordCloud, STOPWORDS


class DataSource():
    def __init__(self):
        self.wordcloud = self.CreateWordCloud()

    def CreateWordCloud(self, text):
        currdir = path.dirname(__file__)
        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open(path.join(currdir, "cloud.png")))

        # create set of stopwords
        stopwords = set(STOPWORDS)

        # create wordcloud object
        wc = WordCloud(background_color="white",
                       max_words=200,
                       mask=mask,
                       stopwords=stopwords)

        # generate wordcloud
        wc.generate(text)

        # save wordcloud
        wc.to_file(path.join(currdir, "wc.png"))

