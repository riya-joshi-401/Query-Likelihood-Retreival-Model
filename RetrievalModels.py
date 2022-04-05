# Importing necessary libraries
import math
import os
import re
import string
from bs4 import BeautifulSoup
import sys
import ast 

# file name which contains list of queries
LIST_OF_QUERY_FILE_NAME='CASM-Files/cacm.query.txt'
# output file name storing the top 100 results of Smoothed Query Likelihood Model score for all queries 
TOP_100_RESULT_QueryLikelihood='Top_100_Query_Result_QueryLikelihoodModel'
# text file of number of unigrams
INVERTED_INDEX=['Indexing/IndexTextFiles/unigram-no_stopping_or_stemming-index.txt',
                'Indexing/IndexTextFiles/unigram-withStopping-index.txt',
                'Indexing/IndexTextFiles/unigram-withStemming-index.txt']
# text file of number of tokens per document in corpus
NUM_OF_TOKEN_PER_DOC=['Indexing/IndexTextFiles/NoTokensPerDoc-no_stopping_or_stemming.txt',
                      'Indexing/IndexTextFiles/NoTokensPerDoc-withStopping.txt',
                      'Indexing/IndexTextFiles/NoTokensPerDoc-withStemming.txt']
# path of list of relevant document files
RELEVANT_DOCS='CASM-Files/cacm.rel.txt'
# list of stemmed queries
STEMMED_QUERIES='CASM-Files/cacm_stem.query.txt'
# Coefficient to control probability of unseen words
COEFFICIENT=0.35
# directory for output files
DIR_OUTPUT='Retrieval/OutputFiles'


# calculate Smoothed Query Likelihood score of each doc that has the query term
# input : inverted index of unigram, query term frequency dictionary
# output : a dictionary of docids storing the score
def calculateSMQL(invertedIndex,queryTermFreq,noOfTokenPerDoc):
    docScore={}
    # size of collection
    noOfTokenPerDoc=ast.literal_eval(noOfTokenPerDoc)
    invertedIndex = ast.literal_eval(invertedIndex)
    print("noOfTokenPerDoc: ",type(noOfTokenPerDoc))
    C=sum([noOfTokenPerDoc[doc] for doc in noOfTokenPerDoc])
    print("queryTermFreq: ",queryTermFreq)
    print("invertedIndex: ", invertedIndex)
    for qTerm in queryTermFreq:
        if qTerm not in invertedIndex:
            continue
        invertedList=invertedIndex[qTerm]
        print("invertedList: ",invertedList)
        cq = sum([int(doc[1]) for doc in invertedList])
        print("cq: ",cq)
        for doc in invertedList:
            # frequency of query term in doc
            fq=int(doc[1])
            # document size
            docSize=noOfTokenPerDoc[doc[0]]
            unseenPart=COEFFICIENT* cq / float(C)
            seenPart=(1-COEFFICIENT)*fq/float(docSize)
            if doc not in docScore:
                docScore[doc]=math.log(seenPart+unseenPart)
            else:
                docScore[doc]+=math.log(seenPart+unseenPart)
            
    return docScore

# fetch relevant docIDs for the given query id
def fetchRelevantDocIds(queryID):
    relDocIds=[]
    fName=RELEVANT_DOCS
    relFile=open(fName,'r')
    for rec in relFile.readlines():
        record=rec.split()
        print("")
        print("record: ",record)
        print(type(queryID))
        if record[0]==queryID:
            relDocIds.append(record[2])
    print(relDocIds)
    return relDocIds

    
    
# generate the term frequency of each query term.
# input : query
# output : a dictionary of all terms and their frequency
def generateQueryTermsFreqDict(query):
    queryTermFreq={}
    for qTerm in query.split():
        if qTerm in queryTermFreq:
            queryTermFreq[qTerm]+=1
        else:
            queryTermFreq[qTerm]=1
    
    return queryTermFreq

# fetch the inverted index of unigram from the file
# input : file of the index
# output : inverted index of the unigrams
def fetchInvertedIndex(invertedIndexFile):
    f = open(invertedIndexFile,'rb')
    invertedIndex=str(f.read(),'UTF-8')
    
    return invertedIndex

