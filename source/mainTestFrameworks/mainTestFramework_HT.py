from dataAccessor import * ;
from NodeComparitors.NearDuplicateFilter import *;
from NodeComparitors.HighConfidenceMatch import *;
from NodeComparitors.DummyHighConfidenceMatcher import *;
from contracts import * ;
from labelNames import *;

import sys;
    

from SQLResultWrittingCode.sqlResultWritter import SQLNullValue;

from mainTestFrameworks.stringForTypeOfMatches import stringFor_nonNearDuplicateNonHighConfidenceMatch, \
                                                      stringFor_highConfidenceMatch, \
                                                      stringFor_nearDuplicate, \
                                                      stringFor_algorithmIndicatesClusterDone, \
                                                      dictMappingExpertFeedbackToString, \
                                                      dictMappingBoolToString;



def HT_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter, typeOfHighConfidenceMatcher=None):


    perSeedQueryBudget = int(dictForMainTableInformation["queryBudget"]);
    pathToLoadData = dictForMainTableInformation["datasetFilePath"];
    requires(isinstance(perSeedQueryBudget, int));
    requires(perSeedQueryBudget > 0);
    requires( typeOfHighConfidenceMatcher in \
        {"RealHCMatcher", "DummyHCMatcher"}); # this 
        # requires, coupled with the default value of typeOfHighConfidenceMatcher, forces the user to set it each time.

    dataObj = dataAccessor(pathToLoadData);
    labelObj = labelsAccessor(pathToLoadData);
    seedNodeObj = seedNodeAccessor(dictForMainTableInformation["seedNodeFilePath"]);

    # Below, HC stands for High Confidence
    HCMatcher = None;
    NDFilter = None;
    # the below conditional can be replaced with something simplier, but it would require looking at the
    #     substrings inside typeOfHighConfidenceMatcher, which we might change later.
    if(typeOfHighConfidenceMatcher in {"RealHCMatcher", "DummyHCMatcher"}):
        NDFilter = NearDuplicateFilter(dataObj);
        if(typeOfHighConfidenceMatcher == "RealHCMatcher"):
            HCMatcher = HighConfidenceMatch(pathToLoadData); 
        else:
            assert(typeOfHighConfidenceMatcher == "DummyHCMatcher");
            HCMatcher = DummyHighConfidenceMatch("fakeValue");
    else:
        raise Exception(); # unsupported input # this should not happen by the requires.
    assert(HCMatcher != None);
    assert(NDFilter != None);
    # below ND stands for Near Duplicate(s)


 
    algoInstance = algorithmToUse(dataObj, ourSQLWritter, dictForMainTableInformation["algorithmParameters"]);


    while(True):
        NDFilter.clearCluster();
        HCMatcher.clearCluster();

        #V~V~V~V~V~V~V~V~V~VV~V~V~V~V~V~V~V~~V~V~VV~V~~V~V~V~V~V~V~V~V~V~VV
        # getting the seed node and recording it in appropraite places....
        #------------------------------------------------------------------
        selectedSeedNode = seedNodeObj.getNextSeedNode();
        print "Seed node selected: " + str(selectedSeedNode);
        if(selectedSeedNode == None):
            return;
        assert(selectedSeedNode != None);
        seedNodeGroundTruthLabel = labelObj.getGroundTruthLabel(selectedSeedNode);
        #^_^_^_^_^_^_^_^_^^_^^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^
        
        
        algoInstance.setSeedNode(selectedSeedNode);
        NDFilter.addToCluster(selectedSeedNode);
        HCMatcher.addToCluster(selectedSeedNode);

        
        assert(perSeedQueryBudget >= 1);
        
        nodeReturned = None;
        
        # NOTE THAT BELOW, WE ASSUME THAT remainingQueries WILL BE TRAVERSE
        # IN a specific order - starting at remainingQueries[0] and incrementing
        # the index till the end....
        for thisQueryIndex in range(0, perSeedQueryBudget):
            repeatForQueryInstance = True;
            while(repeatForQueryInstance):
                #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~VV~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # some loop invariants
                #--------------------------------------------------------------------------------
                assert(nodeReturned != None or thisQueryIndex == 0);
                #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

                repeatForQueryInstance = False;

                #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~VV~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # getting node from algorithm
                #--------------------------------------------------------------------------------
                nodeReturned = algoInstance.getNextNode();
                # If the algorithm returns None for the next seed node, it is 
                # essentially claiming that it is done forming a clustering -
                # for instance, this might occur if all the neighbors of the 
                # seed node are unrelated - then there is no positive length path through the 
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
                         "queryNumberForThisSeedNode": str(thisQueryIndex)});
                    break; # NOTE: right after the while-statement this code is in, we have
                        # another conditional to break out of the nested-loop.
                assert(nodeReturned != None);
                #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


                #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~VV~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # getting expert feedback for node.
                #--------------------------------------------------------------------------------
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



                #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


                # We add members to the near duplicate cluster when:
                #     we add a new duplicate...
                #     we add a high-confidence node...
                #     we add a positive node....
                # these are exactly the set of nodes we expand from... so this should be the same for 
                # our algorithm and the high-confidence filter as well.....

                #V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # handling near duplicates
                #--------------------------------------------------------------------------------------------
                isNearDuplicate = NDFilter.testForNearDuplicate( nodeReturned); 
                if(isNearDuplicate): # if wanted expert-informed: # if(expertFeedbackToGive == positiveLabel and isNearDuplicate)
                    NDFilter.addToCluster(nodeReturned); # pessimistic placement: small mutations in a long chain
                        # may result in interesting difference between end-points
                    HCMatcher.addToCluster(nodeReturned);
                    # NOTE THE HARD-CODING OF positiveLabel BELOW, DESPITE THE GROUND-TRUTH LABEL OF 
                    # nodeReturned AND expertFeedbackToGive
                    # Note below how we hard code in positiveLabel as the expert feedback - it is assumed positive.
                    algoInstance.inputFeedback(nodeReturned, positiveLabel, learnFromExample=False);
                    repeatForQueryInstance = True;


                    #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~VV~V~~V~~V~V~V~V~V~V~V~V~V~V~V~VV~~V~V~V~V~
                    # writting to the file listing compressive information on each node returned by the algorithm
                    #---------------------------------------------------------------------------------------------
                    ourSQLWritter.writeToTable(
                        "clusteringResults" ,\
                        {"seedNode" : selectedSeedNode,\
                         "nodeReturnedByAlgorithm" : nodeReturned,\
                         "categoryOfNodeEvaluation" : stringFor_nearDuplicate,\
                         "returnedNodePositiveOrNegativeLabel" : dictMappingExpertFeedbackToString[expertFeedbackToGive],\
                         "algorithmIndicatesClusterDone" : dictMappingBoolToString[False],\
                         "labelOfSeedNode" : str(seedNodeGroundTruthLabel),\
                         "labelOfNodeReturnedByAlgorithm" : str(groundTruthLabelForNode),\
                         "queryNumberForThisSeedNode": str(thisQueryIndex)});
                    #^_^_^_^_^_^_^_^_^_^_^__^^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


                    continue;
                # if wanted expert-informed: #  assert(expertFeedbackToGive == negativeLabel or not isNearDuplicate);
                assert(not isNearDuplicate);
                assert(not repeatForQueryInstance);
                #^_^_^_^_^_^_^_^^_^_^_^_^_^_^_^_^_^__^^_^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^__^


                #V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # handling high confidence matches.
                #--------------------------------------------------------------------------------------------
                highConfidenceMatch = HCMatcher.testForNearDuplicate( nodeReturned);
                if(highConfidenceMatch):
                    # the same thing happens below as happens for if(isNearDuplicate):, except we put the node into 
                    # a different set.
                    NDFilter.addToCluster(nodeReturned); # pessimistic placement: small mutations in a long chain
                        # may result in interesting difference between end-points
                    HCMatcher.addToCluster(nodeReturned);
                    # NOTE THE HARD-CODING OF positiveLabel BELOW, DESPITE THE GROUND-TRUTH LABEL OF 
                    # nodeReturned AND expertFeedbackToGive
                    # Note below how we hard code in positiveLabel as the expert feedback - it is assumed positive.
                    algoInstance.inputFeedback(nodeReturned, positiveLabel, learnFromExample=False);
                    repeatForQueryInstance = True;


                    #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~VV~V~~V~~V~V~V~V~V~V~V~V~V~V~V~VV~~V~V~V~V~
                    # writting to the file listing compressive information on each node returned by the algorithm
                    #---------------------------------------------------------------------------------------------
                    ourSQLWritter.writeToTable(
                        "clusteringResults" ,\
                        {"seedNode" : selectedSeedNode,\
                         "nodeReturnedByAlgorithm" : nodeReturned,\
                         "categoryOfNodeEvaluation" : stringFor_highConfidenceMatch,\
                         "returnedNodePositiveOrNegativeLabel" : dictMappingExpertFeedbackToString[expertFeedbackToGive],\
                         "algorithmIndicatesClusterDone" : dictMappingBoolToString[False],\
                         "labelOfSeedNode" : str(seedNodeGroundTruthLabel),\
                         "labelOfNodeReturnedByAlgorithm" : str(groundTruthLabelForNode),\
                         "queryNumberForThisSeedNode": str(thisQueryIndex)});
                    #^_^_^_^_^_^_^_^_^_^_^__^^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

                    continue;
                assert(not repeatForQueryInstance);
                assert(not highConfidenceMatch and not isNearDuplicate);
                #^_^_^_^_^_^_^_^^_^_^_^_^_^_^_^_^_^__^^_^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^__^




                #V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V
                # handling nodes that are neither high-confidence matches nor near duplicates.
                #--------------------------------------------------------------------------------------------


                #V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~VV~V~~V~~V~V~V~V~V~V~V~V~V~V~V~VV~~V~V~V~V~
                # writting to the file listing compressive information on each node returned by the algorithm
                #---------------------------------------------------------------------------------------------
                ourSQLWritter.writeToTable(
                    "clusteringResults" ,\
                    {"seedNode" : selectedSeedNode,\
                     "nodeReturnedByAlgorithm" : nodeReturned,\
                     "categoryOfNodeEvaluation" : stringFor_nonNearDuplicateNonHighConfidenceMatch,\
                     "returnedNodePositiveOrNegativeLabel" : dictMappingExpertFeedbackToString[expertFeedbackToGive],\
                     "algorithmIndicatesClusterDone" : dictMappingBoolToString[False],\
                     "labelOfSeedNode" : str(seedNodeGroundTruthLabel),\
                     "labelOfNodeReturnedByAlgorithm" : str(groundTruthLabelForNode),\
                     "queryNumberForThisSeedNode": str(thisQueryIndex)});
                #^_^_^_^_^_^_^_^_^_^_^__^^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


                algoInstance.inputFeedback(nodeReturned, expertFeedbackToGive, learnFromExample=True);
                if(expertFeedbackToGive == positiveLabel):
                    NDFilter.addToCluster(nodeReturned);
                    HCMatcher.addToCluster(nodeReturned); 
                    # adding the node to the algorithm's internal cluster is handled by calling algoInstance.inputFeedback
                    # with the actual value of the expert feedback.

            if(nodeReturned == None): # see nodeReturned = algoInstance.getNextNode(); in the loop above. - we need to break out
                # of a nested loop
                break;

        assert(nodeReturned == None or thisQueryIndex == perSeedQueryBudget - 1);
        algoInstance.clearSeedNode();

    return;


