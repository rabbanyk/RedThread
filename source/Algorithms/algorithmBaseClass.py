from dataAccessor import *;
from contracts import *;
from labelNames import *;
import random;
import re;
from SQLResultWrittingCode.sqlResultWritter import SQLNullValue;
from safeIncrement import safeIncrement;

class AlgorithmBaseClass(object):

    def readParameterString(self, parameterString):
        raise Exception(); # child classes must overwrite this.

    def recordState_helper(self):
        raise Exception(); # child classes must overwrite this.

    def recordState(self):
        requires(self.stateCounter >= 0);
        requires(self.refToWritterObj != None);
        # Note that self.stateCounter serves to group together all the parameters that were set
        #     together at the same time in an algorithm together. For example, if an algorithm has
        #     internal parameters A, B, and C which it changes internally, then we might record thier 
        #     values as:
        #         1,A,<value A in state 1>
        #         1,B,<value B in state 1>
        #         1,C,<value C in state 1>
        #         2,A,<value A in state 2>
        #         2,B,<value B in state 2>
        #         2,C,<value C in state 2>
        #         etc.
        if(self.stateCounter == 0): # all the algorithms, regardless of whether they have interesting internal parameters
            # to record, will have at least this one dummy entry in the algorithmInternalParameters table.
            self.refToWritterObj.writeToTable("algorithmInternalParameters", \
                {"stateNumber" : str(self.stateCounter), "categoryOfParameter" : SQLNullValue(), \
                 "specificParameterName" : SQLNullValue(), "parameterValue" : SQLNullValue()});
        else:
            assert(self.stateCounter > 0);
            listOfDictionariesReturned = self.recordState_helper();
            assert(isinstance(listOfDictionariesReturned, list));
            assert(len(listOfDictionariesReturned) > 0); 
            for thisDictionary in listOfDictionariesReturned:
                assert(isinstance(thisDictionary, dict));
                assert(set(thisDictionary.keys()) == {"categoryOfParameter", "specificParameterName", "parameterValue"});
                self.refToWritterObj.writeToTable("algorithmInternalParameters", \
                    {"stateNumber" : str(self.stateCounter), \
                     "categoryOfParameter" : thisDictionary["categoryOfParameter"], \
                     "specificParameterName" : thisDictionary["specificParameterName"],\
                     "parameterValue" : thisDictionary["parameterValue"]});
        self.stateCounter = safeIncrement(self.stateCounter);
        ensures(self.stateCounter > 0);
        return;

    def __init__(self, dataObj, writterObj, parameterString):
        # TODO: check all the inputs again...
        requires(isinstance(dataObj , dataAccessor));
        requires(isinstance(parameterString, str));
        self.refToDataObj = dataObj;
        self.refToWritterObj = writterObj;
        self.seedNode = None;
        self.parseInputParameters(parameterString);
        self.stateCounter = 0;
        self.recordState();
        return;

    def helper_parseInputParameters_convertStringToDict(self, runningParameterString):
        requires(isinstance(runningParameterString, str));
        requires(runningParameterString.count("__") == 0); # double empty scores would produce empty parameter specification strings
        requires(self.refToWritterObj != None);

        # which would screw things up below.....
        # ([a-zA-Z][a-zA-Z0-9]*:[0-9][0-9]*\.?[0-9]*)
        # ^[a-zA-Z][a-zA-Z0-9]*:[0-9][0-9]*\.?[0-9]*$
        parameterDelimitor = "_";
        keyValueDelimitor = ":";
        splitRunningParameters = runningParameterString.split(parameterDelimitor);
        dictToReturn = {};
        assert(  (len(splitRunningParameters) > 0)  or  (len(runningParameterString) == 0) );
        for thisKeyValuePairAsString in splitRunningParameters:
            # below assert checks that thisKeyValuePairAsString is a string where prior to the occurance of ":"
            #     is an alphanumeric string starting with a letter and after the ":" is a numeric string that can 
            #     have at most one occurance of a period-mark, which must occur (if it occurs) after the first numeric digit, and
            #     may have a leading negative sign.
            assert(re.match("^[a-zA-Z][a-zA-Z0-9]*:-?[0-9][0-9]*\.?[0-9]*$"  ,\
                thisKeyValuePairAsString) != None); # unfortunately, we do not have sufficiant checks ealier in this function to make this 
                # a requires.
            thisKeyValuePairStringsSplit = thisKeyValuePairAsString.split(keyValueDelimitor);
            thisKeyString = thisKeyValuePairStringsSplit[0];
            assert(re.match("^[a-zA-Z][a-zA-Z0-9]*$", thisKeyString) != None);
            thisValueString = thisKeyValuePairStringsSplit[1];
            assert(re.match("^-?[0-9][0-9]*\.?[0-9]*$", thisValueString) != None);
            dictToReturn[thisKeyString] = float(thisValueString);

            # Why, below, do we put str(dictToReturn[thisKeyString]) and not just thisValueString? We do that 
            #     so that strings that represent the same floating point value get mapped to the same string. 
            #     For example, if the user enters 1.00 and 1.0, we want both to be represented by the same string,
            #     preferable the shortest one with the same value, here 1.0 .
            assert(float(str(dictToReturn[thisKeyString])) == float(thisValueString));
            self.refToWritterObj.writeToTable("algorithmRunParameters", \
                {"parameterName" : thisKeyString, "parameterValue" : str(dictToReturn[thisKeyString])});

        return dictToReturn;
    
    

    def seedNodeIsSet(self):
        return self.seedNode != None;

    def clearSeedNode(self):
        self.seedNode = None;
        ensures(not self.seedNodeIsSet());
        return;

    def setSeedNode(self, providedSeedNode):
        requires(not self.seedNodeIsSet()); # requires you to explicitly clear the seed node first
            # using the clearSeedNode function...
        requires(isinstance(providedSeedNode, str));
        #should no longer be necessary#  requires(providedSeedNode in self.nodesInGraph);
        self.seedNode = providedSeedNode;
        return;
        

    def getNextNode(self):
        raise Exception; # Base classes must override this
            # TODO: do force-overriding properly.
        return;


    def inputFeedback(self, nodeConsidered, label, learnFromExample=True):
        # Considered making this class one to be forced to be overriden, like getNextNode
        # but given the utility of the things below, I decided against it.
        requires(self.seedNodeIsSet());
        # TODO: consider making labels a class and using isinstance to check
        #     whether something is a label or not.... 
        requires(isProperLabel(label));
        # in this toy, we ignore all feedback.
        labelStr = "";
        if(label == positiveLabel):
            labelStr = "positive";
        elif(label == negativeLabel):
            labelStr = "negative";
        else:
            raise Exception;
        
        # print "Recieved feedback. Label: " + str(labelStr)
        return;
          
