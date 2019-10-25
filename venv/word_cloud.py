import matplotlib.pyplot as pPlot
from wordcloud import WordCloud, STOPWORDS
import docx2txt
import numpy as npy
from PIL import Image

# dataset = open("files/test.txt", "r").read().lower()
file_text = docx2txt.process("files/PDR.docx")
# print(file_text)

def create_word_cloud(string):
   cloud = WordCloud(background_color = "white", max_words = 200, stopwords = set(STOPWORDS))
   cloud.generate(string)
   pPlot.imshow(cloud)
   pPlot.axis("off")
   pPlot.show()


create_word_cloud(file_text)