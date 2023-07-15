import json

class ConfigParser:
    def __init__(self):
        # Dictionary
        self.data = {}
        
    def readFile(self, fileName, readAsJson=True):
        with open(fileName, encoding="utf8") as F:
            data = F.read()
        return json.loads(data) if readAsJson == True else eval(data)
        
    def writeFile(self, fileName, fileContent) -> None:
        with open(fileName, "w", encoding="utf8") as F:
            json.dumps(fileContent, F)