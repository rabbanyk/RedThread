from datetime import datetime;

def getStringTimeNow():
    dateTimeString = str(datetime.now());
    timeFieldSeperator = "_"
    specialCharactersToRemove = ['-',' ', '.', ":"];
    for thisSpecialCharacter in specialCharactersToRemove:
        dateTimeString = dateTimeString.replace(thisSpecialCharacter, timeFieldSeperator);
    assert(all([ dateTimeString.count(x) == 0  for x in specialCharactersToRemove]));
    return dateTimeString;
