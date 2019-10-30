import matplotlib.pyplot as pPlot
from wordcloud import WordCloud, STOPWORDS
import docx2txt
import numpy as np
import os
from PIL import Image

# dataset = open("files/test.txt", "r").read().lower()
file_text = docx2txt.process("F:\Semester 7\Analytical Approach to Marketing Decisions\Excel Practice.docx")
# print(file_text)

def create_word_cloud(string):
   mask = np.array(Image.open("Word Cloud Maskes/Petal.png"))
   cloud = WordCloud(background_color = "white",mask=mask, max_words = 200, stopwords = set(STOPWORDS))
   cloud.generate(string)
   pPlot.imshow(cloud)
   pPlot.axis("off")
   pPlot.show()


create_word_cloud(file_text)