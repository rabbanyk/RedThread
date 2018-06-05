

CREATE TABLE "ResultUUIDRegistrationTable" ( 
    "status" text,
    "datasetName" text,
    "typeOfRun" text,
    "timeCodeStartedRunningAsInt" numeric,
    "UUID" text NOT NULL,
    "timeCodeFinishedRunningAsInt" numeric,
    "timeCodeFinishedRunningAsString" text,
    "errorInformation" text,
    "terminalInput" text,
    "queryBudget" int,
    "algorithmParameters" text,
    "datasetFilePath" text,
    "seedNodesType" text,
    "seedNodeFilePath" text,
     "gitHashOfLatestCommitOfCodeRun" text,
     "algorithmName" text,
     "directoryCodeRunAt" text,
     "timeCodeStartedRunningAsString" text,
     "queueSize" numeric,
     "categoryOfData" text,
     UNIQUE (
         "UUID")
     );

 
CREATE TABLE "clusteringResults" (
    "UUID" text NOT NULL,
    "totalNumberRecordCount" int,
    "recordNumberInThisTable" int ,
    "seedNode" text,
    "nodeReturnedByAlgorithm" text,
    "categoryOfNodeEvaluation" text,
    "returnedNodePositiveOrNegativeLabel" text,
    "algorithmIndicatesClusterDone" text,
    "labelOfSeedNode" text,
    "labelOfNodeReturnedByAlgorithm" text,
    "queryNumberForThisSeedNode" text,
    UNIQUE (
        "UUID",
        "seedNode",
        "recordNumberInThisTable")
        /* We used to have in the constraint that
           ("UUID", "seedNode", "queryNumberForThisSeedNode")
           should be unique - but this is false for the huamn trafficking 
           datasets, where we may have multiple near duplicates or
           high confidence matchs prior to the next query to the expert */
    );


CREATE TABLE "algorithmInternalParameters" (
    "UUID" text NOT NULL,
    "totalNumberRecordCount" int,
    "recordNumberInThisTable" int,
    "stateNumber" text,
    "categoryOfParameter" text,
    "specificParameterName" text,
    "parameterValue" text,
    UNIQUE (
        "UUID",
        "stateNumber",
        "categoryOfParameter",
        "specificParameterName")
    );

CREATE TABLE "algorithmRunParameters" ( 
    "UUID" text NOT NULL,
    "totalNumberRecordCount" int,
    "recordNumberInThisTable" int,
    "parameterName" text,
    "parameterValue" text,
    UNIQUE (
        "UUID",
        "parameterName")
    );



