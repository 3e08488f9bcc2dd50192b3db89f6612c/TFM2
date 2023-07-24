import math
import time
from src.modules import ByteArray
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils

class ModoPwet:
    def __init__(self, _client, _server):
        self.client = _client
        self.server = _server
        self.lastOpened = time.time()
    
    def changeReportStatusDeleted(self, playerName, deletedby) -> None:
        """
        Change the player status in modopwet to deleted.
        """
        self.client.sendPacket(TFMCodes.game.send.Modopwet_Deleted, ByteArray().writeUTF(playerName).writeUTF(deletedby).toByteArray())
    
    def changeReportStatusDisconnect(self, playerName) -> None:
        """
        Change the player status in modopwet to disconnected.
        """
        self.client.sendPacket(TFMCodes.game.send.Modopwet_Disconnected, ByteArray().writeUTF(playerName).toByteArray())

    def changeReportStatusBanned(self, playerName, banhours, banreason, bannedby) -> None:
        """
        Change the player status in modopwet to banned.
        """
        self.client.sendPacket(TFMCodes.game.send.Modopwet_Banned, ByteArray().writeUTF(playerName).writeBoolean(True).writeUTF(bannedby).writeInt(banhours).writeUTF(banreason).toByteArray())

    def deleteReport(self, playerName, handled) -> None:
        """
        Delete or handle a report from modopwet.
        """
        if handled == 1: # [handled]
            reason = self.getPlayerReportReason(playerName)
            if reason == "Hack":
                self.server.banPlayer(playerName, 0, "Hack", self.client.playerName, False)
            elif reason == "Insults":
                self.server.mutePlayer(playerName, 1, "Insults", self.client.playerName, False)
            elif reason == "Spam / Flood":
                self.server.mutePlayer(playerName, 1, "Flood", self.client.playerName, False)
            elif reason == "Phishing":
                self.server.banPlayer(playerName, 360, "Phishing", self.client.playerName, False)
            else:
                # player is not reported or does not exist.
                pass
        else:
            self.server.serverReports[playerName]["state"] = "deleted"
            self.server.serverReports[playerName]["deletedby"] = self.client.playerName
        self.updateModoPwet()

    def getModopwetLangue(self, playerName) -> str:
        """
        Return the player's language.
        """
        player = self.server.players.get(playerName)
        return player.defaultLanguage.upper() if player else "XX"
        
    def getModopwetMods(self, room) -> list:
        """
        Return all moderators in same room as player's one.
        """
        s = []
        for player in self.server.players.copy().values():
            if player.roomName == room and player.privLevel >= 7:
                s.append(player.playerName)
        return s
        
    def getPlayerReportReason(self, playerName) -> str:
        """
        Return the reported reason.
        """
        player = self.server.players.get(playerName)
        if player:
            return player.reportedType
        else:
            return ""
        
    def getPlayerKarma(self, playerName) -> int:
        """
        Return the player's karma.
        """
        player = self.server.players.get(playerName)
        if player:
            return player.playerKarma
        else:
            return 0
        
    def getReportReason(self, _type) -> str:
        """
        Return the reported reason.
        """
        return "Hack" if _type == 0 else "Spam / Flood" if _type == 1 else "Insults" if _type == 2 else "Phishing" if _type == 3 else "Other"
        
    def insertReport(self, playerName, _type, comment) -> None:
        modName = self.client.playerName
        r1 = self.server.players.get(playerName)
        if r1:
            r1.reportedType = self.getReportReason(_type)
            if r1.defaultLanguage.upper() in self.client.modopwetCommunityNotifications:
                self.client.sendServerMessage(f"<ROSE>[Modopwet]</ROSE> The player <BV>{playerName}</BV> has been reported for <N>{self.getReportReason(_type)}</N> in room [{r1.roomName}]. Press M for more information!", True)
            
            if playerName in self.server.serverReports:
                if modName in self.server.serverReports[playerName]['reporters']:
                    r = self.server.serverReports[playerName]['reporters'][modName]
                    if r[0] != _type:
                        self.server.serverReports[playerName]['reporters'][modName] = [_type, comment, Utils.getTime()]
                else:
                    self.server.serverReports[playerName]['reporters'][modName]=[_type, comment, Utils.getTime()]
                self.server.serverReports[playerName]['state'] = 'online' if self.server.checkConnectedUser(playerName) else 'disconnected'
            else:
                self.server.serverReports[playerName] = {}
                self.server.serverReports[playerName]['reporters'] = {modName:[_type, comment, Utils.getTime()]}
                self.server.serverReports[playerName]['state'] = 'online' if self.server.checkConnectedUser(playerName) else 'disconnected'
                self.server.serverReports[playerName]['language'] = self.getModopwetLangue(playerName)
                
                self.server.serverReports[playerName]['isMuted'] = False
                self.server.serverReports[playerName]['muteHours'] = 0
                self.server.serverReports[playerName]['muteReason'] = ""
                self.server.serverReports[playerName]['mutedBy'] = ""
                
                self.server.serverReports[playerName]["bannedby"] = ""
                self.server.serverReports[playerName]["banhours"] = 0
                self.server.serverReports[playerName]["banreason"] = ""
        self.updateModoPwet()
        
    def sendAllModopwetLangues(self):
        languages = ['EN', 'FR', 'RU', 'BR', 'ES', 'TR', 'VK', 'PL', 'HU', 'NL', 'RO', 'ID', 'DE', 'GB', 'SA', 'PH', 'LT', 'JP', 'CN', 'FI', 'CZ', 'HR', 'SK', 'BG', 'LV', 'IL', 'IT', 'EE', 'AZ', 'PT']
        p = ByteArray().writeShort(len(languages))
        for i in languages: 
            p.writeUTF(i)
        self.client.sendPacket(TFMCodes.game.send.Modopwet_Add_Language, p.toByteArray())
        
    def sortingKey(self, array):
        for i in array[1]["reporters"]:
            return array[1]["reporters"][i][2]
        
    def sortReports(self, reports, sort) -> dict:  
        return sorted(reports.items(), key=self.sortingKey, reverse=True) if sort else sorted(reports.items(), key=lambda x: len(x[1]["reporters"]),reverse=True)
        
    def updateModoPwet(self) -> None:
        for player in self.server.players.copy().values():
            if player.isModoPwet and player.privLevel >= 7:
                player.ModoPwet.openModoPwet(True)
                
    def openChatLog(self, playerName):
        if playerName in self.server.chatMessages:
            chatlogs = []
            whisperlogs = []
            p = ByteArray()
            p.writeUTF(playerName)
            for info in self.server.chatMessages[playerName]:
                if info[3] != '':
                    continue
                chatlogs.append([info[2], info[1], info[0]])
            for info in self.server.chatMessages[playerName]:
                if info[3] == '':
                    continue
                whisperlogs.append([info[3], self.server.chatMessages[playerName], info[1], info[0]])
            p.writeByte(len(chatlogs))
            for info in chatlogs:
                p.writeUTF(info[0])
                p.writeUTF(info[1])
                p.writeUTF(info[2])
            p.writeByte(len(whisperlogs))
            for info in whisperlogs:
                p.writeUTF(info[0])
                p.writeByte(len(info[1]))
                for _chat in info[1]:
                    p.writeUTF(info[2])
                    p.writeUTF(info[3])
            self.client.sendPacket(TFMCodes.game.send.Modopwet_Chatlog, p.toByteArray())

    def openModoPwet(self, isOpen=False, modopwetOnlyPlayerReports=False, sortBy=False):
        if isOpen:
            if (time.time() - self.lastOpened) < 3:
                return
            self.lastOpened = time.time()
            if len(self.server.serverReports) <= 0:
                self.client.sendPacket(TFMCodes.game.send.Open_Modopwet, 0)
            else:
                reports = self.sortReports(self.server.serverReports, sortBy)
                bannedList = {}
                deletedList = {}
                disconnectList = []
                cnt = 0
                _del = 0
                p = ByteArray()  
                for i in reports:
                    playerName = i[0]
                    v = self.server.serverReports[playerName]
                    if self.client.modoPwetLangue == 'ALL' or v["language"] == self.client.modoPwetLangue:
                        for name in v["reporters"]:
                            if int(time.time() - v["reporters"][name][2]) > 86400:
                                del self.server.serverReports[playerName]
                        
                        player = self.server.players.get(playerName)
                        TimePlayed = math.floor(player.playerTime/3600) if player != None else 0
                        playerNameRoom = player.roomName if player != None else "0"
                        roomMods = self.getModopwetMods(playerNameRoom)
                        cnt += 1
                        self.server.lastReportID += 1
                        if cnt >= 255: 
                            break  
                        p.writeByte(cnt)
                        p.writeUnsignedShort(self.server.lastReportID)
                        p.writeUTF(v["language"])
                        p.writeUTF(playerName)
                        p.writeUTF(playerNameRoom)
                        p.writeByte(len(roomMods))
                        for i in roomMods:
                            p.writeUTF(i)
                        p.writeInt(TimePlayed)
                        p.writeByte(int(len(v["reporters"])))
                        for name in v["reporters"]:
                            r = v["reporters"][name]
                            p.writeUTF(name)
                            p.writeShort(self.getPlayerKarma(name))
                            p.writeUTF(r[1])
                            p.writeByte(r[0])
                            p.writeShort(int(Utils.getSecondsDiff(r[2])/60))
                                
                        mute = player.isMuted if player != None else v["isMuted"]
                        p.writeBoolean(mute)
                        if mute:
                            p.writeUTF(v["mutedBy"])
                            p.writeShort(v["muteHours"])
                            p.writeUTF(v["muteReason"])
                            
                        if v['state'] == 'banned':
                            x = {}
                            x['banhours'] = v['banhours']
                            x['banreason'] = v['banreason']
                            x['bannedby'] = v['bannedby']
                            bannedList[playerName] = x
                        if v['state'] == 'deleted':
                            x = {}
                            x['deletedby'] = v['deletedby']
                            deletedList[playerName] = x
                        if v['state'] == 'disconnected':
                            disconnectList.append(playerName)

                self.client.sendPacket(TFMCodes.game.send.Open_Modopwet, ByteArray().writeByte(cnt).toByteArray() + p.toByteArray())
                for user in disconnectList:
                    self.changeReportStatusDisconnect(user)

                for user in deletedList.keys():
                    self.changeReportStatusDeleted(user, deletedList[user]['deletedby'])

                for user in bannedList.keys():
                    self.changeReportStatusBanned(user, bannedList[user]['banhours'], bannedList[user]['banreason'], bannedList[user]['bannedby'])