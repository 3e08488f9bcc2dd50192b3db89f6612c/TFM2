import base64
import datetime
import hashlib
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
        
    def command(self, func=None, tribe=False, args=0, level=0, owner=False, roomStrm=False, lua=False, mc=False, fc=False, fs=False, alies=[], reqrs=[]):
        if not func:
            reqrs=[]
            if tribe > 0: reqrs.append(['tribe',tribe])
            if args > 0: reqrs.append(['args',args])
            if level > 0: reqrs.append(['level',(level,roomStrm,lua,mc,fc,fs)])
            if owner: reqrs.append(['owner'])
            return lambda x: self.command(x,tribe,args,level,owner,roomStrm,lua,mc,fc,fs,alies,reqrs)
        else:
            for i in alies + [func.__name__]: self.commands[i] = [reqrs,func]
        
    async def parseCommand(self, command) -> None:
        values = command.split(" ")
        command = values[0].lower()
        args = values[1:]
        self.args = args
        self.commandName = command
        self.currentArgsCount = len(args)
        self.argsNotSplited = " ".join(args)
        self.Cursor['commandlog'].insert_one({'Time':Utils.getTime(),'Username':self.client.playerName,'Command':command})
        if command in self.commands:
            for i in self.commands[command][0]: 
                if i[0] == "level": 
                    if not self.requireLevel(*i[1]): return
                elif i[0] == "args":
                    if not self.requireArgs(i[1]): return
                elif i[0] == "tribe":
                    if not self.requireTribePerm(i[1]):
                        return
                else:
                    if not self.requireOwner(): return
            await self.commands[command][1](self, *args)
        
    def requireArgs(self, arguments):
        if self.currentArgsCount < arguments:
            self.client.exceptionManager.Invoke("moreargs")
            return False
        return self.currentArgsCount == arguments
        
    def requireLevel(self, level=0, roomStrm=False, lua=False, mc=False, fc=False, fs=False):###########
        return True
        
    def requireOwner(self) -> bool:
        return self.client.playerName in self.server.serverInfo["game_owners"]
        
    def requireTribePerm(self, permId) -> bool:
        if self.client.room.isTribeHouse:
            rankInfo = self.client.tribeRanks.split(";")
            rankName = rankInfo[self.client.tribeRank].split("|")
            return int(rankName[2], 10) & permId
        return False
        
    def parseCommands(self):
