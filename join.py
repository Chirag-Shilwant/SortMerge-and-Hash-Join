import sys
import os
import math
from collections import OrderedDict 

colNo = 1
blockSize = 100


RinterFileNo = 1
SinterFileNo = 1


mapOfJoin = {}

finalOutputFile = None

fileptrofS = None
fileptrofR = None

deleteR = list()
deleteS = list()

def extractName(filePath): 
    numOfLines = sum(1 for line in open(filePath, "r"))
    base=os.path.basename(filePath)
    return base, numOfLines


def my_sort(line):
    global colNo
    line_fields = line.strip().split(' ')
    return line_fields[colNo]


def mergeSort(fileNameR, outputFile):
    ip = open(fileNameR, "r") 
    contents = ip.readlines() 
    ip.close()

    contents.sort(key=my_sort)

    op = open(outputFile, "w") 
    
    for line in contents:
        op.write(line)
    
    op.close() 


def splitFiles(pathofR, opFile, M):
    global deleteR
    global deleteS
    M *= blockSize
    intermediatefiles = 0
    count = 0
    f = open(pathofR,'r')
    nooftuples = 0
    for lines  in f:
        nooftuples = nooftuples+1
    noofsplits = math.ceil(nooftuples/M)
    f.close()

    fp = open(pathofR,'r')
    fpp = open(opFile + str(intermediatefiles)+".txt",'w+')
    if opFile == "R":
        deleteR.append(intermediatefiles)
    else:
        deleteS.append(intermediatefiles)

    for line in fp:
        count += 1
        fpp.write(line)
        if count == M:
            fpp.close()
            intermediatefiles += 1 
            if intermediatefiles != noofsplits:
                fpp = open(opFile + str(intermediatefiles) + ".txt", 'w+')
                if opFile == "R":
                    deleteR.append(intermediatefiles)
                else:
                    deleteS.append(intermediatefiles)
            count = 0

    fp.close()

    return noofsplits


def initSortJoin(pathofR, pathofS):
    global mapOfJoin
    f1 = open(pathofR, "r")
    for line in f1:
        pairKV = line.strip().split(' ')
        key, value = pairKV[1], pairKV[0]
        if key not in mapOfJoin.keys():
            mapOfJoin[key] = list()
        mapOfJoin[key].append([value, "R"])
    f1.close()

    f2 = open(pathofS, "r")
    for line in f2:
        pairKV = line.strip().split(' ')
        key, value = pairKV[0], pairKV[1]
        if key not in mapOfJoin.keys():
            mapOfJoin[key] = list()

        mapOfJoin[key].append([value, "S"])

    f2.close()
    dict1 = OrderedDict(sorted(mapOfJoin.items())) 
    mapOfJoin = dict1


def SortJoin(M, splitsofR, splitsofS):
    global mapOfJoin
    global finalOutputFile
    global RinterFileNo
    global SinterFileNo
    global fileptrofS
    global fileptrofR

    if len(mapOfJoin):
        firstKey = list(mapOfJoin.keys())[0] 
    else:
        return False

    rData = list()
    sData = list()
    rcount = 0
    scount = 0
    
    while(True):
        if len(mapOfJoin) == 0:
            break

        if firstKey != list(mapOfJoin.keys())[0]:
            break
        
        for values in mapOfJoin[firstKey]:
            if values[1] == "R":
                rcount += 1
                rData.append([values[0], firstKey])
            else:
                scount += 1
                sData.append([firstKey, values[0]])


        del mapOfJoin[firstKey]

        
        
        if RinterFileNo < splitsofR and len(rData) >= 1:
            count = 0
            while True:
                line = fileptrofR.readline() 
                if len(line) == 0:
                    fileptrofR.close()
                    RinterFileNo = RinterFileNo + 1
                    if RinterFileNo == splitsofR:
                        break
                    fileptrofR = open("R"+str(RinterFileNo)+".txt", "r")
                    break

                pairKV = line.strip().split(' ')
                key, value = pairKV[1], pairKV[0]
                if key not in mapOfJoin.keys():
                    mapOfJoin[key] = list()
                    mapOfJoin[key].append([value, "R"])
                else:
                    mapOfJoin[key].append([value, "R"])

                count = count + 1
                
                if rcount == count:
                    break


        
        
        if SinterFileNo < splitsofS and len(sData) >= 1:
            count = 0
            while True:
                line = fileptrofS.readline() 
                if len(line) == 0:
                    fileptrofS.close()
                    SinterFileNo = SinterFileNo + 1
                    if SinterFileNo == splitsofS:
                        break
                    fileptrofS = open("S"+str(SinterFileNo)+".txt", "r")
                    break

                pairKV = line.strip().split(' ')
                key, value = pairKV[0], pairKV[1]

                if key not in mapOfJoin.keys():
                    mapOfJoin[key] = list()
                    mapOfJoin[key].append([value, "S"])
                else:
                    mapOfJoin[key].append([value, "S"])
                
                count += 1

                if scount == count:
                    break

    for r in rData:
        for s in sData:
            X = str(r[0])
            Y = str(r[1])
            Z = str(s[1])
            finalOutputFile.write( X + " " + Y + " " + Z)
            finalOutputFile.write("\n")
    
    return True
 

