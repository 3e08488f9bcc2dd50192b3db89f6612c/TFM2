import re
import time
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils
from src.modules import ByteArray

class Tribulle:
    def __init__(self, _client, _server):
        # Instances
        self.client = _client
        self.server = _server
        self.Cursor = _client.Cursor
        
        # Integer
        self.MAXIMUM_PLAYERS = 500 # for friends / ignoreds
        self.MAXIMUM_RANKS = 51
        
        # String
        self.TRIBE_RANKS = "0|${trad#TG_0}|0;0|${trad#TG_1}|0;2|${trad#TG_2}|0;3|${trad#TG_3}|0;4|${trad#TG_4}|32;5|${trad#TG_5}|160;6|${trad#TG_6}|416;7|${trad#TG_7}|932;8|${trad#TG_8}|2044;9|${trad#TG_9}|2046"

    def getTime(self) -> int:
        return int(time.time() // 60)

    def updateTribeData(self) -> None:
        for player in self.server.players.copy().values():
            if player.tribeCode == self.client.tribeCode:
                player.tribeHouse = self.client.tribeHouse
                player.tribeMessage = self.client.tribeMessage
                player.tribeRanks = self.client.tribeRanks

    def parseTribulleCode(self, code, packet) -> None:
        if code == TFMCodes.tribulle.recv.ST_ChangerDeGenre: # 10
            self.changeGender(packet)
        elif code == TFMCodes.tribulle.recv.ST_AjoutAmi: # 18
            self.addFriend(packet)
        elif code == TFMCodes.tribulle.recv.ST_RetireAmi: # 20
            self.removeFriend(packet)
        elif code == TFMCodes.tribulle.recv.ST_DemandeEnMariage: # 22
            self.marriageInvite(packet)
        elif code == TFMCodes.tribulle.recv.ST_RepondDemandeEnMariage: # 24
            self.marriageAnswer(packet)
        elif code == TFMCodes.tribulle.recv.ST_DemandeDivorce: # 26
            self.marriageDivorce(packet)
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
        elif code == TFMCodes.tribulle.recv.ST_EnvoitTribuMessageCanal: # 50
            self.sendTribeChatMessage(packet)
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
        elif code == TFMCodes.tribulle.recv.ST_InviterMembre: # 78
            self.tribeInvite(packet)
        elif code == TFMCodes.tribulle.recv.ST_RepondInvitationTribu: # 80
            self.tribeInviteAnswer(packet)
        elif code == TFMCodes.tribulle.recv.ST_QuitterTribu: # 82
            self.leaveTribe(packet)
        elif code == TFMCodes.tribulle.recv.ST_CreerTribu: # 84
            self.createTribe(packet)
        elif code == TFMCodes.tribulle.recv.ST_ChangerMessageJour: # 98
            self.changeTribeMessage(packet)
        elif code == TFMCodes.tribulle.recv.ST_ChangerCodeMaisonTFM: # 102
            self.server.loop.create_task(self.changeTribeCode(packet))
        elif code == TFMCodes.tribulle.recv.ST_ExclureMembre: # 104
            self.kickPlayerTribe(packet)
        elif code == TFMCodes.tribulle.recv.ST_DemandeInformationsTribu: # 108
            self.sendTribeInfo(packet)
        elif code == TFMCodes.tribulle.recv.ST_FermerTribu: # 110
            self.closeTribe(packet)
        elif code == TFMCodes.tribulle.recv.ST_AffecterRang: # 112
            self.changeTribePlayerRank(packet)
        elif code == TFMCodes.tribulle.recv.ST_SupprimerDroitRang: # 114
            self.setRankPermission(packet)
        elif code == TFMCodes.tribulle.recv.ST_RenommerRang: # 116
            self.renameTribeRank(packet)
        elif code == TFMCodes.tribulle.recv.ST_AjouterRang: # 118
            self.createNewTribeRank(packet)
        elif code == TFMCodes.tribulle.recv.ST_SupprimerRang: # 120
            self.deleteTribeRank(packet)
        elif code == TFMCodes.tribulle.recv.ST_InverserOrdreRangs: # 122
            self.changeRankPosition(packet)
        elif code == TFMCodes.tribulle.recv.ST_DesignerChefSpirituel: # 126
            self.setTribeMaster(packet)
        elif code == TFMCodes.tribulle.recv.ST_DissoudreTribu: # 128
            self.dissolveTribe(packet)
        elif code == TFMCodes.tribulle.recv.ST_ListeHistoriqueTribu: # 132
            self.sendTribeHistorique(packet)
        else:
            print(f"[ERREUR] Not implemented tribulle code -> Code: {code} packet: {repr(packet.toByteArray())}")
            
    def addFriend(self, packet) -> None:
        """
        Receive packet about add friend on friend list.
        """
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
        
            if self.client.openingFriendList:
                self.sendFriendsList("0")
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatAjoutAmi, p.toByteArray())
    
    def addIgnoredPlayer(self, packet) -> None:
        """
        Receive packet about add ignore player on ignored list.
        """
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
            
    def changeGender(self, packet) -> None:
        tribulleID = packet.readInt() 
        gender = packet.readByte()
        self.client.gender = gender
        self.client.sendTribullePacket(12, ByteArray().writeByte(gender).toByteArray())
        for player in self.server.players.copy().values():
            if player.playerName in self.client.friendsList and self.client.playerName in player.friendsList:
                if player.openingFriendList:
                    player.Tribulle.sendFriendsList("0")
        self.client.sendTribullePacket(11, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())
            
    def changeRankPosition(self, packet) -> None:
        tribulleID = packet.readInt() 
        rankID = packet.readByte() 
        rankID2 = packet.readByte()
        ranks = self.client.tribeRanks.split(";")
        rank = ranks[rankID]
        rank2 = ranks[rankID2]
        ranks[rankID] = rank2
        ranks[rankID2] = rank
        self.client.tribeRanks = ";".join(map(str, ranks))
        self.updateTribeRanks()
        self.updateTribeData()
        members = self.server.getTribeMembers(self.client.tribeCode)
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.tribeRank == rankID:
                    player.tribeRank = rankID2
                if rankID2 > rankID:
                    if player.tribeRank == rankID2:
                        player.tribeRank -= 1
                if rankID2 < rankID:
                    if player.tribeRank == rankID2:
                        player.tribeRank += 1
            else:
                rankPlayer = self.Cursor['users'].find_one({'Username':member})['TribeRank']

                if rankPlayer == rankID:
                    self.Cursor['users'].update_one({'Username':member},{'$set':{'TribeRank':rankID2}})
                if rankID2 > rankID:
                    if rankPlayer == rankID2:
                        self.Cursor['users'].update_one({'Username':member},{'$set':{'TribeRank':rankID2-1}})
                if rankID2 < rankID:
                    if rankPlayer == rankID2:
                        self.Cursor['users'].update_one({'Username':member},{'$set':{'TribeRank':rankID2+1}})

        self.updateTribeRanks()
        self.updateTribeData()
        self.sendTribeInfo("")
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")
            
    def changeTribeCode(self, packet) -> None: # Cooming Soon
        pass
            
    def changeTribeMessage(self, packet) -> None:
        """
        Receive packet about change message in the tribe.
        """
        tribulleID = packet.readInt()
        message = packet.readUTF()
        if len(message) > self.MAXIMUM_PLAYERS:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ErreurChangerMessageJour, ByteArray().writeInt(tribulleID).writeByte(22).toByteArray())
            return
            
        if self.server.checkMessage(message):
            self.client.sendServerMessage("You can't use inappropriate content in your tribe message.", True)
            return

        self.Cursor['tribe'].update_one({'Code':self.client.tribeCode},{'$set':{'Message':message}})
        self.client.tribeMessage = message
        self.setTribeHistorique(self.client.tribeCode, 6, self.getTime(), message, self.client.playerName)
        self.updateTribeData()
        self.sendTribeInfo("")
        self.client.sendPacketWholeTribe(TFMCodes.tribulle.send.ET_ResultatChangerMessageJour, ByteArray().writeUTF(self.client.playerName).writeUTF(message).toByteArray(), True)

    def changeTribePlayerRank(self, packet) -> None:
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        rankID = packet.readByte()

        rankInfo = self.client.tribeRanks.split(";")
        rankName = rankInfo[rankID].split("|")[1]
        player = self.server.players.get(playerName)
        if not player:
            rss = self.Cursor['users'].find_one({'Username':playerName})
            rs = [rss['Username'], rss['PlayerID'], rss['Gender'], rss['LastOn']]
            self.Cursor['users'].update_one({'Username':playerName}, {'$set':{'TribeRank':rankID}})
        else:
            rs = [playerName, player.playerID, player.gender, player.lastOn]
            player.tribeRank = rankID
            self.Cursor['users'].update_one({'Username':playerName}, {'$set':{'TribeRank':rankID}})

        self.setTribeHistorique(self.client.tribeCode, 5, self.getTime(), playerName, str(rankID), rankName, self.client.playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleConnexionMembre, ByteArray().writeInt(rs[1]).writeUTF(playerName.lower()).writeByte(rs[2]).writeInt(rs[1]).writeInt(0 if self.server.checkConnectedUser(playerName) else rs[3]).writeByte(rankID).writeInt(1).writeUTF("" if player == None else player.roomName).toByteArray())
        self.client.sendPacketWholeTribe(124, ByteArray().writeUTF(self.client.playerName.lower()).writeUTF(playerName.lower()).writeUTF(rankName).toByteArray(), True)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleChangementRang, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())
        members = self.server.getTribeMembers(self.client.tribeCode)
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")

    def checkFriend(self, playerName, playerName2) -> bool:
        """
        Checks is playerName and playerName2 are friends.
        """
        if playerName in self.server.players:
            checkList = self.server.players[playerName].friendsList
        else:
            rs = self.Cursor['users'].find_one({'Username':playerName})
            checkList = rs['FriendsList'].split(",") if rs else []
        return playerName2 in checkList
            
    def closeFriendsList(self, packet) -> None:
        """
        Receive packet about close the friends list.
        """
        self.client.openingFriendList = False
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatFermerListeAmis, ByteArray().writeBytes(packet.toByteArray()).writeByte(1).toByteArray())

    def closeTribe(self, packet) -> None:
        """
        Receive packet about close the tribe.
        """
        tribulleID = packet.readInt()
        self.client.isTribeOpen = False
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleFermerTribu, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

    def createCustomChat(self, packet) -> None:
        """
        Receive packet about create a global chat.
        """
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

    def createNewTribeRank(self, packet) -> None:
        """
        Receive packet about create a new rank in the tribe.
        """
        tribulleID = packet.readInt() 
        rankName = packet.readUTF()
        if self.server.checkMessage(rankName):
            self.client.sendServerMessage("You can't use inappropriate content while create your rank.", True)
            return
        ranksID = self.client.tribeRanks.split(";")
        if len(ranksID) > self.MAXIMUM_RANKS:
            self.client.sendServerMessage("You have exceeded the total ranks limit.", True)
            return
        s = ranksID[1]
        f = ranksID[1:]
        f = ";".join(map(str, f))
        s = "%s|%s|%s" % ("0", rankName, "0")
        del ranksID[1:]
        ranksID.append(s)
        ranksID.append(f)
        self.client.tribeRanks = ";".join(map(str, ranksID))
        members = self.server.getTribeMembers(self.client.tribeCode)
        for playerName in members:
            player = self.server.players.get(playerName)
            tribeRank = self.server.getPlayerTribeRank(playerName)
            if player != None:
                if player.tribeRank >= 1:
                    player.tribeRank += 1
            else:
                if tribeRank >= 1:
                    self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':tribeRank+1}})

        self.updateTribeRanks()
        self.updateTribeData()
        self.sendTribeInfo("")
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")

    def createTribe(self, packet) -> None:
        if self.client.tribeCode > 0: 
            return
        tribulleID = packet.readInt()
        tribeName = packet.readUTF()
        if self.server.checkMessage(tribeName):
            self.client.sendServerMessage("You can't use inappropriate name in your tribe.", True)
            return
        
        p = ByteArray().writeInt(tribulleID)
        if tribeName == "" or not re.match("^[ a-zA-Z0-9]*$", tribeName) or "<" in tribeName or ">" in tribeName:
            p.writeByte(8)
        elif self.server.checkExistingTribe(tribeName):
            p.writeByte(9)
        elif self.client.shopCheeses < 500:
            p.writeByte(14)
        else:
            p.writeByte(1)
            createTime = self.getTime()
            self.Cursor['tribe'].insert_one({'Code':self.server.lastTribeID, 'Name': tribeName, 'Message': '', 'House': 0, 'Ranks': self.TRIBE_RANKS, 'Historique': '', 'Members': self.client.playerName, 'Chat': 0, 'Points': 0, 'createTime': createTime})
            self.client.shopCheeses -= 500
            self.client.tribeCode = self.server.lastTribeID
            self.client.tribeRank = 9
            self.client.tribeName = tribeName
            self.client.tribeJoined = createTime
            self.client.tribeMessage = ""
            self.client.tribeRanks = self.TRIBE_RANKS

            self.setTribeHistorique(self.client.tribeCode, 1, createTime, self.client.playerName, tribeName)
            self.Cursor['config'].update_one({'lastTribeID':self.server.lastTribeID},{'$set':{'lastTribeID':self.server.lastTribeID + 1}})
            self.server.lastTribeID += 1

            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleCreerTribu, ByteArray().writeUTF(self.client.tribeName).writeInt(self.client.tribeCode).writeUTF(self.client.tribeMessage).writeInt(0).writeUTF(self.client.tribeRanks.split(";")[9].split("|")[1]).writeInt(2049).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatCreerTribu, p.toByteArray())

    def deleteTribeRank(self, packet) -> None:
        """
        Receive packet about delete a rank in the tribe.
        """
        tribulleID = packet.readInt()
        rankID = packet.readByte()

        rankInfo = self.client.tribeRanks.split(";")
        del rankInfo[rankID]
        self.client.tribeRanks = ";".join(map(str, rankInfo))

        self.updateTribeRanks()
        self.updateTribeData()

        members = self.server.getTribeMembers(self.client.tribeCode)
        for playerName in members:
            player = self.server.players.get(playerName)
            if player != None:
                if player.tribeRank != rankID:
                    continue
                    
                player.tribeRank = 0
            else:
                tribeRank = self.server.getPlayerTribeRank(playerName)
                if tribeRank != rankID:
                    continue
                self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':0}})
                
        for playerName in members:
            player = self.server.players.get(playerName)
            tribeRank = self.server.getPlayerTribeRank(playerName)
            if player != None:
                if player.tribeRank >= 1:
                    player.tribeRank -= 1
            else:
                if tribeRank >= 1:
                    self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':tribeRank-1}})
        self.sendTribeInfo("")
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")

    def disableWhispers(self, packet) -> None:
        """
        Receive packet about disable whispers.
        """
        tribulleID = packet.readInt()
        silence_type = packet.readByte()
        silence_msg = packet.readUTF()
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDefinitModeSilence, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

        self.client.silenceType = silence_type
        self.client.silenceMessage = "" if self.server.checkMessage(silence_msg) and self.client.privLevel < 7 else silence_msg

    def dissolveTribe(self, packet) -> None:
        """
        Receive packet when member dissolve their tribe.
        """
        tribulleID = packet.readInt()
        p = ByteArray()
        p.writeInt(tribulleID).writeByte(1)
        members = self.server.getTribeMembers(self.client.tribeCode)
        self.Cursor['tribe'].delete_one({'Code':self.client.tribeCode})
        for member in members:
            player = self.server.players.get(member)
            if player:
                player.tribeCode = 0
                player.tribeRank = 0
                player.tribeJoined = 0
                player.tribeHouse = 0
                player.tribeChat = 0
                player.tribeMessage = ""
                player.tribeName = ""
                player.tribeRanks = ""
                player.sendTribullePacket(93, ByteArray().writeUTF(player.playerName).writeUTF(self.client.playerName).toByteArray())
                if player != self.client:
                    player.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDissoudreTribuJour, p.toByteArray())
                members.remove(member)
        if len(members) > 0:
            self.Cursor['users'].update_one({'TribeCode':self.client.tribeCode},{'$set':{'TribeCode':0,'TribeRank':0,'TribeJoined':0}})
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDissoudreTribu, p.toByteArray())

    def getCustomChatMembers(self, packet) -> None:
        """
        Receive packet about get all members in the specific global chat. (/who command)
        """
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID).writeByte(1).writeShort(len(self.server.chats[chatName]))
        for player in self.server.players.copy().values():
            if chatName in self.server.chats and self.client.playerName in self.server.chats[chatName]:
                p.writeUTF(player.playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDemandeMembresCanal, p.toByteArray())

    def kickPlayerTribe(self, packet) -> None:
        tribulleID = packet.readInt() 
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID)
        player = self.server.players.get(playerName)
        tribeCode = player.tribeCode if player != None else self.server.getPlayerTribeCode(playerName)
        if tribeCode != 0:
            p.writeByte(1)
            members = self.server.getTribeMembers(self.client.tribeCode)
            if playerName in members:
                members.remove(playerName)
                self.setTribeMembers(self.client.tribeCode, members)
                self.setTribeHistorique(self.client.tribeCode, 3, self.getTime(), playerName, self.client.playerName)
                self.client.sendPacketWholeTribe(TFMCodes.tribulle.send.ET_SignaleExclusion, ByteArray().writeUTF(playerName).writeUTF(self.client.playerName).toByteArray(), True)
                if player != None:
                    player.tribeCode = 0
                    player.tribeName = ""
                    player.tribeRank = 0
                    player.tribeJoined = 0
                    player.tribeHouse = 0
                    player.tribeMessage = ""
                    player.tribeRanks = ""
                    player.tribeChat = 0
                else:
                    self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':0,'TribeCode':0,'TribeJoined':0}})
            
            members = self.server.getTribeMembers(self.client.tribeCode)
            for member in members:
                player = self.server.players.get(member)
                if player != None:
                    if player.isTribeOpen:
                        player.Tribulle.sendTribeInfo("")
        
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatExclureMembre, p.toByteArray())

    def leaveCustomChat(self, packet) -> None:
        """
        Receive packet about leave the specific global chat.
        """
        tribulleID = packet.readInt()
        chatName = packet.readUTF()
        if chatName in self.server.chats and self.client.playerName in self.server.chats[chatName]:
            self.server.chats[chatName].remove(self.client.playerName)
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleQuitteCanal, ByteArray().writeUTF(chatName).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatQuitterCanal, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())

    def leaveTribe(self, packet) -> None:
        """
        Receive packet about leave the tribe.
        """
        tribulleID = packet.readInt()
        p = ByteArray().writeInt(tribulleID)

        if self.client.tribeRank == (len(self.client.tribeRanks.split(";")) - 1):
            p.writeByte(4)
        else:
            p.writeByte(1)
            self.client.sendPacketWholeTribe(92, ByteArray().writeUTF(self.client.playerName).toByteArray(), True)

            members = self.server.getTribeMembers(self.client.tribeCode)
            if self.client.playerName in members:
                members.remove(self.client.playerName)
                self.setTribeMembers(self.client.tribeCode, members)
                self.setTribeHistorique(self.client.tribeCode, 4, self.getTime(), self.client.playerName)
                
                self.client.tribeCode = 0
                self.client.tribeName = ""
                self.client.tribeRank = 0
                self.client.tribeJoined = 0
                self.client.tribeHouse = 0
                self.client.tribeMessage = ""
                self.client.tribeRanks = ""
                self.client.tribeChat = 0
            
            for member in members:
                player = self.server.players.get(member)
                if player != None:
                    if player.isTribeOpen:
                        player.Tribulle.sendTribeInfo("")
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatQuitterTribu, p.toByteArray())

    def marriageAnswer(self, packet) -> None:
        """
        Receive packet about answer on marriage.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        answer = packet.readByte()
        self.client.marriageInvite = []

        player = self.server.players.get(playerName)
        p =  ByteArray().writeInt(tribulleID)
        if player != None:
            p.writeByte(1)
            """
            0 - cancel marriage
            1 - accept marriage
            """
            if answer == 0:
                self.client.ignoredMarriageInvites.append(self.client.playerName)
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDemandeEnMariage, ByteArray().writeUTF(self.client.playerName).toByteArray())

            elif answer == 1: # marriaged
                player.marriage = self.client.playerName
                self.client.marriage = player.playerName

                if not self.client.playerName in player.friendsList:
                    player.friendsList.append(self.client.playerName)

                if not player.playerName in self.client.friendsList:
                    self.client.friendsList.append(player.playerName)

                self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleMariage, ByteArray().writeUTF(player.playerName).toByteArray())
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleMariage, ByteArray().writeUTF(self.client.playerName).toByteArray())

                if self.client.openingFriendList:
                    self.sendFriendsList("0")

                if player.openingFriendList:
                    player.Tribulle.sendFriendsList("0")

                self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRetraitAmi, ByteArray().writeInt(player.playerID).toByteArray())
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRetraitAmi, ByteArray().writeInt(self.client.playerID).toByteArray())

            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRepondDemandeEnMariage, p.toByteArray())

    def marriageDivorce(self, packet) -> None:
        """
        Receive packet about marriage divorce.
        """
        tribulleID = packet.readInt()
        time = Utils.getTime() + 3600

        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleDivorce, ByteArray().writeUTF(self.client.marriage).writeByte(1).toByteArray())
        player = self.server.players.get(self.client.marriage)
        if player != None:
            player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleDivorce, ByteArray().writeUTF(player.marriage).writeByte(1).toByteArray())
            player.marriage = ""
            player.lastDivorceTimer = time
        else:
            r1 = self.Cursor['users'].find_one({'Username':self.client.marriage})
            if r1:
                dvr = r1['Marriage']
            self.Cursor['users'].update_one({'Username':self.client.marriage},{'$set':{'Marriage':''}})
            self.Cursor['users'].update_one({'Username':dvr},{'$set':{'Marriage':''}})

        self.client.marriage = ""
        self.client.lastDivorceTimer = time

    def marriageInvite(self, packet) -> None:
        """
        Receive packet about send marriage invitation.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID)

        player = self.server.players.get(playerName)
        if not self.server.checkConnectedUser(playerName) and not self.server.checkExistingUser(playerName):
            p.writeByte(11)
        elif not player.marriage == "":
            p.writeByte(15)
        elif len(player.marriageInvite) > 0:
            p.writeByte(6)
        elif playerName == self.client.playerName or playerName in self.client.ignoredsList:
            p.writeByte(4)
        elif not self.client.playerName in player.ignoredMarriageInvites:
            p.writeByte(1)
            player.marriageInvite = [self.client.playerName, tribulleID]
            player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleDemandeEnMariage, ByteArray().writeUTF(self.client.playerName).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ErreurDemandeEnMariage, p.toByteArray())

    def renameTribeRank(self, packet) -> None:
        """
        Receive packet about rename a rank in tribe.
        """
        tribulleID = packet.readInt()
        rankID = packet.readByte()
        rankName = packet.readUTF()
        if self.server.checkMessage(rankName):
            self.client.sendServerMessage("You can't use inappropriate content while rename your rank.", True)
        
        rankInfo = self.client.tribeRanks.split(";")
        rank = rankInfo[rankID].split("|")
        rank[1] = rankName
        rankInfo[rankID] = "|".join(map(str, rank))
        self.client.tribeRanks = ";".join(map(str, rankInfo))
        self.updateTribeRanks()
        self.updateTribeData()
        self.sendTribeInfo("")
        members = self.server.getTribeMembers(self.client.tribeCode)
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")

    def removeFriend(self, packet) -> None:
        """
        Receive packet about remove a friend.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        player = self.server.players.get(playerName)
        if playerName in self.client.friendsList:
            self.client.friendsList.remove(playerName)
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRetraitAmi, ByteArray().writeInt(self.server.getPlayerID(playerName)).toByteArray())
            if player != None:
                player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeShort(1).writeInt(0).writeUTF("").writeInt(0).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRetireAmi, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())
            
            if self.client.openingFriendList:
                self.sendFriendsList("0")

    def removeIgnoredPlayer(self, packet) -> None:
        """
        Receive packet about remove ignored member.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        p = ByteArray().writeInt(tribulleID).writeByte(1)
        self.client.ignoredsList.remove(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatRetireListeNoire, p.toByteArray())

    def sendCustomChatMessage(self, packet) -> None:
        """
        Receive packet about send a message in specific global chat.
        """
        if self.client.isMuted:
            muteInfo = self.server.getMuteInfo(self.client.playerName)
            timeCalc = Utils.getHoursDiff(muteInfo[1])
            if timeCalc <= 0:
                self.server.removeMute(self.client.playerName, "ServeurMute")
                self.client.isMuted = False
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
            
    def sendFriendConnected(self, playerName) -> None:
        """
        Receive packet when friend connect.
        """
        player = self.server.players.get(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(player.playerID).writeUTF(playerName).writeByte(player.gender).writeInt(player.playerID).writeByte(1).writeByte(1).writeInt(1).writeUTF("").writeInt(player.lastOn).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleConnexionAmi, ByteArray().writeUTF(player.playerName).toByteArray())

    def sendFriendChangedRoom(self, playerName) -> None:
        if playerName in self.client.friendsList:
            player = self.server.players.get(playerName)
            if player == None:
                 return
            self.client.sendTribullePacket(35, ByteArray().writeInt(player.playerID).writeUTF(playerName).writeByte(player.gender).writeInt(player.playerID).writeByte(1).writeByte(1).writeInt(4).writeUTF(player.roomName).writeInt(player.lastOn).toByteArray())

    def sendFriendDisconnected(self, playerName) -> None:
        """
        Receive packet when friend disconnect.
        """
        player = self.server.players.get(playerName)
        if player != None:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleAjoutAmiBidirectionnel, ByteArray().writeInt(player.gender).writeUTF(playerName).writeByte(player.gender).writeInt(player.playerID).writeByte(1).writeByte(0).writeInt(1).writeUTF("").writeInt(player.lastOn).toByteArray())
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleDeconnexionAmi, ByteArray().writeUTF(playerName).toByteArray())

    def sendFriendsList(self, readPacket) -> None:
        p = ByteArray().writeShort(3 if readPacket == None else 34)
        if readPacket == None:
            p.writeByte(self.client.gender).writeInt(self.client.playerID)
        if self.client.marriage == "":
            p.writeInt(0).writeUTF("").writeByte(0).writeInt(0).writeByte(0).writeBoolean(False).writeInt(1).writeUTF("").writeInt(0)
        else:
            player = self.server.players.get(self.client.marriage)
            if player == None:
                rs = self.Cursor['users'].find_one({'Username':self.client.marriage})
            else:
                rs = {'Marriage':self.client.marriage, 'PlayerID': player.playerID, 'Gender': player.gender, 'LastOn': player.lastOn, 'Avatar': player.avatar}
            p.writeInt(rs['PlayerID']).writeUTF(rs['Marriage']).writeByte(rs['Gender']).writeInt(rs['Avatar']).writeByte(1).writeBoolean(self.server.checkConnectedUser(rs['Marriage'])).writeInt(4).writeUTF(player.roomName if player else "").writeInt(rs['LastOn'])
        
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
                infos[friend] = [player.avatar, ",".join(player.friendsList), player.marriage, player.gender, player.lastOn, player.playerID]
                if self.client.playerName in player.friendsList:
                    friendsOn.append(friend)
                else:
                    isOnline.append(friend)
                friendsList.remove(friend)

        for name in friendsList:
            for rs in self.Cursor['users'].find({'Username':name}):
                infos[rs['Username']] = [rs['Avatar'], rs['FriendsList'], rs['Marriage'], rs['Gender'], rs['LastOn'], rs['PlayerID']]
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
            p.writeInt(info[5]).writeUTF(playerName).writeByte(genderID).writeInt(info[0]).writeByte(1 if isFriend else 0).writeBoolean(self.server.checkConnectedUser(playerName)).writeInt(4 if isFriend and player != None else 1).writeUTF(player.roomName if isFriend and player != None else "").writeInt(info[4] if isFriend else 0)
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
        self.client.sendPacket(TFMCodes.game.send.Tribulle_Packet, p.toByteArray())
        if not readPacket == None and not self.client.marriage == "":
            self.client.sendTribullePacket(15 if readPacket == "0" else 29, ByteArray().writeInt(self.client.tribulleID+1).writeByte(1).toByteArray())

    def sendIgnoredList(self, packet) -> None:
        """
        Receive packet about send ignoredlist.
        """
        tribulleID = packet.readInt()
        packet = ByteArray().writeInt(tribulleID).writeUnsignedShort(len(self.client.ignoredsList))
        for playerName in self.client.ignoredsList:
            packet.writeUTF(playerName)
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatListeNoire, packet.toByteArray())

    def sendSilenceMessage(self, playerName, tribulleID) -> None:
        """
        Receive packet about send silenced message.
        """
        player = self.server.players.get(playerName)
        if player != None:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_RecoitMessagePriveSysteme, ByteArray().writeInt(tribulleID).writeByte(25).writeUTF(player.silenceMessage).toByteArray())
    
    def sendTribeChatMessage(self, packet) -> None:
        """
        Receive packet about send message in tribe chat. (/t*, t [msg])
        """
        tribulleID = packet.readInt()
        message = packet.readUTF()
        if time.time() - self.client.msgTime > 3 and not self.server.checkMessage(message):
            self.client.logMessage(message, 'Tribe')
            self.client.sendPacketWholeTribe(TFMCodes.tribulle.send.ET_SignaleEnvoitTribuMessageCanal, ByteArray().writeUTF(self.client.playerName.lower()).writeUTF(message).toByteArray(), all=True)
            self.client.msgTime = time.time()

    def sendTribeHistorique(self, packet) -> None:
        """
        Receive packet about send tribe history.
        """
        tribulleID = packet.readInt()
        historique = self.server.getTribeHistorique(self.client.tribeCode).split("|")
        p = ByteArray().writeInt(tribulleID).writeShort(len(historique) - 1 if historique == [''] else len(historique))
        for event in historique:
            event = event.split("/")
            if not historique == [''] and not event[1] == '':
                p.writeInt(event[1])
                p.writeInt(event[0])
                if int(event[0]) == 8:
                    p.writeUTF('{"code":"%s","auteur":"%s"}' % (event[3], event[2]))
                elif int(event[0]) == 6:
                    p.writeUTF('{"message":"%s","auteur":"%s"}' % (event[2], event[3]))
                elif int(event[0]) == 5:
                    p.writeUTF('{"cible":"%s","ordreRang":"%s","rang":"%s","auteur":"%s"}' % (event[2], event[3], event[4], event[5]))
                elif int(event[0]) == 4:
                    p.writeUTF('{"membreParti":"%s","auteur":"%s"}' % (event[2], event[2]))
                elif int(event[0]) == 3:
                    p.writeUTF('{"membreExclu":"%s","auteur":"%s"}' % (event[2], event[3]))
                elif int(event[0]) == 2:
                    p.writeUTF('{"membreAjoute":"%s","auteur":"%s"}' % (event[3], event[2]))
                elif int(event[0]) == 1:
                    p.writeUTF('{"tribu":"%s","auteur":"%s"}' % (event[3], event[2]))

        p.writeInt(len(historique))
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatListeHistoriqueTribu, p.toByteArray())
    
    def sendTribeInfo(self, packet) -> None:
        """
        Receive packet about send tribe.
        """
        if not packet == "":
            tribulleID, connected = packet.readInt(), packet.readByte()
        else:
            tribulleID = self.client.tribulleID + 1
            connected = 0
        
        if self.client.tribeName == "" or self.client.tribeCode <= 0:
            self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ErreurInformationsTribu, ByteArray().writeInt(self.client.tribulleID).writeByte(17).toByteArray())
            return

        members = self.server.getTribeMembers(self.client.tribeCode)
        packet = ByteArray()
        packet.writeInt(self.client.tribeCode)
        packet.writeUTF(self.client.tribeName)
        packet.writeUTF(self.client.tribeMessage)
        packet.writeInt(self.client.tribeHouse)

        isOnline = []
        isOffline = []
        infos = {}
        for member in members:
            rs = self.Cursor['users'].find_one({'Username':member})
            infos[member] = [rs['PlayerID'], rs['Gender'], rs['LastOn'], rs['TribeRank'], rs['TribeJoined'], rs['Avatar']]
            isOffline.append(member)

        for member in members:
            player = self.server.players.get(member)
            if player != None:
                infos[member] = [player.playerID, player.gender, player.lastOn, player.tribeRank, player.tribeJoined, player.avatar]
                isOnline.append(member)
                isOffline.remove(member)

        if connected == 1:
            playersTribe = isOnline + isOffline
        else:
            playersTribe = isOnline

        packet.writeShort(len(playersTribe))

        for member in playersTribe:
            if not member in infos:
                continue

            info = infos[member]
            player = self.server.players.get(member)
            packet.writeInt(info[0])
            packet.writeUTF(member)
            packet.writeByte(info[1])
            packet.writeInt(info[5])
            packet.writeInt(info[2] if not self.server.checkConnectedUser(member) else 0)
            packet.writeByte(info[3])
            packet.writeInt(0)
            packet.writeUTF(player.roomName if player != None else "")
        packet.writeShort(len(self.client.tribeRanks.split(";")))

        for rank in self.client.tribeRanks.split(";"):
            ranks = rank.split("|")
            packet.writeUTF(ranks[1]).writeInt(ranks[2])

        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatInformationsTribu, packet.toByteArray())
        self.client.isTribeOpen = True

    def sendTribeMemberConnected(self) -> None:
        """
        Receive packet when member from tribe connect.
        """
        self.client.sendPacketWholeTribe(88, ByteArray().writeUTF(self.client.playerName).toByteArray(), True)
        self.client.sendPacketWholeTribe(TFMCodes.tribulle.send.ET_SignaleConnexionMembre, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeInt(0).writeByte(self.client.tribeRank).writeInt(1).writeUTF("").toByteArray())
    
    def sendTribeMemberChangeRoom(self) -> None:
        self.client.sendPacketWholeTribe(131, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeInt(0).writeByte(self.client.tribeRank).writeInt(4).writeUTF(self.client.roomName).toByteArray())
    
    def sendTribeMemberDisconnected(self) -> None:
        """
        Receive packet when member from tribe disconnect.
        """
        self.client.sendPacketWholeTribe(90, ByteArray().writeUTF(self.client.playerName).toByteArray(), True)
        self.client.sendPacketWholeTribe(TFMCodes.tribulle.send.ET_SignaleConnexionMembre, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName).writeByte(self.client.gender).writeInt(self.client.playerID).writeInt(self.client.lastOn).writeByte(self.client.tribeRank).writeInt(1).writeUTF("").toByteArray())
    
    def setTribeHistorique(self, tribeCode, *data) -> None:
        historique = self.server.getTribeHistorique(tribeCode)
        if historique == "":
            historique = "/".join(map(str, data))
        else:
            historique = "/".join(map(str, data)) + "|" + historique
        self.Cursor['tribe'].update_one({'Code':tribeCode},{'$set':{'Historique':historique}})
    
    def setTribeMaster(self, packet) -> None:
        tribulleID = packet.readInt() 
        playerName = packet.readUTF()
        rankInfo = self.client.tribeRanks.split(";")
        self.client.tribeRank = (len(rankInfo)-2)
        player = self.server.players.get(playerName)
        if player:
            player.tribeRank = (len(rankInfo)-1)
            rs = [playerName, player.playerID, player.gender, player.lastOn]
        else:
            self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':len(rankInfo)-1}})
            rss = self.Cursor['users'].find_one({'Username':playerName})
            rs = [rss['Username'],rss['PlayerID'],rss['Gender'],rss['LastOn']]

        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleConnexionMembre, ByteArray().writeInt(rs[1]).writeUTF(playerName.lower()).writeByte(rs[2]).writeInt(rs[1]).writeInt(0 if self.server.checkConnectedUser(playerName) else rs[3]).writeByte(len(rankInfo)-1).writeInt(4).writeUTF("" if player == None else player.roomName).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleConnexionMembre, ByteArray().writeInt(self.client.playerID).writeUTF(self.client.playerName.lower()).writeByte(self.client.gender).writeInt(self.client.playerID).writeInt(0).writeByte(len(rankInfo)-2).writeInt(4).writeUTF(self.client.roomName).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatDesignerChefSpirituel, ByteArray().writeInt(tribulleID).writeByte(1).toByteArray())
        members = self.server.getTribeMembers(self.client.tribeCode)
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")
                    self.Cursor['users'].update_one({'Username':playerName},{'$set':{'TribeRank':len(rankInfo)-1}})
    
    def setTribeMembers(self, tribeCode, members) -> None:
        self.Cursor['tribe'].update_one({'Code':tribeCode},{'$set':{'Members':",".join(map(str, [member for member in members]))}})
    
    def setRankPermission(self, packet) -> None:
        tribulleID = packet.readInt()
        rankID = packet.readByte() 
        permID = packet.readInt() 
        type = packet.readByte()
        rankInfo = self.client.tribeRanks.split(";")
        perms = rankInfo[rankID].split("|")
        soma = 0
        if type == 0:
            soma = int(perms[2]) + 2**permID
        elif type == 1:
            soma = int(perms[2]) - 2**permID
        perms[2] = str(soma)
        join = "|".join(map(str, perms))
        rankInfo[rankID] = join
        self.client.tribeRanks = ";".join(map(str, rankInfo))
        self.updateTribeRanks()
        self.updateTribeData()
        self.sendTribeInfo("")
        members = self.server.getTribeMembers(self.client.tribeCode)
        for member in members:
            player = self.server.players.get(member)
            if player != None:
                if player.isTribeOpen:
                    player.Tribulle.sendTribeInfo("")
    
    def tribeInvite(self, packet) -> None:
        """
        Receive packet about send tribe invitation.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        player = self.server.players.get(playerName)
        p = ByteArray().writeInt(tribulleID)
        
        if len(self.server.getTribeMembers(self.client.tribeCode)) >= self.MAXIMUM_PLAYERS:
            p.writeByte(7)
        elif playerName.startswith("*") or player == None:
            p.writeByte(11)
        elif player.tribeName != "":
            p.writeByte(18)
        elif len(player.tribeInvite) > 0:
            p.writeByte(6)
        elif not self.client.tribeCode in player.ignoredTribeInvites:
            p.writeByte(1)
            player.tribeInvite = [tribulleID, self.client]
            player.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleInvitationTribu, ByteArray().writeUTF(self.client.playerName).writeUTF(self.client.tribeName).toByteArray())
        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatInvitationTribu, p.toByteArray())
    
    def tribeInviteAnswer(self, packet) -> None:
        """
        Receive packet about get answer from tribe invitation.
        """
        tribulleID = packet.readInt()
        playerName = packet.readUTF()
        answer = packet.readByte()
        player = self.client.tribeInvite[1]
        self.client.tribeInvite = []
        p = ByteArray().writeInt(tribulleID)
        members = self.server.getTribeMembers(player.tribeCode)

        if self.client.tribeCode != 0:
            p.writeByte(18)
        elif player == None or player.playerName.startswith('*'):
            p.writeByte(17)
        elif len(members) >= self.MAXIMUM_PLAYERS:
            p.writeByte(7)
        else:
            p.writeByte(1)
            if answer == 0:
                self.client.ignoredTribeInvites.append(player.tribeCode)
                player.sendTribullePacket(87, ByteArray().writeUTF(self.client.playerName).writeByte(0).toByteArray())

            elif answer == 1:
                members.append(self.client.playerName)
                self.setTribeMembers(player.tribeCode, members)

                self.client.tribeCode = player.tribeCode
                self.client.tribeRank = 0
                self.client.tribeName = player.tribeName
                self.client.tribeJoined = self.getTime()
                self.client.tribeMessage = player.tribeMessage
                self.client.tribeHouse = player.tribeHouse
                self.client.tribeRanks = player.tribeRanks
                self.client.tribeChat = player.tribeChat

                self.setTribeHistorique(self.client.tribeCode, 2, self.getTime(), player.playerName, self.client.playerName)

                packet = ByteArray()
                packet.writeUTF(self.client.tribeName)
                packet.writeInt(self.client.tribeCode)
                packet.writeUTF(self.client.tribeMessage)
                packet.writeInt(self.client.tribeHouse)

                rankInfo = self.client.tribeRanks.split(";")
                rankName = rankInfo[self.client.tribeRank].split("|")
                packet.writeUTF(rankName[1])
                packet.writeInt(rankName[2])
                self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleNouveauMembre, packet.toByteArray())
                player.sendTribullePacket(87, ByteArray().writeUTF(self.client.playerName).writeByte(1).toByteArray())
                self.client.sendPacketWholeTribe(91, ByteArray().writeUTF(self.client.playerName).toByteArray(), True)
                for member in members:
                    player = self.server.players.get(member)
                    if player != None:
                        if player.isTribeOpen:
                            player.Tribulle.sendTribeInfo("")

        self.client.sendTribullePacket(TFMCodes.tribulle.send.ET_ResultatInviterMembre, p.toByteArray())
    
    def updateTribeRanks(self) -> None:
        self.Cursor['tribe'].update_one({'Code':self.client.tribeCode},{'$set':{'Ranks':self.client.tribeRanks}})
    
    def whisperMessage(self, packet) -> None:
        """
        Receive packet when send message to somebody else (private).
        """
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
                elif self.client.isMuted:
                    muteInfo = self.server.getMuteInfo(self.client.playerName)
                    timeCalc = Utils.getHoursDiff(muteInfo[1])
                    if timeCalc <= 0:
                        self.server.removeMute(self.client.playerName, "ServeurMute")
                        self.client.isMuted = False
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

                    self.client.logMessage(message, playerName)