import sys;
# see if I need to import the dataAccessor...


class NearDuplicateFilter():

    def requires(self, booleanCondition):
        assert(booleanCondition);

    def ensures(self, booleanCondition):
        assert(booleanCondition);
    

    def __init__(self, dataAccessor):
        self.dataAccessor = dataAccessor;
        self.listOfClusterMemberFeatures = [];        
        self.thresholdForDuplicateText = 0.95;
        return;


    """
    # Below is the dictionary mapping the entity type number to what it is suppose to correspond to.
    dictMappingEntityTypeToNumber = { \
        phoneNumberEntityLabel: 1, \
        personEntityLabel : 2,\
        imageEntityLabel : 3, \
        advertisementEntityLabel : 4, \
        unigramsBodyEntityLabel : 5, \
        bigramsBodyEntityLabel : 6, \
        unigramsTitleEntityLabel : 7, \
        bigramsTitleEntityLabel : 8, \
        urlEntityLabel : 9, \
        perspectiveEntityLabel : 10, \
        emailEntityLabel : 11, \
        dateEntityLabel : 12, \
        locationEntityLabel : 13 \
        };
    """



    def getFeaturesForNode(self, thisNodeID):
        # dictToReturn = {"images" : set(), "bigrams" : set(), "names" : set()};
        neighborsOfThisNode = self.dataAccessor.getNeighbors(thisNodeID);
        entityTypeOfTitleBigrams = '8';
        entityTypeOfBodyBigram = '6';
        entityTypeOfImages = '3';
        entityTypeOfNames = '2';
        assert(len(set([entityTypeOfTitleBigrams, entityTypeOfBodyBigram, \
                        entityTypeOfImages, entityTypeOfNames])) == 4); # i.e., each of the entity types specified above are unique...
        assert(len(entityTypeOfTitleBigrams) > 0);
        assert(len(entityTypeOfBodyBigram) > 0);
        assert(len(entityTypeOfImages) > 0);
        assert(len(entityTypeOfNames) > 0);
        tempList_images = [];
        tempList_bigrams = [];
        tempList_names = [];
        for thisNeighbor in neighborsOfThisNode:
            neighborNodeType = self.dataAccessor.getEntityTypeOfNode(thisNeighbor);
            assert(isinstance(neighborNodeType, str));
            assert(neighborNodeType in {'1', '2', '3', '4', '5', '6', '7', \
                                        '8', '9', '10', '11', '12', '13'});
            if(neighborNodeType == entityTypeOfNames):
                tempList_names.append(thisNeighbor);
            elif(neighborNodeType == entityTypeOfImages):
                tempList_images.append(thisNeighbor);
            elif(neighborNodeType == entityTypeOfTitleBigrams or neighborNodeType == entityTypeOfBodyBigram):
                tempList_bigrams.append(thisNeighbor);
        dictToReturn = {"images"  : set(tempList_images), \
                        "bigrams" : set(tempList_bigrams), \
                        "names"   : set(tempList_names)};
        return dictToReturn;


    def addToCluster(self, thisNodeID):
        self.listOfClusterMemberFeatures.append(self.getFeaturesForNode(thisNodeID));
        assert(len(self.listOfClusterMemberFeatures) > 0);
        return;

    def clearCluster(self):
        self.listOfClusterMemberFeatures = [];
        return;

    def calculateJaccardScore(self, setA, setB):
        self.requires(isinstance(setA, set));
        self.requires(isinstance(setB, set));
        sizeOfIntersectionOfSets = len(setA.intersection(setB));
        assert(sizeOfIntersectionOfSets <= len(setA));
        assert(sizeOfIntersectionOfSets <= len(setB));
        assert(sizeOfIntersectionOfSets >= 0);
        if(len(setA) == 0 or len(setB) == 0):
            return 0.0;
        jaccardScore = float(sizeOfIntersectionOfSets) / float(len(setA) + len(setB) - sizeOfIntersectionOfSets );
        assert(jaccardScore >= 0.0 and jaccardScore <= 1.0);
        return jaccardScore;


    def testIfPairOfDuplicates(self, featuresForNodeA, featuresForNodeB):
        self.requires(isinstance(featuresForNodeA, dict));
        self.requires(len(featuresForNodeA) == 3);
        self.requires(isinstance(featuresForNodeB, dict));
        self.requires(len(featuresForNodeB) == 3);

        if( featuresForNodeA["names"] != featuresForNodeB["names"]):
            return False;
        
        intersectionOfImages = featuresForNodeA["images"].intersection(featuresForNodeB["images"]);
        if(len(intersectionOfImages) == 0 and (len(featuresForNodeA["images"]) > 0 or len(featuresForNodeB["images"]) > 0) ):
            return False;

        jaccardScore = self.calculateJaccardScore(featuresForNodeA["bigrams"] , featuresForNodeB["bigrams"]);
        if(jaccardScore < self.thresholdForDuplicateText):
            return False;

        return True;


    def testForNearDuplicate(self, thisNodeID):
        featuresForThisNode = self.getFeaturesForNode(thisNodeID);
        for thisFeatureSetOfNodeInCluster in self.listOfClusterMemberFeatures:
            assert(isinstance(thisFeatureSetOfNodeInCluster, dict));
            if( self.testIfPairOfDuplicates(thisFeatureSetOfNodeInCluster, featuresForThisNode) ):
                return True;
        return False;

        





