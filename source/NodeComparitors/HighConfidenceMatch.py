import sys;

def requires(booleanStatement):
    assert(booleanStatement);

import re;

import functools as ft;



def getKeyboardSpecailCharacters():
    return "_~!@#$%^&*-+=\(\)\\,.;:<>|\"'/?";


def stringIsComprisedOfAcceptableCharacters(thisString):
    return (re.match("^[a-zA-Z" + getKeyboardSpecailCharacters() + "]+$", thisString) != None);


def cleanCharacters(inputString):
    requires(stringIsComprisedOfAcceptableCharacters(inputString));
    temp =  re.sub("[" + getKeyboardSpecailCharacters() + "]",  "" , inputString);
    assert(temp.lower() == temp or temp == "UREMOVED");
    return temp;


def mightBeEmail(thisString):
    return (thisString.count("@") == 1) and (thisString.count(".") >= 1 or (thisString.lower().count("dot") >= 1));


def mightBeURL(thisString):
    return (thisString.count("/") > 0) or (thisString.lower().count("www") > 0) or (thisString.lower().count(".com") > 0) or (thisString.lower().count("dotcom") > 0);


def quadAroundWord(A, x, nForNGram):
    B = A[max(0, x - (nForNGram - 1)) : min(x + nForNGram, len(A))];
    assert(len(B) <= 1 + (2 * (nForNGram - 1))); 
    B = [x.lower() for x in B];
    return B;


def quadToTheLeft(A, x, nForNGram):
    B = A[max(0, x - (nForNGram - 1)) : (x + 1)];
    assert(len(B) <= 1 + (nForNGram - 1)); 
    B = [x.lower() for x in B];
    return B;


def memberIndicatesURLMightBeInQuad(thisSplitIndividualWordCleanedText, index, nForNGram):
    thisSplitIndividualWordCleanedText = [x.lower() for x in thisSplitIndividualWordCleanedText ];
    thisList = quadAroundWord(thisSplitIndividualWordCleanedText, index, nForNGram);

    for thisURLIndicatorPhrase in ["dot", "dotcom", "dotorg", ".com", ".org", "com", "org"]:
        if(thisURLIndicatorPhrase in thisList): #note that this is a whole-word match, not a substring match....
            return True;
    
    thisList = quadToTheLeft(thisSplitIndividualWordCleanedText, index, nForNGram);

    for thisURLIndicatorPhrase in ["www", "wwwdot", "www."]:
        if(thisURLIndicatorPhrase in thisList): #note that this is a whole-word match, not a substring match....
            return True;
    
    return False;


def cleanMultiwordURLs(thisSplitIndividualWordCleanedText, nForNGram):
    if(len(thisSplitIndividualWordCleanedText) == 0):
        return [];
    # removing empty characters that might have resulted from more than one space.
    thisSplitIndividualWordCleanedText = [x for x in thisSplitIndividualWordCleanedText if len(x) > 0]; 
    tempUnigrams = [ \
        ( thisSplitIndividualWordCleanedText[index].lower() if(not memberIndicatesURLMightBeInQuad(thisSplitIndividualWordCleanedText, index, nForNGram)) else \
          "UREMOVED"  ) \
        for index in range(0, len(thisSplitIndividualWordCleanedText)) \
        ];
    tempToReturn = [tempUnigrams[0]];
    for index in range(1, len(tempUnigrams)):
        if(tempUnigrams[(index - 1):(index + 1)] != ["UREMOVED", "UREMOVED"]):
            tempToReturn.append(tempUnigrams[index])
    return tempToReturn;


def splitAndSanitizeString(inputString):
    # Note that we allow inputTextSplitOnSpaces to be empty
    inputTextSplitOnSpaces = inputString.split(" ");

    if("postid" in inputTextSplitOnSpaces):
        inputTextSplitOnSpaces.remove("postid"); # artifact of original process
    if("post_id" in inputTextSplitOnSpaces):
        inputTextSplitOnSpaces.remove("post_id"); # artifact of original process

    nForNGram = 4; # TODO: do this properly.
    inputTextSplitOnSpaces = cleanMultiwordURLs(inputTextSplitOnSpaces, nForNGram); 

    seperatedWordsToReturn = [];

    stringToPutInForWordsRemovedBecauseOfCharacters = "CREMOVED";
    stringToPutInForWordsRemovedBecauseOfPossibleURL = "UREMOVED";
    stringToPutInForWordsRemovedBecauseOfPossibleEmail = "EREMOVED";
    
    for thisWord in inputTextSplitOnSpaces: 
        if(not stringIsComprisedOfAcceptableCharacters(thisWord)):
            seperatedWordsToReturn.append(stringToPutInForWordsRemovedBecauseOfCharacters);
        elif(mightBeEmail(thisWord)):
            seperatedWordsToReturn.append(stringToPutInForWordsRemovedBecauseOfPossibleEmail);
        elif(mightBeURL(thisWord)):
            seperatedWordsToReturn.append(stringToPutInForWordsRemovedBecauseOfPossibleURL);
        else:
            thisWordCharacterCleaned = cleanCharacters(thisWord);
            seperatedWordsToReturn.append(thisWordCharacterCleaned);

    assert(len(seperatedWordsToReturn) == len(inputTextSplitOnSpaces));        
    return seperatedWordsToReturn;


