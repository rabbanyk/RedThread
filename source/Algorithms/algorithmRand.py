from dataAccessor import *;
from contracts import *;
from labelNames import *;
from algorithmBaseClass import *;
import random;

class AlgorithmRand(AlgorithmBaseClass):    


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



    def __init__(self, dataObj, writterObj, inputString):
        super(AlgorithmRand, self).__init__(dataObj, writterObj, inputString);
        self.perNodeAttributeDictionary = dataObj.entityToTypeDict;
        self.targetEntityType = None;
        self.nodesToSelectFrom = None;
        self.refToWritterObj = writterObj;
        return;
          
    # we look to find the ground-truth clusters across one fixed entity type, which is 
    #    determined by the entity type of the first seednode provided.
    def setSeedNode(self, providedSeedNode):
        # assert(self.targetEntityType == None or (self.targetEntityType in self.entityTypes));
        assert(providedSeedNode in self.perNodeAttributeDictionary);
        requires(self.targetEntityType == None or \
            (self.perNodeAttributeDictionary[providedSeedNode] == self.targetEntityType));
        super(AlgorithmRand, self).setSeedNode(providedSeedNode);
        self.targetEntityType = self.perNodeAttributeDictionary[providedSeedNode];
        ensures(self.seedNode != None);
        self.nodesToSelectFrom = [x for x in self.perNodeAttributeDictionary if self.perNodeAttributeDictionary[x] == self.targetEntityType];
        assert(len(self.nodesToSelectFrom) > 0); # at a minimum, the seed node exists in the nodesToSelectFrom...
        return;

    def getNextNode(self):
        requires(self.seedNodeIsSet());
        assert(self.nodesToSelectFrom != None); # this is something that should follow as a result of the requires, not 
            # an additional condition that the user has to ensure...
        assert(len(self.nodesToSelectFrom) > 0);
        # randomly provide a node
        nodeToReturn = random.choice(self.nodesToSelectFrom);
        assert(isinstance(nodeToReturn , str));
        return nodeToReturn;


    def inputFeedback(self, nodeConsidered, label, learnFromExample=True):
        super(AlgorithmRand, self).inputFeedback(nodeConsidered, label);
        return;
     
     



