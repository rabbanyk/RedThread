from dataAccessor import *;
from contracts import *;
from labelNames import *;
from numpy.random import choice as randomChoice;
import math;
import operator;
import sys


class BaseScorer():

    def __init__(self, entityTypes):
        raise Exception(); # children have to overwrite this.

    def getWeightDict():
        raise Exception(); # children have to overwrite this.

    def calculateScore():
        raise Exception(); # children have to overwrite this.

    def updateWeightVector(self, inputDict, predictedLabel, groundTruthLabel):
        raise Exception(); # children have to overwrite this.

class UniformScorer(BaseScorer):

    def __init__(self, nonTargetEntityTypes):
        self.nonTargetEntityTypes = nonTargetEntityTypes;
        return;

    def calculateScore(self, dictMappingEntityTypeToWeight):
        requires(set(dictMappingEntityTypeToWeight) == set(self.nonTargetEntityTypes));
        return sum(dictMappingEntityTypeToWeight.values());

    def updateWeightVector(self, inputDict, predictedLabel, groundTruthLabel):
        return;

    def getWeightDict(self): # all modalities are weighted equally....
        # raise Exception(); # TODO: have this return a dictionary mapping entity types to their weights.
        # return [1.0] * self.numberOfNonTargetEntityType;
        return {x : 1.0 for x in self.nonTargetEntityTypes};


class RedThreadWithoutEvidenceWeightsScorer(BaseScorer):

    def __init__(self, entityTypes, learningRate, updateOnPositive=False, errorToleranceForFloatingPointComparison=0.0, styleUpdateOnPositive="original"):
        requires(isinstance(learningRate, float));
        requires(learningRate >= 0); # should we allow a learning rate of zero?
        requires(learningRate < 1);
        requires(styleUpdateOnPositive in {"original", "symmetric"});
        # below, we start with 1000 instead of 1.0 (despite them having 
        #     the same effect on the ordering) in hopes of staving of floating-point
        #     precision issues a little longer....
        self.weightVector = { thisEntityType : 1000.0  for thisEntityType in entityTypes};
        self.learningRate = learningRate;
        self.entityTypesInFixedOrder = list(entityTypes);
        self.entityTypesInFixedOrder.sort();
        requires(isinstance(updateOnPositive, bool));
        self.updateOnPositive = updateOnPositive;
        self.errorToleranceForFloatingPointComparison = errorToleranceForFloatingPointComparison;
        self.modalitiesLastUpdated = set();
        self.styleUpdateOnPositive = styleUpdateOnPositive;
        return;
             

    def calculateScore(self, inputDict):
        # if it were not for the fact that this would probably be expensive overall,
        # we would require this#requires(set(inputDict.keys()) == set(self.weightVector.keys()));
        runningScore = 0.0;
        for thisEntityType in inputDict:
            # assert(runningScore + >= runningScore); # weak overflow check....
            runningScore = runningScore + (inputDict[thisEntityType] * self.weightVector[thisEntityType]);
        return runningScore;

    def helper_howUpdateOnPositive(self):
        requires(self.styleUpdateOnPositive in {"original", "symmetric"}); # this perhaps should be really 
            # an assert, since the caller of this function may or may not be resonsible for it being true.
        requires(self.learningRate > 0);
        if(self.styleUpdateOnPositive == "original"):
            return 2 - self.learningRate;
        elif(self.styleUpdateOnPositive == "symmetric"):
            return 1.0 / float(self.learningRate);
        else:
            raise Exception(); # this should not occur by the requires of this 
                # function as well as of the __init__ function.:

    def updateWeightVector(self, inputDict, predictedLabel, groundTruthLabel):

        if(predictedLabel != positiveLabel):
            # For now, we assume that all input we receive are features corresponding
            # to one of the nodes that the RedThreadWithoutEvidenceWeights algorithm suggested. The RedThreadWithoutEvidenceWeights algorithm, as currently
            # coded, only suggests the node that, to it, seems most promising to have a relationship with
            # the rest of the nodes in the proposed cluster - which we will take as the RedThreadWithoutEvidenceWeights algorithm 
            # predicting that the given node has a positive label. Note that this assumption to 
            # some extent depends on when we decide to stop expanding a cluster - if all the members of 
            # the graph that relate to the given seed node are found, but we continue to expand the graph
            # searching for more, then the algorithm will seem to be making a number of mistakes, even 
            # if it initial found and used the optimal weights to find all nodes truly related to the
            # seed node. 
            raise Exception;

        rateToMultipleMaxExpertsWith = self.learningRate;
    
        if(groundTruthLabel == positiveLabel):
            if(not self.updateOnPositive):
                return;
            else:
                # why the 2 below? It is 1 + (1 - self.learningRate), so the distance
                # from 1 is the same as for self.learningRate....
                rateToMultipleMaxExpertsWith = self.helper_howUpdateOnPositive();
        
        assert(groundTruthLabel != positiveLabel or self.updateOnPositive);
        maxScoreAmongExperts = float("-Inf"); # need to use when in AlgorithmRedThread.
        setOfExpertsWithMaxScore = set();
        for thisEntityType in self.entityTypesInFixedOrder:
            scoreThatThisExpertContributed =  (self.weightVector[thisEntityType]) * (inputDict[thisEntityType]);
            # print "    scoreThatThisExpertContributed:" + str(thisEntityType) + "," + str(scoreThatThisExpertContributed);
            if( abs(scoreThatThisExpertContributed - maxScoreAmongExperts) <= self.errorToleranceForFloatingPointComparison ):
                setOfExpertsWithMaxScore = setOfExpertsWithMaxScore.union([thisEntityType]);
                assert(thisEntityType in setOfExpertsWithMaxScore); # not a trivial assert- especailly when adding elements to a set
                    # that, themselves, have an iterator defined on them (example: it is easy to accidentally make a set of characters
                    # instead of a set of strings....)
                maxScoreAmongExperts = max([maxScoreAmongExperts, scoreThatThisExpertContributed]);
            elif(scoreThatThisExpertContributed > maxScoreAmongExperts):
                assert(scoreThatThisExpertContributed - maxScoreAmongExperts > self.errorToleranceForFloatingPointComparison);
                maxScoreAmongExperts = scoreThatThisExpertContributed;
                setOfExpertsWithMaxScore = set([thisEntityType]);
                assert(thisEntityType in setOfExpertsWithMaxScore); # not a trivial assert- especailly when adding elements to a set
                    # that, themselves, have an iterator defined on them (example: it is easy to accidentally make a set of characters
                    # instead of a set of strings....)
        assert(len(setOfExpertsWithMaxScore) > 0);
        self.modalitiesLastUpdated = setOfExpertsWithMaxScore;
        for thisExpertWhoWasWrong in setOfExpertsWithMaxScore:
            self.weightVector[thisExpertWhoWasWrong] = (self.weightVector[thisExpertWhoWasWrong]) * rateToMultipleMaxExpertsWith;
        self.errorToleranceForFloatingPointComparison = self.errorToleranceForFloatingPointComparison * rateToMultipleMaxExpertsWith;
        return;

    def getWeightDict(self):
        return self.weightVector;

    def getCurrentErrorToleranceForFloatingPointComparison(self):
        return self.errorToleranceForFloatingPointComparison;

    def getModalitiesLastUpdated(self):
        return self.modalitiesLastUpdated;