def genericCleanNGramGenerator(thisInstanceTextForBodyOrTitle, nForNGram):
    if(len(thisInstanceTextForBodyOrTitle) == 0):
        return [];

    requires(isinstance(nForNGram, int));
    requires(nForNGram > 0);
    requires(isinstance(thisInstanceTextForBodyOrTitle, str));
    requires(len(thisInstanceTextForBodyOrTitle) > 0);
    cleanedStrings = splitAndSanitizeString(thisInstanceTextForBodyOrTitle);

    nGrams = set();
    # below, there is a +1 because the n in the n-gram describes the number of words to 
    #     be taken to form the gram; the index alone, walking along the entire string, produces
    #     unigrams - any further offset is needed to capture MORE than one character - so 
    #     when nForNGram == 1, we just want to see every word, using index in range(0, len(cleanedStrings)).
    #     When nForNGram is higher, we need to get a non-zero offset from the end, etc...
    maximumNumberOfNGrams = len(cleanedStrings) + 1 - nForNGram;
    for index in range(0, maximumNumberOfNGrams):
        wordsInThisNGram = cleanedStrings[index:(index + nForNGram)];
        assert(len(wordsInThisNGram) == nForNGram);
        
        thisNGram = reduce((lambda x, y: x + "_" + y), wordsInThisNGram);
        # Note: if we did not have the curly-brackets around thisNGram below, nGrams would 
        #     become a set of characters as oppossed to a set of strings.
        nGrams = nGrams.union({thisNGram});

    assert(len(nGrams) <= maximumNumberOfNGrams or (maximumNumberOfNGrams < 0));
    assert(len(nGrams) >= 0); # by the requires, len(thisInstanceTextForBodyOrTitle) > 0

    return nGrams;        


class HighConfidenceMatch():

    def requires(booleanCondition):
        assert(booleanCondition);

    def ensures(booleanCondition):
        assert(booleanCondition);

    def __init__(self, pathToFolderToReadFrom):
        self.listOfClusterMembers = [];
 
        fileToRead = pathToFolderToReadFrom + "dictMappingAdIDToInstanceText.csv";
        fileHandleToFileToRead = open(fileToRead, "r");
        thisLine = fileHandleToFileToRead.readline();
        
        self.dictMappingNodeIDToText = {};
        self.nForNGrams = 4;
        self.cutoffPorportionToAcceptAt = 0.90;

        while(len(thisLine) > 0):
            assert(thisLine[-1] == "\n");
            if(thisLine != "\n"):
                [thisNodeIDAsString , thisDelimitor, textOfAd] = thisLine[:-1].partition(",");
                assert(thisDelimitor == ",");
                assert(len(thisNodeIDAsString) > 0);
                instanceStringToWrite =  textOfAd.replace( "__COMMA__", ",");
                self.dictMappingNodeIDToText[thisNodeIDAsString] = instanceStringToWrite;
            thisLine = fileHandleToFileToRead.readline();
        fileHandleToFileToRead.close();
        return;

    def addToCluster(self, thisNodeID):
        textFromNode = self.dictMappingNodeIDToText[thisNodeID];
        nGramsFromThisNodeText = genericCleanNGramGenerator(textFromNode, self.nForNGrams);
        assert(isinstance(nGramsFromThisNodeText, set));
        self.listOfClusterMembers.append(nGramsFromThisNodeText);
        assert(len(self.listOfClusterMembers) > 0);
        return;

    def clearCluster(self):
        self.listOfClusterMembers = [];

    def testForNearDuplicate(self, thisNodeID):
        textFromNode = self.dictMappingNodeIDToText[thisNodeID];
        nGramsFromThisNodeText = genericCleanNGramGenerator(textFromNode, self.nForNGrams);
        if(len(nGramsFromThisNodeText) == 0):
            return False;
        assert(len(nGramsFromThisNodeText) > 0);
        for thisSetOfNGrams in self.listOfClusterMembers:
            nGramsAlreadyInCluster = nGramsFromThisNodeText.intersection(thisSetOfNGrams);
            jaccardScore = float(len(nGramsAlreadyInCluster)) / float(len(nGramsFromThisNodeText) + len(thisSetOfNGrams) - len(nGramsAlreadyInCluster));
            if(jaccardScore >= self.cutoffPorportionToAcceptAt):
                return True;
        return False;

