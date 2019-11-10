import pickle
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import os.path

# manual_coding = Node("Codes")
cases = Node("Cases")
nodes = Node("Nodes")
sentiments = Node("Sentiment")


def retrieve_code(code_type):
    path = '/code_files' + code_type
    if os.path.isfile(path):
        filehandler = open(path, 'rb')
        code = pickle.load(filehandler)
        return code
    else:
        # create new file and code
        return False


def create_node(topic,text):
    code_type_topic = Node(topic, parent = nodes)
    topic_text = Node(text, parent = code_type_topic)
    Node("% coverage in file ", parent = topic_text)
    Node("References", parent = topic_text)
    return nodes


def create_cases(topic,text):
    code_type_topic = Node(topic, parent = cases)
    topic_text = Node(text, parent = code_type_topic)
    Node("% coverage in file ", parent = topic_text)
    Node("References", parent = topic_text)
    return cases


def create_sentiment(topic,text):
    code_type_topic = Node(topic, parent = sentiments)
    topic_text = Node(text, parent = code_type_topic)
    Node("% coverage in file ", parent = topic_text)
    Node("References", parent = topic_text)
    return sentiments


def save_codes(head,code_type):
    path = 'code_files/' + code_type
    filehandler = open(path,'wb')
    pickle.dump(head,filehandler)
    filehandler.close()


def print_codes(head,code_type):
    path = 'code_files/' + code_type
    filehandler = open(path,'rb')
    codes = pickle.load(filehandler)
    for pre, fill, node in RenderTree(codes):
        print("%s%s" % (pre, node.name))
    return codes

def append_to_case(head,text):
    next = Node(text,parent = head)
    Node("% coverage in file ", parent=next)
    Node("References", parent=next)
    return cases




# create_node("Therapy","Selected Text related to therapy")
# create_cases("Dr.Raza","Selected Text related to Dr.Raza")
# create_cases("Dr.Ahmed","Selected Text related to Dr.Ahmed")
# create_cases("Dr.Haider","Selected Text related to Dr.Haider")
# create_sentiment("Positive","Selected Text identified as positive by user")
# create_sentiment("Negative","Selected Text identified as negative by user")
#
#
# save_codes(cases,"cases")
# print_codes(cases,"cases")
#
# save_codes(sentiments,"sentiments")
# print_codes(sentiments,"sentiments")

append_to_case(cases,"More about Dr.Raza")

# code = retrieve_code("Cases")
print_codes(cases,"cases")



