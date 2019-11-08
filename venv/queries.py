import re
from prettytable import PrettyTable
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer



# testing
myquery = Query()
document_text = "trouble troubling trouble"
myquery.find_exact_word("hello",document_text)
myquery.word_freq_table(document_text)
myquery.find_stemmed_words("trouble",document_text)

