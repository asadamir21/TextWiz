import nltk
import docx2txt, PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
from bs4 import BeautifulSoup
import spacy
import re
import requests
from spacy import displacy
from collections import Counter
from IPython.core.display import Image, display, HTML
from pathlib import Path
import os

#nlp = spacy.load("en_core_web_sm")

pdfReader = PyPDF2.PdfFileReader("C:/Users/Asad/Desktop/AAMD/Mid Term/Midterm Exam.pdf")

text = ""

for page in range(pdfReader.getNumPages()):
    curr_page = pdfReader.getPage(page)
    text = text + curr_page.extractText()



os.system(os.startfile("C:/Users/Asad/Desktop/AAMD/Mid Term/Midterm Exam.pdf"))






# doc = nlp(text)
# pprint([(X.text, X.label_) for X in doc.ents])

#
# def url_to_string(url):
#     res = requests.get(url)
#     html = res.text
#     soup = BeautifulSoup(html, 'html.parser')
#
#     for script in soup(["script", "style", 'aside']):
#         script.extract()
#     return " ".join(re.split(r'[\n\t]+', soup.get_text()))
#
# ny_bb = url_to_string('https://www.nytimes.com/2018/08/13/us/politics/peter-strzok-fired-fbi.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=first-column-region&region=top-news&WT.nav=top-news')
# article = nlp(ny_bb)
#
# items = [x.text for x in article.ents]
# #print(Counter(items).most_common(3))
# #print(Counter(items))
#
# sentences = [x for x in article.sents]
# #print(sentences[20])
#
# svg = HTML(displacy.render(nlp(str(sentences[20])), jupyter=True, style='ent'))
#
# print(svg.url)

#image = Image(svg.url)

#display(image)



