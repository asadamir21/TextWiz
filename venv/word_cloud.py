import matplotlib.pyplot as pPlot
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import docx2txt
import numpy as np
import os
from PIL import Image

# dataset = open("files/test.txt", "r").read().lower()
file_text = docx2txt.process("I:\Semester 7\Analytical Approach to Marketing Decisions\Excel Practice.docx")
# print(file_text)

def create_word_cloud(string):

   mask = np.array(Image.open("C:/Users/Asad/Desktop/Maskes/Maskes.png"))
   cloud = WordCloud(background_color = "white",mask=mask, max_words = 500, stopwords = set(STOPWORDS))
   cloud.generate(string)

   image_colors = ImageColorGenerator(mask)
   pPlot.figure(figsize=[7, 7])
   pPlot.imshow(cloud.recolor(color_func=image_colors), interpolation="bilinear")
   pPlot.axis("off")
   pPlot.show()

create_word_cloud(file_text)