import psutil
import re
import time
from src.modules import ByteArray
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils

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
        self.commandName = ""
        
        self.parseCommands()
        
    def command(self, func=None, tribe=False, args=0, level=0, owner=False, alies=[], reqrs=[]): ###########
        if not func:
            reqrs=[]
            if tribe > 0: reqrs.append(['tribe',tribe])
            if args > 0: reqrs.append(['args',args])
            if level > 0: reqrs.append(['level',(level)])
            if owner: reqrs.append(['owner'])
            return lambda x: self.command(x,tribe,args,level,owner,alies,reqrs)
        else:
            for i in alies + [func.__name__]: self.commands[i] = [reqrs,func]
        
    async def parseCommand(self, command) -> None:###########
        values = command.split(" ")
        command = values[0].lower()
        args = values[1:]
        self.commandName = command
        self.currentArgsCount = len(args)
        self.argsNotSplited = " ".join(args)
        self.Cursor['commandlog'].insert_one({'Time':Utils.getTime(),'Username':self.client.playerName,'Command':command})
        if command in self.commands:
            for i in self.commands[command][0]: 
                if i[0] == "args":
                    if not self.requireArgs(i[1]): return
                elif i[0] == "owner":
                    if not self.requireOwner(): return
                elif i[0] == "level": 
                    if not self.requireLevel(i[1]): return
                elif i[0] == "tribe":
                    if not self.requireTribePerm(i[1]):
                        pass
                        #if command in ["inv", "invkick", "neige"]: # special tribe commands.
                        #    return
                        #elif not (self.client.privLevel > 5 or self.client.room.roomName == "*strm_" + self.client.playerName or (self.client.room.isFuncorp == True and (self.client.privLevel == 4 or self.client.isFunCorpPlayer))):
                        #    return
            await self.commands[command][1](self, *args)
        
    def requireArgs(self, arguments):
        if self.currentArgsCount < arguments:
            self.client.exceptionManager.Invoke("moreargs")
            return False
        return self.currentArgsCount == arguments
        
    def requireLevel(self, level=0):###########
        return True
        
    def requireOwner(self) -> bool:
        return self.client.playerName in self.server.serverInfo["game_owners"]
        
    def requireTribePerm(self, permId) -> bool: ###########
        return False
        
    def parseCommands(self):
