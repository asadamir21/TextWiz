import spacy
from QuestionGenerator.clause import *
from QuestionGenerator.nonClause import *
from QuestionGenerator.identification import *
from QuestionGenerator.questionValidation import *
from QuestionGenerator.nlpNER import nerTagger



class AutomaticQuestionGenerator():
    # AQG Parsing & Generate a question
    def aqgParse(self, sentence):

        #nlp = spacy.load("en")
        nlp = spacy.load('en_core_web_sm')

        singleSentences = sentence.split(".")
        questionsList = []
        if len(singleSentences) != 0:
            for i in range(len(singleSentences)):
                segmentSets = singleSentences[i].split(",")

                ner = nerTagger(nlp, singleSentences[i])

                if (len(segmentSets)) != 0:
                    for j in range(len(segmentSets)):
                        try:
                            questionsList += howmuch_2(segmentSets, j, ner)
                        except Exception:
                            pass

                        if clause_identify(segmentSets[j]) == 1:
                            try:
                                questionsList += whom_1(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += whom_2(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += whom_3(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += whose(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += what_to_do(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += who(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += howmuch_1(segmentSets, j, ner)
                            except Exception:
                                pass
                            try:
                                questionsList += howmuch_3(segmentSets, j, ner)
                            except Exception:
                                pass


                            else:
                                try:
                                    s = subjectphrase_search(segmentSets, j)
                                except Exception:
                                    pass

                                if len(s) != 0:
                                    segmentSets[j] = s + segmentSets[j]
                                    try:
                                        questionsList += whom_1(segmentSets, j, ner)
                                    except Exception:
                                        pass
                                    try:
                                        questionsList += whom_2(segmentSets, j, ner)
                                    except Exception:
                                        pass
                                    try:
                                        questionsList += whom_3(segmentSets, j, ner)
                                    except Exception:
                                        pass
                                    try:
                                        questionsList += whose(segmentSets, j, ner)
                                    except Exception:
                                        pass
                                    try:
                                        questionsList += what_to_do(segmentSets, j, ner)
                                    except Exception:
                                        pass
                                    try:
                                        questionsList += who(segmentSets, j, ner)
                                    except Exception:
                                        pass

                                    else:
                                        try:
                                            questionsList += nwhat_whom1(segmentSets, j, ner)
                                        except Exception:
                                            pass
                                        try:
                                            questionsList += what_whom2(segmentSets, j, ner)
                                        except Exception:
                                            pass
                                        try:
                                            questionsList += whose(segmentSets, j, ner)
                                        except Exception:
                                            pass
                                        try:
                                            questionsList += howmany(segmentSets, j, ner)
                                        except Exception:
                                            pass
                                        try:
                                            questionsList += howmuch_1(segmentSets, j, ner)
                                        except Exception:
                                            pass

                questionsList.append('\n')
        return questionsList



    def DisNormal(self, str):
        print("\n")
        print("------X------")
        print("Start  output:\n")

        count = 0
        out = ""

        for i in range(len(str)):
            count = count + 1
            print("Q-0%d: %s" % (count, str[i]))

        print("")
        print("End  OutPut")
        print("-----X-----\n\n")


    # AQG Display the Generated Question
    def display(self, str):
        print("\n")
        print("------X------")
        print("Start  output:\n")

        count = 0
        out = ""
        for i in range(len(str)):
            if (len(str[i]) >= 3):
                if (hNvalidation(str[i]) == 1):
                    if ((str[i][0] == 'W' and str[i][1] == 'h') or (str[i][0] == 'H' and str[i][1] == 'o') or (
                            str[i][0] == 'H' and str[i][1] == 'a')):
                        WH = str[i].split(',')
                        if (len(WH) == 1):
                            str[i] = str[i][:-1]
                            str[i] = str[i][:-1]
                            str[i] = str[i][:-1]
                            str[i] = str[i] + "?"
                            count = count + 1

                            if (count < 10):
                                print("Q-0%d: %s" % (count, str[i]))
                                out += "Q-0" + count.__str__() + ": " + str[i] + "\n"

                            else:
                                print("Q-%d: %s" % (count, str[i]))
                                out += "Q-" + count.__str__() + ": " + str[i] + "\n"

        print("")
        print("End  OutPut")
        print("-----X-----\n\n")

        output = "DB/output.txt"
        w = open(output, 'w+', encoding="utf8")
        w.write(out)
        w.close()
        return 0
