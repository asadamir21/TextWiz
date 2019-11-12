import pickle
from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
import os.path

class Code:

    cases = Node("Cases")
    nodes = Node("Nodes")
    sentiments = Node("Sentiment")

    def retrieve_code(self,code_type):
        path = 'code_files/' + code_type
        if os.path.isfile(path):
            filehandler = open(path, 'rb')
            code = pickle.load(filehandler)
            # for pre, fill, node in RenderTree(code):
            #     print("%s%s" % (pre, node.name))
            return code
        else:
            # create new file and code
            return False

    def create_code(self,code_type,topic,text):
        code_type_topic = Node(topic,parent=code_type)
        topic_text = Node(text, parent=code_type_topic)
        Node("% coverage in file ", parent=topic_text)
        Node("References", parent=topic_text)
        # return code_type

    def save_codes(self,head, code_type):
        path = 'code_files/' + code_type
        filehandler = open(path, 'wb')
        pickle.dump(head, filehandler)
        filehandler.close()

    def print_codes(self,code_type):
        # path = 'code_files/' + code_type
        # filehandler = open(path, 'rb')
        # codes = pickle.load(filehandler)
        for pre, fill, node in RenderTree(code_type):
            print("%s%s" % (pre, node.name))

    def append_to_code(self,code_type,head,text):
        if code_type == 'cases':
           for node in PreOrderIter(self.cases):
               if node.name == head:
                   new_node = Node(text, parent = node)
                   Node("% coverage in file ", parent=new_node)
                   Node("References", parent=new_node)
        elif code_type == 'sentiments':
           for node in PreOrderIter(self.sentiments):
               if node.name == head:
                   new_node = Node(text, parent = node)
                   Node("% coverage in file ", parent=new_node)
                   Node("References", parent=new_node)


mycode = Code()
mycode.create_code(mycode.cases,"Dr.Ahmed","Text1") # create new case
mycode.save_codes(mycode.cases,"cases") # saving codes in file with respected names
mycode.cases = mycode.retrieve_code("cases") # needs to be called when coding(cases) window opens
mycode.print_codes(mycode.cases) # print tree for cases
mycode.append_to_code("cases","Dr.Ahmed","Text2") # adding selected text to same case
mycode.save_codes(mycode.cases,"cases")
mycode.cases = mycode.retrieve_code("cases")
mycode.print_codes(mycode.cases)

# mycode.create_code(mycode.sentiments,"Positive","Txt3")
# mycode.save_codes(mycode.sentiments,"sentiments")
mycode.sentiments = mycode.retrieve_code("sentiments")
mycode.print_codes(mycode.sentiments)
mycode.append_to_code("sentiments","Positive","Txt 4")
mycode.save_codes(mycode.sentiments,"sentiments")
mycode.sentiments = mycode.retrieve_code("sentiments")
mycode.print_codes(mycode.sentiments)