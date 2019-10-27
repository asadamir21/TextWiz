import os.path,time
import PyPDF2
import docx2txt
# from pyth.plugins.rtf15.reader import Rtf15Reader
# from pyth.plugins.plaintext.writer import PlaintextWriter

def get_extension(filename):
    extension = os.path.splitext(filename)[1]
    return extension


def read_file(filepath,extension):
    if extension == ".pdf":
        pdfReader = PyPDF2.PdfFileReader(filepath)
        for page in range(pdfReader.getNumPages()):
            curr_page = pdfReader.getPage(page)
            # print(curr_page.extractText())
            return curr_page.extractText()
    elif extension == ".txt":
        file = open(filepath,'r')
        file_text = file.read();
        # print(file_text)
        return file_text
    elif extension == ".doc" or extension == ".docx":
        file_text = docx2txt.process(filepath)
        # print(file_text)
        return file_text
    # elif extension ==".rtf":
    #     doc = Rtf15Reader.read(open(filepath))
    #     print(PlaintextWriter.write(doc).getvalue())


def getMetaData(filename):

    print(time.ctime(os.path.getctime(filename)))  # creation time
    print(os.path.getsize(filename))  # file size

# filename = "C:/Users/farma/Desktop/internship docs/submissions/IBA INTERNSHIP REPORT.docx"
# read_file(filename,get_extension(filename))
# print(time.ctime(os.path.getctime(filename)))