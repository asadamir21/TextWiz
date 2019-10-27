from read_files import *
import re
from prettytable import PrettyTable
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer

class Query():

    def generate_freq_list(self,match_pattern):
            frequency = {}
            for word in match_pattern:
                count = frequency.get(word, 0)
                frequency[word] = count + 1


            frequency_list = frequency.keys()

            return frequency_list,frequency

    def find_exact_word(self,word,document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list,frequency = self.generate_freq_list(match_pattern)

        count = 0;
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def word_freq_table(self,document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list, frequency = self.generate_freq_list(match_pattern)

        word_freq_table = PrettyTable()
        word_freq_table.field_names = ["S.NO", "Word", "Length", "Count", "Weighted Percentage"]

        sno = 0;
        total_count = 0;

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            sno = sno + 1
            weighted_percentage = round((frequency[words]/total_count)*100,2)
            word_freq_table.add_row([sno, words, len(words), frequency[words],weighted_percentage])

        print(word_freq_table,)

    def find_stemmed_words(self,word,document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list, frequency = self.generate_freq_list(match_pattern)

        porter = PorterStemmer()

        stem_word = porter.stem(word)

        count = 0;
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                print("Word:",words,"\tReferences:",count)



# testing
myquery = Query()
document_text = "trouble troubling trouble"
myquery.find_exact_word("hello",document_text)
myquery.word_freq_table(document_text)
myquery.find_stemmed_words("trouble",document_text)

