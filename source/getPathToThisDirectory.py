# below taken from : https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
# it prints the current directory that this code is found in....

import os
import inspect

def getPathToThisDirectory():
    pathToThisDirectory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())));
    return pathToThisDirectory + "/";