class RedThreadWithoutParametersPerceptron(BaseScorer):


    def featurize(self, inputDict):
        featureVector = (len(self.entityTypes) + 1) * [0.0];
        if(self.featurizationAndTakeMagnitude or self.featurizationAndTakeNormalizedValues):
            raise Exception();
        else: # we return the orignal, observed weights....
            index = 0;
            for thisEntityType in self.entityTypes:
                index = index + 1;
                featureVector[index] = inputDict[thisEntityType];
        return featureVector;


    def __init__(self, entityTypes, initialValue, specailValueForMagnitude, updateMagnitudeWeight, updateOnPostive, updateOnNegative, \
        concensusClusterViaIntersectingClusters, featurizationAndTakeMagnitude, featurizationAndTakeNormalizedValues):
        requires(isinstance(initialValue, float));
        requires( (specailValueForMagnitude == None) or isinstance(specailValueForMagnitude, float));
        requires(isinstance(updateMagnitudeWeight, bool));
        requires(isinstance(updateOnPostive, bool));
        requires(isinstance(updateOnNegative, bool));
        requires(isinstance(concensusClusterViaIntersectingClusters, bool));
        requires(isinstance(featurizationAndTakeMagnitude, bool));
        requires(isinstance(featurizationAndTakeNormalizedValues, bool));
        self.entityTypes = list(entityTypes); # WE TRAVERSE THESE ASSUMING AN ORDERING ELSEWHERE<---------------------------
        self.updateMagnitudeWeight = updateMagnitudeWeight;
        self.updateOnNegative = updateOnNegative;
        self.updateOnPostive = updateOnPostive;
        self.concensusClusterViaIntersectingClusters = concensusClusterViaIntersectingClusters;
        self.featurizationAndTakeMagnitude = featurizationAndTakeMagnitude;
        self.featurizationAndTakeNormalizedValues = featurizationAndTakeNormalizedValues;
        self.lengthOfFeatureVectors = len(self.entityTypes) + 1;
        self.weightVector = self.lengthOfFeatureVectors * [initialValue];
        if(specailValueForMagnitude != None):
            maxMagnitudeOfTieStrengthVector = math.sqrt(float(len(self.entityTypes)));
            self.weightVector[-1] = specailValueForMagnitude * maxMagnitudeOfTieStrengthVector; 
        return;

    def updateWeightVector(self, inputDict, predictedLabel, groundTruthLabel):
        return;


    def calculateScore(self, inputDict):
        featurizedInput = self.featurize(inputDict);
        return self.dotProduct(featurizedInput, self.weightVector);


    def pairwiseJoinVectors(self, vectorA, vectorB, operatorToUse):
        # requires(isinstance(vectorA , list));
        # requires(isinstance(vectorB , list));
        # requires(len(vectorA) == len(vectorB));
        return [  operatorToUse(float(x[0]), float(x[1])) for x in zip(vectorA , vectorB)];

    def sumVectors(self, vectorA, vectorB):
        return self.pairwiseJoinVectors(vectorA, vectorB, operator.add);

    def subtractVectors(self, vectorA, vectorB):
        return self.pairwiseJoinVectors(vectorA, vectorB, operator.sub);

    def dotProduct(self, vectorA, vectorB):
        # requires(isinstance(vectorA , list));
        # requires(isinstance(vectorB , list));
        # requires(len(vectorA) == len(vectorB));
        pairwiseProductVector = self.pairwiseJoinVectors(vectorA, vectorB, operator.mul);
        # assert(len(pairwiseProductVector) == len(vectorA));
        return sum(pairwiseProductVector);


    def myAll(self, thisIterable):
        return not any([(not x) for x in thisIterable]);


