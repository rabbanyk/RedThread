from mainTestFrameworks.mainTestFramework_HT import HT_mainTestFramework_helper;
from mainTestFrameworks.mainTestFramework_memeDisc import memeDisc_mainTestFramework_helper;
from getPathToThisDirectory import *;
from dataAccessor import * ;
from contracts import * ;

from getStringTimeNow import *;
import labelNames;
import random;
import sys;

from runScriptInputParameters import getRunScriptParameters;
import re;


# chechking that the HT matcher,etc., is only set for the HT graph data sets, etc....

def checkDatasetPathIsValid(nameOfDatasetToRun):
    requires(isinstance(nameOfDatasetToRun, str));
    # needs seedNode, weighted adjacency list, node attribute file, ground truth labels....
    if(len(nameOfDatasetToRun) <= 0):
        return False;
    if(nameOfDatasetToRun[0] != "/"): # paths are required to be rooted.
        return False;
    if(nameOfDatasetToRun[-1] != "/"): # the path provided my specify a directory...
        return False;

    pathToAdjacencyList = nameOfDatasetToRun + "weightedAdjacencyList.csv";
    pathToSeedNodes = nameOfDatasetToRun + "nodeAttributeFile.csv";
    pathToEntityTypes = nameOfDatasetToRun + "seedNodes.csv";
    pathToGroundTruthLabels =  nameOfDatasetToRun + "groundTruthNodeLabels.csv";
    for thisPathToEnsureExists in [pathToAdjacencyList, pathToSeedNodes, pathToEntityTypes, pathToGroundTruthLabels]:
        if(not os.path.exists(thisPathToEnsureExists)):
            sys.stdout.flush();
            print thisPathToEnsureExists;
            sys.stdout.flush();
            return False;

    return True;



def runScript(dictForMainTableInformation, algorithmToUse, ourSQLWritter):

    dictOfRunscriptParameters = getRunScriptParameters();
    algorithmNameToClassDict = dictOfRunscriptParameters["algorithmNameToFunctionDict"]; 

    algorithmName = dictForMainTableInformation["algorithmName"];
    algorithmClass = algorithmNameToClassDict[algorithmName];
    typeOfRun = dictForMainTableInformation["typeOfRun"];

    requires(typeOfRun in {"HT_HCM", "HT_noHCM", "nonHT", "HT_alt_HCM", "HT_alt_noHCM"});
    requires(checkDatasetPathIsValid(dictForMainTableInformation["datasetFilePath"]));

    if(typeOfRun == "HT_HCM"):
        HT_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter, typeOfHighConfidenceMatcher="RealHCMatcher");
    elif(typeOfRun == "HT_noHCM"):
        HT_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter, typeOfHighConfidenceMatcher="DummyHCMatcher");
    elif(typeOfRun == "HT_alt_HCM"):
        HT_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter, typeOfHighConfidenceMatcher="alternateHighConfidenceMatcherAndNearDuplicateDetector_RealHCMatcher");
    elif(typeOfRun == "HT_alt_noHCM"):
        HT_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse, ourSQLWritter, typeOfHighConfidenceMatcher="alternateHighConfidenceMatcherAndNearDuplicateDetector_DummyHCMatcher");
    else:
        assert(typeOfRun == "nonHT");
        memeDisc_mainTestFramework_helper(dictForMainTableInformation, algorithmToUse,  ourSQLWritter);

    return;



import sys, traceback
import fnmatch;
from SQLResultWrittingCode.sqlResultWritter import SQLResultWritter;

def setupSQLResultWritter(dictForMainTableInformation):
    requires(isinstance(dictForMainTableInformation, dict));
    requires(set(dictForMainTableInformation.keys()) == \
       {"datasetName" , "algorithmName", "queueSize", "queryBudget", "typeOfRun",\
        "seedNodeFilePath", "datasetFilePath", "terminalInput", "seedNodesType", \
        "algorithmParameters"});
    requires(dictForMainTableInformation["typeOfRun"] in {"HT_HCM", "HT_noHCM", "nonHT", "HT_alt_HCM", "HT_alt_noHCM"});

    # maybe ensure that all the tables, regardless of whether they use the stuff or not, record at least one value for each of the below (putting NULLs in as necessary)...
    tableSpecifications = {\
            "algorithmRunParameters" : ["parameterName", "parameterValue"] , \
            "clusteringResults" : ["seedNode", "nodeReturnedByAlgorithm", "categoryOfNodeEvaluation", \
                                   "returnedNodePositiveOrNegativeLabel", "algorithmIndicatesClusterDone", \
                                   "labelOfSeedNode", "labelOfNodeReturnedByAlgorithm", "queryNumberForThisSeedNode"], \
            "algorithmInternalParameters" : ["stateNumber", "categoryOfParameter" , "specificParameterName", "parameterValue"] \
        };
    # TODO: enable entering NULL into the database:
    #     You insert NULL value by typing NULL:
    #     INSERT INTO table(number1,number2,number3) VALUES (1,NULL,3);
    return SQLResultWritter(dictForMainTableInformation, tableSpecifications);




