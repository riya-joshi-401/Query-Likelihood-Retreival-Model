# importing necessary libraries
import glob
import os
import shutil
import re
import string
import sys
from bs4 import BeautifulSoup
from math import ceil

# files to be used
DIR_RAW_HTML='CASM-Files/Corpus'
STOPPED_WORDS_FILE='CASM-Files/common_words.txt'
STEMMED_QUERIES='CASM-Files/cacm_stem.txt'

# output directories
DIR_CORPUS='CorpusGeneration/TokenizedCorpus'
DIR_CORPUS_WITH_STOPPING='CorpusGeneration/TokenizedCorpusWithStopping'
DIR_CORPUS_WITH_STEMMING='CorpusGeneration/TokenizedCorpusWithStemming'


# method to convert HTML content into plain text
# Given: HTML content
# Returns: plain text
def parseHTML(htmlContent):
    soup = BeautifulSoup(htmlContent, 'html.parser')
    print(soup.get_text())
    text=soup.get_text()
    matchObj=re.search(r'[ \t\n\r\f\v]AM|[ \t\n\r\f\v]PM',text,re.M|re.I)
    if matchObj:
        return text[:matchObj.end()]
    return text


# method to case-fold the text provided
# Given: plain text
# Return: case folded plain text  
def caseFold(plainText):
    return plainText.lower()


# method to remove punctuation from the text provided
# Given: plain text
# Return:  plain text with removed punctuation
def removePunctuation(tokens):
    newList=[]
    for tok in tokens:
        tok=tok.strip(string.punctuation)
        matchNum=re.compile(r'^[\-]?[0-9]*\.?[0-9]+$')
        if not matchNum.match(tok):
            tok=re.sub(r'[^a-zA-Z0-9\--]','',tok)
            tok=tok.strip(string.punctuation)
        newList.append(tok)
        
    return newList
    
    
# method to generate tokens from plain text
# Given: plain text
# Return: list of tokens     
def generateTokens(plainText):
    return list(filter(re.compile('[a-zA-Z0-9_]').search,plainText.split()))


def parser(fileName):
    f = open(fileName, 'r')
    # fileName = "CASM - Files / Corpus / CACM - 0001.html"
    fileName = fileName.replace(" ", "")
    docName=fileName.split('/')[-1].split('.')[0]+'.txt'
    content = f.read()
    f.close()
    plainText=parseHTML(content)
    caseFoldedPlainText=caseFold(plainText)
    tokens=generateTokens(caseFoldedPlainText)
    tokens=removePunctuation(tokens)
    
    return (tokens,docName)

def writeTokenizedFiles(joinTokens,docName,corpusDirectory):
    try:    
        if not os.path.exists(corpusDirectory):
            os.makedirs(corpusDirectory)
        if os.path.exists(corpusDirectory+docName):
            print('same name file exists' ,corpusDirectory+'/'+docName)
        tokenFile=open(corpusDirectory+'/'+docName,'w')
        tokenFile.write(joinTokens)
        tokenFile.close()
    except Exception:
        print(Exception)
    
def performStopping(tokens):
    f=open(STOPPED_WORDS_FILE,'r')
    stopList=f.read().split()
    newTokenList=[]
    for t in tokens:
        if t not in stopList:
            newTokenList.append(t)
    f.close()
    
    return  newTokenList   

def stemParser(corpusDirectory):
    f=open(STEMMED_QUERIES,'r')
    stemmedCorpus={}
    for line in f.readlines():
        if line[0]=='#':
            line=line.strip('\n')
            docName='CACM-'+'0'*(abs(len(line[2:])-4))+line[2:]
            stemmedCorpus[docName]=""
        else:
            line=line.strip('\n')
            stemmedCorpus[docName]+=line
    i=1
    for docName in stemmedCorpus:
        data=stemmedCorpus[docName]
        matchObj=re.search(r'[ \t\n\r\f\v]AM|[ \t\n\r\f\v]PM',data,re.M|re.I)
        if matchObj:
            data=data[:matchObj.end()]
        
        stemmedCorpus[docName]=data
        writeTokenizedFiles(data, docName+'.txt',corpusDirectory)
        if i%160==0:
            print("Parsing and Tokenization "+str(ceil(i/float(len(stemmedCorpus))*100))+'% complete')
        i+=1
       
    f.close()

def selectTypeOfTextTransformation():
     
    while True:
        print("\nSelect transformation technique:")
        print("Enter 1 No Stopping No Stemming")
        print("Enter 2 With Stopping")
        print("Enter 3 With Stemming")
        print("Enter 4 to exit")
        x=int(input("Enter choice: "))
        if x==1:
            corpusDirectory=DIR_CORPUS
            path = os.path.join(DIR_RAW_HTML, r"*.html")
            rawFiles = glob.glob(path)
            i = 1
            print("Starting to generate corpus.....")
            print("Parsing and Tokenization 0% complete")
            for fileName in rawFiles:
                # print(fileName)
                tokens, docName = parser(fileName)
                joinTokens = " ".join(tokens)
                writeTokenizedFiles(joinTokens, docName, corpusDirectory)
                if i % 160 == 0:
                    print("Parsing and Tokenization " + str(ceil(i / float(len(rawFiles)) * 100)) + '% complete')
                i += 1
        elif x==2:
            corpusDirectory=DIR_CORPUS_WITH_STOPPING
            path = os.path.join(DIR_RAW_HTML, r"*.html")
            rawFiles = glob.glob(path)
            i = 1
            print("Starting to generate corpus.....")
            print("Parsing and Tokenization 0% complete")
            for fileName in rawFiles:
                #print(fileName)
                tokens, docName = parser(fileName)
                tokens = performStopping(tokens)
                joinTokens = " ".join(tokens)
                writeTokenizedFiles(joinTokens, docName, corpusDirectory)
                if i % 160 == 0:
                    print("Parsing and Tokenization " + str(ceil(i / float(len(rawFiles)) * 100)) + '% complete')
                i += 1
        elif x==3:
            corpusDirectory=DIR_CORPUS_WITH_STEMMING
            stemParser(corpusDirectory)
        else:
            break

if __name__ == '__main__':
    selectTypeOfTextTransformation()