# Guest / Souris Commands
        @self.command(alies=['profil','perfil','profiel'])
        async def profile(self, name=''):
            self.client.sendProfile(name if name else self.client.playerName)
    
        @self.command(alies=["temps"])
        async def time(self):
            self.client.playerTime += abs(Utils.getSecondsDiff(self.client.loginTime))
            self.client.loginTime = Utils.getTime()
            temps = map(int, [self.client.playerTime // 86400, self.client.playerTime // 3600 % 24, self.client.playerTime // 60 % 60, self.client.playerTime % 60])
            self.client.sendLangueMessage("", "$TempsDeJeu", *temps)
            
        
# Player Commands
        @self.command(level=1)
        async def mapcrew(self):
            staffMessage = "$MapcrewPasEnLigne"
            staffMembers = {}
            for player in self.server.players.copy().values():
                if player.privLevel == 6 or player.isMapCrew:
                    if player.defaultLanguage in staffMembers:
                        names = staffMembers[player.defaultLanguage]
                        names.append(player.playerName)
                        staffMembers[player.defaultLanguage] = names
                    else:
                        names = []
                        names.append(player.playerName)
                        staffMembers[player.defaultLanguage] = names
            if len(staffMembers) > 0:
                staffMessage = "$MapcrewEnLigne"
                for member in staffMembers.items():
                    staffMessage += f"<br>[{member[0]}] <BV>{('<BV>, </BV>').join(member[1])}</BV>"
            self.client.sendLangueMessage("", staffMessage)

        @self.command(level=1)
        async def mod(self):
            staffMessage = "$ModoPasEnLigne"
            staffMembers = {}
            for player in self.server.players.copy().values():
                if player.privLevel == 8:
                    if player.defaultLanguage in staffMembers:
                        names = staffMembers[player.defaultLanguage]
                        names.append(player.playerName)
                        staffMembers[player.defaultLanguage] = names
                    else:
                        names = []
                        names.append(player.playerName)
                        staffMembers[player.defaultLanguage] = names
            if len(staffMembers) > 0:
                staffMessage = "$ModoEnLigne"
                for member in staffMembers.items():
                    staffMessage += f"<br>[{member[0]}] <BV>{('<BV>, </BV>').join(member[1])}</BV>"
            self.client.sendLangueMessage("", staffMessage)
            
# Private-Moderator Commands
        @self.command(level=7, args=1)
        async def chatlog(self, playerName):
            if self.server.checkConnectedUser(playerName):
                self.client.ModoPwet.openChatLog(playerName)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
            
        @self.command(level=7, args=1, alies=['chercher'])
        async def find(self, text):
            result = ""
            for player in self.server.players.copy().values():
                if player.playerName.startswith(text):
                    result += "<BV>%s</BV> -> %s\n" %(player.playerName, player.room.name)
            self.client.sendServerMessage(result, True) if result != "" else self.client.sendServerMessage("No results were found.", True)
            
        @self.command(level=7)
        async def iban(self, playerName, hours, *args):
            if self.server.checkExistingUser(playerName):
                if len(self.server.getBanInfo(playerName)) > 0:
                    self.client.exceptionManager.Invoke("useralreadybanned", playerName)
                else:
                    banhours = int(hours) if hours.isdigit() else 24
                    if banhours > 129600:
                        banhours = 129600
                    if banhours <= 0:
                        banhours = 1
                    reason = self.argsNotSplited.split(" ", 2)[2]
                    self.server.banPlayer(playerName, banhours, reason, self.client.playerName, True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")

        @self.command(level=7)
        async def imute(self, playerName, hours, *args):
            if self.server.checkExistingUser(playerName):
                if len(self.server.getMuteInfo(playerName)) > 0:
                    self.client.exceptionManager.Invoke("useralreadymuted", playerName)
                else:
                    reason = self.argsNotSplited.split(" ", 2)[2]
                    mutehours = int(hours) if hours.isdigit() else 1
                    if mutehours > 129600:
                        mutehours = 129600
                    if mutehours <= 0:
                        mutehours = 1
                    self.server.mutePlayer(playerName, mutehours, reason, self.client.playerName, True)
                    self.client.sendServerMessage(f"The player {playerName} got muted", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7)
        async def mute(self, playerName, hours, *args):
            if self.server.checkExistingUser(playerName):
                if len(self.server.getMuteInfo(playerName)) > 0:
                    self.client.exceptionManager.Invoke("useralreadymuted", playerName)
                else:
                    reason = self.argsNotSplited.split(" ", 2)[2]
                    mutehours = int(hours) if hours.isdigit() else 1
                    if mutehours > 129600:
                        mutehours = 129600
                    if mutehours <= 0:
                        mutehours = 1
                    self.server.mutePlayer(playerName, mutehours, reason, self.client.playerName, False)
                    self.client.sendServerMessage(f"The player {playerName} got muted", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7, args=1, alies=['demute'])
        async def unmute(self, playerName):
            player = self.server.players.get(playerName)
            if player:
                if len(self.server.getMuteInfo(playerName)) > 0:
                    self.client.sendServerMessage(f"The player {playerName} got unmuted.", True)
                    self.server.removeMute(playerName, self.client.playerName)
                    player.isMuted = False
                else:
                    self.client.exceptionManager.Invoke("usernotmuted", playerName)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7, args=1, alies=['deban'])
        async def unban(self, playerName):
            if self.server.checkExistingUser(playerName):
                if len(self.server.getBanInfo(playerName)) > 0:
                    self.client.sendServerMessage(f"The player {playerName} got unbanned.", True)
                    self.server.removeBan(playerName, self.client.playerName)
                else:
                    self.client.exceptionManager.Invoke("usernotbanned", playerName)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
# Moderator Commands
        @self.command(level=8)
        async def mm(self, *args):
            self.client.room.sendAll(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(0).writeUTF("").writeUTF(self.argsNotSplited).writeShort(0).writeByte(0).toByteArray())
            
