from builtins import dict

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from PIL import Image
from gensim import *
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from wordcloud import WordCloud, STOPWORDS
from anytree import Node, RenderTree, PreOrderIter, exporter

from stat import *
from PIL import *
from pyglet import *
from Sentiments import *
#from urllib.parse import urlparse

from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn

from spacy import displacy
from spacy.lang.en import English


import pyLDAvis.gensim
import en_core_web_sm
import numpy as np
import pandas as pd
import pickle

from QuestionGenerator.identification import *
from QuestionGenerator.questionValidation import *
from QuestionGenerator.nlpNER import *
from QuestionGenerator.nonClause import *
from QuestionGenerator.clause import *
from QuestionGenerator.aqgFunction import *

import matplotlib, re, nltk, os, spacy

nlp = spacy.load('en_core_web_sm')

import pyautogui, qstylizer.style

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

class Query():
    # Word Cloud
    def CreateWordCloud(self, DataSourceText, WCBGColor, maxword, maskname):
        # create numpy araay for wordcloud mask image
        mask = np.array(Image.open("Word Cloud Maskes/" + maskname + ".png"))

        # create wordcloud object
        wc = WordCloud(background_color=WCBGColor, max_words=int(maxword), mask=mask, stopwords=set(STOPWORDS))

        # generate wordcloud
        wc.generate(DataSourceText)

        return wc.to_image()

    def text_preprocessing(self,document_text):
        # convert all text to lowercase
        doc_text = document_text.lower()

        # remove numbers
        doc_text = re.sub(r'\d+', '', doc_text)

        # remove punctuation, characters and whitespaces
        doc_text = re.sub('\W+', ' ', doc_text)

        # remove stopwords and tokenize
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(doc_text)
        result = [i for i in tokens if not i in stop_words]

        result2 = []

        for word in result:
            if len(word) > 2:
                result2.append(word)

        return result2

    def GenerateFrequencyList(self, match_pattern):
        frequency = {}

        for word in match_pattern:
            count = frequency.get(word, 0)
            frequency[word] = count + 1

        frequency_list = frequency.keys()
        return frequency_list,frequency

    def find_exact_word(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\w+', doc_text)
        frequency_list,frequency = self.GenerateFrequencyList(match_pattern)

        count = 0
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def FindWordFrequency(self, DataSourceText):
        WordFrequencyRow = []
        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)

        total_count = 0
        # stop_words = set(stopwords.words('english'))

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            syns = wn.synsets(words)

            synonyms = []
            antonyms = []
            i = 0


            if len(syns) != 0:
                for syn in syns:
                    if len(syn.lemmas()) != 0:
                        for l in syn.lemmas():
                            for w1 in frequency_list:
                                if w1 == l.name():
                                    synonyms.append(l.name())
                                    if (len(l.antonyms()) != 0):
                                        if l.antonyms():
                                            for w2 in frequency_list:
                                                if w2 == l.antonyms()[0].name():
                                                    antonyms.append(l.antonyms()[0].name())
                                                    break

            if len(synonyms) == 0:
                synonyms.append('-')
            else:
                synonyms = list(dict.fromkeys(synonyms))

            if len(antonyms) == 0:
                antonyms.append('-')
            else:
                antonyms = list(dict.fromkeys(antonyms))

            weighted_percentage = round((frequency[words]/total_count)*100,2)

            if len(syns) != 0:
                WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage, syns[0].definition(), ', '.join(set(synonyms)), ', '.join(set(antonyms))])
            else:
                WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage, '-', ', '.join(set(synonyms)), ', '.join(set(antonyms))])

        return WordFrequencyRow

    def FindSimpleFrequency(self, DataSourceText):
        WordFrequencyRow = []

        DataSourceTextLower = DataSourceText

        match_pattern = re.findall(r'\w+', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)

        total_count = 0

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            weighted_percentage = round((frequency[words]/total_count)*100,2)
            WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage])

        return WordFrequencyRow

    def FindStemmedWords(self, StemWord, DataSourceText):
        StemWordList = []

        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)

        porter = PorterStemmer()

        stem_word = porter.stem(StemWord)

        count = 0
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                StemWordList.append([words, count])

        return StemWordList

    def GetDistinctWords(self, DataSourceText):
        result = self.text_preprocessing(DataSourceText)
        frequency_list, frequency = self.GenerateFrequencyList(result)
        return frequency_list

    # Part of Speech
    def PartOfSpeech(self, DataSourceName, DataSourceText, limit):
        os.environ["PATH"] += os.pathsep + 'Graphviz2.38/bin/'

        WordFrequencyTable = self.FindWordFrequency(DataSourceText)

        word_list = [i[0] for i in WordFrequencyTable]

        freq_list = [i[2] for i in WordFrequencyTable]

        stra = " "
        list_to_string = stra.join(word_list)

        # nlp = spacy.load("en_core_web_sm")

        # doc = nlp(list_to_string)

        tokens = nltk.word_tokenize(list_to_string)
        doc = nltk.pos_tag(tokens)
        # print(tokens)
        # print(doc)

        pos_list = []
        i = 0
        for word, pos in doc:
            pos_list.append([word, pos, freq_list[i]])
            i += 1

        # print(pos_list)
        pos_list = sorted(pos_list, key=lambda l: l[2], reverse=True)

        root = Node(DataSourceName)
        noun_node = Node("Noun", parent=root)
        verb_node = Node("Verb", parent=root)
        adj_node = Node("Adj", parent=root)

        noun_limit = 0
        verb_limit = 0
        adj_limit = 0

        for word, tag, freq in pos_list:
            if (tag == "NN" or tag == 'NNS') and (noun_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=noun_node)
                noun_limit += 1

            elif (tag == "VB" or tag == 'VBD') and (verb_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=verb_node)
                verb_limit += 1

            elif (tag == "JJ" or tag == 'JJR' or tag == 'JJS') and (adj_limit < limit):
                word_tag = Node(word + "\n" + str(freq), parent=adj_node)
                adj_limit += 1

        # png image of tree
        exporter.DotExporter(root).to_picture("tree.png")
        POSTreeImage = Image.open("tree.png")
        ImageArray = np.array(POSTreeImage)
        POSTreeImage = Image.fromarray(ImageArray)
        os.remove('tree.png')

        noun_count = 0
        verb_count = 0
        adj_count = 0

        blob2 = TextBlob(DataSourceText)

        for word, tag, freq in pos_list:
            if tag == "NN" or tag == 'NNS':
                noun_count += 1
            elif tag == "VB" or tag == 'VBD':
                verb_count += 1
            elif tag == "JJ" or tag == 'JJR' or tag == 'JJS':
                adj_count += 1

        return ([POSTreeImage, pos_list, noun_count, verb_count, adj_count])

    #Entity RelationShip
    def EntityRelationShip(self, DataSourceText):
        nlp = en_core_web_sm.load()
        DataSourceTextER = nlp(DataSourceText)

        Entity_List = [(X.text, X.label_) for X in DataSourceTextER.ents]

        Entity_Labels = [x.label_ for x in DataSourceTextER.ents]

        newlist = []

        for row in Entity_List:
            list(row)
            Chkflag = False
            for itm, freq, value in newlist:
                if itm == row[0]:
                    newlist[newlist.index([itm, freq, value])] = [itm, freq + 1, value]
                    Chkflag = True
                    break

            if not Chkflag:
                newlist.append([row[0].rstrip(), 1, row[1]])

        return [newlist, displacy.render(nlp(str(DataSourceTextER)), jupyter=False, style='ent'),
                displacy.render(nlp(str(DataSourceTextER)), jupyter=False, style='dep')]

    #  *********************************** Topic Modelling **********************************

    def tokenize(self, DataSourceText):
        parser = English()
        lda_tokens = []
        tokens = parser(DataSourceText)
        for token in tokens:
            if token.orth_.isspace():
                continue
            elif token.like_url:
                lda_tokens.append('URL')
            elif token.orth_.startswith('@'):
                lda_tokens.append('SCREEN_NAME')
            else:
                lda_tokens.append(token.lower_)
        return lda_tokens

    def get_lemma(self, word):
        lemma = wn.morphy(word)
        if lemma is None:
            return word
        else:
            return lemma

    def get_lemma2(self, word):
        return WordNetLemmatizer().lemmatize(word)

    def prepare_text_for_lda(self, text):
        en_stop = set(nltk.corpus.stopwords.words('english'))
        tokens = self.tokenize(text)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [token for token in tokens if token not in en_stop]
        tokens = [self.get_lemma(token) for token in tokens]
        return tokens

    def TopicModelling(self, DataSourceText, Topic_NUM):
        #spacy.load('en_core_web_sm')

        text_data = []

        tokens = self.prepare_text_for_lda(DataSourceText)

        text_data.append(tokens)

        dictionary = corpora.Dictionary(text_data)
        corpus = [dictionary.doc2bow(text) for text in text_data]
        pickle.dump(corpus, open('Topic Modelling Files/corpus.pkl', 'wb'))
        dictionary.save('Topic Modelling Files/dictionary.gensim')

        ldamodel = models.ldamodel.LdaModel(corpus, num_topics=Topic_NUM, id2word=dictionary, passes=15)
        ldamodel.save('Topic Modelling Files/model5.gensim')
        topics = ldamodel.print_topics(num_words=4)

        new_doc = 'Practical Bayesian Optimization of Machine Learning Algorithms'
        new_doc = self.prepare_text_for_lda(new_doc)
        new_doc_bow = dictionary.doc2bow(new_doc)

        dictionary = corpora.Dictionary.load('Topic Modelling Files/dictionary.gensim')
        corpus = pickle.load(open('Topic Modelling Files/corpus.pkl', 'rb'))
        lda = models.ldamodel.LdaModel.load('Topic Modelling Files/model5.gensim')

        lda_display = pyLDAvis.gensim.prepare(lda, corpus, dictionary, sort_topics=True)
        return pyLDAvis.prepared_data_to_html(lda_display)

    #  *********************************** Question Generator **********************************

    def GenerateQuestion(self, DataSourceText):
        aqg = AutomaticQuestionGenerator()
        questionList = aqg.aqgParse(DataSourceText)

        returnList = []

        for row in questionList:
            if len(row) == 1:
                pass
            else:
                returnList.append(row)

        return returnList

