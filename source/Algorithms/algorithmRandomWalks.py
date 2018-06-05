from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmBaseClass import *;
from numpy.random import choice as randChoice;

class AlgorithmRandomWalk(AlgorithmBaseClass):


    def parseInputParameters(self, inputString):
        dictOfValuesFromString = self.helper_parseInputParameters_convertStringToDict(inputString);

        # checking values
        # whole dictionary is in the right form
        assert(set(dictOfValuesFromString.keys()) == \
            {"degreeCutoffForNeighborsToExpand", "onNegativeFeednbackGoToSeedNode", \
             "walkOverRevisitedPositives", "noRepeat", "queueSize"});
        assert(all([isinstance(x, float) for x in dictOfValuesFromString.values()]));
        # queueSize is proper
        assert( dictOfValuesFromString["queueSize"] % 1 == 0.0 ); # this is an assert and not a requires since it come from something we derive after 
            # manipulating the input... This, by the way, basically checks that the queue size is an integer.
        assert( dictOfValuesFromString["queueSize"] > 0 );
        # onNegativeFeednbackGoToSeedNode is proper
        assert( dictOfValuesFromString["onNegativeFeednbackGoToSeedNode"] in {1.0, 0.0} ); # binary values for boolean variable
        # walkOverRevisitedPositives is proper
        assert( dictOfValuesFromString["walkOverRevisitedPositives"] in {1.0, 0.0} ); # binary values for boolean variable
        # noRepeat is proper
        assert( dictOfValuesFromString["noRepeat"] in {1.0, 0.0} ); # binary values for boolean variable
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
        self.onNegativeFeednbackGoToSeedNode= (dictOfValuesFromString["onNegativeFeednbackGoToSeedNode"] == 1.0);
        self.walkOverRevisitedPositives= (dictOfValuesFromString["walkOverRevisitedPositives"] == 1.0);
        self.noRepeat=(dictOfValuesFromString["noRepeat"] == 1.0);

        # degreeCutoffForNeighborsToExpand is proper
        assert( isinstance(self.degreeCutoffForNeighborsToExpand, int) or (self.degreeCutoffForNeighborsToExpand == float("Inf")));
        assert( self.degreeCutoffForNeighborsToExpand > 0 );
        # onNegativeFeednbackGoToSeedNode is proper
        assert( isinstance(self.onNegativeFeednbackGoToSeedNode, bool) );
        # walkOverRevisitedPositives is proper
        assert( isinstance(self.walkOverRevisitedPositives, bool) );
        # noRepeat is proper
        assert( isinstance(self.noRepeat, bool) );

        return;

    def __init__(self, dataObj, writterObj, parameterString):
        # TODO: check, perhaps by using inspect.Signature, that nodeSelectionFunction takes
        # one argument other than self.... or something....
        super(AlgorithmRandomWalk, self).__init__(dataObj, writterObj, parameterString);
        self.previousNode = None;
        self.ourGraph = dataObj;
        self.targetEntityType = None;
        self.nodesAlreadyGotExpertAnnotation = set();
        self.positivelyLabeledNode = set();
        return;

    def keepNode(self, thisNode):
        # Note that the fact that we use non-strict inequality below for self.ourGraph.getDegreeOfSingleNode(thisNeighborNode) >=  self.hack_degreeCutoffForNeighborsToExpand
        # matches what goes on int expansionManagerPrimitive.
        if(self.targetEntityType != None and \
           self.ourGraph.getEntityTypeOfNode(thisNode) != self.targetEntityType and \
           self.ourGraph.getDegreeOfSingleNode(thisNode) >=  self.degreeCutoffForNeighborsToExpand):
            return False;
        return True;

    def selectNeighbor(self, nodeCurrentlyOn):
        raise Exception; # classes deriving this one have to implement this. TODO: do this in 
            # a more appropraite way.
        return;


    def setSeedNode(self, providedSeedNode):
        # requires(providedSeedNode not in self.nodesFromOldClusters); # TODO
        ##############assert(self.targetEntityType == None or (self.targetEntityType in self.entityTypes));
        requires(self.targetEntityType == None or \
            (self.ourGraph.getEntityTypeOfNode(providedSeedNode) == self.targetEntityType));
        super(AlgorithmRandomWalk, self).setSeedNode(providedSeedNode);
        self.targetEntityType = self.ourGraph.getEntityTypeOfNode(providedSeedNode);
        self.previousNode = self.seedNode;
        self.nodesAlreadyGotExpertAnnotation = set({providedSeedNode});
        if(self.walkOverRevisitedPositives):
            self.positivelyLabeledNode = set({providedSeedNode});
        ensures(self.seedNode != None);
        ensures(self.previousNode != None);
        ensures(self.seedNode == self.previousNode);
        ensures(providedSeedNode in self.nodesAlreadyGotExpertAnnotation);
        return;

    def clearSeedNode(self):
        requires(self.seedNodeIsSet());
        # the below are assers as oppossed to requires since, after the users
        # ensures the above condition in the requires, the rest should follow 
        # unless there is a bug in our code...
        ### Below code is left over from other areas, but might be useful to encorporate here
        ###     later
        #### assert(len(self.nodesInCurrentCluster) > 0); # the current set of nodes should
        ####     # at least contain the seed node provided before...
        #### assert(self.seedNode in self.nodesInCurrentCluster);
        assert(self.previousNode != None);
        super(AlgorithmRandomWalk, self).clearSeedNode();
        self.previousNode = None;   
        self.nodesAlreadyGotExpertAnnotation = set();
        self.positivelyLabeledNode = set();
        return;       



    def keepOrClear_nodesAlreadyGotExpertAnnotation(self):
        if(not self.noRepeat):
            self.nodesAlreadyGotExpertAnnotation = set();
        ensures((not self.noRepeat) or (len(self.nodesAlreadyGotExpertAnnotation) > 0)); # self.nodesAlreadyGotExpertAnnotation should at 
            # least contain the seed node unless we reset it.
        return;


    def getNextNode(self):
        self.keepOrClear_nodesAlreadyGotExpertAnnotation();
        requires(self.seedNodeIsSet());
        requires(self.ourGraph.getEntityTypeOfNode(self.previousNode) == self.ourGraph.getEntityTypeOfNode(self.seedNode));
        # the below are assers as oppossed to requires since, after the users
        # ensures the above condition in the requires, the rest should follow 
        # unless there is a bug in our code...
        assert(self.previousNode != None);
        # below, neighborNodeOrSelf may be self.previousNode if self.previousNode has no neighbors...
        maximumNumberOfTimeRepeat = 100;
        selectedNeighborNeighborNodeOrSelf = None;
        selectedNeighborNodeOrSelf =  None;
        previousNodeToStartFrom = self.selectPreviousNodeToStartFrom();
        while(maximumNumberOfTimeRepeat > 0 and ( \
            (selectedNeighborNeighborNodeOrSelf in self.nodesAlreadyGotExpertAnnotation) or selectedNeighborNodeOrSelf == None)):
            maximumNumberOfTimeRepeat = maximumNumberOfTimeRepeat - 1;
            selectedNeighborNodeOrSelf = self.selectNeighbor(previousNodeToStartFrom);
            assert(self.ourGraph.getEntityTypeOfNode(selectedNeighborNodeOrSelf) != self.ourGraph.getEntityTypeOfNode(self.seedNode) or \
                selectedNeighborNodeOrSelf == previousNodeToStartFrom);
            selectedNeighborNeighborNodeOrSelf = self.selectNeighbor(selectedNeighborNodeOrSelf);
            assert(self.ourGraph.getEntityTypeOfNode(selectedNeighborNeighborNodeOrSelf) == self.ourGraph.getEntityTypeOfNode(self.seedNode) or \
                selectedNeighborNeighborNodeOrSelf == selectedNeighborNodeOrSelf);
            if(self.walkOverRevisitedPositives and (selectedNeighborNeighborNodeOrSelf in self.positivelyLabeledNode)):
                previousNodeToStartFrom = selectedNeighborNeighborNodeOrSelf; # Note that we only let the random walk stay on a previously labeled
                    # node if it was previously labeled positive.
        # Below can happen when we have already seen all the neighbors.... see the selectNeighbor function in AlgorithmSimpleRandomWalkNoRepeat
        assert(selectedNeighborNeighborNodeOrSelf != None);
        assert(selectedNeighborNodeOrSelf != None);
        assert(isinstance(selectedNeighborNeighborNodeOrSelf, str));
        assert(isinstance(selectedNeighborNodeOrSelf, str));
        if(selectedNeighborNeighborNodeOrSelf == selectedNeighborNodeOrSelf): # TODO: record when this happens and do more robust cornedr-case handling.
            self.previousNode = self.seedNode;
            return self.seedNode;
        else:
            self.previousNode = selectedNeighborNeighborNodeOrSelf;
            return selectedNeighborNeighborNodeOrSelf;


    def inputFeedback(self, nodeConsidered, label, learnFromExample=True):
        super(AlgorithmRandomWalk, self).inputFeedback(nodeConsidered, label);
        if(self.onNegativeFeednbackGoToSeedNode and (label == negativeLabel)):
            self.previousNode = self.seedNode;
        if(learnFromExample and (label == positiveLabel) and self.walkOverRevisitedPositives):
            self.positivelyLabeledNode = self.positivelyLabeledNode.union([nodeConsidered]);
        self.nodesAlreadyGotExpertAnnotation = \
            self.nodesAlreadyGotExpertAnnotation.union({nodeConsidered});
        return;


    def selectPreviousNodeToStartFrom(self):
        return self.previousNode;

