from read_files import *
import re
from prettytable import PrettyTable
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as pPlot
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


class Query():

    def generate_freq_list(self, match_pattern):
        frequency = {}
        for word in match_pattern:
            count = frequency.get(word, 0)
            frequency[word] = count + 1

        frequency_list = frequency.keys()

        return frequency_list, frequency

    def find_exact_word(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list, frequency = self.generate_freq_list(match_pattern)

        count = 0;
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def word_freq_table(self, document_text, min_word_length):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list, frequency = self.generate_freq_list(match_pattern)

        word_freq_table = PrettyTable()
        word_freq_table.field_names = ["S.NO", "Word", "Length", "Count", "Weighted Percentage"]
        word_freq_table.sortby = "Count"
        word_freq_table.reversesort = True

        sno = 0;
        total_count = 0;

        for words in frequency_list:
            if len(words) >= min_word_length:
                total_count += frequency[words]

        for words in frequency_list:
            if len(words) >= min_word_length:
                sno = sno + 1
                weighted_percentage = round((frequency[words] / total_count) * 100, 2)
                word_freq_table.add_row([sno, words, len(words), frequency[words], weighted_percentage])

        print(word_freq_table)

    def find_stemmed_words(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list, frequency = self.generate_freq_list(match_pattern)

        porter = PorterStemmer()

        stem_word = porter.stem(word)

        count = 0;
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                print("Word:", words, "\tReferences:", count)

    def word_cloud(self,doc_text):
        cloud = WordCloud(background_color="black", max_words=50, stopwords=set(STOPWORDS))
        cloud.generate(doc_text)
        pPlot.imshow(cloud)
        pPlot.axis("off")
        pPlot.show()

    def word_freq_graph(self,document_text):

        # convert all text to lowercase
        doc_text = document_text.lower()

        # remove numbers
        doc_text = re.sub(r'\d+', '', doc_text)

        # remove punctuation, characters and whitespaces
        doc_text = re.sub('\W+', ' ', doc_text)

        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(doc_text)
        result = [i for i in tokens if not i in stop_words]

        fdist = FreqDist(result)
        fdist.plot(30, cumulative=False)
        pPlot.show()

# testing
myquery = Query()
filename = "C:/Users/farma/Desktop/internship docs/submissions/IBA INTERNSHIP REPORT.docx"
document_text = read_file(filename, get_extension(filename))
myquery.find_exact_word("dcc", document_text)
myquery.word_freq_table(document_text,4)
myquery.find_stemmed_words("provide", document_text)
# myquery.word_cloud(document_text)
myquery.word_freq_graph(document_text)