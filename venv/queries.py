import re
from prettytable import PrettyTable
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer

class Query():
    def GenerateFrequencyList(self, match_pattern):
            frequency = {}

            for word in match_pattern:
                count = frequency.get(word, 0)
                frequency[word] = count + 1


            frequency_list = frequency.keys()

            return frequency_list,frequency

    def find_exact_word(self, word, document_text):
        doc_text = document_text.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', doc_text)
        frequency_list,frequency = self.GenerateFrequencyList(match_pattern)


        count = 0;
        for words in frequency_list:
            if word == words:
                count = frequency[words]

        print("Word: ", word, "\tReferences: ", count)

    def FindWordFrequency(self, DataSourceText):
        WordFrequencyRow = []

        DataSourceTextLower = DataSourceText

        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)

        total_count = 0;

        for words in frequency_list:
            total_count += frequency[words]

        for words in frequency_list:
            weighted_percentage = round((frequency[words]/total_count)*100,2)
            WordFrequencyRow.append([words, len(words), frequency[words], weighted_percentage])

        return WordFrequencyRow

    def FindStemmedWords(self, StemWord, DataSourceText):
        StemWordList = []

        DataSourceTextLower = DataSourceText.lower()

        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)

        porter = PorterStemmer()

        stem_word = porter.stem(StemWord)

        count = 0;
        for words in frequency_list:
            if stem_word == porter.stem(words):
                count = frequency[words]
                StemWordList.append([words, count])

        return StemWordList

    def GetDistinctWords(self, DataSourceText):
        DataSourceTextLower = DataSourceText.lower()
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', DataSourceTextLower)
        frequency_list, frequency = self.GenerateFrequencyList(match_pattern)
        return frequency_list


# testing
myquery = Query()
document_text = "trouble troubling trouble"
#myquery.find_exact_word("hello",document_text)
#myquery.FindWordFrequency(document_text)
print(myquery.FindStemmedWords("trouble",document_text))

