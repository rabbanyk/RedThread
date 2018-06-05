positiveLabel = 1;
negativeLabel = 0;

# NOTE: considering the fact that this file now contains a function, we might want to 
#     change the name to reflect the fact that it contains more than just the definition of
#     the labels.....
def isProperLabel(proposedLabel):
    if(not isinstance(proposedLabel, int)):
        return False;
    elif(proposedLabel != positiveLabel and proposedLabel != negativeLabel):
        return False;
    else:
        return True;
