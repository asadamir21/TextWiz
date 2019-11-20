# coding=utf-8
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from anytree import Node, RenderTree, PreOrderIter
import numpy as np
from queries import *
from read_files import *
from anytree.exporter import DotExporter
from graphviz import Source
from graphviz import render
from graphviz import Digraph
import os
import spacy

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

# pip install -U textblob
# python -m textblob.download_corpora


# noun phrases
def noun_phrases(text):
    wiki = TextBlob(text)
    for nouns in wiki.noun_phrases:
        print(nouns)


# POS tagging (noun, verb, adjectives)
def pos_tagging(text,limit): #limit is the top n words required

    query = Query()
    table = query.FindWordFrequency(text)

    word_list = [i[0] for i in table]
    freq_list = [i[2] for i in table]

    str = " "
    list_to_string = str.join(word_list)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(list_to_string)

    pos_list = []
    i = 0
    for token in doc:
        pos_list.append([token,token.pos_,freq_list[i]])
        i += 1

    # print(pos_list)
    pos_list = sorted(pos_list, key=lambda l: l[2], reverse=True)

    root = Node("Root")
    noun_node = Node("Noun",parent=root)
    verb_node = Node("Verb", parent=root)
    adj_node = Node("Adj", parent=root)

    noun_limit = 0
    verb_limit = 0
    adj_limit = 0
    for word, tag, freq in pos_list:
                if (tag == "NOUN") and (noun_limit < limit):
                    # tag = "noun"
                    # print(word,tag)
                    word_tag = Node(word, parent=noun_node)
                    # Node(freq, parent = word_tag)
                    noun_limit += 1

                elif (tag == "VERB") and (verb_limit < limit):
                    # tag = "verb"
                    # print(word,tag)
                    word_tag = Node(word, parent=verb_node)
                    # Node(freq, parent = word_tag)
                    verb_limit += 1

                elif (tag == "ADJ") and (adj_limit < limit):
                    # tag = "adjective"
                    # print(word,tag)
                    word_tag = Node(word, parent=adj_node)
                    # Node(freq, parent = word_tag)
                    adj_limit += 1

    # png image of tree
    DotExporter(root).to_dotfile('tree.dot')
    Source.from_file('tree.dot')
    render('dot', 'png', 'tree.dot')

    # printing tree
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    noun_count = 0
    verb_count = 0
    adj_count = 0

    blob2 = TextBlob(text)
    for word, tag, freq in pos_list:
                if tag == "NOUN":
                    # tag = "noun"
                    # print(word,tag)
                    noun_count += 1
                elif tag == "VERB":
                    # tag = "verb"
                    # print(word,tag)
                    verb_count += 1
                elif tag == "ADJ":
                    # tag = "adjective"
                    # print(word,tag)
                    adj_count += 1
    #counts
    print("Number of nouns in this text:", noun_count)
    print("Number of verbs in this text:", verb_count)
    print("Number of adjectives in this text:", adj_count)


def sentiment_analysis(text):
    blob = TextBlob(text)
    print(blob.sentiment)
    polarity = blob.sentiment.polarity  # polarity means its a true fact
    subjectivity = blob.sentiment.subjectivity  # subjectivity means its an opinion

    if polarity > subjectivity:
        print("This text is a true fact")
    else:
        print("This text is an opinion")


def sentiment_pos_or_neg(text):
    blob = TextBlob(text,analyzer = NaiveBayesAnalyzer())
    print(blob.sentiment)
    positive = blob.sentiment.p_pos
    negative = blob.sentiment.p_neg

    if positive > negative:
        print("This text is positive")
    else:
        print("This text is negative")


# translate text to only in english
def detection_and_translation(text):
    blob = TextBlob(text)
    try:
        if blob.detect_language() == 'en':
            print("Text is already in english")
        else:
            print(blob.translate(to='en'))
    except:
        print("Language not detected or text could not be translated")


def spelling_correction(text):
    blob = TextBlob(text)
    print(blob.correct())


# testing
# text = "Interstellar is a flawed, ambitious, gorgeous film that has the potential to either emotionally gob smack or " \
#        "befuddle. Interstellar is a flawed, ambitious, gorgeous film flawed"
# chinese_text = "美丽优于丑陋"
#
filename = "C:/Users/farma/Desktop/internship docs/submissions/IBA INTERNSHIP REPORT.docx"
file_text = read_file(filename,get_extension(filename))
pos_tagging(file_text,2)
# detection_and_translation(chinese_text)

# sentiment_analysis(text)
# sentiment_pos_or_neg(text)