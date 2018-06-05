from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmAlphaACG import AlgorithmAlphaACG; 
from numpy import random;
import sys


from Algorithms.components.scorers import RedThreadWithoutParametersPerceptron;
from Algorithms.algorithmAlphaACG import AlgorithmAlphaACG;
from Algorithms.components.implementedExpansionManagers import ExpansionManagerAlphaACG;



class AlgorithmRedThreadWithoutParameters(AlgorithmAlphaACG):

    def __init__(self, dataObj, writterObj, inputString):
        super(AlgorithmRedThreadWithoutParameters, self).__init__(dataObj, writterObj, inputString);
        return;



    def parseInputParameters(self, inputString):
        dictOfValuesFromString = self.helper_parseInputParameters_convertStringToDict(inputString);

        # checking values
        # whole dictionary is in the right form
        assert(set(dictOfValuesFromString.keys()) == \
            {"initialValue", "specailValueForMagnitude", "updateMagnitudeWeight", \
             "updateOnPostive", "updateOnNegative", \
             "concensusClusterViaIntersectingClusters", "featurizationAndTakeMagnitude", \
             "featurizationAndTakeNormalizedValues", "queueSize", "degreeCutoffForNeighborsToExpand", 
             "whetherOrNotToResetWithSeedNode"});
        assert(all([isinstance(x, float) for x in dictOfValuesFromString.values()]));
        # queueSize is proper
        assert( dictOfValuesFromString["queueSize"] % 1 == 0.0 ); # this is an assert and not a requires since it come from something we derive after 
            # manipulating the input... This, by the way, basically checks that the queue size is an integer.
        assert( dictOfValuesFromString["queueSize"] > 0 );
        # boolean values are proper.
        for thisParameterName in ["updateMagnitudeWeight", "updateOnPostive", "updateOnNegative", \
                                  "concensusClusterViaIntersectingClusters", "featurizationAndTakeMagnitude", \
                                  "featurizationAndTakeNormalizedValues", "whetherOrNotToResetWithSeedNode"]:
            assert( dictOfValuesFromString[thisParameterName] in {1.0, 0.0} ); # binary values for boolean variable
        # degreeCutoffForNeighborsToExpand is proper
        assert( dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] % 1 == 0.0); # must be interger
        assert( (dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] > 0) or \
            (dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] == -1.0) ); # we use negative one ot indicate an infinite degree
            # cutoff - which is equivalent to no degree cutoff at all...
        # TODO: check "initialValue" and "specailValueForMagnitude"


        # Note that the random walks do not actually use the queue-size - but we require that it be passed in
        #     for the sake of grouping these results with the proper set of experiments.
        if(dictOfValuesFromString["degreeCutoffForNeighborsToExpand"] == -1.0):
            self.degreeCutoffForNeighborsToExpand = float("inf");
        else:
            self.degreeCutoffForNeighborsToExpand = int(dictOfValuesFromString["degreeCutoffForNeighborsToExpand"]);
        # setting queue size
        self.queueSize = int(dictOfValuesFromString["queueSize"]);
        # setting boolean values
        self.perceptronSettings_updateMagnitudeWeight = (dictOfValuesFromString["updateMagnitudeWeight"] == 1.0);
        self.perceptronSettings_updateOnPostive = (dictOfValuesFromString["updateOnPostive"] == 1.0);
        self.perceptronSettings_updateOnNegative = (dictOfValuesFromString["updateOnNegative"] == 1.0);
        self.perceptronSettings_concensusClusterViaIntersectingClusters = (dictOfValuesFromString["concensusClusterViaIntersectingClusters"] == 1.0);
        self.perceptronSettings_featurizationAndTakeMagnitude = (dictOfValuesFromString["featurizationAndTakeMagnitude"] == 1.0);
        self.perceptronSettings_featurizationAndTakeNormalizedValues = (dictOfValuesFromString["featurizationAndTakeNormalizedValues"] == 1.0);
        self.whetherOrNotToResetWithSeedNode = (dictOfValuesFromString["whetherOrNotToResetWithSeedNode"] == 1.0);
        # setting the other values
        self.perceptronSettings_initialValue = dictOfValuesFromString["initialValue"];
        self.perceptronSettings_specailValueForMagnitude = dictOfValuesFromString["specailValueForMagnitude"];


        # checking that values read are reasonable.
        assert(isinstance(self.queueSize, int));
        assert( self.queueSize > 0 );
        # checking that the values that should be boolean are in fact boolean.
        for thisValue in [self.perceptronSettings_updateMagnitudeWeight , self.perceptronSettings_updateOnPostive , \
                          self.perceptronSettings_updateOnNegative , self.perceptronSettings_concensusClusterViaIntersectingClusters , \
                          self.perceptronSettings_featurizationAndTakeMagnitude , self.perceptronSettings_featurizationAndTakeNormalizedValues ,\
                          self.whetherOrNotToResetWithSeedNode]:
            assert(isinstance(thisValue, bool));
        # checking self.degreeCutoffForNeighborsToExpand
        assert( isinstance(self.degreeCutoffForNeighborsToExpand, int) or (self.degreeCutoffForNeighborsToExpand == float("inf")));
        assert( self.degreeCutoffForNeighborsToExpand > 0);

        return;




    def setSeedNode(self, providedSeedNode):            

        super(AlgorithmAlphaACG, self).setSeedNode(providedSeedNode); # TODO: call the algorithm base class here.
        self.seedNode = providedSeedNode;
        if(self.targetEntityType == None):
            self.targetEntityType = self.perNodeAttributeDictionary[providedSeedNode];

        self.seedNode = providedSeedNode;
        if(self.targetEntityType == None):
            self.targetEntityType = self.perNodeAttributeDictionary[providedSeedNode];
        # raise Exception; # rebrew this code.
        # self.ourExpansionManager = ExpansionManager(self.ourGraph, self.entityTypes, \
        #                                             self.perNodeAttributeDictionary, providedSeedNode, queueSize, errorToleranceOnQueueSize);
        self.nodesInCurrentCluster = {providedSeedNode};
        self.nodesWeRecievedExpertInputFor = self.nodesWeRecievedExpertInputFor.union({self.seedNode});
        if(self.ourPerceptron == None or self.whetherOrNotToResetWithSeedNode):
            # below we remove self.targetEntityType since we are (or should be) dealing with a multi-layer
            # bipartite graph, so there are no edges from the target type node to the target type nodes.
            # For this reason, ExpansionManager only has one  ExpansionManagerByType for each non-target type
            # entity - there are no direct relations between the target type nodes and other target type nodes
            # the the perceptron will have to weigh.... Note that we only initialize the perceptron once - 
            # not once for each new cluster; we want to reuse what we learn about the importance of different
            # entity-type relationships from forming an old cluster when we form a new cluster.
            self.ourPerceptron = \
                RedThreadWithoutParametersPerceptron(\
                    self.entityTypes.difference({self.targetEntityType}), \
                    self.perceptronSettings_initialValue, \
                    self.perceptronSettings_specailValueForMagnitude,\
                    self.perceptronSettings_updateMagnitudeWeight, \
                    self.perceptronSettings_updateOnPostive, \
                    self.perceptronSettings_updateOnNegative, \
                    self.perceptronSettings_concensusClusterViaIntersectingClusters, \
                    self.perceptronSettings_featurizationAndTakeMagnitude, \
                    self.perceptronSettings_featurizationAndTakeNormalizedValues);
        assert(isinstance(self.ourPerceptron, RedThreadWithoutParametersPerceptron));
        self.ourExpansionManager = ExpansionManagerAlphaACG(self.ourGraph, self.entityTypes, \
                                                     providedSeedNode, self.ourPerceptron, self.queueSize, capDegreeOfNodesToExpand=self.degreeCutoffForNeighborsToExpand);
        return;




