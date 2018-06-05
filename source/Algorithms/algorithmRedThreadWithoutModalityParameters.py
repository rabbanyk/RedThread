from dataAccessor import *;
from contracts import *;
from labelNames import *;
# from algorithmBaseClass import *;
import sys;


from Algorithms.algorithmAlphaACG import AlgorithmAlphaACG;
from Algorithms.components.scorers import UniformScorer;
from Algorithms.components.implementedExpansionManagers import ExpansionManagerForRedThreadWithoutModalityParameters;



class AlgorithmRedThreadWithoutModalityParameters(AlgorithmAlphaACG): #TODO: check this



    def parseInputParameters(self, inputString):
        dictOfValuesFromString = self.helper_parseInputParameters_convertStringToDict(inputString);

        # checking values
        # whole dictionary is in the right form
        assert(set(dictOfValuesFromString.keys()) == \
            {"queueSize", "degreeCutoffForNeighborsToExpand"});
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
        # setting values
        self.queueSize = int(dictOfValuesFromString["queueSize"]);

        # checking that values read are reasonable.
        assert(isinstance(self.queueSize, int));
        assert( self.queueSize > 0 );
        # capDegreeOfNodesToExpand is proper
        assert( isinstance(self.degreeCutoffForNeighborsToExpand, int) or ( self.degreeCutoffForNeighborsToExpand == float("inf")));
        assert( self.degreeCutoffForNeighborsToExpand > 0);

        return;



    def setSeedNode(self, providedSeedNode):
        # requires(providedSeedNode not in self.nodesFromOldClusters);
        # assert(self.targetEntityType == None or (self.targetEntityType in self.entityTypes));
        # assert(providedSeedNode in self.perNodeAttributeDictionary);
        # requires(self.targetEntityType == None or \
        #    (self.perNodeAttributeDictionary[providedSeedNode] == self.targetEntityType));
        super(AlgorithmAlphaACG, self).setSeedNode(providedSeedNode);
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
        if(self.ourPerceptron == None):
            # below we remove self.targetEntityType since we are (or should be) dealing with a multi-layer
            # bipartite graph, so there are no edges from the target type node to the target type nodes.
            # For this reason, ExpansionManager only has one  ExpansionManagerByType for each non-target type
            # entity - there are no direct relations between the target type nodes and other target type nodes
            # the the scorer will have to weigh.... Note that we only initialize the scorer once - 
            # not once for each new cluster; we want to reuse what we learn about the importance of different
            # entity-type relationships from forming an old cluster when we form a new cluster.
            self.ourPerceptron = UniformScorer(self.entityTypes.difference({self.targetEntityType}));
        # NOTE: the ExpansionManager automatically does the expansion around providedSeedNode for us...
        assert(isinstance(self.ourPerceptron, UniformScorer)); # not trivial - suppose we called the wrong super class
            # and accidentally use the same scorer as alphaACG. 
        self.ourExpansionManager = ExpansionManagerForRedThreadWithoutModalityParameters(\
            self.ourGraph, self.entityTypes, providedSeedNode, self.ourPerceptron, \
            queueSize=self.queueSize, capDegreeOfNodesToExpand=self.degreeCutoffForNeighborsToExpand);
        return;









