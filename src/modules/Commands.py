import psutil
import re
import time

class Commands:
    def __init__(self, _client, _server):
        # Instances
        self.client = _client
        self.server = _server
        self.Cursor = _client.Cursor
        
        # Dictionary
        self.commands = {}
        
        # Integer
        self.currentArgsCount = 0
        
        # String
        self.argsNotSplited = ""
        
    def requireOwner(self) -> bool:
        return self.client.playerName in self.server.serverInfo["game_owners"]