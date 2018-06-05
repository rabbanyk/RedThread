from dataAccessor import *;
from contracts import *;
from labelNames import *;
from numpy.random import choice as randomChoice;
import sys

from Algorithms.algorithmAlphaACG import AlgorithmAlphaACG;
from Algorithms.algorithmRedThreadWithoutEvidenceWeights import AlgorithmRedThreadWithoutEvidenceWeights;
from Algorithms.components.scorers import RedThreadWithoutEvidenceWeightsScorer;
from Algorithms.components.implementedExpansionManagers import ExpansionManagerForRedThreadWithoutModalityParameters;


class AlgorithmRedThread(AlgorithmRedThreadWithoutEvidenceWeights):

    def setSeedNode(self, providedSeedNode):
        assert(self.queueSize > 0);

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
            # note that below, by re-initializing ourScorer, we essentially reset for each new seed node...
            self.ourScorer = RedThreadWithoutEvidenceWeightsScorer(self.entityTypes.difference({self.targetEntityType}), 
                                 self.learningRate, updateOnPositive=self.updateOnPositive, \
                                           styleUpdateOnPositive=self.styleUpdateOnPositive);
        assert(isinstance(self.ourScorer, RedThreadWithoutEvidenceWeightsScorer));# not trivial - suppose we called the wrong super class
            # and accidentally use the same scorer as alphaACG. 
        self.ourExpansionManager = ExpansionManagerForRedThreadWithoutModalityParameters(self.ourGraph, self.entityTypes, providedSeedNode, \
            self.ourScorer, queueSize=self.queueSize, capDegreeOfNodesToExpand = self.degreeCutoffForNeighborsToExpand);
        return;


