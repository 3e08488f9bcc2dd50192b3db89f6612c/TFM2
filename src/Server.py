import asyncio
import psutil
import pygeoip
import pymongo
import random
import os
import re
import string
import src.modules as _module
from Api import apisrv
from colorconsole import win
from importlib import reload
from src import Client, Room
from src.modules import ByteArray, Config, Exceptions
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils

class Server(asyncio.Transport):
    def __init__(self):
        # Integer
        self.lastPlayerID = 0
        self.lastCafeTopicID = 0
        self.lastCafePostID = 0
        self.lastChatID = 0
        self.lastReportID = 0
        self.lastTribeID = 0
    
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
        self.Cursor = None
        self.geoIPData = pygeoip.GeoIP('./include/GeoIP.dat')
        self.exceptionManager = Exceptions.ServeurException()
        self.rebootTimer = None
                
        # Informations
        self.antiCheatInfo = self.config.readFile("./include/settings/anticheat.json")
        self.badIPS = self.config.readFile("./include/settings/bad_ips.json")
        self.badWords = self.config.readFile("./include/settings/bad_words.json")
        self.captchaList = self.config.readFile("./include/settings/captchas.json", False)
        self.eventInfo = self.config.readFile("./include/settings/event.json")
        self.japanExpoCodes = self.config.readFile("./include/settings/codes.json")
        self.serverPartners = self.config.readFile("./include/settings/partners.json")
        self.serverInfo = self.config.readFile("./include/settings/gameinfo.json")
        self.serverLanguagesInfo = self.config.readFile("./include/settings/languages.json")
        self.serverReports = self.config.readFile("./include/settings/reports.json")
        self.swfInfo = self.config.readFile("./include/settings/swf_properties.json")
        self.titleInfo = self.config.readFile("./include/settings/titles.json", False)

    def banPlayer(self, playerName, hours, reason, modName, silent):
        player = self.players.get(playerName)
        if self.checkExistingUser(playerName):
            if modName == "ServeurBan":
                msg = f"The player <BV>{playerName}</BV> was banned for {hours} hour(s). Reason: {reason}" # Vote Populaire.
            elif self.checkConnectedUser(playerName):
                msg = f"{modName} banned the player <BV>{playerName}</BV> for {hours}h ({reason})."
            else:
                msg = f"{modName} offline banned the player <BV>{playerName}</BV> for {hours}h ({reason})."
            self.removeBan(playerName, "ServeurBan")
            
            if playerName in self.serverReports:
                self.serverReports[playerName]["state"] = "banned"
                self.serverReports[playerName]['banhours'] = hours
                self.serverReports[playerName]['banreason'] = reason
                self.serverReports[playerName]['bannedby'] = modName

            self.userBanCache.append(playerName)
            self.Cursor['usertempban'].insert_one({'Username':playerName,'Reason':reason,'Time':int(Utils.getTime() + (hours * 60 * 60))})
            if player != None:
                player.sendBanMessage(hours, reason, silent)
            self.sendStaffMessage(msg, 7, False)
            self.saveCasier(playerName, "BAN", modName, hours, reason)
            self.receiveKarma(playerName)

    def checkAlreadyExistingGuest(self, playerName) -> str:
        """
        Checks if guest with given name exist and generate a new name if exist.
        """
        playerName = re.sub('[^0-9a-zA-Z]+', '', playerName)
        if len(playerName) == 0 or self.checkConnectedUser("*" + playerName):
            playerName = "*Souris_%s" %("".join([random.choice(string.ascii_lowercase) for x in range(4)]))
        else:
            playerName = "*" + playerName
        return playerName

    def checkConnectedUser(self, playerName) -> bool:
        """
        Checks if user is online.
        """
        return playerName in self.players
    
    def checkExistingUser(self, playerName) -> bool:
        """
        Checks if user exist in the database.
        """
        return self.Cursor['users'].find_one({'Username':playerName}) != None
        
    def checkExistingTribe(self, tribeName) -> bool:
        """
        Checks if tribe exist in the database.
        """
        return self.Cursor['tribe'].find_one({'Name':tribeName}) != None
        
    def checkMessage(self, message) -> bool:
        """
        Checks if message contains any bad word.
        """
        i = 0
        while i < len(self.badWords):
            if re.search("[^a-zA-Z]*".join(self.badWords[i]), message.lower()):
                return True
            i += 1
        return False

    def getAdventureInfo(self, adv_id):
        for info in self.eventInfo["adventures"]:
            if info["id"] == adv_id:
                return info
        return []

    def getBanInfo(self, playerName) -> list:
        """
        Get additional information about playerName's ban.
        """
        rs = self.Cursor['usertempban'].find_one({'Username':playerName})
        if rs:
            return [rs["Reason"], rs["Time"]]
        else:
            return []

    def getEmailAddressCount(self, emailAddress) -> int:
        """
        Get total count of players with same email address.
        """
        return len(list(self.Cursor['users'].find({'Email':emailAddress})))

    def getConfigID(self, config_id) -> int:
        try:
            r1 = self.Cursor['config'].find()
            return r1[0][config_id]
        except:
            print(f"[ERREUR] Unable to find the game config. Are you sure you added it to mongodb? Unable to find {config_id}")
            exit(0)

    def getMuteInfo(self, playerName) -> list:
        """
        Get additional information about playerName's mute.
        """
        rs = self.Cursor['usertempmute'].find_one({'Username':playerName})
        if rs:
            return [rs['Reason'], rs['Time']]
        else:
            return []

    def getPlayerAvatar(self, playerName) -> int:
        """
        Receive the player avatar.
        """
        if playerName in self.players:
            return self.players[playerName].avatar
        else:
            rs = self.Cursor['users'].find_one({'Username':playerName})
            if rs:
                return rs['Avatar']
            else:
                return 0

    def getPlayerID(self, playerName) -> int:
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

    def getPlayerIP(self, playerName) -> str:
        """
        Receive the player's ip address.
        """
        player = self.players.get(playerName)
        return Utils.EncodeIP(player.ipAddress) if player != None else "offline"

    def getPlayerName(self, playerID) -> str:
        """
        Receive the player name
        """
        if '@' in playerID:
            rs = self.Cursor['users'].find_one({'Email':playerID})
        else:
            rs = self.Cursor['users'].find_one({'PlayerID':playerID})
        return rs['Username'] if rs else ""

    def getPlayerTribeCode(self, playerName) -> int:
        """
        Receive the player's tribe unique code.
        """
        player = self.server.players.get(playerName)
        if playerName:
            return player.tribeCode

        rs = self.Cursor['users'].find_one({'Username':playerName})
        return rs['TribeCode'] if rs else 0

    def getPlayerTribeRank(self, playerName) -> str:
        """
        Receive the player's rank in the tribe.
        """
        player = self.players.get(playerName)
        if player != None:
            return self.players[playerName].tribeRank
        rs = self.Cursor['users'].find_one({'Username':playerName})
        return rs['TribeRank'] if rs else ""

    def getProfileColor(self, playerName) -> str:
        """
        Receive the player's profile color.
        """
        if playerName.privLevel == 9:
            return "EB1D51"
        elif playerName.privLevel == 8:
            return "BABD2F"
        elif playerName.privLevel == 6 or playerName.isMapCrew:
            return "2F7FCC"
        elif playerName.privLevel == 5 or playerName.isFunCorpTeam:
            return "F89F4B"
        return "009D9D"

    def getTribeMembers(self, tribeCode) -> list:
        """
        Receive all members from the tribe.
        """
        rs = self.Cursor['tribe'].find_one({'Code':tribeCode})
        return rs['Members'].split(",") if rs else []

    def getTribeHistorique(self, tribeCode) -> str:
        """
        Receive the tribe history.
        """
        rs = self.Cursor['tribe'].find_one({'Code':tribeCode})
        return rs['Historique'] if rs else ""

    def mumutePlayer(self, playerName, modName):
        player = self.players.get(playerName)
        if player != None:
            self.sendStaffMessage(f"{modName} mumuted {playerName}.", 7)
            self.saveCasier(playerName, "MUMUTE", modName, "", "")
            player.isMumuted = True

    def mutePlayer(self, playerName, hours, reason, modName, silent) -> None:
        player = self.players.get(playerName)
        if player != None:
            self.sendStaffMessage(f"{modName} muted the player {playerName} for {hours}h ({reason})", 7, False)
            self.removeMute(playerName, "ServeurMute")
            
            if playerName in self.serverReports:
                self.serverReports[playerName]['isMuted'] = True
                self.serverReports[playerName]['muteHours'] = hours
                self.serverReports[playerName]['muteReason'] = reason
                self.serverReports[playerName]['mutedBy'] = modName
                
            player.isMuted = True
            player.sendMuteMessage(playerName, hours, reason, silent)
            if not silent:
                player.sendMuteMessage(playerName, hours, reason, False)
            self.userMuteCache.append(playerName)
            self.Cursor['usertempmute'].insert_one({'Username':playerName,'Time':int(Utils.getTime() + (hours * 60 * 60)),'Reason':reason})
            self.saveCasier(playerName, "MUTE", modName, hours, reason)
            self.receiveKarma(playerName)

    def receiveKarma(self, playerName) -> None:
        if playerName in self.serverReports:
            for name in self.serverReports[playerName]["reporters"]:  
                player = self.players.get(name) 
                if player != None:
                    player.playerKarma += 1
                    player.sendServerMessage(f"Your report regarding the player {playerName} has been handled. (karma: {str(player.playerKarma)})", True)

    async def reloadServer(self):
        reload(_module)
        self.config.writeFile("./include/settings/bad_ips.json", self.badIPS)
        self.config.writeFile("./include/settings/bad_words.json", self.badWords)
        self.config.writeFile("./include/settings/codes.json", self.japanExpoCodes)
        self.config.writeFile("./include/settings/partners.json", self.serverPartners)
        self.config.writeFile("./include/settings/reports.json", self.serverReports)
        for player in self.players.copy().values():
            player.updateDatabase()
            await asyncio.sleep(1)
            player.AntiCheat = _module.AntiCheat(player, self)
            player.Cafe = _module.Cafe(player, self)
            player.modoPwet = _module.ModoPwet(player, self)
            player.tribulle = _module.Tribulle(player, self)
            player.Shop = _module.Shop(player, self)
            player.Skills = _module.Skills(player, self)
            player.Packets = _module.Packets(player, self)
            player.Commands = _module.Commands(player, self)
            player.DailyQuests = _module.DailyQuests(player, self)

    def removeBan(self, playerName, modName) -> None:
        """
        Removes ban on given player.
        """
        if playerName in self.serverReports:
            self.serverReports[playerName]["state"] = "online" if self.checkConnectedUser(playerName) else "disconnected"
            self.serverReports[playerName]['banhours'] = 0
            self.serverReports[playerName]['banreason'] = ""
            self.serverReports[playerName]['bannedby'] = ""
        
        if playerName in self.userBanCache:
            self.userBanCache.remove(playerName)
        self.Cursor['usertempban'].delete_one({'Username':playerName})
        if modName != "ServeurBan":
            self.sendStaffMessage(f"{modName} unbanned the player {playerName}.", 7, False)
            self.saveCasier(playerName, "UNBAN", modName, 0, "")
    
    def removeMute(self, playerName, modName) -> None:
        """
        Removes mute on given player.
        """
        if playerName in self.serverReports:
            self.serverReports[playerName]['isMuted'] = False
            self.serverReports[playerName]['muteHours'] = 0
            self.serverReports[playerName]['muteReason'] = ""
            self.serverReports[playerName]['mutedBy'] = ""
        
        if playerName in self.userMuteCache:
            self.userMuteCache.remove(playerName)
        self.Cursor['usertempmute'].delete_one({'Username':playerName})
        if modName != "ServeurMute":
            self.sendStaffMessage(f"{modName} unmuted the player {playerName}.", 7, False)
            self.saveCasier(playerName, "UNMUTE", modName, 0, "")

    def saveCasier(self, playerName, state, mod, duration, reason="") -> None:   
        self.Cursor['casierlog'].insert_one({'Name':playerName,'IP':self.getPlayerIP(playerName),'State':state,'Timestamp':Utils.getTime(),'Moderator':mod,'Time':duration,'Reason':reason})

    def sendConnectionInformation(self) -> None:
        """
        Send additional information in the console when the server was started.
        """
        T = win.Terminal()
        T.set_title("Transformice is online!")
    
        T.cprint(15, 0, "[#] Server Debug: ")
        T.cprint(1,  0,  f"{self.serverInfo['server_debug']}\n")
        
        T.cprint(15, 0, "[#] Server Initialized ports: ")
        T.cprint(10, 0, f"{self.serverInfo['server_ports']}\n")
        
        T.cprint(15, 0, "[#] Server Name: ")
        T.cprint(12, 0, f"{self.serverInfo['game_name']}\n")
        
        T.cprint(15, 0, "[#] Server IP: ")
        T.cprint(13, 0, f"{self.serverInfo['server_ip']}\n")
        if self.serverInfo["server_debug"]:
            T.cprint(15, 0, "[#] Server Version: ")
            T.cprint(14, 0, f"1.{self.swfInfo['version']}\n")
            
            T.cprint(15, 0, "[#] Server Connection Key: ")
            T.cprint(11, 0, f"{self.swfInfo['ckey']}\n")
            
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

    def sendMessageAll(self, minLevel, message):
        for player in self.players.copy().values():
            if player.privLevel == minLevel:
                player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
            else:
                if minLevel == 3 and player.isFashionSquad:
                    player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
                elif minLevel == 4 and player.isLuaCrew:
                    player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
                elif minLevel == 5 and player.isFunCorpTeam:
                    player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
                elif minLevel == 6 and player.isMapCrew:
                    player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
                elif minLevel == 7 and player.privLevel >= 7:
                    player.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())

    def sendServerRestart(self, no=0, sec=1):
        if sec > 0 or no != 5:
            self.sendServerRestartSEC(120 if no == 0 else (60 if no == 1 else (30 if no == 2 else (20 if no == 3 else (10 if no == 4 else sec)))))
            if self.rebootTimer != None:
                self.rebootTimer.cancel()
            self.rebootTimer = self.loop.call_later(60 if no == 0 else 30 if no == 1 else 10 if no == 2 or no == 3 else 1, lambda: self.sendServerRestart(no if no == 5 else no + 1, 9 if no == 4 else sec - 1 if no == 5 else 0))
        return

    def sendServerRestartSEC(self, seconds):
        for player in self.players.copy().values():
            player.sendPacket(TFMCodes.game.send.Server_Restart, ByteArray().writeInt(seconds * 1000).toByteArray())
        if seconds < 1:
            for player in self.players.copy().values():
                player.transport.close()
            self.Cursor['loginlogs'].delete_many({})
            self.Cursor['commandlog'].delete_many({})
            os._exit(5)

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


    def translateMessage(self, message):
        return ""


    def recommendRoom(self, langue=""):
        return "1"

    def loadShopList(self):
        return
        
    def addClientToRoom(self, player, roomName): # Cooming soon
        if roomName in self.rooms:
            self.rooms[roomName].addClient(player)
        else:
            room = Room.Room(self, roomName, player)
            self.rooms[roomName] = room
            room.addClient(player, True)
            #if room.minigame != "":
            #    room.loadLuaModule(room.minigame)
            #else:
            #    room.mapChange2()

    def startServer(self) -> None:
        """
        Obviously
        """
        self.loop.run_until_complete(apisrv.startApi(self).startServer())
        
        
        if self.serverInfo["db_password"] != "":
            self.Cursor = pymongo.MongoClient(f"mongodb://{self.serverInfo['db_username']}:{self.serverInfo['db_password']}@{self.serverInfo['db']}")['transformice']
        else:
            self.Cursor = pymongo.MongoClient(f"mongodb://{self.serverInfo['db']}")['transformice']
        
        self.lastPlayerID = self.getConfigID("lastPlayerID")
        self.lastCafeTopicID = self.getConfigID("lastCafeTopicID") # OK
        self.lastCafePostID = self.getConfigID("lastCafePostID") # OK
        self.lastTribeID = self.getConfigID("lastTribeID") # OK
        
        
        for port in self.serverInfo["server_ports"]:
            self.loop.run_until_complete(self.loop.create_server(lambda: Client.Client(self, self.Cursor), self.serverInfo["server_ip"], port))
        self.sendConnectionInformation()
                
        self.loop.run_forever()