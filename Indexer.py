# Importing necessary libraries
import glob
import os
import sys

# corpus directory without stopped and stemmed data
DIR_CORPUS='CorpusGeneration/TokenizedCorpus'
# corpus directory with stopped data
DIR_CORPUS_WITH_STOPPING='CorpusGeneration/TokenizedCorpusWithStopping'
# corpus directory with stemmed data
DIR_CORPUS_WITH_STEMMING='CorpusGeneration/TokenizedCorpusWithStemming'
# directory for index text files
DIR_INDEX_TEXT_FILES='Indexing/IndexTextFiles/'


# method to create index
#  TERM:{docId:tf}
def buildIndex(corpusDirectory):
    invertedList={}
    noOfTokensInDoc={}
    path=os.path.join(corpusDirectory,r"*.txt")
    tokenFiles=glob.glob(path)
    for fName in tokenFiles:
        f=open(fName,'r')
        listOfTokens=f.read().split()
        docName = fName.split('/')[-1].split('.')[0]
        print(docName)
        noOfTokensInDoc[docName]=len(listOfTokens)
        for token in listOfTokens:
            if not token in invertedList:
                invertedList[token]={docName:1}
            else:
                doc=invertedList[token]
                if not docName in doc: 
                    doc[docName]=1
                else:
                    doc[docName]+=1
    
    print("No. of indexed terms: ",str(len(invertedList)))
    return (invertedList,noOfTokensInDoc)

  
# create text files for each unigram index
def writeIndexToTextFile(index,mode):
    if not os.path.exists(DIR_INDEX_TEXT_FILES):
        os.makedirs(DIR_INDEX_TEXT_FILES)
    fName=DIR_INDEX_TEXT_FILES+'unigram-'+mode+'-index.txt'
    if os.path.exists(fName):
        os.remove(fName)
    fileIndex=open(fName,'w')
    # fileIndex.write('##########################################################################################\n')
    # fileIndex.write('################################ Unigram Inverted Index ##################################\n')
    # fileIndex.write('##########################################################################################\n\n\n')
    fileIndex.write("{")
    for term in index:
        fileIndex.write("'"+term+"' : ")
        docDic=index[term]
        s=[]
        for doc in docDic:
            tup=()+(str(doc),)+(str(docDic[doc]),)
            s.append(tup)
        fileIndex.write(str(s)+",")
    fileIndex.write("}")
    fileIndex.close()


def generateNoOfTermsPerDocFile(noOfTokensPerDoc,mode):
    if not os.path.exists(DIR_INDEX_TEXT_FILES):
        os.makedirs(DIR_INDEX_TEXT_FILES)
    fName=DIR_INDEX_TEXT_FILES+'NoTokensPerDoc-'+mode+'.txt'
    if os.path.exists(fName):
        os.remove(fName)
    fileIndex=open(fName,'w')
    # fileIndex.write('##########################################################################################\n')
    # fileIndex.write('#################################### Tokens Per Document #################################\n')
    # fileIndex.write('##########################################################################################\n\n\n')
    fileIndex.write("{")
    for doc in noOfTokensPerDoc:
        fileIndex.write("'"+doc+"':  "+str(noOfTokensPerDoc[doc])+",")
    fileIndex.write("}")
    fileIndex.close()
                

def selectTheCorpusForIndexing1():
    while True:
        print("\nSelect the corpus for indexing:")
        print("Enter 1 No Stopping and Stemming")
        print("Enter 2 With Stopping")
        print("Enter 3 With Stemming")
        print("Enter 4 to exit!!")
        x=int(input("Enter choice: "))
        if x==1:
            corpusDirectory=DIR_CORPUS
            mode="no_stopping_or_stemming"
        elif x==2:
            corpusDirectory=DIR_CORPUS_WITH_STOPPING
            mode="withStopping"
        elif x==3:
            corpusDirectory=DIR_CORPUS_WITH_STEMMING
            mode="withStemming"
        else:
            break

        print('Generating Unigram Index.......')
        unigramIndex,noOfTokensInDoc=buildIndex(corpusDirectory)
        generateNoOfTermsPerDocFile(noOfTokensInDoc,mode)
        writeIndexToTextFile(unigramIndex,mode)     
    
if __name__=='__main__':
    selectTheCorpusForIndexing1()