# Guest / Souris Commands
        @self.command
        async def ping(self):
            self.client.sendPing()
            self.client.sendServerMessage(f"ping ~{int(self.client.ping)}", True)

        @self.command(alies=['profil','perfil','profiel'])
        async def profile(self, name=''):
            self.client.sendProfile(name if name else self.client.playerName)
    
        @self.command(alies=["temps"])
        async def time(self):
            self.client.playerTime += abs(Utils.getSecondsDiff(self.client.loginTime))
            self.client.loginTime = Utils.getTime()
            temps = map(int, [self.client.playerTime // 86400, self.client.playerTime // 3600 % 24, self.client.playerTime // 60 % 60, self.client.playerTime % 60])
            self.client.sendLangueMessage("", "$TempsDeJeu", *temps)
            
        @self.command
        async def tutorial(self):
            self.client.enterRoom("\x03[Tutorial] %s" %(self.client.playerName))
        
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
            
            
# MapCrew Commands
        @self.command(level=6, mc=True)
        async def lsmc(self):
            Mapcrews = ""
            for player in self.server.players.copy().values():
                if player.isMapCrew or player.privLevel == 6:
                    Mapcrews += "<BV>• ["+str(player.room.name)[:2]+"] "+str(player.playerName)+" : "+str(player.room.name)+" </BV><br>"
            if Mapcrews != "":
                self.client.sendMessage(Mapcrews.rstrip("\n"))
            else:
                self.client.sendServerMessage("Don't have any online MapCrew at moment.", True)
            
# Private-Moderator Commands
        @self.command(level=7)
        async def chatfilter(self, option, *args):
            if option == "list":
                msg = "Filtered strings:\n"
                for message in self.server.badWords:
                    msg += message + ", "
                self.client.sendLogMessage(msg)
                
            elif option == "del":
                name = self.argsNotSplited.split(" ", 1)[1].replace("http://www.", "").replace("https://www.", "").replace("http://", "").replace("https://", "").replace("www.", "")
                if not name in self.server.badWords:
                    self.client.sendServerMessage(f"The string <N>[{name}]</N> is not in the filter.", True)
                else:
                    self.server.badWords.remove(name)
                    self.client.sendServerMessage(f"The string <N>[{name}]</N> has been removed from the filter.", True)
                    
            elif option == "add":
                name = self.argsNotSplited.split(" ", 1)[1].replace("http://www.", "").replace("https://www.", "").replace("http://", "").replace("https://", "").replace("www.", "")
                if name in self.server.badWords:
                    self.client.sendServerMessage(f"The string <N>[{name}]</N> is already filtered (matches [{name}]).", True)
                else:
                    self.server.badWords.append(name)
                    self.client.sendServerMessage(f"The string <N>[{name}]</N> has been added to the filter.", True)

        @self.command(level=7, args=1)
        async def chatlog(self, playerName):
            if self.server.checkConnectedUser(playerName):
                self.client.ModoPwet.openChatLog(playerName)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
            
        @self.command(level=7, args=1, alies=['clearvotebans', 'clvbans'])
        async def clearban(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                if len(player.voteBan) > 0:
                    player.voteBan = []
                    self.client.sendServerMessageOthers(f"{self.client.playerName} removed all ban votes of {playerName}.")
                    self.client.sendServerMessage(f"Successfully removed all ban votes of {playerName}", True)
                else:
                    self.client.sendServerMessage(f"{playerName} does not contains any ban votes.", True)
            else:
                 self.client.exceptionManager.Invoke("unknownuser")
            
        @self.command(level=7)
        async def creator(self, *args):
            roomName = self.argsNotSplited.split(" ", 0)[0]
            if roomName == '':
                self.client.sendServerMessage("Room [<J>"+self.client.room.name+"</J>]'s creator: <BV>"+self.client.room.creator.playerName+"</BV>", True)
            else:
                for room in self.server.rooms.values():
                    if room.langue == roomName[0:2] and room.roomName == roomName[3:]:
                        self.client.sendServerMessage(f"Room [<J>{roomName}</J>]'s creator: <BV>"+room.creator.playerName+"</BV>", True)
                        return
                self.client.sendServerMessage(f"Room [<J>{roomName}</J>] does not exist.", True)
            
        @self.command(level=7, args=1, alies=['chercher'])
        async def find(self, text):
            result = ""
            for player in self.server.players.copy().values():
                if player.playerName.startswith(text):
                    result += "<BV>%s</BV> -> %s\n" %(player.playerName, player.room.name)
            self.client.sendServerMessage(result, True) if result != "" else self.client.sendServerMessage("No results were found.", True)
            
        @self.command(level=7, args=1, alies=['join'])
        async def follow(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                self.client.enterRoom(player.roomName)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
            
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
                
        @self.command(level=7, args=1)
        async def ip(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                self.client.sendServerMessage(f"<BV>{playerName}</BV>'s IP address: {Utils.EncodeIP(player.ipAddress)}\n {player.countryCode} - {player.countryName} ({player.countryContinent}) - Community [{player.defaultLanguage}]", True)
            else:
                self.client.playerException.Invoke("unknownuser")
                
        @self.command(level=7, args=1)
        async def ipnom(self, ipAddress):
            if not Utils.isValidIP(ipAddress):
                self.client.exceptionManager.Invoke("invalidIP")
                return
            List = "Logs for the IP address ["+ipAddress+"]:"
            for rs in self.Cursor['loginlog'].find({'IP':ipAddress}).distinct("Username"):
                if self.server.checkConnectedUser(rs):
                    List += "<br>" + rs + " <G>(online)</G>"
                else:
                    List += "<br>" + rs
            self.client.sendServerMessage(List, True)
                
        @self.command(level=7, args=1)
        async def kick(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                player.transport.close()
                self.server.sendStaffMessage(f"The player {playerName} has been kicked by {self.client.playerName}.", 7)
                self.client.sendServerMessage(f"The player {playerName} got kicked", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7, args=1)
        async def l(self, xxx):
            if "." not in xxx:
                r = self.Cursor['loginlog'].find({'Username':xxx})
                if r == None:
                    self.client.playerException.Invoke("notloggedin", xxx)
                else:
                    message = "<p align='center'>Connection logs for player: <BL>"+xxx+"</BL>\n</p>"
                    for rs in r[0:200]:
                        message += f"<p align='left'><V>[ {xxx} ]</V> <BL>{rs['Time']}</BL><G> ( <font color = '#{rs['IPColor']}'>{rs['IP']}</font> - {rs['Country']} ) {rs['ConnectionID']} - {rs['Community']}</G><br>"
                    self.client.sendLogMessage(message)
            else:
                r = self.Cursor['loginlog'].find({'IP':xxx})
                if r == None:
                    pass
                else:
                    message = "<p align='center'>Connection logs for IP Address: <V>"+xxx.upper()+"</V>\n</p>"
                    for rs in r[0:200]:
                        message += f"<p align='left'><V>[ {rs['Username']} ]</V> <BL>{rs['Time']}</BL><G> ( <font color = '#{rs['IPColor']}'>{xxx}</font> - {rs['Country']} ) {rs['ConnectionID']} - {rs['Community']}</BL><br>"
                    self.client.sendLogMessage(message)
                
        @self.command(level=7)
        async def lsarb(self):
            Arbitres = ""
            for player in self.server.players.copy().values():
                if player.privLevel == 7:
                    Arbitres += "<font color='#B993CA'>• ["+str(player.room.name)[:2]+"] "+str(player.playerName)+" : "+str(player.room.name)+" </font><br>"
            if Arbitres != "":
                self.client.sendMessage(Arbitres.rstrip("\n"))
            else:
                self.client.sendServerMessage("Don't have any online Arbitres at moment.", True)
                
        @self.command(level=7)
        async def lsc(self):
            result = {}
            for room in self.server.rooms.values():
                if room.langue in result:
                    result[room.langue] = result[room.langue] + room.getPlayerCount()
                else:
                    result[room.langue] = room.getPlayerCount()
            message = ""
            for room in result.items():
                if room[1] > 0:
                    message += f"<BL>{room[0]}:<BL> <V>{room[1]}</V>\n"
            message += f"<J>Total players:</J> <R>{sum(result.values())}</R>"
            self.client.sendLogMessage(message)
                
        @self.command(level=7)
        async def lsmodo(self):
            Moderateurs = ""
            for player in self.server.players.copy().values():
                if player.privLevel > 8:
                    Moderateurs += "<font color='#C565FE'>• ["+str(player.room.name)[:2]+"] "+str(player.playerName)+" : "+str(player.room.name)+" </font><br>"
            if Moderateurs != "":
                self.client.sendMessage(Moderateurs.rstrip("\n"))
            else:
                self.client.sendServerMessage("Don't have any online Moderators at moment.", True)
                
        @self.command(level=7)
        async def lsroom(self, *args):
            if self.currentArgsCount == 0:
                Message = f"Players in room [{str(self.client.roomName[:2].lower() + self.client.roomName[2:])}]: {str(self.client.room.getPlayerCount())}\n"
                for player in [*self.client.room.clients.copy().values()]:
                    if not player.isHidden:
                        Message += "<BL>%s / </BL><font color = '#%s'>%s</font> <G>(%s)</G>\n" % (player.playerName, player.ipColor, Utils.EncodeIP(player.ipAddress), player.countryName)
                    else:
                        Message += "<BL>%s / </BL><font color = '#%s'>%s</font> <G>(%s)</G> <BL>(invisible)</BL>\n" % (player.playerName, player.ipColor, Utils.EncodeIP(player.ipAddress), player.countryName)
                self.client.sendServerMessage(Message.rstrip("\n"), True)
            else:
                roomName = self.argsNotSplited.split(" ", 0)[0]
                try:
                    players = 0
                    for player in [*self.server.rooms[roomName].clients.values()]:
                        players += 1
                    Message = f"Players in room [{roomName}]: {str(players)}\n"
                    for player in [*self.server.rooms[roomName].clients.values()]:
                        if not player.isHidden:
                            Message += "<BL>%s / </BL><font color = '#%s'>%s</font> <G>(%s)</G>\n" % (player.playerName, player.ipColor, Utils.EncodeIP(player.ipAddress), player.countryName)
                        else:
                            Message += "<BL>%s / </BL><font color = '#%s'>%s</font> <G>(%s)</G> <BL>(invisible)</BL>\n" % (player.playerName, player.ipColor, Utils.EncodeIP(player.ipAddress), player.countryName)
                    self.client.sendServerMessage(Message.rstrip("\n"), True)
                except KeyError:
                    self.client.sendServerMessage(f"The room [{roomName}] doesn't exist.", True)
                
        @self.command(level=7)
        async def max(self):
            self.client.sendServerMessage(f"Total Players: {len(self.server.players.copy().values())} / {self.server.serverInfo['maximum_players']}", True)
                
        @self.command(level=7, args=1)
        async def mumute(self, playerName):
            if self.server.checkConnectedUser(playerName):
                self.server.mumutePlayer(playerName, self.client.playerName)
                self.client.sendServerMessage(""+ playerName + " got mumuted.", True)
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
                
        @self.command(level=7, args=1)
        async def nomip(self, playerName):
            if self.server.checkExistingUser(playerName):
                ipList = f"{playerName}'s last known IP addresses:"
                for rs in self.Cursor['loginlog'].find({'Username':playerName}).distinct("IP"):
                    ipList += "<br>" + rs
                self.client.sendServerMessage(ipList, True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7, args=1)
        async def prison(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                if player.isPrisoned:
                    player.isPrisoned = False
                    self.server.sendStaffMessage(f"{player.playerName} unprisoned by {self.client.playerName}.", 7)
                    self.client.sendServerMessage(f"{player.playerName} got unprisoned.", True)
                    player.enterRoom(self.server.recommendRoom(player.defaultLanguage))
                else:
                    player.enterRoom("Bad Girls")
                    player.isPrisoned = True
                    self.server.sendStaffMessage(f"{player.playerName} prisoned by {self.client.playerName}.", 7)
                    self.client.sendServerMessage(f"{player.playerName} got prisoned.", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
        @self.command(level=7)
        async def realname(self, *args):
            if self.client.room.isFunCorp:
                playerFakeName = self.argsNotSplited.split(" ", 0)[0]
                for player in [*self.client.room.clients.copy().values()]:
                    if player.playerFakeName == playerFakeName:
                        self.client.sendServerMessage(f"{player.playerFakeName} --> {player.playerName}", True)
                        return
                self.client.sendServerMessage(f"No results were found.", True)
                
        @self.command(level=7, args=1)
        async def relation(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                displayed = []
                List = "The player <BV>"+str(player.playerName)+"</BV> has the following relations:"
                rss = self.Cursor['loginlog'].find({"IP":Utils.EncodeIP(player.ipAddress)})
                for rs in rss:
                    if rs['Username'] in displayed: continue
                    if self.server.players.get(str(rs['Username'])) == None:
                        d = self.Cursor['loginlog'].find({"Username":str(rs['Username'])})
                        ips = []
                        ips2 = []
                        for i in d:
                            if i['IP'] in ips2: continue
                            ips.append(f"<font color='#{i['IPColor']}'>{i['IP']}</font>")
                            ips2.append(i['IP'])
                        toshow = ", ".join(ips)
                        List += f"<br>- <BV>{rs['Username']}</BV> : {toshow}"
                    else:
                        ip31 = self.server.players.get(str(rs['Username']))
                        List += f"<br>- <BV>{rs['Username']}</BV> : <font color='#{player.ipColor}'>{Utils.EncodeIP(ip31.ipAddress)}</font> (current IP)"
                    displayed.append(rs['Username'])
                self.client.sendServerMessage(List, True)
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
                
                
# Public-Moderator Commands
        @self.command(level=8)
        async def clearchat(self):
            self.client.room.sendAll(TFMCodes.game.send.Message, ByteArray().writeUTF("\n" * 10000).toByteArray())

        @self.command(level=8)
        async def mm(self, *args):
            self.client.room.sendAll(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(0).writeUTF("").writeUTF(self.argsNotSplited).writeShort(0).writeByte(0).toByteArray())

        @self.command(level=8)
        async def moveplayer(self, playerName, *args):
            player = self.server.players.get(playerName)
            if player != None:
                newRoom = player.room.name
                roomName = self.argsNotSplited.split(" ", 1)[1]
                if not '-' in roomName:
                    roomName = player.defaultLanguage + '-' + roomName
                player.startBulle(roomName)
                self.server.sendStaffMessage(f"{player.playerName} has been moved from ({str.lower(newRoom)}) to ({roomName}) by {self.client.playerName}.", 7)
                self.client.sendServerMessage(f"{player.playerName} has been moved from {str.lower(newRoom)} to {roomName} ", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")

# Admin Commands
        @self.command(level=9, args=1)
        async def banip(self, ipAddress):
            decip = Utils.DecodeIP(ipAddress)
            if not Utils.isValidIP(ipAddress):
                self.client.exceptionManager.Invoke("invalidIP")
            elif decip in self.server.badIPS:
                self.client.sendServerMessage(f"The ip address {ipAddress} is already banned.", True)
            else:
                self.server.badIPS.append(decip)
                for player in self.server.players.copy().values():
                    if player.ipAddress == decip:
                        player.transport.close()
                self.server.sendStaffMessage(f"{self.client.playerName} banned the ip address {ipAddress}.", 7)
                self.client.sendServerMessage("The IP got banned.", True)

        @self.command(level=9, args=2, alies=["changepass"])
        async def changepassword(self, playerName, newPassword):
            player = self.server.players.get(playerName)
            if player != None:
                salt = b'\xf7\x1a\xa6\xde\x8f\x17v\xa8\x03\x9d2\xb8\xa1V\xb2\xa9>\xddC\x9d\xc5\xdd\xceV\xd3\xb7\xa4\x05J\r\x08\xb0'
                hashtext = base64.b64encode(hashlib.sha256(hashlib.sha256(newPassword.encode()).hexdigest().encode() + salt).digest()).decode()
                self.Cursor['users'].update_one({'Username':playerName},{'$set':{'Password': hashtext}})
                player.updateDatabase()
                player.transport.close()
            else:
                self.client.exceptionManager.Invoke("unknownuser")

        @self.command(level=9, args=1, alies=["comlog"])
        async def commandlog(self, playerName):
            r = self.Cursor['commandlog'].find({'Username':playerName})
            message = "<p align='center'>Command Log of (<V>"+playerName+"</V>)\n</p>"
            for rs in r:
                d = str(datetime.datetime.fromtimestamp(float(int(rs['Time']))))
                message += f"<p align='left'><V>[{playerName}]</V> <FC> - </FC><VP>used command:</VP> <V>/{rs['Command']}</V> <FC> ~> </FC><VP>[{d}]\n"
            self.client.sendLogMessage(message)
            
        @self.command(level=9, args=1, alies=['deluser', 'deleteaccount'])
        async def deleteuser(self, playerName):
            if playerName == self.client.playerName:
                self.client.sendServerMessage("You cannot delete yourself, idiot!", True)
            elif self.server.checkExistingUser(playerName):
                self.Cursor['users'].delete_one({'Username':playerName})
                self.server.sendStaffMessage(f"The account {playerName} was deleted by {self.client.playerName}", 9)
                self.client.sendServerMessage(f"The account {playerName} got deleted.", True)
            else:
                self.client.exceptionManager.Invoke("unknownuser")

        @self.command(level=9)
        async def deletereports(self):
            for report in self.server.serverReports.copy():
                if self.server.serverReports[report]["state"] == "deleted":
                    del self.server.serverReports[report]
            self.client.sendServerMessage(f"Done!", True)

        @self.command(level=9)
        async def japanexpo(self, option, name, *args):
            if option == "add":
                for info in self.server.japanExpoCodes:
                    if info["name"] == name:
                        self.client.sendServerMessage(f"The code <N>[{name}]</N> is already in the database.", True)
                        return
                _type = self.args[2]
                if not _type in ["cheese", "fraise"]:
                    self.client.sendServerMessage("Supported operations are cheese and fraise.", True)
                    return
                amount = self.args[3]
                self.server.japanExpoCodes.append({"name": name, "type": _type, "amount":int(amount), "havegot":False})
                self.client.sendServerMessage(f"The code <N>[{name}]</N> has been added to the database.", True)
                
            elif option == "del":
                for info in self.server.japanExpoCodes:
                    if info["name"] == name:
                        self.server.japanExpoCodes.remove(info)
                        self.client.sendServerMessage(f"The code <N>[{name}]</N> has been deleted from the database.", True)
                        return
                self.client.sendServerMessage(f"The code <N>[{name}]</N> does not exist on the database.", True)

        @self.command(level=9)
        async def move(self, roomName):
            for player in [*self.client.room.clients.copy().values()]:
                player.enterRoom(self.argsNotSplited)

        @self.command(level=9, args=1, alies=['debanip'])
        async def unbanip(self, ipAddress):
            decip = Utils.DecodeIP(ipAddress)
            if not Utils.isValidIP(ipAddress):
                self.client.exceptionManager.Invoke("invalidIP")
            elif decip in self.server.badIPS:
                self.server.badIPS.remove(decip)
                self.server.sendStaffMessage(f"{self.client.playerName} unbanned the ip address {ipAddress}.", 7)
                self.client.sendServerMessage(f"The ip address {ipAddress} got unbanned.", True)
            else:
                self.client.sendServerMessage("The IP is not banned.", True)

        @self.command(level=9)
        async def smc(self, *args):
            for room in self.server.rooms.values():
                room.sendAll(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(6).writeUTF(self.client.defaultLanguage + " " + self.client.playerName).writeUTF(self.argsNotSplited).writeShort(0).writeByte(0).toByteArray())

# Owner Commands
        @self.command(owner=True)
        async def fshutdown(self):
            self.server.sendServerRestart(4, 1)

        @self.command(owner=True)
        async def luaadmin(self):
            self.client.isLuaAdmin = not self.client.isLuaAdmin
            self.client.sendServerMessage("You can run lua programming as administrator." if self.client.isLuaAdmin else "You can't run lua programming as administrator.", True)

        @self.command(owner=True, alies=['restart'])
        async def reboot(self):
            self.server.sendServerRestart()

        @self.command(owner=True)
        async def reload(self):
            try:
                await self.server.reloadServer()
                self.client.sendServerMessage("Successfull reloaded all modules.", True)
            except Exception as e:
                self.client.sendServerMessage(f"Failed reload all modules. Error: {e}", True)
                
        @self.command(owner=True)
        async def updatesql(self):
            for player in self.players.copy().values():
                player.updateDatabase()
            self.client.sendServerMessage(f"Done!", True)
            
        @self.command(owner=True, args=1)
        async def opensetting(self, fileName):
            try:
                with open(f"./include/settings/{fileName}.json", 'r') as File:
                    Log = File.read()
                    File.close()
                self.client.sendLogMessage(Log.replace("<", "&amp;lt;").replace("\x0D\x0A", "\x0A"))
            except Exception as e:
                self.client.sendServerMessage(f"Failed open the file {fileName}. Error: {e}", True)
                
        @self.command(owner=True)
        async def openerrorlog(self):
            try:
                with open(f"./include/logs/errors/serveur.log", 'r') as File:
                    Log = File.read()
                    File.close()
                if Log == "":
                    self.client.sendServerMessage(f"No errors were found.", True)
                else:
                    self.client.sendLogMessage(Log.replace("<", "&amp;lt;").replace("\x0D\x0A", "\x0A"))
            except Exception as e:
                self.client.sendServerMessage(f"Failed open the error log. Error: {e}", True)
                
        @self.command(level=9, args=1)
        async def resetprofile(self, playerName):
            player = self.server.players.get(playerName)
            if player != None:
                self.Cursor['users'].update_one({'Username':playerName}, {'$set':{"FirstCount": 0,"CheeseCount": 0,"BootcampCount": 0,"ShamanCheeses": 0,"ShopCheeses": 0,"ShopFraises": 0,"NormalSaves": 0,"NormalSavesNoSkill": 0,"HardSaves": 0,"HardSavesNoSkill": 0,"DivineSaves": 0,"DivineSavesNoSkill": 0,"ShopItems": "","ShopShamanItems": "","ShopCustomItems": "","ShopEmojies": "","ShopClothes": "","ShopGifts": "","ShopMessages": "","CheeseTitleList": "","FirstTitleList": "","ShamanTitleList": "","ShopTitleList": "","BootcampTitleList": "","HardModeTitleList": "","DivineModeTitleList": "","EventTitleList": "","StaffTitleList": "","ShamanLevel": 0,"ShamanExp": 0,"ShamanExpNext": 0,"Skills": "","Gender": 0,"LastOn": 0,"LastDivorceTimer": 0,"Marriage": "","TribeCode": 0,"TribeRank": 0,"TribeJoined": 0,"SurvivorStats": "0,0,0,0","RacingStats": "0,0,0,0","DefilanteStats": "0,0,0","Consumables": "","EquipedConsumables": "","Pet": 0,"PetEnd": 0,"Fur": 0,"FurEnd": 0,"Badges": "","ShamanBadges": "", "EquipedShamanBadge": 0, "Letters": "","Karma": 0,"AdventureInfo": "[]","TotemInfo": "","Roles":""}})
                self.server.sendStaffMessage(f"The account {playerName} was reset by {self.client.playerName}", 9)
                self.client.sendServerMessage(f"The account {playerName} got reset.", True)
                player.transport.close()
            else:
                self.client.exceptionManager.Invoke("unknownuser")
                
# SWF Build Commands
        @self.command(level=1, args=1)
        async def codecadeau(self, code):
            for info in self.server.japanExpoCodes:
                if info["name"].upper() == code and info["havegot"] == False:
                    amount = info["amount"]
                    if info["type"] == "cheese":
                        self.client.shopCheeses += amount
                    else:
                        self.client.shopFraises += amount
                    self.client.sendPacket(TFMCodes.game.send.JapanExpo_Prize_Popup, ByteArray().writeByte(info["type"] == "fraise").writeInt(amount).toByteArray())
                    self.client.sendPacket(TFMCodes.game.send.JapanExpo_Prize_Message, ByteArray().writeInt(amount if info["type"] == "cheese" else 0).writeInt(amount if info["type"] == "fraise" else 0).toByteArray())
                    info["havegot"] = True