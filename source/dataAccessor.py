from contracts import *;
import csv;
import sys;
import numpy;
from scipy.sparse import csr_matrix;

from scipy import uint64;
from getStringTimeNow import *;


class dataAccessor:
 
     def getSizeOfAdjacencyMatrix(self, pathToData):

        nameOfWeightedAdjacencyListFile = "weightedAdjacencyList.csv";
        # below, WAL in the variable names stands for Weighted Adjacency List...
        fileHandleForWAL = open(pathToData + nameOfWeightedAdjacencyListFile, 'r');

        # for the below, see: 
        #     https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
        csv.field_size_limit(sys.maxsize)
        csvReaderForWAL = csv.reader(fileHandleForWAL, quoting=csv.QUOTE_NONE);
        # for now we assume there is no header and that the format is:
        # node1, node2, weightOfEdge
        sys.stdout.flush();
        print "START: getSizeOfAdjacencyMatrix. " + getStringTimeNow();
        # sizeAdjacencyList
        sys.stdout.flush();
        counter = 0;
        for thisRow in csvReaderForWAL:
            if(len(thisRow) > 0 and len(thisRow[0]) > 0 and thisRow[0] != "\n"): # the final line in the weighted adjacency list might be a newline....
                assert(counter < counter + 1); # overflow check....
                counter = counter + 1;
        sys.stdout.flush();
        print "END: getSizeOfAdjacencyMatrix. " + getStringTimeNow();
        sys.stdout.flush();
        fileHandleForWAL.close();

        return counter;


     def __init__(self, pathToData, nameOfNodeAttributeFile=None, nameOfWeightedAdjacencyListFile=None): # matrixToUse not used here..
        sys.stdout.flush();
        print "START";
        sys.stdout.flush();
        requires(isinstance(pathToData, str));
        requires(len(pathToData) > 0);
        requires(pathToData[0] == '/'); # we require an absolute path
        requires(pathToData[-1] == '/'); # we require that the path define a dictory - this is a 
            # weak check of that....

        sizeAdjacencyList = self.getSizeOfAdjacencyMatrix(pathToData);
        print "\nsizeAdjacencyList     " + str(sizeAdjacencyList)

        if(nameOfWeightedAdjacencyListFile == None):
            nameOfWeightedAdjacencyListFile = "weightedAdjacencyList.csv";
        if(nameOfNodeAttributeFile == None):
            nameOfNodeAttributeFile = "nodeAttributeFile.csv";
        # below, WAL in the variable names stands for Weighted Adjacency List...
        fileHandleForWAL = open(pathToData + nameOfWeightedAdjacencyListFile, 'r');
        # below, NA in the variable names stands for Node Attributes...
        fileHandleForNA = open(pathToData + nameOfNodeAttributeFile, 'r');

        self.indexToEntityNameDict = {};
        self.entityNameToIndexDict = {};
        self.entityToTypeDict = {};
        self.entityTypes = set();
        sizeOurArrays = 2 * sizeAdjacencyList;
        leftColumnArray = numpy.zeros(sizeOurArrays, dtype=uint64);
        rightColumnArray = numpy.zeros(sizeOurArrays, dtype=uint64);


        # for the below, see: 
        #     https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
        csv.field_size_limit(sys.maxsize)
        csvReaderForNA = csv.reader(fileHandleForNA, quoting=csv.QUOTE_NONE);
        currentIndex = 0;
        sys.stdout.flush();
        print "START:reading node attribute file. " + getStringTimeNow();
        sys.stdout.flush();
        for thisRow in csvReaderForNA:
            #oldIndexing# assert(currentIndex >= 1);
            assert(currentIndex + 1 > currentIndex);
            assert(currentIndex >= 0);
            assert(len(thisRow) == 2);

            thisEntityName = thisRow[0];
            thisEntityType = thisRow[1];

            self.entityToTypeDict[thisEntityName] = thisEntityType;
            self.entityNameToIndexDict[thisEntityName] = currentIndex;
            self.indexToEntityNameDict[currentIndex] = thisEntityName;
            assert(self.indexToEntityNameDict[self.entityNameToIndexDict[thisEntityName]] == thisEntityName);
            assert(self.entityNameToIndexDict[self.indexToEntityNameDict[currentIndex]] == currentIndex);
            # note that the minimal index we actually have data for is 
            #     0...
            currentIndex = currentIndex + 1;
        fileHandleForNA.close();
        self.entityTypes = set(self.entityToTypeDict.values());
        sys.stdout.flush();
        print "END:reading node attribute file. " + getStringTimeNow();
        sys.stdout.flush();
 

        # for the below, see: 
        #     https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
        csv.field_size_limit(sys.maxsize)
        csvReaderForWAL = csv.reader(fileHandleForWAL, quoting=csv.QUOTE_NONE);
        # for now we assume there is no header and that the format is:
        # node1, node2, weightOfEdge
        sys.stdout.flush();
        print "START: weighted adjacency list. " + getStringTimeNow();
        # sizeAdjacencyList
        sys.stdout.flush();
        counter = 0;
        numberOfExceptions = 0;
        for thisRow in csvReaderForWAL:
            assert(counter >= 0);
            assert(counter < sizeOurArrays);
            if(counter % 20000 == 0):
                sys.stdout.flush();
                print str(counter) + "," + getStringTimeNow();
                sys.stdout.flush();

            if(True): # try:
                indexA = self.entityNameToIndexDict[thisRow[0]];
                indexB = self.entityNameToIndexDict[thisRow[1]];

              
                # below, we implement an undirected graph - we could save memory and 
                # time by 
                leftColumnArray[counter] = indexA;
                rightColumnArray[counter] = indexB;
                assert(indexA != indexB);
                counter = counter + 1;
                leftColumnArray[counter] = indexB;
                rightColumnArray[counter] = indexA;
                counter = counter + 1;
                # the fact that we have strict inequality below should come from the fact that
                #     our graph does not have self-loops....
            
            else: # except Exception as inst: 
                # note that when an  exception happens, the end portion of the arrays get
                # filled with self-loops from member zero to itself....
                numberOfExceptions = numberOfExceptions + 1;
                sys.stdout.flush();
                print "EXCEPTION CAUGHT"
                sys.stdout.flush(); 
            

        print "counter: " + str(counter)
        print "numberOfExceptions: " + str(numberOfExceptions);
        print "sizeOurArrays: " + str(sizeOurArrays);
        # why two-times the number of excepctions below? Because each time an
        #    exception occurs, we miss iterating the counter by two....
        assert(counter + 2 * numberOfExceptions == sizeOurArrays);
        # assert(sum(leftColumnArray[counter:sizeOurArrays]) < 0.5);
        assert(sum(leftColumnArray[counter:sizeOurArrays]) == 0.0);
        assert(sum(rightColumnArray[counter:sizeOurArrays]) == 0.0);

        sys.stdout.flush();
        print "END: weighted adjacency list. " + getStringTimeNow();
        sys.stdout.flush();
        fileHandleForWAL.close();

        
        dumbySparseValues = numpy.ones(counter, dtype=uint64); # we could put scipy bools here,
            # but to make summing rows in the matrix easier, we put an integer....

        self.rawData = csr_matrix(( dumbySparseValues , (leftColumnArray[0:counter], rightColumnArray[0:counter])) , dtype=uint64);
        tempShapeForCheckPurposes = self.rawData.get_shape();
        assert( tempShapeForCheckPurposes[0] == tempShapeForCheckPurposes[1] );
        sys.stdout.flush();
        print "END";
        sys.stdout.flush();
        return;


     def getEntityTypeOfNode(self, thisNode):
         return self.entityToTypeDict[thisNode];


     def getNeighbors(self, nodeToGetNeighborsFor):
         return [self.indexToEntityNameDict[thisNeighborID] for thisNeighborID in self.rawData[self.entityNameToIndexDict[nodeToGetNeighborsFor]].nonzero()[1]];

     
     def getNumberOfNodes():
         return len(self.entityNameToIndexDict);
         # Use sypy, something, something...

     def getDegreesNetworkxStyle(self, listOfNodesToFindDegreesFor):
         assert(isinstance(listOfNodesToFindDegreesFor, list));
         degreeDict = {};
         for thisNode in listOfNodesToFindDegreesFor:
             degreeDict[thisNode] = self.rawData[self.entityNameToIndexDict[thisNode]].nnz;
             assert(degreeDict[thisNode] >= 0);
         return degreeDict;

     def getDegreeOfSingleNode(self, thisNode):
         return self.rawData[self.entityNameToIndexDict[thisNode]].nnz; # count_nonzero();


