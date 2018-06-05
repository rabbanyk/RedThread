from nameOfFolderToSaveResultsTo import nameOfFolderToSavePostgresSQLFile;
from contracts import *;
from sys import stdout;
from getGitCommitHash import getGitCommitHash;
from getPathToThisDirectory import getPathToThisDirectory;
from getStringTimeNow import getStringTimeNow;
from myUUIDGenerator import myUUIDImplementation;
from sanitizeStringForPostgresSQL import postgres_escape_string;

import re;

from os.path import exists as pathExists;
from os import mkdir, rmdir, remove;
import sys;

import traceback; # to be able to get and record error messages (exceptions, etc.)

from safeIncrement import *;

class SQLNullValue(): # The entire point of this class is to allow users to specify writting out NULL values to postgress when trying
    # to write to a table.

    def __init__(self):
        return 

class SQLResultWritter():
    

    #V~V~V~V~~V~V~V~V~V~V~V`V~V~V~V~V~V~~V~V~V~V~V~V~V~VV~V~~VV~V~V~V~V~V~V~V~V~V~V
    # general utility functions.
    #------------------------------------------------------------------------------
    def getCurrentTimeAsStringAndInt(self):
        self.baseTimeString = getStringTimeNow();
        timeRunAsInterpreatableForm = postgres_escape_string(self.baseTimeString);
        timeRunAsSingleInt = self.baseTimeString.replace("_", ""); # we store this as an integer in the database
            # so we can more easily find the lastest records, noting that the higher order digits in this
            # representation correspond to the time units of larger value.
        ensures(isinstance(timeRunAsInterpreatableForm, str));
        ensures(isinstance(timeRunAsSingleInt, str));
        ensures(re.match("^[0-9]*$", timeRunAsSingleInt) != None); # we check that timeRunAsSingleInt is a numeric string
        return {"stringTime" : timeRunAsInterpreatableForm, "intTime" : timeRunAsSingleInt};

    def getString_statusRunning(self):
        return "RUNNING";

    def getString_statusDied(self):
        return "DIED";

    def getString_statusFinished(self):
        return "FINISHED";
    #^_^_^^_^_^_^_^_^_^_^_^^_^_^_^_^_^_^_^_^_^_^_^^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

    #V~V~V~V~~V~V~V~V~V~V~V`V~V~V~V~V~V~~V~V~V~V~V~V~V~VV~V~~VV~V~V~V~V~V~V~V~V~V~V
    # functions used to set up writting values out
    #------------------------------------------------------------------------------
    def __init__(self, input_dictOfKeysAndValuesForPostgresRowInsert, tableSpecifications):
        self.globalRecordCounter = 0;
        self.formMainFile(input_dictOfKeysAndValuesForPostgresRowInsert );
        self.setUpTableFiles(tableSpecifications); 
        return;

    def formMainFile(self, input_dictOfKeysAndValuesForPostgresRowInsert ):
        requires(isinstance(input_dictOfKeysAndValuesForPostgresRowInsert, dict));
        requires(set(input_dictOfKeysAndValuesForPostgresRowInsert.keys()) == \
            {"datasetName", "algorithmName", "queueSize", "queryBudget", "typeOfRun", "seedNodeFilePath", \
             "datasetFilePath", "terminalInput", "algorithmParameters", "seedNodesType"});

        requires(isinstance(input_dictOfKeysAndValuesForPostgresRowInsert["seedNodeFilePath"], str));
        requires(len(input_dictOfKeysAndValuesForPostgresRowInsert["seedNodeFilePath"]) > 0);
        requires(input_dictOfKeysAndValuesForPostgresRowInsert["seedNodeFilePath"][0] == "/"); # we require an absolute path in 
            # the seed node file provided.
        requires(input_dictOfKeysAndValuesForPostgresRowInsert["seedNodeFilePath"][-1] != "/"); # the seed node file should
            # NOT specify a directory.      
        requires(input_dictOfKeysAndValuesForPostgresRowInsert["datasetFilePath"][0] == "/"); # we require an absolute path in 
            # the dataset file provided.
        requires(input_dictOfKeysAndValuesForPostgresRowInsert["datasetFilePath"][-1] == "/"); # the data set file SHOULD
            # specify a directory.    

        # still need to work-out how it will add content to the row listing how it has finished the run

        dictOfValuesToWriteIntoPostgresTable = {};

        self.integerRunningNumberOfRecords = 0;

        categoryOfData = postgres_escape_string("experiment");
        self.uuidNotEscaped = myUUIDImplementation();
        uuidEscaped = postgres_escape_string(self.uuidNotEscaped); # To avoid confusion in other parts of the 
            # code, we do not store this as a class variable, since self.uuidNotEscaped already is.
        startTimeDict = self.getCurrentTimeAsStringAndInt();
        directoryCodeRunAt = postgres_escape_string(getPathToThisDirectory());
        gitHashForLatestCommitRunBeingRunBuildOn = postgres_escape_string(getGitCommitHash(self.uuidNotEscaped));

        startOfPostgresCommand = "INSERT INTO \"ResultUUIDRegistrationTable\" ( ";
        middleOfPostgresCommand = " ) VALUES ( ";
        endOfPostgresCommand = ");";

        # Note - below actually mutates the dictionary passed in.
        dictOfValuesToWriteIntoPostgresTable["categoryOfData"] = categoryOfData;
        dictOfValuesToWriteIntoPostgresTable["UUID"] = uuidEscaped;
        dictOfValuesToWriteIntoPostgresTable["timeCodeStartedRunningAsString"] = startTimeDict["stringTime"];
        dictOfValuesToWriteIntoPostgresTable["timeCodeStartedRunningAsInt"] = startTimeDict["intTime"];
        dictOfValuesToWriteIntoPostgresTable["directoryCodeRunAt"] = directoryCodeRunAt;
        dictOfValuesToWriteIntoPostgresTable["gitHashOfLatestCommitOfCodeRun"] = gitHashForLatestCommitRunBeingRunBuildOn;
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsString"] = "NULL";# we put a NULL value here because the column is not yet applicable. Note that
            # it is important we do NOT escape this value so that Postgresql DOES interpreate it as NULL.....
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsInt"] = "NULL"; # we put a NULL value here because the column is not yet applicable. Note that
            # it is important we do NOT escape this value so that Postgresql DOES interpreate it as NULL.....
        dictOfValuesToWriteIntoPostgresTable["status"] =  postgres_escape_string(self.getString_statusRunning());
        dictOfValuesToWriteIntoPostgresTable["errorInformation"] = "NULL"; # we put a NULL value here because the column is not yet applicable (and
            # if the code runs successful, this should remain NULL....). Note that it is important we do NOT escape this value so that Postgresql
            # DOES interpreate it as NULL.....

        for thisKey in input_dictOfKeysAndValuesForPostgresRowInsert:
            assert(isinstance(thisKey, str));
            assert(len(thisKey) > 0);
            assert(isinstance(input_dictOfKeysAndValuesForPostgresRowInsert[thisKey], str));
            assert(len(input_dictOfKeysAndValuesForPostgresRowInsert[thisKey]) > 0);
            if(thisKey in {"queueSize", "queryBudget"}):
                assert(re.match("^[0-9]*$", input_dictOfKeysAndValuesForPostgresRowInsert[thisKey]) != None);# we check 
                    # that the values passed in for the query budget and queue size are numeric strings...
                dictOfValuesToWriteIntoPostgresTable[thisKey] = input_dictOfKeysAndValuesForPostgresRowInsert[thisKey];
            else:
                dictOfValuesToWriteIntoPostgresTable[thisKey] = postgres_escape_string(\
                    input_dictOfKeysAndValuesForPostgresRowInsert[thisKey]);  

        stringSeperator = "";
        for thisKey in dictOfValuesToWriteIntoPostgresTable:
            assert(isinstance(thisKey, str));
            assert(len(thisKey) > 0);
            assert(isinstance(dictOfValuesToWriteIntoPostgresTable[thisKey], str));
            assert(len(dictOfValuesToWriteIntoPostgresTable[thisKey]) > 0);
            startOfPostgresCommand = startOfPostgresCommand + stringSeperator + "\"" + thisKey + "\"";
            middleOfPostgresCommand = middleOfPostgresCommand + stringSeperator + dictOfValuesToWriteIntoPostgresTable[thisKey];
            stringSeperator = " , ";

        self.nameOfMainFileToWriteTo = nameOfFolderToSavePostgresSQLFile + self.uuidNotEscaped + ".sql";
        assert(not pathExists(self.nameOfMainFileToWriteTo)); #not strictly guarenteed, but highly probable given out UUIDs.... 
        mainFileHandleToWriteTo = open(self.nameOfMainFileToWriteTo, "w");
        mainFileHandleToWriteTo.write(startOfPostgresCommand + middleOfPostgresCommand + endOfPostgresCommand + "\n");
        mainFileHandleToWriteTo.flush();                      
        mainFileHandleToWriteTo.close(); 
        assert(pathExists(self.nameOfMainFileToWriteTo)); #not strictly guarenteed, but highly probable given out UUIDs.... 
        
        return None; # python requires that init functions return None (makes sense - how else would yuou write the object return).

    def isProperSpecificationOfTables(self, tableSpecification):
        if(not isinstance(tableSpecification, dict)):
            return False;
        # note that having no tables is fine.
        for thisKey in tableSpecification:
            # We require table names to be alphanumeric strings, perhaps with underscores, but
            #     must start with a letter.
            if(re.match("^[a-zA-Z][a-zA-Z0-9_]*$", thisKey) == None):
                return False;
            if(not isinstance(tableSpecification[thisKey], list)):
                return False; 
            # on second thought, we allow this possibility- may be useful for counting occurances, for instance, since values in addition to what the user provides already. # if(len(tableSpecification[thisKey]) == 0):
            #    return False;
            if(len(tableSpecification[thisKey]) != len(set(tableSpecification[thisKey]))): # we require the column names to be
                # unique.
                return False;
            for thisColumn in tableSpecification[thisKey]:
                # We require column names to be alphanumeric strings, perhaps with underscores but
                #     must start with a letter.
                if(re.match("^[a-zA-Z][a-zA-Z0-9_]*$", thisColumn) == None):
                    return False;
        return True;
 
    def formPostgresHeader(self, tableName, tableSpecifications):
        # this requires should be captured by the second requires below # requires(re.match("^[a-zA-Z][a-zA-Z0-9_]*$", tableName) != None);
        requires(self.isProperSpecificationOfTables(tableSpecifications));
        requires(tableName in tableSpecifications.keys());
 
        listConvertedToPostgresColumnNamesString = "";
        for thisColumnName in tableSpecifications[tableName]:
            # Note that below, we are save putting a comma in directly behind thisColumnName since, per
            #     what is shown forming stringToReturn, we do put values in before it.
            listConvertedToPostgresColumnNamesString = listConvertedToPostgresColumnNamesString + " , \""+ \
                thisColumnName + "\"";
        assert( (listConvertedToPostgresColumnNamesString.count(",") == len(tableSpecifications[tableName])) or \
                (len(tableSpecifications[tableName]) == 0) ); 

        # NOTE THAT WE INSERT THREE ADDITIONAL COLUMNS AT THE START OF EACH RECORD- the UUID of the run that 
        #     produced the record, the total number of records produce by that run up to an including this one, and
        #     the number of records inserted in this particular table up to and including this one.
        stringToReturn = "INSERT INTO \"" + tableName + "\" ( \"UUID\", \"totalNumberRecordCount\", \"recordNumberInThisTable\" " + listConvertedToPostgresColumnNamesString + " ) VALUES \n";
        # The below ensures are not meant to be comprehensive.
        ensures(re.match("^[a-zA-Z][a-zA-Z0-9_)(,\" ]*$", stringToReturn) != None); # We ensure that the result is an alphanumeric strings, perhaps with underscores, paranethesis, commas, quotation marks (around column names, etc.) and spaces
        ensures(stringToReturn.count("(") == 1);
        ensures(stringToReturn.count(")") == 1);
        ensures(stringToReturn.count(";") == 0);
        ensures(stringToReturn.count("\"") == 2 * (4 + len(tableSpecifications[tableName])) ); # we should have
            # a pair of quotation marks around each of the table elements
        ensures(stringToReturn.count(",") == (len(tableSpecifications[tableName]) + 3) - 1); # there should be one comma seperating each of the column names (
            # including the 3 additional ones we added)

        return stringToReturn;

    # We require tableSpecifications to be a dictionary mapping a table name to a
    #     list of tabel columns to write to.
    def setUpTableFiles(self, tableSpecifications):
        requires(self.isProperSpecificationOfTables(tableSpecifications));
        
        self.pathToSaveTemporaryResults = nameOfFolderToSavePostgresSQLFile + "temp/";
        if(not pathExists(self.pathToSaveTemporaryResults)):
            mkdir(self.pathToSaveTemporaryResults);
        self.pathToSaveTemporaryResults = self.pathToSaveTemporaryResults + self.uuidNotEscaped + "/";
        if(not pathExists(self.pathToSaveTemporaryResults)):
            mkdir(self.pathToSaveTemporaryResults);

        self.tableSpecifications = tableSpecifications;
        self.tableTempFiles = {};
        self.tableRecordCounts = { thisTableName : 0 for thisTableName in tableSpecifications};
        assert(isinstance(self.tableRecordCounts, dict));
        assert(set(self.tableRecordCounts.keys()) == set(tableSpecifications.keys()));
        assert(set(self.tableRecordCounts.values()) == set([0]));

        for thisTableName in tableSpecifications:
            pathToWriteThisTableTempFiles = self.pathToSaveTemporaryResults + thisTableName;
            assert(not pathExists(pathToWriteThisTableTempFiles));
            self.tableTempFiles[thisTableName] = open(pathToWriteThisTableTempFiles, "w");
            assert(pathExists(pathToWriteThisTableTempFiles));              

            self.tableTempFiles[thisTableName].write(self.formPostgresHeader(thisTableName, tableSpecifications));
            self.tableTempFiles[thisTableName].flush();

        return;
    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^



    #V~V~V~V~V~V~V~V~V~V~~VV~V~V~~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V
    # functions used during the run of the algorithm
    #---------------------------------------------------------------------


    def writeToTable(self, tableName, valuesToWrite): # TODO: allow writting NULL....
        requires(tableName in self.tableSpecifications);
        requires(isinstance(valuesToWrite, dict));
        requires(set(valuesToWrite.keys()) == set(self.tableSpecifications[tableName]));
        requires(all([ (isinstance(x, str) or isinstance(x, SQLNullValue)) for x in valuesToWrite.values()])); # the values of the dictionary must all be strings.
        valuesSeperator = "";
        if(self.tableRecordCounts[tableName] > 0):
            valuesSeperator = ",";
        startOfPostgresSQLTuple = \
            "    " + valuesSeperator +"( " + \
                postgres_escape_string(self.uuidNotEscaped) + " , " + \
                str(self.globalRecordCounter) + " , " + \
                str(self.tableRecordCounts[tableName]);

        endOfPostgresSQLTuple = ")\n"; # NOTE THAT WE DO NOT END THE COMMAND - see the self.__del__
           # function for where that happens.
        valueSeperator = "";
        for thisKey in self.tableSpecifications[tableName]: # note that python iterators respect the list 
            # ordering (note that, per self.isProperSpecificationOfTables, self.tableSpecifications[tableName] is a list),
            # and that by the requires, the keys of valuesToWrite are exactly self.tableSpecifications[tableName],
            # so this for loop ensures that we write out the values in the same order as intended for the keys.
            if(isinstance(valuesToWrite[thisKey], str)):
                thisStringEscaped = postgres_escape_string(valuesToWrite[thisKey]);
                startOfPostgresSQLTuple = startOfPostgresSQLTuple + " , " + thisStringEscaped; # Note that here, 
                    # we after save putting a comma before thisStringEscaped since we know there are already column
                    # values before thisStringEscaped.
            else:
                assert(isinstance(valuesToWrite[thisKey], SQLNullValue));
                startOfPostgresSQLTuple = startOfPostgresSQLTuple + " , NULL ";

        stringToWrite = startOfPostgresSQLTuple + endOfPostgresSQLTuple;
        # In the below asserts, note that we have inequalities since the values written out to the tuple 
        #     may have such additional characters (perhaps escaped out).
        assert(stringToWrite.count("(") >= 1);
        assert(stringToWrite.count(")") >= 1);
        assert(stringToWrite.count(",") >= (len(self.tableSpecifications[tableName]) + 3) - 1); # there should be one comma seperating each of the column names (
            # including the 3 additional ones we added)

        # incrementing record counters
        self.tableRecordCounts[tableName] = safeIncrement(self.tableRecordCounts[tableName]);
        self.globalRecordCounter = safeIncrement(self.globalRecordCounter);

        self.tableTempFiles[tableName].write(stringToWrite);
        self.tableTempFiles[tableName].flush();
        return;

    def getBaseTimeString(self):
        return self.baseTimeString; # TODO: rename this to startTimeSting.

    def getUUID(self):
        return self.uuidNotEscaped;

    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

    #V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~VV~V~V~V~V~V~V
    # functions used after the experiment
    #-----------------------------------------------------------------------
 
    def writeAtLeastOneRecordPerTablePerRun(self): # the pont of this function is to:
        # (1) ensure that each table has at least one entry for each run
        # (2) ensure that, even if an experiment errors-out or dies, that postgres can swallow
        #     the data we provide for it- in particular, due to the way we set up how the values
        #     will be written out, this requires that at least one entry be listed to be written per table,
        for thisTableName in self.tableSpecifications:
            if(self.tableRecordCounts[thisTableName] == 0): # if we have never written something for this table.
                valuesToWrite = {thisKey : SQLNullValue() for thisKey in self.tableSpecifications[thisTableName]};
                self.writeToTable(thisTableName, valuesToWrite);
        return;

    def updateFirstRowOfResultUUIDRegistrationTable(self, dictOfValuesToUpdate):
        requires(isinstance(dictOfValuesToUpdate , dict));
        requires(set(dictOfValuesToUpdate.keys()) == \
            {"timeCodeFinishedRunningAsString", "timeCodeFinishedRunningAsInt", "status", "errorInformation"});

        self.writeAtLeastOneRecordPerTablePerRun();

        startOfPostgresSQLCommand = "UPDATE \"ResultUUIDRegistrationTable\" SET ";
        endOfPostgresSQLCommand = " WHERE \"UUID\" = " + postgres_escape_string(self.uuidNotEscaped) + " ;\n";

        seperator = "";
        for thisKey in dictOfValuesToUpdate:
            thisStringEscaped = "";
            if(thisKey not in { "timeCodeFinishedRunningAsInt", "timeCodeFinishedRunningAsString"}): # Note that we
                # do not escape out "timeCodeFinishedRunningAsString" below since the self.getCurrentTimeAsStringAndInt
                # already did that.
                thisStringEscaped = postgres_escape_string(dictOfValuesToUpdate[thisKey]);
            else:
                assert((thisKey != "timeCodeFinishedRunningAsInt") or (re.match("^[0-9]*$", dictOfValuesToUpdate[thisKey]) != None)); # we check that timeRunAsSingleInt is a numeric string
                thisStringEscaped = dictOfValuesToUpdate[thisKey];
            startOfPostgresSQLCommand = startOfPostgresSQLCommand + seperator + "\"" + thisKey + "\" = " + thisStringEscaped; 
            seperator = " , ";

        stringToWrite = startOfPostgresSQLCommand + endOfPostgresSQLCommand;
        mainFileHandleToWriteTo = open(self.nameOfMainFileToWriteTo, "a");
        mainFileHandleToWriteTo.write(stringToWrite);
        mainFileHandleToWriteTo.flush();
        mainFileHandleToWriteTo.close();
        return;

    def recordExperimentFinished(self):
        endTimeDict = self.getCurrentTimeAsStringAndInt();
        dictOfValuesToWriteIntoPostgresTable = dict();
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsString"] = endTimeDict["stringTime"];
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsInt"] = endTimeDict["intTime"];
        dictOfValuesToWriteIntoPostgresTable["status"] = self.getString_statusFinished();
        dictOfValuesToWriteIntoPostgresTable["errorInformation"] = "NULL"; # we put a NULL value here because the column is not applicable
        self.updateFirstRowOfResultUUIDRegistrationTable(dictOfValuesToWriteIntoPostgresTable);
        return;

    def recordExperimentDied(self):
        endTimeDict = self.getCurrentTimeAsStringAndInt();
        dictOfValuesToWriteIntoPostgresTable = dict();
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsString"] = endTimeDict["stringTime"];
        dictOfValuesToWriteIntoPostgresTable["timeCodeFinishedRunningAsInt"] = endTimeDict["intTime"];
        dictOfValuesToWriteIntoPostgresTable["status"] = self.getString_statusDied();
        dictOfValuesToWriteIntoPostgresTable["errorInformation"] = \
            "".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback));
        self.updateFirstRowOfResultUUIDRegistrationTable(dictOfValuesToWriteIntoPostgresTable);
        sys.stdout.flush();
        print(dictOfValuesToWriteIntoPostgresTable["errorInformation"]);
        sys.stdout.flush();
        return;

    def __del__(self):
        for thisTableFile in self.tableTempFiles.values():
            thisTableFile.close();
        mainFileHandleToWriteTo = open(self.nameOfMainFileToWriteTo, "a");
        for thisTableName in self.tableSpecifications:
            pathToWriteThisTableTempFiles = self.pathToSaveTemporaryResults + thisTableName;
            assert(pathExists(pathToWriteThisTableTempFiles));
            thisTableFileHandle = open(pathToWriteThisTableTempFiles, "r");
            for thisLine in thisTableFileHandle:
                mainFileHandleToWriteTo.write(thisLine);
                mainFileHandleToWriteTo.flush();
            thisTableFileHandle.close();
            remove(pathToWriteThisTableTempFiles); # deleting the temporary file.
            assert(not pathExists(pathToWriteThisTableTempFiles));
            mainFileHandleToWriteTo.write(";\n"); # this end the PostgresSQL insertion command. Note
                # that we do not do this in the self.writeToTable function.

        mainFileHandleToWriteTo.flush();
        mainFileHandleToWriteTo.close();

        assert( ("/temp/" + self.uuidNotEscaped + "/")  in self.pathToSaveTemporaryResults); # weak check that we are deleting the write file.
        rmdir(self.pathToSaveTemporaryResults);

        return;

    #^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^

