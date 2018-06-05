import os;
from getPathToThisDirectory import getPathToThisDirectory;
import re;
from contracts import *;

def getGitCommitHash(UUID):
    requires(isinstance(UUID, str));
    requires(re.match("^[0-9_]+$", UUID) != None); # we requires the UUID to
        # be a numeric string perhaps with underscores. We primarly require this
        # to ensure that a file name we generate below will be accepted by the 
        # system - no space, no special character, etc....)

    pathToThisDirectory = getPathToThisDirectory();
    assert(isinstance(pathToThisDirectory , str));
    assert(len(pathToThisDirectory) > 0);
    assert(pathToThisDirectory[0] == "/"); # we require the path name an absolute path
    assert(pathToThisDirectory[-1] == "/"); # we require that pathToThisDirectory specify a directory.

    # Below we name the file with the UUID so that if multiple processes are running this same
    #     code in the same directory, they do not conflict over generating then deleting the file.
    pathToFileToSaveCommitInfo = pathToThisDirectory + "SQLResultWrittingCode/tempForGitHash" + UUID  +".txt"
    # tempted to make the file not visible with .tempForGitHash
    successOfQuery = os.system("git log -n1 > " + pathToFileToSaveCommitInfo);
    if(successOfQuery != 0): # zero means no error
        return None;
    assert(successOfQuery == 0);
    fh = open(pathToFileToSaveCommitInfo, "r");
    firstLine = fh.readline();
    fh.close();
    assert(isinstance(firstLine, str));
    assert(len(firstLine) > 8); # at least 7 characters for the beginning "commit "
        # and one character for the ending newline.
    assert(firstLine[0:7] == "commit ");
    assert(firstLine[-1] == "\n");

    proposedCommitHash = firstLine[7:-1];
    # below assert is checking that we extracted the full hash in the range
    assert("commit " + proposedCommitHash + "\n" == firstLine);
    # the below assert checks that the proposed hash is an alphanumeric string from 
    # beginning to end
    assert(re.match("^[a-zA-Z0-9]*$", proposedCommitHash) != None);

    os.system("rm " + pathToFileToSaveCommitInfo); # removing the temporary file after having
        # read it.

    return proposedCommitHash;
