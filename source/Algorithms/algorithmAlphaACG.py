from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmBaseClass import *;
from Algorithms.components.expansionManagerPrimitive import ExpansionManagerPrimitive;
import sys;




class AlgorithmAlphaACG(AlgorithmBaseClass):


    #V~VVV~V~V~~VV~~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V
    # basic functions to set up the algorithm datastructure
    #---------------------------------------------------------------------
    def __init__(self, dataObj, writterObj, parameterString):
        sys.stdout.flush();
        print("START:__init__");
        sys.stdout.flush();
        super(AlgorithmAlphaACG, self).__init__(dataObj, writterObj, parameterString);

        self.ourGraph = dataObj; # TODO: clean this up. It is repeatative given what is in the algorithm base class
            # , the only difference is that there we set a variable that has a different name.

        self.perNodeAttributeDictionary = self.ourGraph.entityToTypeDict;
        self.entityTypes = set(self.perNodeAttributeDictionary.values());
        self.nodesFromOldClusters = set();
        self.nodesInCurrentCluster = set();
        self.targetEntityType = None;
        self.ourExpansionManager = None;
        self.ourPerceptron = None;
        self.seedNode = None;
        self.nodesWeRecievedExpertInputFor = set(); # we never have an expert annotate the same node twice. We preserve
            # the content of this set across the various seed nodes that might be provided. Futher, this enforces 



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

        #uncomment this line for the runs were you want to record what the queue looks like prior to getting a new seed node....# self.refToWritterObj.writeToQueueLogFilesForACG(self.ourExpansionManager.dictsMappingEntityTypeToDictsMappingNodesToWeight, self.targetEntityType);

        super(AlgorithmAlphaACG, self).clearSeedNode();
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
            ########## print "\n\ngetMaxScoringNode:thisNode:\n" + str(thisNode) + "\n\n";
            ########## print "\n\ngetMaxScoringNode:self.nodesInCurrentCluster:\n" + str(self.nodesInCurrentCluster) + "\n\n";
            perEntityTypeWeightsDictForThisNode = self.ourExpansionManager.getWeightOfNode(thisNode);
            scoreForThisNode = self.ourPerceptron.calculateScore(perEntityTypeWeightsDictForThisNode);
            # scoreForThisNode = self.ourExpansionManager.getCurrentScoreOfNode(thisNode);
            if(nodeWithMaxScore == None or (scoreForThisNode > maxScore )):
               maxScore = scoreForThisNode;
               nodeWithMaxScore = thisNode;
        # ensures(nodeWithMaxScore != None);
        # TODO: strengthen the ensures.
        return {"nodeWithMaxScore" : nodeWithMaxScore, "maxScore" : maxScore};



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
        ########## print "\n\nsetOfNodesToConsider:\n" + str(setOfNodesToConsider) + "\n\n";
        resultFromGetMaxScore = self.getMaxScoringNode(setOfNodesToConsider);
        nodeWithMaxScore = resultFromGetMaxScore["nodeWithMaxScore"];
        maxScore =  resultFromGetMaxScore["maxScore"];
        #COMMENTED_OUT_ASSERT# ensures(isinstance(maxScore, float) or maxScore == None);
        #COMMENTED_OUT_ASSERT# ensures(isinstance(nodeWithMaxScore, str) or nodeWithMaxScore == None);
        return nodeWithMaxScore;


    def inputFeedback(self, nodeConsidered, labelProvided, learnFromExample=True):
        # requires(self.isNodeOfTargetType(nodeConsidered));
        # requires(nodeConsidered not in self.nodesFromOldClusters);
        # requires(isProperLabel(labelProvided));
        # TODO: need to made sure the node provided is in the expanded set of nodes -
        #     if it is not, then it is going to have all weights zero, which will be an issue.
        super(AlgorithmAlphaACG, self).inputFeedback(nodeConsidered, labelProvided);
        perEntityTypeWeightsDictForThisNode = self.ourExpansionManager.getWeightOfNode(nodeConsidered);
        # assert( len(perEntityTypeWeightsDictForThisNode) == len(self.entityTypes) - 1 ); # we have minus 1 here, becuase 
            # the target entity type should not be a key in this dictionary...
        # assert(self.targetEntityType not in perEntityTypeWeightsDictForThisNode);
        # See the note in the updateWeightVector function of the AlphaACGPerceptron
        # class for why, below, we fix the predicted label as positive.
        if(learnFromExample):
            self.ourPerceptron.updateWeightVector(perEntityTypeWeightsDictForThisNode, \
                positiveLabel, labelProvided);
        if(labelProvided == positiveLabel):
            self.addNodeToCluster(nodeConsidered);
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({nodeConsidered});
        # BELOW: NOTE CAREFULLY THAT WE UPDATE THE EXPANSION MANAGER AFTER UPDATING OUR SCORER, SO THE
        #     EXPANSION MANAGER USING THE NEWLY UPDATED SCORES TO DETERMINE WHAT STAYS IN THE QUEUE....
        self.ourExpansionManager.expandSeenNodeSet(nodeConsidered, labelProvided, self.ourPerceptron);
        # assert( nodeConsidered in self.nodesWeRecievedExpertInputFor );
        return;


    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

    def addNodeToCluster(self, thisNode):
        # requires(self.seedNodeIsSet());
        # requires(self.isNodeOfTargetType(thisNode));
        self.nodesInCurrentCluster = self.nodesInCurrentCluster.union({thisNode});
        # ensures(len(self.nodesInCurrentCluster) > 0);
        # ensures(thisNode in self.nodesInCurrentCluster);