# fetch the number of tokens per document from the file
# generated in previous assignment
# output : number of tokens per document 
def fetchNoOfTokensPerDocDic(noOfTokensFile):
    f = open(noOfTokensFile, 'rb')
    noOfTokensPerDoc = str(f.read(),'UTF-8')
    
    return noOfTokensPerDoc

# write the result 
def writeResultToFile(docScore,qID,model,outputFileName):
    fileModel=open(outputFileName,'a')
    fileModel.write("\nQuery Q"+str(qID)+"\n\n")
    sortedDocScore=sorted(docScore,reverse=True)
    count=0
    for doc,score in sortedDocScore:
        fileModel.write(doc+" " + str(score) +"\n")
        count+=1
        if count+1 > 100:
            break
    fileModel.close()

def fetchQueryMap():
    queryMap={}
    f=open(LIST_OF_QUERY_FILE_NAME,'r')
    content =f.read()
    content='<DATA>'+content+'</DATA>'
    soup = BeautifulSoup(content, 'xml')
    docList= soup.findAll('DOC')
    for doc in docList:
        child=doc.findChild()
        qID=int(child.get_text().encode('utf-8'))
        child.decompose()
        text = doc.get_text().encode('utf-8')
        caseFoldedtext= caseFold(text)
        tokens = generateTokens(caseFoldedtext)
        refinedText=removePunctuation(tokens)
        queryMap[qID]=refinedText
    
    return queryMap
         
    f.close()
    
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
        #print(tok)
        matchNum=re.compile(r'^[\-]?[0-9]*\.?[0-9]+$')
        if not matchNum.match(tok):
            tok=re.sub(r'[^a-zA-Z0-9\--]','',tok)
        newList.append(tok)
            
    return  (' ').join(newList)   
    
# method to generate tokens from plain text
# Given: plain text
# Return: list of tokens     
def generateTokens(plainText):
    print(plainText)
    return list(filter(re.compile('[a-zA-Z0-9_]').search,str(plainText,'UTF-8').split()))

# fetch stemmed queries
def fetchStemmedQueries():
    queryMap={}
    f=open(STEMMED_QUERIES,'r')
    i=1
    for query in f.readlines():
        queryMap[i]=query 
        i+=1
    f.close()
    return queryMap


def selectRetrievalModel1(ch,invertedIndexFile,noOfTokensFile):
    
    print("Smoothed Query Likelihood retrieval model")
    model="Smoothed Query Likelihood Model"
    outputFileName=DIR_OUTPUT+"/"+TOP_100_RESULT_QueryLikelihood+"_"+str(ch)+".txt"
    if not os.path.exists(DIR_OUTPUT):
        os.makedirs(DIR_OUTPUT)
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    fileModel=open(outputFileName,'a')
    topic=" Top 100 Query Results Using "+model+" "
    hashLen=90-len(topic)
    hashLen=hashLen//2
    filler="#"*hashLen+topic+"#"*hashLen
    if len(filler)<90:
        filler+="#"
    fileModel.write("#"*90+"\n"+filler+"\n"+"#"*90+"\n\n")
    fileModel.close()
    print("Loading inverted index from text file....")
    invertedIndex = fetchInvertedIndex(invertedIndexFile)
    print("Loading number of tokens per document from text file....")
    noOfTokenPerDoc = fetchNoOfTokensPerDocDic(noOfTokensFile)
    queryMap=fetchQueryMap()
    queryList=sorted(queryMap)
    for queryID in queryList:
        print("\nQuery --> "+str(queryID)+": " +queryMap[queryID])
        print("Generating query term frequency....")
        queryTermFreq=generateQueryTermsFreqDict(queryMap[queryID])
        print("Calculating "+model+" score for documents for the current query....")
        docScore=calculateSMQL(invertedIndex,queryTermFreq,noOfTokenPerDoc)
        print(" ")
        print(docScore)
        print("Writing the top 100 results in the file....")
        writeResultToFile(docScore,queryID,model,outputFileName)

  
if __name__=='__main__':
    ch=int(input("Enter your choice 0-nothing , 1-stopping , 2-stemming: "))
    selectRetrievalModel1(ch,INVERTED_INDEX[ch],NUM_OF_TOKEN_PER_DOC[ch])