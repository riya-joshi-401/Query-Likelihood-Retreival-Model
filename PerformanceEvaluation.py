# Importing necessary libraries
import os
import shutil
import RetrievalModels

# name of relevant doc file:
RELEVANT_DOCS='CASM-Files/cacm.rel.txt'
# ranks to calculate P@K
K1,K2=5,20
# name of file to fetch doc scores per query per run
DOC_SCORES_PER_QUERY_PER_RUN = 'Retrieval/OutputFiles/Top_100_Query_Result_QueryLikelihoodModel_0.txt'
# Evaluation output directory
DIR_FOR_EVALUATION_OUTPUTS='Evaluation/OutputFiles'


def generateMAP(tableQueryMap):
    return sum([tableQueryMap[queryID][1] for queryID in tableQueryMap])/float(len(tableQueryMap)) 

# method to generate MRR for each run
def generateMRR(tableQueryMap):
    return sum([tableQueryMap[queryID][2] for queryID in tableQueryMap])/float(len(tableQueryMap))


# method for generating Precision and Recall tables
def generatePrecisionRecallTables(docScores_with_docids,relevantDocs,queryID):
    precRecallTable=[]
    docScores=docScores_with_docids[0]
    docIDss = docScores_with_docids[1]
    docIDs = [i for _, i in sorted(zip(docScores, docIDss))] # doc ids sorted in reverse order according to the scores
    #print(result_list)
    print("docscores: ")
    print(" ")
    print(docScores)
    docScores.sort()
    print(docScores)
    sortedDocScore=docScores[:100][::-1] # reverse
    numOfDocsCounter,relDocsCounter=0,0
    R=len(relevantDocs)
    relOrNonRel="N"
    sumPrecision=0
    flag=True
    RR=0
    for docId in docIDs:
        numOfDocsCounter += 1
        if docId in relevantDocs:
            relDocsCounter += 1
            relOrNonRel = "R"
        else:
            relOrNonRel = "N"
        recall = relDocsCounter / float(R)
        precision=relDocsCounter/float(numOfDocsCounter)
        if relOrNonRel=='R':
            if flag:
                RR=1/float(numOfDocsCounter)
                flag=False
            sumPrecision+=precision
        precRecallTable+=[(queryID,docId,numOfDocsCounter,relOrNonRel,"{0:.2f}".format(recall),"{0:.6f}".format(precision))]

    AP=sumPrecision/float(R)
    return (precRecallTable, AP, RR)



# method to write the Precision recall table to file
def writePrecisionRecallTablePerRunToFile(tableQueryMap,run,statistics):
    print("  ")
    print("tableQueryMap")
    print(tableQueryMap)
    print(" ")
    print("run")
    print(run)
    print(" ")
    print("statistics")
    print(statistics)
    f=open(DIR_FOR_EVALUATION_OUTPUTS+'/EvalFileFor-'+str(run)+".txt",'w')
    topic=" Effectiveness Evaluation for "+str(run)+" "
    hashLen=90-len(topic)
    hashLen=hashLen/2
    filler="#"*int(hashLen)+topic+"#"*int(hashLen)
    if len(filler)<90:
        filler+="#"
    f.write("#"*90+"\n"+filler+"\n"+"#"*90+"\n\n")
    f.write('Evaluation Measures:\nMAP: '+str("{0:.2f}".format(statistics[0]))+'\nMRR: '+str("{0:.2f}".format(statistics[1]))+'\n')
    f.write('-'*80)
       
    for queryID in tableQueryMap:
        f.write('\n\nQueryID: '+str(queryID))
        f.write('\nP@K = '+str(K1)+': '+str(tableQueryMap[queryID][0][K1][5]))
        f.write('\nP@K = '+str(K2)+': '+str(tableQueryMap[queryID][0][K2][5]))
        f.write('\n\n\nPrecision & Recall Tables\n\n')
        f.write('QueryID'+' '*6+'DocId'+' '*10+'Rank'+' '*6+'R/N'+' '*6+'Recall'+' '*6+'Precision'+' '*6+'\n')
        f.write('-'*80+'\n')
        t=9         
        for qID,docId,numOfDocsCounter,relOrNonRel,recall,precision in tableQueryMap[queryID][0]:
            if numOfDocsCounter>9:
                t=8
            if numOfDocsCounter>99:
                t=7
            f.write(str(qID)+' '*9+docId+' '*9+str(numOfDocsCounter)+' '*t+\
                    relOrNonRel+' '*9+str(recall)+' '*9+str(precision)+'\n')

    f.close()


def fetchDocScoresPerQueryPerRun():
    f=open(DOC_SCORES_PER_QUERY_PER_RUN)
    docScoresPerQueryPerRun = f.read()
    
    return docScoresPerQueryPerRun

def evaluate(docScoresPerQuery):
    tableQueryMap={}
    for queryID in docScoresPerQuery:
        relevantDocs=RetrievalModels.fetchRelevantDocIds(queryID[1:])
        print(" ")
        print("relevantDocs: ",relevantDocs)
        if len(relevantDocs)==0:
            continue
        tableQueryMap[queryID]=generatePrecisionRecallTables(docScoresPerQuery[queryID],relevantDocs,queryID)
    return tableQueryMap

def fetchScoresFromDocScore():
    docScorePerQuery={}
    f=open(DOC_SCORES_PER_QUERY_PER_RUN, 'r')
    data=f.read()
    index=data.rfind('#')
    data=data[index+1:]
    listOfData=data.split('Query ')
    listOfData=listOfData[1:]
    newList=[]
    for text in listOfData:
        data="\n".join([data for data in text.splitlines() if data!=''])
        newList+=[data]
    for data in newList:
        splitData=data.splitlines()
        x=splitData[0]
        splitData=splitData[1:]
        docScore=[]
        reldocids_dcpq=[]
        for lines in splitData:
            record=lines.split()
            docScore.append(int(record[1]))
            reldocids_dcpq.append(record[0])
        docScorePerQuery[x]=[docScore,reldocids_dcpq]
            
    f.close()
    return docScorePerQuery

def main(docScorePerQuery):
    performanceMap={}
    print("Performance Evaluation!!!")
    if os.path.exists(DIR_FOR_EVALUATION_OUTPUTS):
        shutil.rmtree(DIR_FOR_EVALUATION_OUTPUTS)
    if not os.path.exists(DIR_FOR_EVALUATION_OUTPUTS):
        os.makedirs(DIR_FOR_EVALUATION_OUTPUTS)
    for run in range(100):
        print("Performance Evaluation for : "+str(run))
        tableQueryMap=evaluate(docScorePerQuery)
        MAP=generateMAP(tableQueryMap)
        MRR=generateMRR(tableQueryMap)
        statistics=(MAP,MRR)
        writePrecisionRecallTablePerRunToFile(tableQueryMap,run,statistics)
        performanceMap[run]=(tableQueryMap,statistics)
    return performanceMap

if __name__=='__main__':

    docScorePerQuery = fetchScoresFromDocScore()
    print(docScorePerQuery)
    performanceMap=main(docScorePerQuery)
    print(performanceMap)

        