class labelsAccessor:

    def __init__(self, pathToData):
        requires(isinstance(pathToData, str));
        requires(len(pathToData) > 0);
        requires(pathToData[0] == '/'); # we require an absolute path
        requires(pathToData[-1] == '/'); # we require that the path define a dictory - this is a 
            # weak check of that....

        nameOfGroundTruthLabelsFile = "groundTruthNodeLabels.csv";
        # below, GTL in the variable names stands for Ground Truth Labels...
        fileHandleForGTL = open(pathToData + nameOfGroundTruthLabelsFile, 'r');

        # for the below, see: 
        #     https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
        csv.field_size_limit(sys.maxsize)
        csvReaderForGTL = csv.reader(fileHandleForGTL, quoting=csv.QUOTE_NONE);
        self.labelDictionary = {};
        for thisRow in csvReaderForGTL:
            assert(len(thisRow) == 2);
            #    We remove the below assert becuase we are actually in a multiclass setting - 
            #    each cluster we want to find actually, if we are lucky, are all and only of one
            #    class. The feedback we give our classifier, however, is a binary label informed
            #    by the expert that indicates whether or not the node provided by the algorithm has
            #    the same ground-truth label as the seednode provided.
            # assert(isProperLabel(int(thisRow[1])));


            thisKey = thisRow[0];
            thisValue = set({thisRow[1]}); # NOTE: we have to put the inner curly
                # bracket around the string so that thisValue does not become a set of characters - as checked
                # by the assert below (assuming that the string has more than one character - it in most cases
                # we will be dealing with they do - it sees that the value is one string as opposed to multiple characters...


            assert(len(thisValue) == 1);
            if(thisKey in self.labelDictionary):
                self.labelDictionary[thisKey] = self.labelDictionary[thisKey].union(thisValue);
            else:
                self.labelDictionary[thisKey] = thisValue;
            assert(len(self.labelDictionary[thisKey]) >= 1);
        fileHandleForGTL.close();
        return;

    def getGroundTruthLabel(self, thisNode):
        # the below line checks that thisNode is in the keyset of 
        # self.labelDictionary
        if(thisNode in self.labelDictionary):
            return self.labelDictionary[thisNode];
        else:
            return set(); # Given the likelyhood of error or messy data here, I question whether we
                 # want to return an empty set or some clearly label-is-missing output, like None, as 
                 # we had done previously.... #None;



class seedNodeAccessor:
 
    def __init__(self, pathToData):
        requires(isinstance(pathToData, str));
        requires(len(pathToData) > 0);
        requires(pathToData[0] == '/'); # we require an absolute path
        requires(pathToData[-1] != '/'); # we require that the path define a file - this is a 
            # weak check of that
       
        # below, SN in the variable names stands for Seed Nodes...
        fileHandleForSN = open(pathToData, 'r');

        # for the below, see: 
        #     https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
        csv.field_size_limit(sys.maxsize)
        csvReaderForSN = csv.reader(fileHandleForSN, quoting=csv.QUOTE_NONE);
        self.seedNodes = [];
        for thisRow in csvReaderForSN:
            assert(len(thisRow) == 1);
            self.seedNodes.append(str(thisRow[0]));
        fileHandleForSN.close();
        return;

    def getNextSeedNode(self):
        if(len(self.seedNodes) == 0):
            return None;
        seedNodeToReturn = self.seedNodes.pop();
        ensures(isinstance(seedNodeToReturn, str));
        return seedNodeToReturn;


