from dataAccessor import *;
from contracts import *;
from labelNames import *;
from numpy.random import choice as randomChoice;
from Algorithms.components.expansionManagerPrimitive import ExpansionManagerPrimitive;
from Algorithms.components.scorers import BaseScorer;
import sys


class ExpansionManagerAlphaACG(ExpansionManagerPrimitive):
 
    def computeWeightToAddToNeighborNeighbors(self, thisNeighborNode, nodeLabel, neighborsOfNeighbor ):
        requires(isinstance(thisNeighborNode, str));
        requires(nodeLabel == positiveLabel);
        requires(len(neighborsOfNeighbor) > 0);
        valueToGiveEachNeighborNeighbor =  (1.0/ float(len(neighborsOfNeighbor)))**2;
        return {x : valueToGiveEachNeighborNeighbor for x in neighborsOfNeighbor};

    def expandSeenNodeSet(self, nodeToExpand, nodeLabel, scorer):
        requires(isinstance(scorer, BaseScorer));
        requires(isProperLabel(nodeLabel));
        requires(isinstance(nodeToExpand, str));

        if(nodeLabel != positiveLabel):
            return;
        assert(nodeLabel == positiveLabel);
        super(ExpansionManagerAlphaACG, self).expandSeenNodeSet(nodeToExpand, nodeLabel, scorer);
        return;


class ExpansionManagerForRedThreadWithoutModalityParameters(ExpansionManagerPrimitive):

    def computeWeightToAddToNeighborNeighbors(self, thisNeighborNode, nodeLabel, neighborsOfNeighbor ):
        requires(isProperLabel(nodeLabel));
        requires(isinstance(thisNeighborNode, str));
        requires(len(neighborsOfNeighbor) > 0);

        weightToAddToNeighborNeighbors = (1.0/ float(len(neighborsOfNeighbor)))**2;
        if(nodeLabel == negativeLabel):
            weightToAddToNeighborNeighbors = -weightToAddToNeighborNeighbors;
        return {x : weightToAddToNeighborNeighbors  for x in neighborsOfNeighbor};



