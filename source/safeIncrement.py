from contracts import *;

def safeIncrement(intToIncrement):
    requires(isinstance(intToIncrement, int));
    requires(intToIncrement >= 0);
    if(intToIncrement + 1 > intToIncrement):
        intToIncrement = intToIncrement + 1;
    else: # This case is extremely unlikely to occur, but it is always good to
        # check....
        raise Exception(); # TODO: output an error string.
    ensures(isinstance(intToIncrement, int));
    ensures(intToIncrement >= 1 ); # We explicitly added one to a 
        # non-negative integer and tested that overflow did not occur.
    return intToIncrement;



