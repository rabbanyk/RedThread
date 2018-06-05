from Algorithms.algorithmRandomWalks import AlgorithmSimpleRandomWalk, AlgorithmWeightedRandomWalk;
from Algorithms.algorithmRedThreadWithoutFeedback import AlgorithmRedThreadWithoutFeedback;
from Algorithms.algorithmRedThreadWithoutEvidenceWeights import AlgorithmRedThreadWithoutEvidenceWeights;
from Algorithms.algorithmRedThread import AlgorithmRedThread;
from Algorithms.algorithmRand import AlgorithmRand;
from Algorithms.algorithmRedThreadWithoutModalityParameters import AlgorithmRedThreadWithoutModalityParameters;
from Algorithms.algorithmRedThreadWithoutParameters import AlgorithmRedThreadWithoutParameters;

from mainTestFrameworks.mainTestFramework_memeDisc import memeDisc_mainTestFramework_helper;
from getPathToThisDirectory import *;
from dataAccessor import * ;
from contracts import * ;

from getStringTimeNow import *;
import labelNames;
import random;
import sys;






def getRunScriptParameters():
    

    datasetsToUseDict = {\
        "memeTracker" : getPathToThisDirectory() +  "../publicDatasets/memetracker/", \
        "discogs" : getPathToThisDirectory() + "../publicDatasets/discogs/" \
    };



    algorithmNameToFunctionDict = {\
        "AlgorithmRandom" : AlgorithmRand, \
        "AlgorithmSimpleRandomWalk" : AlgorithmSimpleRandomWalk, \
        "AlgorithmWeightedRandomWalk" : AlgorithmWeightedRandomWalk, \
        "AlgorithmRedThreadWithoutFeedback" : AlgorithmRedThreadWithoutFeedback, \
        "AlgorithmRedThreadWithoutEvidenceWeights" : AlgorithmRedThreadWithoutEvidenceWeights, \
        "AlgorithmRedThread" : AlgorithmRedThread, \
        "AlgorithmRedThreadWithoutModalityParameters" : AlgorithmRedThreadWithoutModalityParameters, \
        "AlgorithmRedThreadWithoutParameters" : AlgorithmRedThreadWithoutParameters \
    };


    dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath = {\
        "memeTracker" : \
            {"normal" : datasetsToUseDict["memeTracker"] + "seedNodes.csv"}, \
        "discogs" : \
            {"normal" : datasetsToUseDict["discogs"] + "seedNodes.csv"} \
   };


    return {"algorithmNameToFunctionDict" : algorithmNameToFunctionDict, \
            "datasetsToUseDict" : datasetsToUseDict, \
            "dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath" : dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath};



def getRestOfAlgorithmParametersUsedInPaper():

    # the queuesize does not actually do anything for AlgorithmRand or the random walks
    #     degreeCutoffForNeighborsToExpand does not actually do anything for algorithmRand
    algorithmNameToParametersDict = {\
        "AlgorithmRandom" : "degreeCutoffForNeighborsToExpand:10000_queueSize:1000", \
        "AlgorithmSimpleRandomWalk" : "noRepeat:1.0_onNegativeFeednbackGoToSeedNode:1.0_walkOverRevisitedPositives:1.0_degreeCutoffForNeighborsToExpand:10000_queueSize:1000", \
        "AlgorithmWeightedRandomWalk" : "noRepeat:1.0_onNegativeFeednbackGoToSeedNode:1.0_walkOverRevisitedPositives:1.0_degreeCutoffForNeighborsToExpand:10000_queueSize:1000", \
        "AlgorithmRedThreadWithoutFeedback" : "degreeCutoffForNeighborsToExpand:10000", \
        "AlgorithmRedThreadWithoutEvidenceWeights" : "errorToleranceForFloatingPointComparison:0.0_randomizedNodeSelection:0.0_updateOnPositive:1.0_degreeCutoffForNeighborsToExpand:10000", \
        "AlgorithmRedThread" : "errorToleranceForFloatingPointComparison:0.0_randomizedNodeSelection:0.0_updateOnPositive:1.0_degreeCutoffForNeighborsToExpand:10000", \
        "AlgorithmRedThreadWithoutModalityParameters" : "degreeCutoffForNeighborsToExpand:10000", \
        "AlgorithmRedThreadWithoutParameters" : "concensusClusterViaIntersectingClusters:0.0_featurizationAndTakeMagnitude:0.0_featurizationAndTakeNormalizedValues:0.0_initialValue:1.0_specailValueForMagnitude:1.0_updateMagnitudeWeight:0.0_updateOnNegative:0.0_updateOnPostive:0.0_whetherOrNotToResetWithSeedNode:0.0_degreeCutoffForNeighborsToExpand:10000" \
    };
    
    return algorithmNameToParametersDict;













