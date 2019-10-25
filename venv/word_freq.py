import re
from prettytable import PrettyTable

document_text = open('files/screens.txt','r')
frequency = {}
text_string = document_text.read().lower()

match_pattern = re.findall(r'\b[a-z]{3,15}\b',text_string)

word_freq_table = PrettyTable()
word_freq_table.field_names = ["S.NO","Word","Length","Count"]

for word in match_pattern:
    count = frequency.get(word, 0)
    frequency[word] = count + 1

frequency_list = frequency.keys()
sno = 0
for words in frequency_list:
    sno = sno + 1
    word_freq_table.add_row([sno,words,len(words),frequency[words]])

print(word_freq_table)


def findWord(word):

    count = 0;
    for words in frequency_list:
        if word == words:
            count = frequency[words]

    print("Word: ",word,"\tReferences: ",count)


findWord("python")