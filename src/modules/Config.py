import json

class ConfigParser:
    def __init__(self):
        # Dictionary
        self.data = {}
        
    def readFile(self, fileName) -> dict:
        with open(fileName, encoding="utf8") as F:
            data = json.load(F)
        return data
        
    def writeFile(self, fileName, fileContent) -> None:
        with open(fileName, "w", encoding="utf8") as F:
            json.dump(fileContent, F)