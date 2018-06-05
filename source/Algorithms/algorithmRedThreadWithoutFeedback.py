from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmBaseClass import *;
import math; # used for the sqrt function...
import operator;
import sys;


from Algorithms.components.scorers import UniformScorer;
from Algorithms.components.implementedExpansionManagers import ExpansionManagerAlphaACG;



class AlgorithmRedThreadWithoutFeedback(AlgorithmBaseClass):

    def parseInputParameters(self, inputString):
        dictOfValuesFromString = self.helper_parseInputParameters_convertStringToDict(inputString);
        # checking values
        # whole dictionary is in the right form
        assert(set(dictOfValuesFromString.keys()) == {"queueSize", "degreeCutoffForNeighborsToExpand"});
        assert(all([isinstance(x, float) for x in dictOfValuesFromString.values()]));
        # queueSize is proper
        assert( dictOfValuesFromString["queueSize"] % 1 == 0.0 ); # this is an assert and not a requires since it come from something we derive after 
            # manipulating the input... This, by the way, basically checks that the queue size is an integer.
        assert( dictOfValuesFromString["queueSize"] > 0 );
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
        self.queueSize = int(dictOfValuesFromString["queueSize"]);


        # checking that values read are reasonable.
        assert(isinstance(self.queueSize, int));
        assert( self.queueSize > 0 );
        # capDegreeOfNodesToExpand is proper
        assert( isinstance(self.degreeCutoffForNeighborsToExpand, int ) or (self.degreeCutoffForNeighborsToExpand == float("inf")));
        assert( self.degreeCutoffForNeighborsToExpand > 0);

        return;


    #V~VVV~V~V~~VV~~V~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V
    # basic functions to set up the algorithm datastructure
    #---------------------------------------------------------------------
    def __init__(self, dataObj, writterObj, inputString):
        sys.stdout.flush();
        print("START:__init__");
        sys.stdout.flush();
        super(AlgorithmRedThreadWithoutFeedback, self).__init__(dataObj, writterObj, inputString);
        self.ourGraph = self.refToDataObj; 
        self.perNodeAttributeDictionary = self.ourGraph.entityToTypeDict;
        self.entityTypes = set(self.perNodeAttributeDictionary.values());
        self.nodesFromOldClusters = set();
        self.nodesInCurrentCluster = set();
        self.targetEntityType = None;
        self.ourExpansionManager = None;
        self.seedNode = None;
        self.nodesWeRecievedExpertInputFor = set(); # we never have an expert annotate the same node twice. We preserve
            # the content of this set across the various seed nodes that might be provided. Futher, this enforces 
        return;


    def setSeedNode(self, providedSeedNode):
        # requires(providedSeedNode not in self.nodesFromOldClusters);
        # assert(self.targetEntityType == None or (self.targetEntityType in self.entityTypes));
        # assert(providedSeedNode in self.perNodeAttributeDictionary);
        # requires(self.targetEntityType == None or \
        #    (self.perNodeAttributeDictionary[providedSeedNode] == self.targetEntityType));
        super(AlgorithmRedThreadWithoutFeedback, self).setSeedNode(providedSeedNode);
        self.seedNode = providedSeedNode;
        if(self.targetEntityType == None):
            self.targetEntityType = self.perNodeAttributeDictionary[providedSeedNode];           
        self.nonTargetEntityTypes = self.entityTypes.difference([self.targetEntityType]);
        assert(len(self.nonTargetEntityTypes) == len(self.entityTypes) - 1); # This could fail to happen, for instance, 
            # if self.targetEntityType not in self.entityTypes 
        # NOTE: the ExpansionManager automatically does the expansion around providedSeedNode for us... 
        self.ourExpansionManager = ExpansionManagerAlphaACG(self.ourGraph, self.entityTypes, providedSeedNode, \
                                                    UniformScorer(self.nonTargetEntityTypes) , queueSize=self.queueSize, \
                                                    capDegreeOfNodesToExpand=self.degreeCutoffForNeighborsToExpand );
        # assert(self.nodesInCurrentCluster == set()); # this should have either been done by the __init__
            # function or the clearSeedNode function below.
        self.nodesInCurrentCluster = {providedSeedNode};
        # for the below to actually work, we have to ensure that None is not 
        #     an entity type...
        # ensures(self.targetEntityType != None and (self.targetEntityType in self.entityTypes));
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({self.seedNode});
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
        # assert(self.seedNode in self.nodesInCurrentCluster)
        super(AlgorithmRedThreadWithoutFeedback, self).clearSeedNode();
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
            perEntityTypeWeightsDictForThisNode = \
                self.ourExpansionManager.getWeightOfNode(thisNode);
            scoreForThisNode = sum(perEntityTypeWeightsDictForThisNode.values());
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
        labelProvided = positiveLabel; # hack that makes this RedThreadWithoutFeedback - does not use updates.
        # requires(self.isNodeOfTargetType(nodeConsidered));
        # requires(nodeConsidered not in self.nodesFromOldClusters);
        # requires(isProperLabel(labelProvided));
        # TODO: need to made sure the node provided is in the expanded set of nodes -
        #     if it is not, then it is going to have all weights zero, which will be an issue.
        super(AlgorithmRedThreadWithoutFeedback, self).inputFeedback(nodeConsidered, labelProvided);
        perEntityTypeWeightsDictForThisNode = self.ourExpansionManager.getWeightOfNode(nodeConsidered);
        # assert( len(perEntityTypeWeightsDictForThisNode) == len(self.entityTypes) - 1 ); # we have minus 1 here, becuase 
            # the target entity type should not be a key in this dictionary...
        # assert(self.targetEntityType not in perEntityTypeWeightsDictForThisNode);
        # See the note in the updateWeightVector function of the AlphaACGPerceptron
        # class for why, below, we fix the predicted label as positive.
        if(labelProvided == positiveLabel):
            self.addNodeToCluster(nodeConsidered);
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({nodeConsidered});
        self.ourExpansionManager.expandSeenNodeSet(nodeConsidered, labelProvided, UniformScorer(self.nonTargetEntityTypes));
        # assert( nodeConsidered in self.nodesWeRecievedExpertInputFor );
        return;


    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


    def addNodeToCluster(self, thisNode):
        # requires(self.seedNodeIsSet());
        # requires(self.isNodeOfTargetType(thisNode));
        self.nodesInCurrentCluster = self.nodesInCurrentCluster.union({thisNode});
        # ensures(len(self.nodesInCurrentCluster) > 0);
        # ensures(thisNode in self.nodesInCurrentCluster);

