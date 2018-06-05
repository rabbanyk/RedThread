import random;

from datetime import datetime;
from time import sleep; # to force unique timestamps, and possibly unique random seeds....

from getStringTimeNow import getStringTimeNow;

def getLargeRandomInteger():
    sleep(0.05);
    maxRandomValue = 1000000;
    thisRandomString = str(random.randint(0, maxRandomValue));
    # below, we zero-pad the result to keep all the UUIDs the same length in terms of number of characters.
    while(len(thisRandomString) < len(str(maxRandomValue))):
        thisRandomString = "0" + thisRandomString;
    return thisRandomString;

def myUUIDImplementation():
    numberOfRandomParts = 6;
    myUUID = getStringTimeNow().replace("_", "");
    for index in range(0, numberOfRandomParts):
        myUUID = myUUID + "_" + getLargeRandomInteger();
    assert(myUUID.count("_") == numberOfRandomParts); # this should hold since we insert one underscore for 
        # each random part, and the rest had no underscores.
    return myUUID;