def parseStdinInput_convertStringToDict(runningParameterString):
        requires(isinstance(runningParameterString, str));
        requires(runningParameterString.count("__") == 0); # double underscore would produce empty parameter specification strings
            # which would screw things up below.....
        # ([a-zA-Z][a-zA-Z0-9]*:[0-9][0-9]*\.?[0-9]*)
        # ^[a-zA-Z][a-zA-Z0-9]*:[0-9][0-9]*\.?[0-9]*$
        parameterDelimitor = ",";
        keyValueDelimitor = ":";
        splitRunningParameters = runningParameterString.split(parameterDelimitor);
        dictToReturn = {};
        assert(  (len(splitRunningParameters) > 0)  or  (len(runningParameterString) == 0) );
        for thisKeyValuePairAsString in splitRunningParameters:
            # below assert checks that thisKeyValuePairAsString is a string where prior to the occurance of ":"
            #     is an alphanumeric string starting with a letter and after the ":" is an alpha numeric string that can 
            #     underscores, colons, period marks (to delimit decimals), and dashes (to represent negatives)
            assert(re.match("^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z0-9_:\.-]+$"  ,\
                thisKeyValuePairAsString) != None); # unfortunately, we do not have sufficiant checks ealier in this function to make this 
                # a requires.
            # Note that below, we us PARTITION not SPLIT becuase we only want to break up the the FIRST key value, not
            #     any others. This is important for the string that contains the parameters we pass to the algorithms, which
            #     we expect to be of form:
            #     algorithmParameters:<key1>:<value1>_<key2>:<value2>_...<keyN>:<valueN>            
            thisKeyValuePairStringsSplit = thisKeyValuePairAsString.partition(keyValueDelimitor);
            assert(len(thisKeyValuePairStringsSplit) == 3);
            assert(thisKeyValuePairStringsSplit[1] == ":");
            assert(re.match("^[a-zA-Z][a-zA-Z0-9]*", thisKeyValuePairStringsSplit[0]) != None);
            assert(re.match("[a-zA-Z0-9_:\.]+", thisKeyValuePairStringsSplit[2]) != None);
            thisKeyString = thisKeyValuePairStringsSplit[0];
            thisValueString = thisKeyValuePairStringsSplit[2];
            if( thisKeyString in {"algorithmParameters", "algorithmName", "datasetName", "typeOfRun", \
                "seedNodesType"}):
                dictToReturn[thisKeyString] = thisValueString;
                if(thisKeyString == "algorithmParameters"):
                    assert("queueSize:" in thisValueString);
                    (ignoreA, queueSizeKeyString, restOfAlgorithmParameters) = thisValueString.partition("queueSize:");
                    assert(queueSizeKeyString == "queueSize:");
                    (valueOfQueueSizeString, ignoreB, ignoreC) = restOfAlgorithmParameters.partition("_");
                    assert(re.match("^[1-9][0-9]*$", valueOfQueueSizeString) != None);
                    # Why do we convert a string to an int then back to an string? Doing this provides
                    #     a uniform representtion for strings that represent the same values, like
                    #     001 and 1.
                    dictToReturn["queueSize"] = str(int(valueOfQueueSizeString));
                    ensures( dictToReturn["queueSize"] > 0 );
            elif("queryBudget" == thisKeyString):
                # Why do we convert a string to an int then back to an int? Doing this provides
                #     a uniform representtion for strings that represent the same values, like
                #     001 and 1.
                dictToReturn[thisKeyString] = int(thisValueString);
                assert(isinstance(dictToReturn[thisKeyString], int));
                assert(dictToReturn[thisKeyString] > 0);
                dictToReturn[thisKeyString] = str(dictToReturn[thisKeyString]);
                assert(isinstance(dictToReturn[thisKeyString], str));
            else:
                print("Unrecognized key:" + str(thisKeyString));
                sys.stdout.flush();
                raise Exception();
            dictToReturn[thisKeyString] = thisValueString;
        return dictToReturn;



