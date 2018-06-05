from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmBaseClass import *;
from numpy.random import choice as randomChoice;
from numpy.random import binomial as numpyRandomBinomial;
import sys;


from Algorithms.components.implementedExpansionManagers import ExpansionManagerAlphaACG;
from Algorithms.components.scorers import RedThreadWithoutEvidenceWeightsScorer;




class AlgorithmRedThreadWithoutEvidenceWeights(AlgorithmBaseClass):


    def parseInputParameters(self, inputString):
        dictOfValuesFromString = self.helper_parseInputParameters_convertStringToDict(inputString);

        # checking values
        # whole dictionary is in the right form
        assert(set(dictOfValuesFromString.keys()).issuperset(\
            {"queueSize", "clearWeightsWithNewSeedNode", "learningRate", \
             "randomizedNodeSelection", "updateOnPositive", "errorToleranceForFloatingPointComparison", \
             "degreeCutoffForNeighborsToExpand"}) );
        assert( (set(dictOfValuesFromString.keys()).difference(\
            {"queueSize", "clearWeightsWithNewSeedNode", "learningRate", \
             "randomizedNodeSelection", "updateOnPositive", "errorToleranceForFloatingPointComparison", \
             "degreeCutoffForNeighborsToExpand"})).issubset({"symmetricUpdateOnPositive"}));
        assert(all([isinstance(x, float) for x in dictOfValuesFromString.values()]));
        # queueSize is proper
        assert( dictOfValuesFromString["queueSize"] % 1 == 0.0 ); # this is an assert and not a requires since it come from something we derive after 
            # manipulating the input... This, by the way, basically checks that the queue size is an integer.
        assert( dictOfValuesFromString["queueSize"] > 0 );
        # clearWeightsWithNewSeedNode is proper
        assert( dictOfValuesFromString["clearWeightsWithNewSeedNode"] in {1.0, 0.0} ); # binary values for boolean variable
        # learningRate is proper
        assert( dictOfValuesFromString["learningRate"] > 0.0);
        assert( dictOfValuesFromString["learningRate"] < 1.0);
        # randomizedNodeSelection is proper
        assert( dictOfValuesFromString["randomizedNodeSelection"] in {1.0, 0.0} ); # binary values for boolean variable
        # updateOnPositive is proper
        assert( dictOfValuesFromString["updateOnPositive"] in {1.0, 0.0} ); # binary values for boolean variable
        # errorToleranceForFloatingPointComparison is proper
        assert( dictOfValuesFromString["errorToleranceForFloatingPointComparison"] >= 0.0); # Note that we ALLOW equivalence to zero...
        assert( dictOfValuesFromString["errorToleranceForFloatingPointComparison"] < 1.0);
        # degreeCutoffForNeighborsToExpand is proper
        assert( dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] % 1 == 0.0); # must be interger
        assert( (dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] > 0) or \
            (dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] == -1.0) ); # we use negative one ot indicate an infinite degree
            # cutoff - which is equivalent to no degree cutoff at all...


        # Note that the random walks do not actually use the queue-size - but we require that it be passed in
        #     for the sake of grouping these results with the proper set of experiments.
        if(dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] == -1.0):
            self.degreeCutoffForNeighborsToExpand = float("inf");
        else:
            self.degreeCutoffForNeighborsToExpand = int(dictOfValuesFromString["degreeCutoffForNeighborsToExpand"]);
        # setting values
        self.queueSize = int(dictOfValuesFromString["queueSize"]);
        self.clearWeightsWithNewSeedNode = (dictOfValuesFromString["clearWeightsWithNewSeedNode"] == 1.0);
        self.learningRate = dictOfValuesFromString["learningRate"];
        self.randomizedNodeSelection = (dictOfValuesFromString["randomizedNodeSelection"] == 1.0);
        self.updateOnPositive = (dictOfValuesFromString["updateOnPositive"] == 1.0);
        self.errorToleranceForFloatingPointComparison = dictOfValuesFromString["errorToleranceForFloatingPointComparison"];
        if("symmetricUpdateOnPositive" in dictOfValuesFromString):
            if(dictOfValuesFromString["symmetricUpdateOnPositive"] != 1.0):
                raise Exception(); # if the symmetric keyword is even mentioned in the 
                    # set of input arguments, we requires that it be recorded as 1.0 (boolean for True). We require
                    # this primarly so that runs of RedThreadWithoutEvidenceWeights that were done prior to the introduction of this
                    # feature can be more easily be matched and and found with any reruns of RedThreadWithoutEvidenceWeights under the same
                    # parameters that are run later (later than now when this feature was introduced).
            self.styleUpdateOnPositive = "symmetric";
        else:
            self.styleUpdateOnPositive = "original";

        # checking that values read are reasonable.
        assert(isinstance(self.queueSize, int));
        assert( self.queueSize > 0 );
        # clearWeightsWithNewSeedNode is proper
        assert( isinstance(self.clearWeightsWithNewSeedNode, bool) );
        # learningRate is proper
        assert( self.learningRate > 0.0);
        assert( self.learningRate < 1.0);
        # randomizedNodeSelection is proper
        assert( isinstance(self.randomizedNodeSelection, bool) );
        # updateOnPositive is proper
        assert( isinstance(self.updateOnPositive, bool) );
        # errorToleranceForFloatingPointComparison is proper
        assert( self.errorToleranceForFloatingPointComparison >= 0.0); # Note that we ALLOW equivalence to zero...
        assert( self.errorToleranceForFloatingPointComparison < 1.0);  
        # capDegreeOfNodesToExpand is proper
        assert( isinstance(self.degreeCutoffForNeighborsToExpand, int) or (self.degreeCutoffForNeighborsToExpand == float("inf")));
        assert( self.degreeCutoffForNeighborsToExpand > 0);
        # styleUpdateOnPositive is proper
        assert(self.styleUpdateOnPositive in {"original", "symmetric"});

        return;


    def recordState_helper(self):
        weightDict = self.ourScorer.getWeightDict();
        assert(isinstance(weightDict, dict));
        setOfModalitiesLastUpdate = self.ourScorer.getModalitiesLastUpdated();
        assert(isinstance(setOfModalitiesLastUpdate, set));
        currentErrorTolerance = self.ourScorer.getCurrentErrorToleranceForFloatingPointComparison();
        assert(isinstance(currentErrorTolerance, float));

        listOfDictsToReturn = [];
        
        stringForCategoryOfParameter = "modalityWeighting";
        stringForListingModalitiesUpdated = "modalityUpdated_";
        counterOfNumberOfModalitiesUpdated = 0; # we use this to ensure that the 
            # (UUID, categoryOfParameter, specificParameterName)'s in a row stay unique in the table-
            # the issues created by appending in this counter can easily be gotten around by using
            # regular expression matching in PostgreSQL.
        for thisUpdatedModality in setOfModalitiesLastUpdate:
            assert(isinstance(thisUpdatedModality, str));
            assert(counterOfNumberOfModalitiesUpdated + 1 > counterOfNumberOfModalitiesUpdated); # weak 
                # check for overflow.
            counterOfNumberOfModalitiesUpdated = counterOfNumberOfModalitiesUpdated + 1;
            listOfDictsToReturn.append(\
                {"categoryOfParameter" : stringForCategoryOfParameter ,\
                 "specificParameterName" : stringForListingModalitiesUpdated + \
                                           str(counterOfNumberOfModalitiesUpdated),\
                 "parameterValue" : thisUpdatedModality});
        listOfDictsToReturn.append(\
            {"categoryOfParameter" : stringForCategoryOfParameter ,\
             "specificParameterName" : "errorToleranceForFloatingPointComparison",\
             "parameterValue" : str(currentErrorTolerance)});
        for thisModality in weightDict:
            assert(isinstance(thisModality, str));
            listOfDictsToReturn.append(\
                {"categoryOfParameter" : stringForCategoryOfParameter ,\
                 "specificParameterName" : thisModality,\
                 "parameterValue" : str(weightDict[thisModality])});

        assert(len(listOfDictsToReturn) == len(weightDict) + len(setOfModalitiesLastUpdate) + 1); # the 
            # plus one is to account for the entry that was used to store the errorToleranceForFloatingPointComparison
        return listOfDictsToReturn;


    #V~VVV~V~V~~VV~~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V
    # basic functions to set up the algorithm datastructure
    #---------------------------------------------------------------------
    def __init__(self, dataObj, writterObj, inputString):
        sys.stdout.flush();
        print("START:__init__");
        sys.stdout.flush();
        super(AlgorithmRedThreadWithoutEvidenceWeights, self).__init__(dataObj, writterObj, inputString);
        self.ourGraph = self.refToDataObj;
        self.perNodeAttributeDictionary = self.ourGraph.entityToTypeDict;
        self.entityTypes = set(self.perNodeAttributeDictionary.values());
        self.nodesFromOldClusters = set();
        self.nodesInCurrentCluster = set();
        self.targetEntityType = None;
        self.ourExpansionManager = None;
        self.ourScorer = None;
        self.seedNode = None;
        self.nodesWeRecievedExpertInputFor = set(); # we never have an expert annotate the same node twice. We preserve
            # the content of this set across the various seed nodes that might be provided. Futher, this enforces 


    def setSeedNode(self, providedSeedNode):
        # requires(providedSeedNode not in self.nodesFromOldClusters);
        # assert(self.targetEntityType == None or (self.targetEntityType in self.entityTypes));
        # assert(providedSeedNode in self.perNodeAttributeDictionary);
        # requires(self.targetEntityType == None or \
        #    (self.perNodeAttributeDictionary[providedSeedNode] == self.targetEntityType));
        super(AlgorithmRedThreadWithoutEvidenceWeights, self).setSeedNode(providedSeedNode);
        self.seedNode = providedSeedNode;
        if(self.targetEntityType == None):
            self.targetEntityType = self.perNodeAttributeDictionary[providedSeedNode];           

        # assert(self.nodesInCurrentCluster == set()); # this should have either been done by the __init__
            # function or the clearSeedNode function below.
        self.nodesInCurrentCluster = {providedSeedNode};
        # for the below to actually work, we have to ensure that None is not 
        #     an entity type...
        # ensures(self.targetEntityType != None and (self.targetEntityType in self.entityTypes));
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({self.seedNode});
        if(self.ourScorer == None or self.clearWeightsWithNewSeedNode):
            # below we remove self.targetEntityType since we are (or should be) dealing with a multi-layer
            # bipartite graph, so there are no edges from the target type node to the target type nodes.
            # For this reason, ExpansionManager only has one  ExpansionManagerByType for each non-target type
            # entity - there are no direct relations between the target type nodes and other target type nodes
            # the the scorer will have to weigh.... 
            self.ourScorer = RedThreadWithoutEvidenceWeightsScorer(self.entityTypes.difference({self.targetEntityType}), self.learningRate, \
                                 updateOnPositive=self.updateOnPositive, \
                                 errorToleranceForFloatingPointComparison=self.errorToleranceForFloatingPointComparison, \
                                 styleUpdateOnPositive=self.styleUpdateOnPositive);
        self.ourExpansionManager = ExpansionManagerAlphaACG(self.ourGraph, self.entityTypes, \
                                                    providedSeedNode, self.ourScorer , queueSize=self.queueSize, \
                                                    capDegreeOfNodesToExpand=self.degreeCutoffForNeighborsToExpand);
        self.recordState();
        return;


    # we need to clear the seed node as opposed to just make a new object since
    # our internal graphs and per-entity-type weights need to be preserved.
    def clearSeedNode(self):
        # requires(self.seedNodeIsSet());
        # the below are assers as oppossed to requires since, after the users
        # ensures the above condition in the requires, the rest should follow 
        # unless there is a bug in our code...
        # assert(len(self.nodesInCurrentCluster) > 0); # the current set of nodes should
            # at least contain the seed node provided before...
        # assert(self.seedNode in self.nodesInCurrentCluster);

        # self.refToWritterObj.writeToQueueLogFilesForACG(self.ourExpansionManager.dictsMappingEntityTypeToDictsMappingNodesToWeight, self.targetEntityType);

        super(AlgorithmRedThreadWithoutEvidenceWeights, self).clearSeedNode();
        self.nodesFromOldClusters = self.nodesFromOldClusters.union( \
            self.nodesInCurrentCluster);
        # assert(self.nodesInCurrentCluster.issubset(self.nodesFromOldClusters));
        self.nodesInCurrentCluster = set();
        # ensures(len(self.nodesInCurrentCluster) == 0);
        # ensures(len(self.nodesFromOldClusters) > 0);
        # ensures(self.seedNode == None);
        return;


    def isNodeOfTargetType(self, nodeToConsider):
        if(nodeToConsider not in self.perNodeAttributeDictionary):
            return False;
        elif(self.perNodeAttributeDictionary[nodeToConsider] != self.targetEntityType):
            return False;
        else:
            return True;



    def getMaxScoringNode(self, setOfNodesToConsider):
        # requires(isinstance(setOfNodesToConsider , set));
        # requires(len(setOfNodesToConsider) > 0);
        nodeWithMaxScore = None;
        maxScore = None;
        for thisNode in setOfNodesToConsider:
            perEntityTypeWeightsDictForThisNode = self.ourExpansionManager.getWeightOfNode(thisNode);
            scoreForThisNode = self.ourScorer.calculateScore(perEntityTypeWeightsDictForThisNode);
            # scoreForThisNode = self.ourExpansionManager.getCurrentScoreOfNode(thisNode);
            if(nodeWithMaxScore == None or (scoreForThisNode > maxScore )):
               maxScore = scoreForThisNode;
               nodeWithMaxScore = thisNode;
        ensures(  (nodeWithMaxScore != None  and maxScore != None) or \
            len(setOfNodesToConsider) == 0);
        # TODO: strengthen the ensures.
        return {"nodeWithMaxScore" : nodeWithMaxScore, "maxScore" : maxScore, };



    def getNodesToConsiderQueringExpertWith(self):
        setOfNodesToConsider = set();
        currentSetOfSeenNodes = self.ourExpansionManager.getPathLength2NeighborsOfPositiveNodes();
        setOfNodesToConsider = currentSetOfSeenNodes.difference(self.nodesWeRecievedExpertInputFor);
        # With the current setup, setOfNodesToConsider should be exactly the same after the below line is executed...
        ##### As noted in the comment above, if the graph structure is as we expect - bipartite - then the below filtering 
        #####     should not be necessary.
        #####setOfNodesToConsider = set([x for x in setOfNodesToConsider if self.perNodeAttributeDictionary[x] == self.targetEntityType]);
        return setOfNodesToConsider;



    # TODO: remove nodes that we gain labels for from consideration.
    def getNextNode(self):
        setOfNodesToConsider = self.getNodesToConsiderQueringExpertWith();
        if(not self.randomizedNodeSelection):
            ########## print "\n\nsetOfNodesToConsider:\n" + str(setOfNodesToConsider) + "\n\n";
            resultFromGetMaxScore = self.getMaxScoringNode(setOfNodesToConsider);
            nodeWithMaxScore = resultFromGetMaxScore["nodeWithMaxScore"];
            maxScore =  resultFromGetMaxScore["maxScore"];
            #COMMENTED_OUT_ASSERT# ensures(isinstance(maxScore, float) or maxScore == None);
            #COMMENTED_OUT_ASSERT# ensures(isinstance(nodeWithMaxScore, str) or nodeWithMaxScore == None);
            return nodeWithMaxScore;
        else:
            nodeToReturn = self.getNodeWeightedRandom(setOfNodesToConsider);
            return nodeToReturn;

    def inputFeedback(self, nodeConsidered, labelProvided, learnFromExample=True):
        # requires(self.isNodeOfTargetType(nodeConsidered));
        # requires(nodeConsidered not in self.nodesFromOldClusters);
        # requires(isProperLabel(labelProvided));
        # TODO: need to made sure the node provided is in the expanded set of nodes -
        #     if it is not, then it is going to have all weights zero, which will be an issue.
        super(AlgorithmRedThreadWithoutEvidenceWeights, self).inputFeedback(nodeConsidered, labelProvided);
        perEntityTypeWeightsDictForThisNode = self.ourExpansionManager.getWeightOfNode(nodeConsidered);
        # assert( len(perEntityTypeWeightsDictForThisNode) == len(self.entityTypes) - 1 ); # we have minus 1 here, becuase 
            # the target entity type should not be a key in this dictionary...
        # assert(self.targetEntityType not in perEntityTypeWeightsDictForThisNode);
        # See the note in the updateWeightVector function of the AlphaACGPerceptron
        # class for why, below, we fix the predicted label as positive.
        if(learnFromExample):
            self.ourScorer.updateWeightVector(perEntityTypeWeightsDictForThisNode, \
                positiveLabel, labelProvided);
        if(labelProvided == positiveLabel):
            self.addNodeToCluster(nodeConsidered);
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({nodeConsidered});
        # BELOW: NOTE CAREFULLY THAT WE UPDATE THE EXPANSION MANAGER AFTER UPDATING OUR SCORER, SO THE
        #     EXPANSION MANAGER USING THE NEWLY UPDATED SCORES TO DETERMINE WHAT STAYS IN THE QUEUE....
        self.ourExpansionManager.expandSeenNodeSet(nodeConsidered, labelProvided, self.ourScorer);
        # assert( nodeConsidered in self.nodesWeRecievedExpertInputFor );
        self.recordState();
        return;


    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

    

    def addNodeToCluster(self, thisNode):
        # requires(self.seedNodeIsSet());
        # requires(self.isNodeOfTargetType(thisNode));
        self.nodesInCurrentCluster = self.nodesInCurrentCluster.union({thisNode});
        # ensures(len(self.nodesInCurrentCluster) > 0);
        # ensures(thisNode in self.nodesInCurrentCluster);


