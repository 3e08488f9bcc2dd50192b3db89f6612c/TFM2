import asyncio
import psutil
import pymongo
import random
import os
import re
import string
from api.Api import Api
from colorconsole import win
from src import Client
from src.modules import Config, Exceptions


class Server(asyncio.Transport):
    def __init__(self):
        # Integer
        self.lastPlayerID = 0
        self.lastCafeTopicID = 0
        self.lastCafePostID = 0
        self.lastChatID = 0
    
        # Float/Double
    
        # String
    
        # Dictionary
        self.chatMessages = {}
        self.chats = {}
        self.connectedCounts = {}
        self.moderatedCafeTopics = {}
        self.rooms = {}
        self.players = {}
        
        # List
        self.userBanCache = []
        self.userMuteCache = []

        # Loops
        self.loop = asyncio.get_event_loop()
        
        # Other
        self.config = Config.ConfigParser()
        self.exceptionManager = Exceptions.ServeurException()
        #self.api = None
        self.Cursor = None
                
        # Informations
        self.antiCheatInfo = self.config.readFile("./include/settings/anticheat.json")
        self.badIPS = self.config.readFile("./include/settings/bad_ips.json")
        self.badWords = self.config.readFile("./include/settings/bad_words.json")
        self.captchaList = self.config.readFile("./include/settings/captchas.json", False)
        self.eventInfo = self.config.readFile("./include/settings/event.json")
        self.serverInfo = self.config.readFile("./include/settings/gameinfo.json")
        self.serverLanguagesInfo = self.config.readFile("./include/settings/languages.json")
        self.swfInfo = self.config.readFile("./include/settings/swf_properties.json")
        self.titleInfo = self.config.readFile("./include/settings/titles.json", False)

    def checkAlreadyExistingGuest(self, playerName):
        """
        Checks if guest with given name exist and generate a new name if exist.
        """
        playerName = re.sub('[^0-9a-zA-Z]+', '', playerName)
        if len(playerName) == 0 or self.checkConnectedUser("*" + playerName):
            playerName = "*Souris_%s" %("".join([random.choice(string.ascii_lowercase) for x in range(4)]))
        else:
            playerName = "*" + playerName
        return playerName

    def checkConnectedUser(self, playerName):
        """
        Checks if user is online.
        """
        return playerName in self.players
    
    def checkExistingUser(self, playerName):
        """
        Checks if user exist in the database.
        """
        return self.Cursor['users'].find_one({'Username':playerName}) != None
        
    def checkMessage(self, message):
        """
        Checks if message contains any bad word.
        """
        i = 0
        while i < len(self.badWords):
            if re.search("[^a-zA-Z]*".join(self.badWords[i]), message.lower()):
                return True
            i += 1
        return False

    def getBanInfo(self, playerName):
        """
        Get additional information about playerName's ban.
        """
        rs = self.Cursor['usertempban'].find_one({'Username':playerName})
        if rs:
            return [rs["Reason"], rs["Time"]]
        else:
            return ["", 0]

    def getEmailAddressCount(self, emailAddress):
        """
        Get total count of players with same email address.
        """
        return len(list(self.Cursor['users'].find({'Email':emailAddress})))

    def getConfigID(self, config_id):
        try:
            r1 = self.Cursor['config'].find()
            return r1[0][config_id]
        except:
            print(f"[ERREUR] Unable to find the game config. Are you sure you added it to mongodb? Unable to find {config_id}")
            exit(0)

    def getMuteInfo(self, playerName):
        """
        Get additional information about playerName's mute.
        """
        rs = self.Cursor['usertempmute'].find_one({'Username':playerName})
        if rs:
            return [rs['Reason'], rs['Time']]
        else:
            return ["", 0]

    def getPlayerID(self, playerName):
        """
        Receive the player id.
        """
        if playerName in self.players:
            return self.players[playerName].playerID
        else:
            rs = self.Cursor['users'].find_one({'Username':playerName})
            if rs:
                return rs['PlayerID']
            else:
                return -1

    def removeBan(self, playerName):
        """
        Removes ban on given player.
        """
        if playerName in self.userBanCache:
            self.userBanCache.remove(playerName)
        self.Cursor['usertempban'].delete_one({'Username':playerName})
    
    def removeMute(self, playerName):
        """
        Removes mute on given player.
        """
        if playerName in self.userMuteCache:
            self.userMuteCache.remove(playerName)
        self.Cursor['usertempmute'].delete_one({'Username':playerName})

    def sendBanPunishment(self, playerName, hours, reason, modName, silent=False): #########
        pass

    def sendConnectionInformation(self) -> None:
        """
        Send additional information in the console when the server was started.
        """
        T = win.Terminal()
        T.set_title("Transformice is online!")
    
        T.cprint(15, 0, "[#] Server Debug: ")
        T.cprint(1,  0,  f"{self.serverInfo['server_debug']}\n")
        
        T.cprint(15, 0, "[#] Initialized ports: ")
        T.cprint(10, 0, f"{self.serverInfo['game_ports']}\n")
        
        T.cprint(15, 0, "[#] Server Name: ")
        T.cprint(12, 0, f"{self.serverInfo['game_name']}\n")
        
        T.cprint(15, 0, "[#] Server IP: ")
        T.cprint(13, 0, f"{self.serverInfo['game_ip']}\n")
        if self.serverInfo["server_debug"]:
            T.cprint(15, 0, "[#] Server Version: ")
            T.cprint(14, 0, f"1.{self.swfInfo['version']}\n")
            
            T.cprint(15, 0, "[#] Server Connection Key: ")
            T.cprint(13, 0, f"{self.swfInfo['ckey']}\n")
            
            if len(self.swfInfo["packetKeys"]) > 0:
                T.cprint(15, 0, "[#] Server Packet_Keys: ")
                T.cprint(9,  0,  f"{self.swfInfo['packetKeys']}\n")
        
        T.cprint(15, 0, "[#] Minimum Players (Farm): ")
        T.cprint(2,  0,  f"{self.serverInfo['minimum_players']}\n")
        
        T.cprint(15, 0, "[#] Server Maximum Players: ")
        T.cprint(3,  0,  f"{self.serverInfo['maximum_players']}\n\n")
        
        T.cprint(15, 0, "[#] CPU Usage: ")
        T.cprint(5,  0,  f"{round(psutil.cpu_percent())}%\n")
        
        T.cprint(15, 0, "[#] Memory Usage: ")
        T.cprint(4,  0,  f"{round(psutil.virtual_memory().percent)}%\n")
        
        T.cprint(15, 0, "")
        return

    def sendStaffMessage(self, message, minLevel, tab=False) -> None:
        """
        Send a private message in #Server channel.
        
        Arguments:
        message - message context
        minLevel - minimum level to see the message
        """
        for client in self.players.copy().values():
            if client.privLevel >= minLevel:
                client.sendServerMessage(message, tab)

    def startServer(self) -> None:
        """
        Obviously
        """
        if self.serverInfo["db_password"] != "":
            self.Cursor = pymongo.MongoClient(f"mongodb://{self.serverInfo['db_username']}:{self.serverInfo['db_password']}@{self.serverInfo['db']}")['transformice']
        else:
            self.Cursor = pymongo.MongoClient(f"mongodb://{self.serverInfo['db']}")['transformice']
        
        self.lastPlayerID = self.getConfigID("lastPlayerID")
        self.lastCafeTopicID = self.getConfigID("lastCafeTopicID") # OK
        self.lastCafePostID = self.getConfigID("lastCafePostID") # OK
        
        
        for port in self.serverInfo["game_ports"]:
            self.loop.run_until_complete(self.loop.create_server(lambda: Client.Client(self, self.Cursor), self.serverInfo["game_ip"], port))
        
        self.sendConnectionInformation()
        self.loop.run_forever()