from runScriptInputParameters import getRestOfAlgorithmParametersUsedInPaper;

def insertParametersUsedInPaper(thisInputString):
    requires(re.match("^(.+,)*algorithmParameters:(([^_])|($))+.*$", thisInputString) != None);
    requires(thisInputString.count("algorithmParameters:") == 1); # problems might ocur if users provided
        # a pathological case where they name part of thier path with the substring "algorithmParameters:".
    AlgorithmNameToParametersDict = getRestOfAlgorithmParametersUsedInPaper();    
    
    for thisAlgorithmName in AlgorithmNameToParametersDict:
        if(re.match("^(.+,)*algorithmName:" + thisAlgorithmName + "(,.*)*$", thisInputString) != None):
            seperator = "_";
            if(re.match("^(.+,)*algorithmParameters:(,.*)*$", thisInputString) != None): # i.e., the user provides no
                # algorithm parameters.
                seperator = "";
            return thisInputString.replace("algorithmParameters:" , \
                "algorithmParameters:" + AlgorithmNameToParametersDict[thisAlgorithmName] + seperator);
    raise Exception(); # the provided algorithm name is unknown. 


# expect input to be comma seperates, with 
#     <key>:<value>
# between commas, where key is a member of:
#     datasetName
#     seedNodesType
#     algorithmName
#     queueSize
#     queryBudget
#     typeOfRun
#     algorithmParameters
for line in sys.stdin: 

    clearLine = line.replace("\n", "");

    clearLine = insertParametersUsedInPaper(clearLine);

    dictForMainTableInformation = parseStdinInput_convertStringToDict(clearLine);
    assert( set(dictForMainTableInformation.keys()) == \
       {"datasetName" , "algorithmName","seedNodesType", "queueSize", "queryBudget", "typeOfRun"\
        , "algorithmParameters"}); # , "terminalInput"
    requires(int(dictForMainTableInformation["queueSize"]) >= int(dictForMainTableInformation["queryBudget"]));

    dictOfInfoForNamesToPaths = getRunScriptParameters();
    datasetsToUseDict = dictOfInfoForNamesToPaths["datasetsToUseDict"];
    dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath = \
        dictOfInfoForNamesToPaths["dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath"];


    dictForMainTableInformation["datasetFilePath"] = datasetsToUseDict[dictForMainTableInformation["datasetName"]];
    # the path to the dataset should be an absolute path that specifies a directory
    assert(isinstance(dictForMainTableInformation["datasetFilePath"], str));
    assert(len(dictForMainTableInformation["datasetFilePath"]) > 0);
    assert(dictForMainTableInformation["datasetFilePath"][0] == "/");
    assert(dictForMainTableInformation["datasetFilePath"][-1] == "/");
    dictForMainTableInformation["seedNodeFilePath"] = \
        dictMappingAlgoNameToDictMappingSeedNodeDescriptionToSeedNodeFilePath[\
            dictForMainTableInformation["datasetName"]][\
            dictForMainTableInformation["seedNodesType"]];
    assert(isinstance(dictForMainTableInformation["seedNodeFilePath"], str));
    assert(len(dictForMainTableInformation["seedNodeFilePath"]) > 0);
    assert(dictForMainTableInformation["seedNodeFilePath"][0] == "/");
    assert(dictForMainTableInformation["seedNodeFilePath"][-1] != "/");
    # the path to the seed node file should be an absolute path that specifies a file.
    dictForMainTableInformation["terminalInput"] = clearLine;
    assert( set(dictForMainTableInformation.keys()) == \
       {"datasetName" , "algorithmName", "queueSize", "seedNodesType", "queryBudget", "typeOfRun",\
        "seedNodeFilePath", "datasetFilePath", "terminalInput", "algorithmParameters"});
    ourSQLWritter = setupSQLResultWritter(dictForMainTableInformation);

    algorithmToUse = dictOfInfoForNamesToPaths["algorithmNameToFunctionDict"][\
                                               dictForMainTableInformation["algorithmName"]];

    try:
        runScript(dictForMainTableInformation, algorithmToUse, ourSQLWritter);
        ourSQLWritter.recordExperimentFinished();
    except:
        ourSQLWritter.recordExperimentDied();



