from labelNames import *; # used for dictMappingExpertFeedbackToString below.
stringFor_nonNearDuplicateNonHighConfidenceMatch = "nonNearDuplicateNonHighConfidenceMatch";
stringFor_highConfidenceMatch = "highConfidenceMatch";
stringFor_nearDuplicate = "nearDuplicate";
stringFor_algorithmIndicatesClusterDone = "algorithmIndicatesClusterDone";
dictMappingExpertFeedbackToString = {positiveLabel : "POSITIVE", negativeLabel : "NEGATIVE"};
dictMappingBoolToString = {False : "False", True : "True"}; # This seems trivial, but it ensures that
    # we don't slip up and do write the same string for the same thing to the database.
