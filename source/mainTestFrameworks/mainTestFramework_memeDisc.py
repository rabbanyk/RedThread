from dataAccessor import * ;
from contracts import * ;
from labelNames import *;

from mainTestFrameworks.stringForTypeOfMatches import stringFor_nonNearDuplicateNonHighConfidenceMatch, \
                                                      stringFor_algorithmIndicatesClusterDone, \
                                                      dictMappingExpertFeedbackToString, \
                                                      dictMappingBoolToString;

import sys;

from SQLResultWrittingCode.sqlResultWritter import SQLNullValue;


def memeDisc_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter):

    print str(dictForMainTableInformation);

    perSeedQueryBudget = int(dictForMainTableInformation["queryBudget"]);
    pathToLoadData = dictForMainTableInformation["datasetFilePath"];
    requires(isinstance(perSeedQueryBudget, int));
    requires(perSeedQueryBudget > 0);
    dataObj = dataAccessor(pathToLoadData);
    labelObj = labelsAccessor(pathToLoadData);
    seedNodeObj = seedNodeAccessor(dictForMainTableInformation["seedNodeFilePath"]);

    algoInstance = algorithmToUse(dataObj, ourSQLWritter, dictForMainTableInformation["algorithmParameters"]);


    while(True):
        selectedSeedNode = seedNodeObj.getNextSeedNode();
        print "Seed node selected: " + str(selectedSeedNode);
        if(selectedSeedNode != None):
            setOfNodesAlgorithmAlreadyReturned = set({selectedSeedNode});
            seedNodeGroundTruthLabel = labelObj.getGroundTruthLabel(selectedSeedNode);


            algoInstance.setSeedNode(selectedSeedNode);

            assert(perSeedQueryBudget >= 1);

            for queryNumber in range(0, perSeedQueryBudget):
                nodeReturned = algoInstance.getNextNode();


                # If the algorithm returns None for the next seed node, it is 
                # essentially claiming that it is done forming a clustering -
                # for instance, this might occur if all the neighbors of the 
                # seed node are unrelated - then there is no positive length-2 path through the 
                # graph such that the seed node is truly related to each node on the path.
                if(nodeReturned == None):
                    ourSQLWritter.writeToTable(
                        "clusteringResults" ,\
                        {"seedNode" : selectedSeedNode,\
                         "nodeReturnedByAlgorithm" : SQLNullValue(),\
                         "categoryOfNodeEvaluation" : stringFor_algorithmIndicatesClusterDone,\
                         "returnedNodePositiveOrNegativeLabel" : SQLNullValue(),\
                         "algorithmIndicatesClusterDone" : dictMappingBoolToString[True],\
                         "labelOfSeedNode" : str(seedNodeGroundTruthLabel),\
                         "labelOfNodeReturnedByAlgorithm" : SQLNullValue(),\
                         "queryNumberForThisSeedNode": str(queryNumber)});
                    break;


                expertFeedbackToGive = None;
                groundTruthLabelForNode = labelObj.getGroundTruthLabel(nodeReturned);    
                # in our more generalized scheme, we need to check that the ground truth label of the thing returned matches the ground truth
                # label of the seed provided - if they do match, we give a positive - if they do not match, we give a  negative....
                if(len(seedNodeGroundTruthLabel.intersection(groundTruthLabelForNode)) > 0):
                    expertFeedbackToGive = positiveLabel;
                    print "positive";
                else:
                    expertFeedbackToGive = negativeLabel;
                    print "negative";
                assert(expertFeedbackToGive != None);
                assert(isProperLabel(expertFeedbackToGive));    

                ourSQLWritter.writeToTable(
                    "clusteringResults" ,\
                    {"seedNode" : selectedSeedNode,\
                     "nodeReturnedByAlgorithm" : nodeReturned,\
                     "categoryOfNodeEvaluation" : stringFor_nonNearDuplicateNonHighConfidenceMatch,\
                     "returnedNodePositiveOrNegativeLabel" : dictMappingExpertFeedbackToString[expertFeedbackToGive],\
                     "algorithmIndicatesClusterDone" : dictMappingBoolToString[False],\
                     "labelOfSeedNode" : str(seedNodeGroundTruthLabel),\
                     "labelOfNodeReturnedByAlgorithm" : str(groundTruthLabelForNode),\
                     "queryNumberForThisSeedNode": str(queryNumber)});

                algoInstance.inputFeedback(nodeReturned, expertFeedbackToGive);

            algoInstance.clearSeedNode();
        else:
            break;
    return;





