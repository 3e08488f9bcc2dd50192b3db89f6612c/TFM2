import re
import time
from collections import deque
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils
from src.modules import ByteArray

class Tribulle:
    def __init__(self, _client, _server):
        self.client = _client
        self.server = _server
        self.Cursor = _client.Cursor # Wawa#2456
        
        self.MAXIMUM_PLAYERS = 500 # for friends / ignoreds

    def parseTribulleCode(self, code, packet):
        print(code)
        if code == TFMCodes.tribulle.recv.ST_AjoutAmi: # 18
            self.addFriend(packet)
        elif code == TFMCodes.tribulle.recv.ST_RetireAmi: # 20
            self.removeFriend(packet)
        elif code == TFMCodes.tribulle.recv.ST_ListeAmis: # 28
            self.sendFriendsList(packet)
        elif code == TFMCodes.tribulle.recv.ST_FermerListeAmis: # 30
            self.closeFriendsList(packet)
        elif code == TFMCodes.tribulle.recv.ST_AjoutListeNoire: # 42
            self.addIgnoredPlayer(packet)
        elif code == TFMCodes.tribulle.recv.ST_RetireListeNoire: # 44
            self.removeIgnoredPlayer(packet)
        elif code == TFMCodes.tribulle.recv.ST_ListeNoire: # 46
            self.sendIgnoredList(packet)
        elif code == TFMCodes.tribulle.recv.ST_EnvoitMessageCanal: # 48
            self.sendCustomChatMessage(packet)
        elif code == TFMCodes.tribulle.recv.ST_EnvoitMessagePrive: # 52
            self.whisperMessage(packet)
        elif code == TFMCodes.tribulle.recv.ST_RejoindreCanal: # 54
            self.createCustomChat(packet)
        elif code == TFMCodes.tribulle.recv.ST_QuitterCanal: # 56
            self.leaveCustomChat(packet)
        elif code == TFMCodes.tribulle.recv.ST_DemandeMembresCanal: # 58
            self.getCustomChatMembers(packet)
        elif code == TFMCodes.tribulle.recv.ST_DefinitModeSilence: # 60
            self.disableWhispers(packet)
        elif code == TFMCodes.tribulle.recv.ST_DemandeInformationsTribu: # 108
            pass
                
        
        else:
            print(f"[ERREUR] Not implemented tribulle code -> Code: {code} packet: {repr(packet.toByteArray())}")
            
    def addFriend(self, packet):
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID)
        if len(self.client.friendsList) >= self.MAXIMUM_PLAYERS:
            p.writeByte(7)
        elif not self.server.checkExistingUser(playerName) or playerName.startswith('*'):
            p.writeByte(12)
        elif playerName == self.client.playerName or playerName in self.client.friendsList:
            p.writeByte(4)
        else:
            p.writeByte(1)
            player = self.server.players.get(playerName)
            isFriend = self.checkFriend(playerName, self.client.playerName)
            if not player:
                rss = self.Cursor['users'].find_one({'Username':playerName})
                rs = [playerName, rss['PlayerID'], rss['Gender'], rss['LastOn']]
            else:
                rs = [playerName, player.playerID, player.gender, player.lastOn]

            if playerName in self.client.ignoredsList:
                self.client.ignoredsList.remove(playerName)
            self.client.friendsList.append(playerName)
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmi, ByteArray().writeInt(rs[1]).writeUTF(playerName).writeByte(rs[2]).writeInt(rs[1]).writeShort(self.server.checkConnectedUser(playerName)).writeInt(4 if isFriend else 0).writeUTF(player.roomName if isFriend and player != None else "").writeInt(rs[3] if isFriend else 0).toByteArray())
            if player != None:
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeByte(1).writeByte(self.server.checkConnectedUser(self.client.playerName)).writeInt(4 if isFriend else 0).writeUTF(self.client.roomName if isFriend else "").writeInt(self.client.lastOn if isFriend else 0).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatAjoutAmi, p.toByteArray())
    
    def addIgnoredPlayer(self, packet):
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID)
        
        if playerName.startswith('*') or not self.server.checkExistingUser(playerName):
            p.writeByte(12)
        elif playerName == self.client.playerName or playerName in self.client.ignoredsList:
            p.writeByte(4)
        elif len(self.client.ignoredsList) > self.MAXIMUM_PLAYERS:
            p.writeByte(7)
        else:
            p.writeByte(1)
            self.client.ignoredsList.append(playerName)
            if playerName in self.client.friendsList:
                self.client.friendsList.remove(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatAjoutListeNoire, p.toByteArray())
            
    def checkFriend(self, playerName, playerName2):
        if playerName in self.server.players:
            checkList = self.server.players[playerName].friendsList
        else:
            rs = self.Cursor['users'].find_one({'Username':playerName})
            checkList = rs['FriendsList'].split(",") if rs else []
        return playerName2 in checkList
            
    def closeFriendsList(self, packet):
        self.client.openingFriendList = False
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatFermerListeAmis, ByteArray().writeBytes(packet.toByteArray()).writeByte(1).toByteArray())

    def createCustomChat(self, packet):
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID)
        if chatName in self.server.chats and len(self.server.chats[chatName]) >= self.MAXIMUM_PLAYERS:
            p.writeByte(7)
        if re.match("^(%s=^(%s:(%s!.*_$).)*$)(%s=^(%s:(%s!_{2,}).)*$)[A-Za-z][A-Za-z0-9_]{2,11}$", chatName):
            p.writeByte(8)
        else:
            p.writeByte(1)
            if chatName in self.server.chats and not self.client.playerName in self.server.chats[chatName]:
                self.server.chats[chatName].append(self.client.playerName)
            elif not chatName in self.server.chats:
                self.server.lastChatID += 1
                self.server.chats[chatName] = [self.client.playerName]
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRejointCanal, ByteArray().writeUTF(chatName).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRejoindreCanal, p.toByteArray())

    def disableWhispers(self, packet):
        tribulleID = packet.readInt()
        silence_type = packet.readByte()
        print(silence_type)
        silence_msg = packet.readUTF()
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDefinitModeSilence, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

        self.client.silenceType = silence_type
        self.client.silenceMessage = "" if self.server.checkMessage(silence_msg) and self.client.privLevel < 7 else silence_msg

    def getCustomChatMembers(self, packet):
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID).writeByte(1).writeShort(len(self.server.chats[chatName]))
        for player in self.server.players.copy().values():
            if chatName in self.server.chats and self.client.playerName in self.server.chats[chatName]:
                p.writeUTF(player.playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDemandeMembresCanal, p.toByteArray())

    def leaveCustomChat(self, packet):
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        if chatName in self.server.chats and self.client.playerName in self.server.chats[chatName]:
            self.server.chats[chatName].remove(self.client.playerName)
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleQuitteCanal, ByteArray().writeUTF(chatName).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatQuitterCanal, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

    def removeFriend(self, packet):
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        player = self.server.players.get(playerName)
        if playerName in self.client.friendsList:
            self.client.friendsList.remove(playerName)
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRetraitAmi, ByteArray().writeInt(self.server.getPlayerID(playerName)).toByteArray())
            if player != None:
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeShort(1).writeInt(0).writeUTF("").writeInt(0).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRetireAmi, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

    def removeIgnoredPlayer(self, packet):
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID).writeByte(1)
        self.client.ignoredsList.remove(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRetireListeNoire, p.toByteArray())

    def sendCustomChatMessage(self, packet):
        if self.client.isMute:
            muteInfo = self.server.getMuteInfo(self.client.playerName)
            timeCalc = Utils.getHoursDiff(muteInfo[1])
            if timeCalc <= 0:
                self.server.removeMute(self.client.playerName)
            else:
                self.client.sendMuteMessage(self.client.playerName, timeCalc, muteInfo[0], True)
                return
    
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        message = packet.readUTF()
        
        if not chatName in self.server.chats:
            self.server.lastChatID += 1
            self.server.chats[chatName] = [self.client.playerName]
        elif chatName in self.server.chats and not self.client.playerName in self.server.chats[chatName]:
            self.server.chats[chatName].append(self.client.playerName)
    
        self.client.sendPacketWholeChat(chatName, TFMCodes.tribulle.send.ET_SignaleMessageCanal, ByteArray().writeUTF(self.client.playerName).writeInt(self.client.defaultLanguageID).writeUTF(chatName).writeUTF(message).toByteArray(), True)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatMessageCanal, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())
            
    def sendFriendConnected(self, playerName):
        player = self.server.players.get(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(player.playerID).writeUTF(playerName.lower()).writeByte(player.gender).writeInt(player.playerID).writeByte(1).writeByte(1).writeInt(1).writeUTF("").writeInt(player.lastOn).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleConnexionAmi, ByteArray().writeUTF(player.playerName.lower()).toByteArray())

    def sendFriendDisconnected(self, playerName):
        player = self.server.players.get(playerName)
        if player != None:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(player.gender).writeUTF(playerName).writeByte(player.gender).writeInt(player.playerID).writeByte(1).writeByte(0).writeInt(1).writeUTF("").writeInt(player.lastOn).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleDeconnexionAmi, ByteArray().writeUTF(playerName).toByteArray())

    def sendIgnoredList(self, packet):
        tribulleID = packet.readInt()
        packet = ByteArray().writeInt(tribulleID).writeUnsignedShort(len(self.client.ignoredsList))
        for playerName in self.client.ignoredsList:
            packet.writeUTF(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatListeNoire, packet.toByteArray())

    def sendSilenceMessage(self, playerName, tribulleID):
        player = self.server.players.get(playerName)
        if player != None:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_RecoitMessagePriveSysteme, ByteArray().writeInt(tribulleID).writeByte(25).writeUTF(player.silenceMessage).toByteArray())
    
    def whisperMessage(self, packet):
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        message = packet.readUTF().replace("\n", "").replace("&amp;#", "&#").replace("<", "&lt;")
        isCheck = self.server.checkMessage(message)
        
        if self.client.isGuest:
            self.client.sendLangueMessage("", "$Créer_Compte_Parler")
        else:
            if message != "":
                p = ByteArray().writeInt(tribulleID)
                if playerName.startswith("*") or not playerName in self.server.players:
                    p.writeByte(12)
                    p.writeShort(0)
                    self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_RecoitMessagePriveSysteme, p.toByteArray())
                    return
                elif self.client.isMute:
                    muteInfo = self.server.getMuteInfo(self.client.playerName)
                    timeCalc = Utils.getHoursDiff(muteInfo[1])
                    if timeCalc <= 0:
                        self.server.removeMute(self.client.playerName)
                        self.client.isMute = False
                    else:
                        self.client.sendMuteMessage(self.client.playerName, timeCalc, muteInfo[0], True)
                        return
                else:
                    player = self.server.players.get(playerName)
                    if player != None:
                        """
                        1 - Whisper with everyone
                        2 - Whisper with friends only
                        3 - Whisper with nobody.
                        """
                        if player.silenceType > 1:
                            if self.client.privLevel == 9 or (player.silenceType == 2 and self.checkFriend(playerName, self.client.playerName)):
                                pass
                            else:
                                self.sendSilenceMessage(playerName, tribulleID)
                                return
                            
                    if not (self.client.playerName in player.ignoredsList):
                        if player.playerName != self.client.playerName:
                            player.sendTribullePacket(TFMCodes.tribulle.send.ET_RecoitMessagePrive, ByteArray().writeUTF(self.client.playerName).writeInt(self.client.defaultLanguageID).writeUTF(player.playerName).writeUTF(message).toByteArray())
                        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_RecoitMessagePrive, ByteArray().writeUTF(self.client.playerName).writeInt(self.client.defaultLanguageID).writeUTF(player.playerName).writeUTF(message).toByteArray())
                    
                    if isCheck:
                        self.server.sendStaffMessage(f"The player <BV>{self.client.playerName}</BV> whispered <J>{playerName}</J> a blacklisted string <N2>[{message}]</N2>.", 7)

                    if not self.client.playerName in self.server.chatMessages:
                        messages = deque([], 60)
                        messages.append([time.strftime("%Y/%m/%d %H:%M:%S"), message, self.client.roomName])
                        self.server.chatMessages[self.client.playerName] = messages
                    else:
                        self.server.chatMessages[self.client.playerName].append([time.strftime("%Y/%m/%d %H:%M:%S"), message, self.client.roomName])




    def sendFriendsList(self, readPacket):
        p = ByteArray().writeShort(3 if readPacket == None else 34)
        if readPacket == None:
            p.writeByte(self.client.gender).writeInt(self.client.playerID)
        if self.client.marriage == "":
            p.writeInt(0).writeUTF("").writeByte(0).writeInt(0).writeByte(0).writeByte(0).writeInt(1).writeUTF("").writeInt(0)
        else:
            player = self.server.players.get(self.client.marriage)
            if player == None:
                rs = self.Cursor['users'].find_one({'Username':self.client.marriage})
            else:
                rs = {'Marriage':self.client.marriage, 'PlayerID': player.playerID, 'Gender': player.gender, 'LastOn': player.lastOn}
            p.writeInt(rs['PlayerID']).writeUTF(rs['Marriage'].lower()).writeByte(rs['Gender']).writeInt(rs['PlayerID']).writeByte(1).writeBoolean(self.server.checkConnectedUser(rs['Marriage'])).writeInt(4).writeUTF(player.roomName if player else "").writeInt(rs['LastOn'])
        self.client.openingFriendList = readPacket != None
        isOnline = []
        friendsOn = []
        friendsOff = []
        isOffline = []
        infos = {}
        friendsList = self.client.friendsList.copy()
        for friend in friendsList:
            player = self.server.players.get(friend)
                
            if player != None:
                infos[friend] = [player.playerID, ",".join(player.friendsList), player.marriage, player.gender, player.lastOn]
                if self.client.playerName in player.friendsList:
                    friendsOn.append(friend)
                else:
                    isOnline.append(friend)
                friendsList.remove(friend)

        for name in friendsList:
            for rs in self.Cursor['users'].find({'Username':name}):
                infos[rs['Username']] = [rs['PlayerID'], rs['FriendsList'], rs['Marriage'], rs['Gender'], rs['LastOn']]
                if self.client.playerName in map(str, filter(None, rs['FriendsList'].split(","))):
                    friendsOff.append(rs['Username'])
                else:
                    isOffline.append(rs['Username'])

        playersNames = friendsOn + isOnline + friendsOff + isOffline
        if "" in playersNames:
            playersNames.remove("")
        if "" in self.client.ignoredsList:
            self.client.ignoredsList.remove("")
        p.writeShort(len(playersNames))
        for playerName in playersNames:
            if not playerName in infos:
                continue

            info = infos[playerName]
            player = self.server.players.get(playerName)
            isFriend = self.client.playerName in player.friendsList if player != None else self.client.playerName in map(str, filter(None, info[1].split(",")))
            genderID = player.gender if player else int(info[3])
            isMarriage = self.client.playerName == player.marriage if player else info[2] == self.client.playerName
            p.writeInt(info[0]).writeUTF(playerName.lower()).writeByte(genderID).writeInt(info[0]).writeByte(1 if isFriend else 0).writeBoolean(self.server.checkConnectedUser(playerName)).writeInt(4 if isFriend and player != None else 1).writeUTF(player.roomName if isFriend and player != None else "").writeInt(info[4] if isFriend else 0)
        if readPacket == None:
            p.writeShort(len(self.client.ignoredsList))

            for playerName in self.client.ignoredsList:
                p.writeUTF(playerName.lower())
            p.writeUTF(self.client.tribeName)
            p.writeInt(self.client.tribeCode)
            p.writeUTF(self.client.tribeMessage)
            p.writeInt(self.client.tribeHouse)
            if not self.client.tribeRanks == "":
                rankInfo = self.client.tribeRanks.split(";")
                rankName = rankInfo[self.client.tribeRank].split("|")
                p.writeUTF(rankName[1])
                p.writeInt(rankName[2])
            else:
                p.writeUTF("")
                p.writeInt(0)
        self.client.sendPacket([60, 3], p.toByteArray())
        if not readPacket == None and not self.client.marriage == "":
            self.client.sendTribullePacket(15 if readPacket == "0" else 29, ByteArray().writeInt(self.client.tribulleID+1).writeByte(1).toByteArray())