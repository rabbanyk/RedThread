-- the end result of this is put into the temporary table ""numberPositivesPerRun",
--     which lists the UUID of each run, and the resulting array of the number of 
--     non-nearDuplicate, non-seed node, unique found nodes that are positive.





--V~V~V~V~V~V~V~V~V~VV~V~V~~V~V~VV~V~V~~V~V~V~~V~V~V~V~V~V~V~V~V~V~V~V~V~~V~V~V~V~V~V~V~~V~V
--                               Forming count table
--------------------------------------------------------------------------------------------



CREATE TEMPORARY TABLE "tableOfUniqueFoundNodesForEachSeedNode" 
    ("UUID" text, 
     "seedNode" text, 
     "foundNode" text,
     "returnedNodePositiveOrNegativeLabel" text,
     "categoryOfNodeEvaluation" text,
     "firstRecordNumberInTableWhereFound" int ,
      CONSTRAINT uniqueSeedFoundNodePairs UNIQUE ("UUID", "seedNode", "foundNode")
    );
-- below gets the most recent results from runs with certain sets of parametes.
INSERT INTO "tableOfUniqueFoundNodesForEachSeedNode"  
    ("UUID" , "seedNode", "foundNode", "firstRecordNumberInTableWhereFound")
SELECT a."UUID", a."seedNode", a."nodeReturnedByAlgorithm", min(a."recordNumberInThisTable") 
FROM "clusteringResults" a 
GROUP BY (a."UUID", a."seedNode", a."nodeReturnedByAlgorithm");
UPDATE "tableOfUniqueFoundNodesForEachSeedNode"
SET "categoryOfNodeEvaluation" = "clusteringResults"."categoryOfNodeEvaluation", 
    "returnedNodePositiveOrNegativeLabel" = "clusteringResults"."returnedNodePositiveOrNegativeLabel"
FROM "clusteringResults"
WHERE "tableOfUniqueFoundNodesForEachSeedNode"."UUID" = "clusteringResults"."UUID" AND 
      "tableOfUniqueFoundNodesForEachSeedNode"."seedNode" = "clusteringResults"."seedNode" AND 
      "tableOfUniqueFoundNodesForEachSeedNode"."foundNode" = "clusteringResults"."nodeReturnedByAlgorithm" AND 
      "tableOfUniqueFoundNodesForEachSeedNode"."firstRecordNumberInTableWhereFound" = "clusteringResults"."recordNumberInThisTable";


----------------finding the number of positives and negatives-----------------------


CREATE TEMPORARY TABLE "numberPositiveAndNegativePerSeedNode" (
    "UUID" text,
    "seedNode" text,
    "numberPositiveForThisSeedNode" int DEFAULT 0,
    "numberNegativeForThisSeedNode" int DEFAULT 0,
    CONSTRAINT uniqueUUIDAndSeedNodePairs UNIQUE("UUID", "seedNode") );
INSERT INTO "numberPositiveAndNegativePerSeedNode"
SELECT a."UUID", a."seedNode"
FROM "tableOfUniqueFoundNodesForEachSeedNode" a
GROUP BY (a."UUID" , a."seedNode");
UPDATE "numberPositiveAndNegativePerSeedNode" b
SET  "numberPositiveForThisSeedNode" = (
    SELECT COALESCE( COUNT(*) , 0)
    FROM "tableOfUniqueFoundNodesForEachSeedNode" a
    WHERE a."categoryOfNodeEvaluation" != E'nearDuplicate' AND
          a."seedNode" != a."foundNode" AND
          a."returnedNodePositiveOrNegativeLabel" = E'POSITIVE' AND
          a."UUID" = b."UUID" AND
          a."seedNode" = b."seedNode"
    ),
      "numberNegativeForThisSeedNode" = (
    SELECT COALESCE( COUNT(*) , 0)
    FROM "tableOfUniqueFoundNodesForEachSeedNode" a
    WHERE a."categoryOfNodeEvaluation" != E'nearDuplicate' AND
          a."seedNode" != a."foundNode" AND
          a."returnedNodePositiveOrNegativeLabel" = E'NEGATIVE' AND
          a."UUID" = b."UUID" AND
          a."seedNode" = b."seedNode"
    );


CREATE TEMPORARY TABLE "numberPositivesAndNegativesPerRun" (
    "UUID" text PRIMARY KEY,
    "numberPositivesFoundForThisRun" int[],
    "numberNegativesFoundForThisRun" int[] 
    );
INSERT INTO "numberPositivesAndNegativesPerRun" (
                 "UUID", 
                 "numberPositivesFoundForThisRun", 
                 "numberNegativesFoundForThisRun")
    -- note that, critically below we order
    -- the positive counts and the negative counts by the seed node, so that 
    -- the i^{th} element from each correspond to the same seed node.
    -- Note that to calculate the precision correctly, this ordering correspondence does need to 
    -- be maintain for each seed node...
SELECT 
    "UUID", 
    array_agg("numberPositiveForThisSeedNode" ORDER BY "seedNode"), 
    array_agg("numberNegativeForThisSeedNode" ORDER BY "seedNode")
FROM "numberPositiveAndNegativePerSeedNode"
GROUP BY "UUID";


----------------------------------------------------------------------


CREATE TABLE "preminantNumberPositivesAndNegativesPerRun" ("UUID" text, "numberPositivesFoundForThisRun" integer[], "numberNegativesFoundForThisRun" integer[]);
INSERT INTO "preminantNumberPositivesAndNegativesPerRun" (
    "UUID",
    "numberPositivesFoundForThisRun", 
    "numberNegativesFoundForThisRun"
) SELECT "UUID", "numberPositivesFoundForThisRun", "numberNegativesFoundForThisRun"
FROM "numberPositivesAndNegativesPerRun";


CREATE TABLE "backUp_2_7_2018_preminantNumberPositivesAndNegativesPerRun" ("UUID" text, "numberPositivesFoundForThisRun" integer[], "numberNegativesFoundForThisRun" integer[]);
INSERT INTO "backUp_2_7_2018_preminantNumberPositivesAndNegativesPerRun" (
    "UUID",
    "numberPositivesFoundForThisRun", 
    "numberNegativesFoundForThisRun"
) SELECT "UUID", "numberPositivesFoundForThisRun", "numberNegativesFoundForThisRun"
FROM "numberPositivesAndNegativesPerRun";


DROP TABLE "tableOfUniqueFoundNodesForEachSeedNode";
DROP TABLE "numberPositiveAndNegativePerSeedNode";
--^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^^__^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^_^


