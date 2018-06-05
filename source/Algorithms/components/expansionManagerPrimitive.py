from dataAccessor import *;
from contracts import *;
from labelNames import *;
from numpy.random import choice as randomChoice;
import sys
import Queue;




class ExpansionManagerPrimitive(object):

    # function: __init__
    # description: initializes instances of the ExpansionManagerPrimitive class.
    # inputs:
    #     ourGraph - an instance of dataAccessor that contains the data for the graph we want
    #         the algorithm to traverse.
    #     entityTypes - a set containing the set of entity types in the graph... #TODO: remove this
    #     seedNode - the string name of the seedNode from which the algorithm which is using
    #         this instance of ExpansionManagerPrimitive is starting. 
    #     ourScorer - the scorer that our algorithm is using. # TODO: improve this description, maybe have all scorers inherit
    #         # from a base class.....
    # Modifies object internal parameters:
    #     self.queueSize - sets the queuSize to the value passed in
    #     self.targetEntityType - sets the target entity type, determined from the seed node provided and the 
    #         graph (ourGraph) provided.
    #     self.nonTargetEntityTypes - set the non-target entity types, determined from the seed node provided and the 
    #         graph (ourGraph) provided.
    #     self.ourGraph - sets self.ourGraph to be the value provided, the input ourGraph
    #     self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength - initializes to be 
    #         a dicitionary, with a keyset of entityTypes. Ultimately, this internal variable with be a 
    #         dicitionary of dictionaries, where the first key is the entity type, and the second key is the 
    #         name of a node, the values being the tie strength through modality <first key> to node <second key>.
    #         This dictionary must maintain information for all target entities that have a length-2 path to a labeled
    #         node, regardless of whether the labebed node is positively labeled or negatively labeled. Tie strengths
    #         for unlabeled nodes as they are connected to labeled nodes through each modality are maintained in this
    #         structure - this maintains the tie-strength vectors and is our "shell".
    #     self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores - initialized to be an empty 
    #         dicitionary. Eventually, this with be a dictionary of dictionaries, where the first key is an (TODO: check - unlabeled node?)
    #         node and the second key is a non-target entity type, the values being the tie-strength between <first key>
    #         and the labeled nodes through modality <second key>. This contains only a subset of the nodes listed in 
    #         self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength, and is the primary structure
    #         responsible for maintaing our "queue" of values - the nodes that had highest scores previously have thier tie-strengths
    #         stored in this structure. When we expand, we consider each of the new nodes and each of the nodes listed in 
    #         self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores, and only keep the subset that
    #         is no larger than the queue size and has highest score - this subset is then used to fill  
    #         self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores on the next iteration.
    #     self.neighborsOfPositiveNodes - the set of target entities that are length-2-path neighbors of positive nodes.
    #         This should be a subset of the nodes listed in self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength
    #         (since self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength has to track values
    #         that result from being length-2 neighbors of any labeled nodes, whether positive or negative) and contain all
    #         nodes listed in self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores (since we only
    #         expand from positive nodes, and the queue should contain no more nodes than what we expand to).
    #     self.capDegreeOfNodesToExpand - the degree for which, if a piece of evidence has a degree a or above this value,
    #         we do not examine it. I.e., if degree(evidence) >= self.capDegreeOfNodesToExpand, we do not consider the
    #         tie strengths, etc., that it provides to its neighbors.
    def __init__(self, ourGraph, entityTypes, seedNode, ourScorer, queueSize, capDegreeOfNodesToExpand=None, \
            filterEvidenceForNodesOfType = None): # putting capDegreeOfNodesToExpand
        # as None is a hacky way of forcing users to set it and allow it to be set using explicit passing (i.e.,  
        #     ExpansionManagerPrimitive(..., capDegreeOfNodesToExpand=...)  )
        requires(isinstance(queueSize, int));
        requires(queueSize > 0);
        requires(isinstance(entityTypes, set));
        requires(isinstance(ourGraph, dataAccessor));
        requires(isinstance(seedNode, str));
        requires(len(seedNode) > 0);
        requires(seedNode in ourGraph.entityNameToIndexDict);
        # requires(len(entityTypes) >= 2); # we are working with a heterogenous graph.
        # requires(seedNode in perNodeAttributeDictionary);
        self.queueSize = queueSize; 
        self.targetEntityType = ourGraph.getEntityTypeOfNode(seedNode);
        self.nonTargetEntityTypes = entityTypes.difference({self.targetEntityType});
        # TODO: document why in the world we have the below two dictionaries and what we use them for....
        self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength = {x : {} for x in entityTypes };
        self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores = { };
        self.ourGraph = ourGraph;
        # Note, below, self.neighborsOfPositiveNodes is used in  expandSeenNodeSet, so
        # we have to declare it prior to that....
        self.neighborsOfPositiveNodes = set();
        ### self.dictOfCurrentScores = {};
        # NOTE: we have to set capDegreeOfNodesToExpand before calling self.expandSeenNodeSet
        requires(isinstance(capDegreeOfNodesToExpand, int) or (capDegreeOfNodesToExpand == float("inf")));
        self.capDegreeOfNodesToExpand = capDegreeOfNodesToExpand;

        # TODO: move the below requires further up in the code.
        requires( (filterEvidenceForNodesOfType == None) or \
                 (filterEvidenceForNodesOfType in self.nonTargetEntityTypes));
        # Note that below, we set self.filterEvidenceForNodesOfType prior to calling self.expandSeenNodeSet
        #     since self.expandSeenNodeSet depends on the value of self.filterEvidenceForNodesOfType
        self.filterEvidenceForNodesOfType = filterEvidenceForNodesOfType;

        self.labeledNodes = [];
        self.labeledNodes.append(seedNode);
        assert(seedNode == self.labeledNodes[-1]);

        self.expandSeenNodeSet(seedNode, positiveLabel, ourScorer );
        return;

    def computeWeightToAddToNeighborNeighbors(self, thisNeighborNode, nodeLabel, neighborsOfNeighbor ):
        raise Exception; # children must override this.
        return;

    def helper_primitiveExpandSeenNodeSet(self, nodeToExpand, nodeLabel):
        requires(isProperLabel(nodeLabel));

        # below is an assert instead of a requires because it should be maintained by the rest of the code,
        # and this function does not require it to be true in order to function properly....
        assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) <= \
            self.queueSize);

        neighborsOfNodeToExpand = self.ourGraph.getNeighbors(nodeToExpand);
        assert(isinstance(neighborsOfNodeToExpand , list));

        # NOTE: below, the neighbor nodes add weight to the nodes we just expanded from (since they
        #     add weigh to every node adjacent to them),
        #     but since alphaACG does not hand the analyst the same node to label twice,
        #     this is fine...
        for thisNeighborNode in neighborsOfNodeToExpand:

            if(self.ourGraph.getDegreeOfSingleNode(thisNeighborNode) >= self.capDegreeOfNodesToExpand):
                continue;

            # Below assert should hold by the bipartite-along-entity-types nature of the graphs
            # we are considering.
            entityTypeOfThisNeighborNode = self.ourGraph.getEntityTypeOfNode(thisNeighborNode);
            assert(entityTypeOfThisNeighborNode != self.targetEntityType);
            if( (self.filterEvidenceForNodesOfType != None) and \
                (entityTypeOfThisNeighborNode != self.filterEvidenceForNodesOfType) ):
                # Note that since we are working over a bipartite graph, filtering in the manner we do
                # does NOT impact any perception of the degree of immedaite relations of the evidence
                # retained.
                continue;
            assert( (self.filterEvidenceForNodesOfType == None) or \
                (entityTypeOfThisNeighborNode != self.filterEvidenceForNodesOfType));

            neighborsOfNeighbor = self.ourGraph.getNeighbors(thisNeighborNode);
            assert(isinstance(neighborsOfNeighbor , list));
            # NOTE: the below assert might be expensive, possibly....
            assert(len(neighborsOfNeighbor) > 0); # has to be true since thisNeighborNode is the neighbor, at the very least, of the
                # node we expanded from...
            assert(nodeToExpand in neighborsOfNeighbor);

            initialLengthForCheckPurposes_neighborsOfPositiveNodes = len(self.neighborsOfPositiveNodes);
            if(nodeLabel == positiveLabel):
                # TODO: rename neighborsOfPositiveNodes to convey the fact that it is actually a set of neighbor-neighbors...
                self.neighborsOfPositiveNodes = self.neighborsOfPositiveNodes.union(neighborsOfNeighbor);

            assert(  (not (nodeLabel == positiveLabel)) or \
                (len(self.neighborsOfPositiveNodes) >= initialLengthForCheckPurposes_neighborsOfPositiveNodes)  );
            assert(  (not (nodeLabel == positiveLabel)) or \
                (len(self.neighborsOfPositiveNodes) >= len(neighborsOfNeighbor))  );
            assert(  (nodeLabel == positiveLabel) or \
                (len(self.neighborsOfPositiveNodes) >= initialLengthForCheckPurposes_neighborsOfPositiveNodes)  );
            # below, note that len(neighborsOfNeighbor) == degree(thisNeighborNode), since we are dealing with a simple
            # graph. Note that degree(thisNeighborNode) > 0 since, well, it is the neighbor of another node, otherwise it would not
            # even be considered here.
            assert(len(neighborsOfNeighbor) == self.ourGraph.getDegreeOfSingleNode(thisNeighborNode));
            dictOfWeightToAddToNeighborNeighbors = self.computeWeightToAddToNeighborNeighbors( \
                thisNeighborNode, nodeLabel, neighborsOfNeighbor );  
            assert(isinstance( dictOfWeightToAddToNeighborNeighbors , dict ));
            assert(set(dictOfWeightToAddToNeighborNeighbors.keys()) == set(neighborsOfNeighbor));

            initialLengthForCheckPurposes_dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores = \
                len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores);
            initialLengthForCheckPurposes_dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength_entityTypeThisNei = \
                len(self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode]);
            for thisNeighborNeighbor in neighborsOfNeighbor:

                assert(thisNeighborNeighbor in dictOfWeightToAddToNeighborNeighbors);
                weightToAddToNeighborNeighbors = dictOfWeightToAddToNeighborNeighbors[thisNeighborNeighbor];
                assert(isinstance(weightToAddToNeighborNeighbors, float));

                # Below assert should hold by the bipartite-along-entity-types nature of the graphs
                # we are considering.
                # below we use get for a dictionary access in case the node we are examining had
                # yet to be added to the dictionary....
                # TODO: consider checking the below addition for numerical stuff, etc., etc.
                self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode][thisNeighborNeighbor] =\
                    self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode].get(thisNeighborNeighbor, 0) + \
                    weightToAddToNeighborNeighbors;
                assert( (not (nodeLabel == positiveLabel) ) or (thisNeighborNeighbor in self.neighborsOfPositiveNodes) ); # basically, if a
                    # node is positive, then it must already be in self.neighborsOfPositiveNodes by the if-statement prior to the loop...
                if( (nodeLabel == positiveLabel) or (thisNeighborNeighbor in self.neighborsOfPositiveNodes)): # note that by the assert preceeding this
                    # conditional, checking (nodeLabel == positiveLabel) is not necessary - however, it is likely more efficient than 
                    # checking (thisNeighborNeighbor in self.neighborsOfPositiveNodes) in all cases.
                    if( thisNeighborNeighbor  not in  self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores):
                        self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores[thisNeighborNeighbor] = {}; # making a ton
                            # of python dictionaires is probably an unnecessary burden on memery, given that we know the 
                            # max queue-size a priori....
                    self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores[thisNeighborNeighbor][entityTypeOfThisNeighborNode] = \
                        self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode][thisNeighborNeighbor];
                assert(thisNeighborNeighbor in self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode]);
                assert(  (not (nodeLabel == positiveLabel) ) or \
                    (thisNeighborNeighbor in self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores));
            assert(len(self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[entityTypeOfThisNeighborNode]) >= \
                len(neighborsOfNeighbor));
            assert( \
                sum([len(self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength[x]) for x in self.nonTargetEntityTypes]) >= \
                len(self.neighborsOfPositiveNodes) );
            assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) >= \
                initialLengthForCheckPurposes_dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores);
            # A node that is new to self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores
            #    might not be new to self.neighborsOfPositiveNodes (because it was found when expanding another modality), hence we have 
            #    non-strict inequality, not equality.... 
            assert(\
                (    len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) - \
                     initialLengthForCheckPurposes_dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores   ) >= \
                (    len(self.neighborsOfPositiveNodes) - initialLengthForCheckPurposes_neighborsOfPositiveNodes) \
            );
        assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) <= len(self.neighborsOfPositiveNodes));
        # below assert might be expensive in general.
        assert(set(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores.keys()).issubset(self.neighborsOfPositiveNodes));
        return;

    # the below function depends on two internal variables: the queuSize and self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength
    def helper_filterDictionaryEntityTypeToDictsMappingNodesToWeight(self, scorer):
        if(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) > self.queueSize):
            ourPriorityQueue = Queue.PriorityQueue();
            # self.dictOfCurrentScores = {};
            assert(ourPriorityQueue.qsize() == 0);
            for thisNode in self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores:
                # note carefully in calling getWeightOfNode below that we had just called helper_primitiveExpandSeenNodeSet, which 
                # filled self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores with entries from 
                # self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength for all the nodes whose entries were updated.
                # Further, note that thisNode is in getWeightOfNode. We mention this since getWeightOfNode is uses dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores
                # to find the weight, not self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength....
                scoreOfThisNode = scorer.calculateScore(self.getWeightOfNode(thisNode));
                ourPriorityQueue.put((scoreOfThisNode, thisNode));
            assert(ourPriorityQueue.qsize() == len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores));
            lastSeenValueForCheckPurposes = None;

            # removing nodes that we already have labels so to leave room in the queue for
            # nodes we have set to consider. Note that, since the query budget is 
            # limited - and even with the high confidence matcher for there to be a small
            # number of nodes returned by the algorithm compared to the size of the graph -
            # we expect this loop to have few iterations.
            checkVariable_numberNodesLabeledBefore = 0;
            for thisNodeAlreadyLabeled in self.labeledNodes :
                thisNodeOrNone = self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores.pop(thisNodeAlreadyLabeled , None);
                if(thisNodeOrNone != None):
                    assert(checkVariable_numberNodesLabeledBefore + 1 > checkVariable_numberNodesLabeledBefore); # weak check for overflow -
                        # almost certainly unnecessary, but good practice to do...
                    checkVariable_numberNodesLabeledBefore = checkVariable_numberNodesLabeledBefore + 1;

            assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) == \
                   ourPriorityQueue.qsize() - checkVariable_numberNodesLabeledBefore);

            checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore = 0;
            while(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) > self.queueSize):
                # The first assert below should hold since we fill the priority queue with one duple for each key-value pair in
                #      self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores, then, for each item we pop 
                #      from ourPriorityQueue, we remove one item from self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores
                assert( ourPriorityQueue.qsize() - \
                    len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) <= \
                    checkVariable_numberNodesLabeledBefore ); # the < handles the cases where the queue
                    # removes a node that was previously labeled.
                assert( ourPriorityQueue.qsize() - \
                    len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) == \
                    checkVariable_numberNodesLabeledBefore - checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore ); 
                assert(ourPriorityQueue.qsize() > self.queueSize);

                valueKeyPairFromPriorityQueue = ourPriorityQueue.get();
                assert(len(valueKeyPairFromPriorityQueue) == 2);
                # # the priority queue should return keys in increasing-value order, so we get the elements
                # # with lowest priority number first, as checked below.
                # assert(lastSeenValueForCheckPurposes == None or \
                #     valueKeyPairFromPriorityQueue[0] >= lastSeenValueForCheckPurposes);
                lastSeenValueForCheckPurposes = valueKeyPairFromPriorityQueue[0];
                keyFromPriorityQueue = valueKeyPairFromPriorityQueue[1];
                # valueReturnedForCheckPurposes should never be the default value, None -it should
                # contain the dictionary previously stored under  keyFromPriorityQueue in the dictionary
                # self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength ...
                valueReturnedForCheckPurposes = \
                    self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores.pop(keyFromPriorityQueue, None);
                if(valueReturnedForCheckPurposes == None):
                    assert(checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore + 1 > \
                           checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore); # weak overflow check.
                    checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore = \
                        checkVariable_countOfQueueRemovingMembersOfNodesLabeledBefore + 1;
                
                assert(valueReturnedForCheckPurposes != None or (keyFromPriorityQueue in self.labeledNodes ) ); # note that 
                    # the ordering of the disjuncts here is more efficient than the alternative due to short circuit evaulation.
            assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) == self.queueSize or \
                (\
                    ( len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) < self.queueSize  ) and \
                    ( len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) + checkVariable_numberNodesLabeledBefore > \
                      self.queueSize\
                    )
                )\
            );
            assert( ( ourPriorityQueue.qsize() == self.queueSize ) or \
                (\
                    ( ourPriorityQueue.qsize() > self.queueSize  ) and \
                    ( ourPriorityQueue.qsize() - checkVariable_numberNodesLabeledBefore <= self.queueSize) \
                ) \
            );
        assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) <= self.queueSize);
        # assert(set(self.dictOfCurrentScores.keys()).issuperset(set(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores.keys())) ); # expensive, remove later....
        return; 


    def expandSeenNodeSet(self, nodeToExpand, nodeLabel, scorer):
        requires(isProperLabel(nodeLabel));

        self.labeledNodes.append(nodeToExpand);
        assert(nodeToExpand == self.labeledNodes[-1]);

        initialLengthForCheckPurposes_dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength = \
            len(self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength);
        self.helper_primitiveExpandSeenNodeSet(nodeToExpand, nodeLabel);
        self.helper_filterDictionaryEntityTypeToDictsMappingNodesToWeight(scorer); 
        assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores) <= self.queueSize);
        assert( nodeLabel == positiveLabel or \
             (nodeLabel == negativeLabel and (\
                  initialLengthForCheckPurposes_dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength == \
                  len(self.dictsMappingEntityTypeToDictsMappingNodesToWeight_usedToMaintainTieStrength)    ) \
             )    );

        return;


    # TODO: change names from "weight" to "tie strength".
    def getWeightOfNode(self, nodeToConsider):
        entityTypeToWeightDict = {};
        if(nodeToConsider in self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores):
            assert(len(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores[nodeToConsider]) <= \
                len(self.nonTargetEntityTypes));
            for thisEntityType in self.nonTargetEntityTypes:
                entityTypeToWeightDict[thisEntityType] = \
                    self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores[nodeToConsider].get(thisEntityType, 0.0);
        else: # strictly speaking, unnecessary, but nice to provide uniform format (unnecessary in the sense that the
            # rest of the code does not depend on this being the case....
            raise Exception();
            entityTypeToWeightDict = {thisEntityType : 0.0 for thisEntityType in self.nonTargetEntityTypes};
        assert(len(self.nonTargetEntityTypes) == len(entityTypeToWeightDict));
        assert(set(entityTypeToWeightDict.keys()) == self.nonTargetEntityTypes);
        return entityTypeToWeightDict;

    def getCurrentSetOfSeenNodes(self):
        print "\n" + self.__class__.__name__ + ":" + inspect.stack()[0][3] + ":" +\
            "This Function is no longer supported\n";
        raise Exception;
        return;

    def getPathLength2NeighborsOfPositiveNodes(self):
        # we only want functions to compute scores across things we have kept in the queue. ...
        # the below implementation unfortunately creates a new python set each time..... could use views...
        return set(self.dictsMappingNodesToDictsMappingEntityTypeToWeights_usedToCalculateScores.keys());