def rollingHash(key, M):
    hashVal = 0
    for c in str(key):
        hashVal = 31*hashVal + ord(c)
    
    return hashVal % int(M-1)


def hashJoin(filePath, filePrefix, M, CountArray):
    hashTable = {}

    filePtr = open(filePath, "r")
    for line in filePtr:
        pairKV = line.strip().split(' ')
        key = " "
        value = " "
        if filePrefix == "S":
            key, value = pairKV[0], pairKV[1]
        else:
            key, value = pairKV[1], pairKV[0]

        hashValue = rollingHash(key, M)
        CountArray[hashValue] += 1

        if hashValue not in hashTable.keys():
            hashTable[hashValue] = list()
        
        if len(hashTable[hashValue]) == M-1:
            f = open(filePrefix + str(hashValue)+".txt", "a")
            for lists in hashTable[hashValue]:
                X, Y = lists[0], lists[1]   
                f.write(str(X)+" "+str(Y))
                f.write("\n")

            del hashTable[hashValue]
        
        if hashValue not in hashTable.keys():
            hashTable[hashValue] = list()

        if(filePrefix == "R"):
            hashTable[hashValue].append([value, key])
        else:
            hashTable[hashValue].append([key, value])
    
    
    for key in hashTable.keys():
        f = open(filePrefix + str(key)+".txt", "a")
        for value in hashTable[key]:
            f.write(str(value[0])+" "+str(value[1]))
            f.write("\n")      


def getNext(index, RCount, SCount, M):

    if RCount[index] == 0 or SCount[index] == 0:
        return

    global finalOutputFile
    rIsSmall = False

    if(RCount[index] <= SCount[index]):
        rIsSmall = True
    

    fpSmall = ""

    if rIsSmall:
        fpSmall = open("R"+str(index)+".txt",'r')
    else:
        fpSmall = open("S"+str(index)+".txt",'r')

    smallTupleList = list()

    for line in fpSmall:
        pairKV = line.strip().split(' ')
        key = " "
        value = " "
        if rIsSmall:
            key, value = pairKV[1], pairKV[0]
            smallTupleList.append([value, key])
        else:
            key, value = pairKV[0], pairKV[1]
            smallTupleList.append([key, value])


    fpSmall.close()
    
    fpBig = " "

    if rIsSmall:
        fpBig = open("S"+str(index)+".txt",'r')
    else:
        fpBig = open("R"+str(index)+".txt",'r')


    for line in fpBig:
        pairKV = line.strip().split(' ')

        # if rsmall then S is in big file....so pairkv has S tuple
        if rIsSmall:
            key,value = pairKV[0], pairKV[1]
        else:
            key, value = pairKV[1], pairKV[0]

        for tuples in smallTupleList:
            if rIsSmall:
                key1, value1  = tuples[1], tuples[0]
            else:
                key1, value1 = tuples[0], tuples[1]
            
            if key1 == key:
                if rIsSmall:
                    finalOutputFile.write(str(value1) + " " + str(key)+ " " + str(value))
                else:
                    finalOutputFile.write(str(value) + " " + str(key)+ " " + str(value1))

                finalOutputFile.write("\n")


def main():
    if len(sys.argv) != 5:    
        print("Wrong input format") 
        exit(0)

    pathofR, pathofS, algoType, M = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

    fileNameR, numOfLinesinR = extractName(pathofR)
    fileNameS, numOfLinesinS = extractName(pathofS)

    global finalOutputFile
    global deleteR
    global deleteS
    global blockSize

    finalOutputFile = open(str(fileNameR)+ "_" + str(fileNameS) + "_join.txt", "w")

    if algoType.lower() == "sort":
       
        if ((numOfLinesinR + numOfLinesinS) / blockSize) > M**2:
            print("Insufficient main memory")
            sys.exit(0)

        mergeSort(pathofR, "sortedR.txt")
        
        global colNo
        colNo = 0
        mergeSort(pathofS, "sortedS.txt")

        splitsofR = splitFiles("./sortedR.txt", "R", M)
        splitsofS = splitFiles("./sortedS.txt", "S", M)

        initSortJoin("./R0.txt", "./S0.txt")

        global fileptrofR
        global fileptrofS

        if splitsofS >= 2:
            fileptrofS = open("S"+str(1)+".txt",'r')

        os.remove("./sortedS.txt")
        os.remove("./sortedR.txt")

        if splitsofR >= 2:
            fileptrofR = open("R"+str(1)+".txt",'r')

        while SortJoin(M*blockSize, splitsofR, splitsofS):
            pass

        for no in deleteR:
            os.remove("R"+str(no)+".txt")
        
        for no in deleteS:
            os.remove("S"+str(no)+".txt")


    elif algoType.lower() == "hash":
        if min(numOfLinesinR/blockSize, numOfLinesinS/blockSize) > (M**2):
            print("Insufficient main memory")
            sys.exit(0)

        RCount = [0]*M
        SCount = [0]*M
        hashJoin(pathofR, "R", M, RCount)
        hashJoin(pathofS, "S", M, SCount)
        for i in range(0, M):
            getNext(i, RCount, SCount, M)
            if SCount[i] != 0: 
                os.remove("S"+str(i)+".txt")

            if RCount[i] != 0:
                os.remove("R"+str(i)+".txt")

main()