class AlgorithmSimpleRandomWalk(AlgorithmRandomWalk):
    
    def selectNeighbor(self, nodeCurrentlyOn):
        neighborNodes= self.ourGraph.getNeighbors(nodeCurrentlyOn);
        while(len(neighborNodes) > 0): # TODO: make sure this does not mutate the underlying graph....
            nodeToReturn =  randChoice(neighborNodes);
            if(not self.keepNode(nodeToReturn)):
                neighborNodes.remove(nodeToReturn);           
            else:
                return nodeToReturn;
        return nodeCurrentlyOn;


class AlgorithmWeightedRandomWalk(AlgorithmRandomWalk):

    def selectNeighbor(self, nodeCurrentlyOn):
        self.keepOrClear_nodesAlreadyGotExpertAnnotation();

        if(self.ourGraph.getEntityTypeOfNode(nodeCurrentlyOn) !=  self.targetEntityType):
            return self.selectNeighbor_simple(nodeCurrentlyOn);

        neighborNodes = set(self.ourGraph.getNeighbors(nodeCurrentlyOn));
        neighborNodes = list(neighborNodes.difference(self.nodesAlreadyGotExpertAnnotation));
        # NOTE: the below line is the only difference between this function and the 
        #     selectNeighbor function in AlgorithmWeightedRandomWalkNoRepeat
        ## neighborNodes = list(neighborNodes.difference(self.nodesAlreadyGotExpertAnnotation));
        if(len(neighborNodes) > 0):
            degreesOfNeighbors_initial = self.ourGraph.getDegreesNetworkxStyle(neighborNodes);
 
            #V~V~V~V~VV~V~~VV~V~VV~VV~~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~VV~V~
            # filtering out neighbors with too large a degree. Note that, in principle, this could be
            # done without forming a new dictionary simply by changing thier probabilities to zero...
            #--------------------------------------------------------------------------------------
            degreesOfNeighbors = {};
            neighborNodes =[];
            for thisKey in degreesOfNeighbors_initial:
                # note that use of strict less-than below matches the cutoff-criteria elsewhere....
                if(degreesOfNeighbors_initial[thisKey] < self.degreeCutoffForNeighborsToExpand):
                    neighborNodes.append(thisKey);
                    degreesOfNeighbors[thisKey] = degreesOfNeighbors_initial[thisKey];
            if(len(neighborNodes) == 0):
                return nodeCurrentlyOn;
            #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^
                    
            # [assert(x > 0) for x in degreesOfNeighbors.values()] # a bit hacky...
            probabilityOfSelectingNeighbor = (len(neighborNodes)) * [0];
            for index in range(0, len(neighborNodes)):
                assert(neighborNodes[index] in degreesOfNeighbors);
                assert(degreesOfNeighbors[neighborNodes[index]] >= 1); # since the nodes under consideration 
                    # are neighbors of the one currently on, they all must have an edge leading to
                    # nodeCurrentlyOn, at least.
                # assert(degreesOfNeighbors[neighborNodes[index]] <= totalDegreeOfNeighbors);
                probabilityOfSelectingNeighbor[index] = 1/ float(degreesOfNeighbors[neighborNodes[index]]);
                assert(probabilityOfSelectingNeighbor[index] > 0);
            totalInverseDegreeOfNeighbors = sum(probabilityOfSelectingNeighbor);
            assert(totalInverseDegreeOfNeighbors > 0);
            assert(totalInverseDegreeOfNeighbors > max(probabilityOfSelectingNeighbor) or len(neighborNodes) == 1); # recall that each entry in
                # probabilityOfSelectingNeighbor is postive.
            probabilityOfSelectingNeighbor = [x / totalInverseDegreeOfNeighbors for x in probabilityOfSelectingNeighbor];
            assert(min(probabilityOfSelectingNeighbor) >= 0);
            assert(max(probabilityOfSelectingNeighbor) <= 1);
            errorTolerance = 0.001;
            assert(abs(sum(probabilityOfSelectingNeighbor) - 1)  <= errorTolerance);
            return (randChoice(neighborNodes, 1, probabilityOfSelectingNeighbor))[0];
        else:
            return nodeCurrentlyOn;

    def selectNeighbor_simple(self, nodeCurrentlyOn): # copied from simple random walk....
        assert(self.ourGraph.getEntityTypeOfNode(nodeCurrentlyOn) !=  self.targetEntityType);
        assert(self.keepNode(nodeCurrentlyOn));
        neighborNodes = set(self.ourGraph.getNeighbors(nodeCurrentlyOn));
        neighborNodes = list(neighborNodes.difference(self.nodesAlreadyGotExpertAnnotation));
        if(len(neighborNodes) > 0):
            nodeToReturn =  randChoice(neighborNodes);        
            return nodeToReturn;
        else:
            # The below (commented out with ###) might be more appropraite than returning nodeCurrentlyOn...
            #     but I seem to recall other parts of the code using returning nodeCurrentlyOn as an indicator of failure....
            #     uh... TODO: more robust failure handling, geez.
            ### # Note, below, in the case where len(neighborNodes.difference(self.nodesAlreadyGotExpertAnnotation)) == 0,
            ### #     self.nodesAlreadyGotExpertAnnotation == neighborNodes, so wwe don't need to recalculater anything...
            ### return randChoice(list(self.nodesAlreadyGotExpertAnnotation));
            return nodeCurrentlyOn;



