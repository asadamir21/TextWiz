import numpy as np
import re
import nltk
from sklearn.datasets import load_files
import pickle
from nltk.corpus import stopwords
from read_files import *
import string
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split


def text_preprocessing(document_text):

    # convert all text to lowercase
    doc_text = document_text.lower()

    # remove numbers
    doc_text = re.sub(r'\d+','',doc_text)

    # remove punctuation, characters and whitespaces
    doc_text = re.sub('\W+',' ',doc_text)

    # remove stopwords and tokenize
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(doc_text)
    result = [i for i in tokens if not i in stop_words]

    # stemming
    # stemmed_words = []
    # stemmer = PorterStemmer()
    # for word in result:
    #     stemmed_words.append(stemmer.stem(word))


    # lemmatization
    final_text = []
    lem = WordNetLemmatizer()
    for word in result:
        final_text.append(lem.lemmatize(word))

    # print(final_text)
    return final_text

filename = "C:/Users/farma/Desktop/internship docs/submissions/IBA INTERNSHIP REPORT.docx"
document_text = read_file(filename,get_extension(filename))
documents = text_preprocessing(document_text)

# vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
# X = vectorizer.fit_transform(documents).toarray()
#
# tfidfconverter = TfidfTransformer()
# X = tfidfconverter.fit_transform(X).toarray()
#
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
#
# classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
# classifier.fit(X_train, y_train)
# y_pred = classifier.predict(X_test)
