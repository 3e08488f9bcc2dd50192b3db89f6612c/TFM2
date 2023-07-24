import asyncio
import datetime
import json
import pycountry_convert
import random
import time
from collections import deque
from src.modules import AntiCheat, ByteArray, Cafe, Commands, DailyQuests, Exceptions, ModoPwet, Packets, Shop, Skills, Tribulle
from src.utils.Utils import Utils
from src.utils.TFMCodes import TFMCodes

class Client:
    def __init__(self, _server, _cursor):
        # Istances
        self.server = _server
        self.Cursor = _cursor
        self.clientPacket = ByteArray()

        # Boolean
        self.hasCheese = False
        self.isCafeOpen = False
        self.isClosed = False
        self.isDead = False
        self.isEnterRoom = False
        self.isFashionSquad = False
        self.isFunCorpTeam = False
        self.isGuest = False
        self.isHidden = False
        self.isLuaAdmin = False
        self.isLuaCrew = False
        self.isMapCrew = False
        self.isModoPwet = False
        self.isMumuted = False
        self.isMuted = False
        self.isPrisoned = False
        self.isReloadCafe = False
        self.isShaman = False
        self.isTribeOpen = False
        self.sendFlashPlayerNotice = False
        self.receivePunishmentPopup = False
        self.openingFriendList = False
        self.validatingVersion = False

        # Integer
        self.aventure_points = 0
        self.bootcampCount = 0
        self.cheeseCount = 0
        self.defaultLanguageID = 0
        self.divineSaves = 0
        self.divineSavesNoSkill = 0
        self.equipedShamanBadge = 0
        self.firstCount = 0
        self.fur = 0
        self.furEnd = 0
        self.gender = 0
        self.hardSaves = 0
        self.hardSavesNoSkill = 0
        self.lastPacketID = 0
        self.lastDivorceTimer = 0
        self.lastOn = 0
        self.loginTime = 0
        self.normalSaves = 0
        self.normalSavesNoSkill = 0
        self.pet = 0
        self.petEnd = 0
        self.ping = 0
        self.playerCode = 0
        self.playerID = 0
        self.playerKarma = 0
        self.playerScore = 0
        self.playerTime = 0
        self.privLevel = 0
        self.regDate = 0
        self.shamanCheeses = 0
        self.shamanExp = 0
        self.shamanExpNext = 32
        self.shamanLevel = 0
        self.shamanType = 0
        self.shopCheeses = 0
        self.shopFraises = 0
        self.silenceType = 0
        self.titleID = 0
        self.titleStars = 0
        self.tribeCode = 0
        self.tribeChat = 0
        self.tribeJoined = 0
        self.tribeHouse = 0
        self.tribeRank = 0
        self.tribulleID = 0
        self.verifycoder = random.choice(range(0, 10000))

        # Float/Double

        # String
        self.aventureInfo = ""
        self.avatar = ""
        self.currentCaptcha = ""
        self.countryCode = ""
        self.countryContinent = ""
        self.countryName = ""
        self.defaultLanguage = ""
        self.emailAddress = ""
        self.flashPlayerVersion = ""
        self.flashPlayerInformation = ""
        self.ipAddress = ""
        self.ipColor = ""
        self.lastMessage = ""
        self.lastRoom = ""
        self.marriage = ""
        self.modoPwetLangue = "ALL"
        self.mouseColor = "78583a"
        self.osLanguage = ""
        self.osVersion = ""
        self.playerFakeName = ""
        self.playerLetters = ""
        self.playerLook = "1;0,0,0,0,0,0,0,0,0,0,0"
        self.playerName = ""
        self.playerNameColor = "95d9d6"
        self.shamanColor = "95d9d6"
        self.shamanLook = "0,0,0,0,0,0,0,0,0,0"
        self.shopClothes = ""
        self.shopCustomItems = ""
        self.shopEmojies = ""
        self.shopGifts = ""
        self.shopItems = ""
        self.shopMessages = ""
        self.shopShamanItems = ""
        self.silenceMessage = ""
        self.swfUrl = ""
        self.tempMouseColor = ""
        self.totemInfo = ""
        self.tribeMessage = ""
        self.tribeName = ""
        self.tribeRanks = ""
        self.roomName = ""

        # Dictionary
        self.playerConsumables = {}
        self.playerSkills = {}
        self.shamanBadges = {}
        self.shopBadges = {}

        # List
        self.bootcampTitleList = []
        self.cheeseTitleList = []
        self.defilanteStats = [0, 0, 0]
        self.divineModeTitleList = []
        self.eventTitleList = []
        self.equipedConsumables = []
        self.firstTitleList = []
        self.friendsList = []
        self.hardModeTitleList = []
        self.ignoredsList = []
        self.ignoredMarriageInvites = []
        self.ignoredTribeInvites = []
        self.invitedTribeHouses = []
        self.marriageInvite = []
        self.modopwetCommunityNotifications = []
        self.playerRoles = []
        self.racingStats = [0, 0, 0, 0]
        self.shamanTitleList = []
        self.shopTitleList = []
        self.staffTitleList = []
        self.survivorStats = [0, 0, 0, 0]
        self.titleList = []
        self.tribeInvite = []
        self.voteBan = []

        # Loops
        self.loop = asyncio.get_event_loop()
        
        # Timers
        self.awakeTimer = None
        self.CMDTime = time.time()
        self.msgTime = time.time()
        self.pingTime = time.time()
        self.room = None
        self.transport = None
         
    def connection_made(self, transport: asyncio.Transport) -> None:
        """
        Make connection between client and server.
        """
        self.transport = transport
        self.ipAddress = transport.get_extra_info("peername")[0]
        
        if self.ipAddress in self.server.badIPS:
            self.transport.close()
        
        self.AntiCheat = AntiCheat(self, self.server)
        self.Cafe = Cafe(self, self.server)
        self.Commands = Commands(self, self.server)
        self.DailyQuests = DailyQuests(self, self.server)
        self.exceptionManager = Exceptions.ClientException(self)
        self.ModoPwet = ModoPwet(self, self.server)
        self.Packets = Packets(self, self.server)
        self.Shop = Shop(self, self.server)
        self.Skills = Skills(self, self.server)
        self.Tribulle = Tribulle(self, self.server)
        
        if self.ipAddress in self.server.connectedCounts:
            self.server.connectedCounts[self.ipAddress] += 1
        else:
            self.server.connectedCounts[self.ipAddress] = 1

    def connection_lost(self, *args) -> None: ##########
        """
        Lost connection between client and server.
        """
        self.isClosed = True
        if self.ipAddress in self.server.connectedCounts:
            count = self.server.connectedCounts[self.ipAddress] - 1
            if count <= 0:
                del self.server.connectedCounts[self.ipAddress]
            else:
                self.server.connectedCounts[self.ipAddress] = count
                
        if self.playerName in self.server.players:
            for player in self.server.players.copy().values():
                if player.playerName in self.friendsList and self.playerName in player.friendsList:
                    player.Tribulle.sendFriendDisconnected(self.playerName)
            del self.server.players[self.playerName]

            if self.tribeCode != 0:
                self.Tribulle.sendTribeMemberDisconnected()
            self.sendModInfo(False)

            if self.playerName in self.server.chatMessages:
                self.server.chatMessages[self.playerName] = {}
                del self.server.chatMessages[self.playerName]
                
            if self.playerName in self.server.serverReports:
                if not self.server.serverReports[self.playerName]["state"] in ["banned", "deleted"]:
                    self.server.serverReports[self.playerName]["state"] = "disconnected"
                    
        if self.room != None:
            self.room.removeClient(self)
                    
            self.updateDatabase()
        self.transport.close()

    def data_received(self, data: bytes) -> None:
        """
        Receive new data from the connection.
        """
        if self.isClosed or len(data) < 2:
            return
    
        if data == b'<policy-file-request/>\x00':
            self.transport.write(b'<cross-domain-policy><allow-access-from domain=\"*\" to-ports=\"*\"/></cross-domain-policy>\x00')
            self.transport.close()
            return
            
        self.clientPacket.write(data)
        old_packet = self.clientPacket.copy()
        while self.clientPacket.getLength() > 0:
            packet_length, lenlen = Utils.get_new_len(self.clientPacket)
            if self.clientPacket.getLength() >= packet_length:
                read = ByteArray(self.clientPacket._bytes[:packet_length])
                old_packet._bytes = old_packet._bytes[packet_length:]
                self.clientPacket._bytes = self.clientPacket._bytes[packet_length:]
                self.loop.create_task(self.parsePacket(read))
            else:
                self.clientPacket = old_packet
            
    def eof_received(self) -> None:
        return
            
    async def parsePacket(self, packet) -> None:
        """
        Parse the given packet from the data receiving function.
        """
        if self.isClosed:
            return
            
        packet_id = packet.readByte()
        C = packet.readByte()
        CC = packet.readByte()
        try:
            self.lastPacketID = packet_id
            self.AntiCheat.readPacket(C + CC)
            await self.Packets.parsePacket(packet_id, C, CC, packet)
        except Exception as e:
            self.server.sendStaffMessage(f"The player <BV>{self.playerName}</BV> made error in the system. Check erreur.log for more information.", 9, True)
            self.server.exceptionManager.setException(e)
            self.server.exceptionManager.SaveException(self, "serveur", "servererreur")

    def sendPacket(self, identifiers, data=b"") -> None:
        self.loop.create_task(self.Packets.sendPacket(identifiers, data))

    async def loginPlayer(self, playerName, password, startRoom) -> None: ##########
        """
        Function that handle login.
        """
        if password == "":
            self.playerName = self.server.checkAlreadyExistingGuest(playerName)
            startRoom = "\x03[Tutorial] %s" %(playerName)
            self.isGuest = True
        else:
            if "@" in playerName:
                # Email
                rss = self.Cursor['users'].find({'Email':playerName,'Password':password})
                players = []
                for rs in rss:
                    players.append(rs['Username'])
                if len(players) > 1:
                    i = 0
                    p = ByteArray()
                    while i != len(players):
                        p.writeBytes(players[i]).writeShort(-15708)
                        i += 1
                    self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(11).writeShort(len(p.toByteArray())).writeBytes(p.toByteArray()).writeShort(0).toByteArray())
                    return
                else:
                    playerName = self.server.getPlayerName(playerName)
        
        if not self.fillLoginInformation(playerName, password):
            if not self.isGuest:
                return
        
        self.playerCode += 1
        self.server.players[self.playerName] = self
        #if len(self.server.players) > self.server.MaximumPlayers:
        #    self.sendPacket(Identifiers.send.Queue_popup, ByteArray().writeInt(len(self.server.players) - self.server.MaximumPlayers).toByteArray())
        #    await asyncio.sleep(10)
        #    self.transport.close()
        #    return
        self.loginTime = Utils.getTime()
        self.logConnection()
        self.sendLoginSourisInfo()
        self.sendSwitchTribulle(True)
        self.sendServerPartners()
        self.sendPing()
        if not self.isGuest:
            # Staff Positions
            if "FashionSquad" in self.playerRoles:
                self.isFashionSquad = True
            if "FunCorp" in self.playerRoles:
                self.isFunCorpTeam = True
            if "LuaCrew" in self.playerRoles:
                self.isLuaCrew = True
            if "MapCrew" in self.playerRoles:
                self.isMapCrew = True
                
            self.sendPlayerIdentification()
            self.sendTimeStamp()
            self.fillTribeInformation(self.tribeCode)
            self.Tribulle.sendFriendsList(None)
            self.sendModInfo(True)
            self.sendDefaultChat()
            self.sendAventurePoints()
            
            for player in self.server.players.values():
                if self.playerName in player.friendsList and player.playerName in self.friendsList:
                    player.Tribulle.sendFriendConnected(self.playerName)
                    
            if self.tribeCode != 0:
                self.Tribulle.sendTribeMemberConnected()
                
            if self.playerName in self.server.serverReports:
                self.server.serverReports[self.playerName]["state"] = "online"
        else:
            self.sendPlayerIdentification()
        
            
            

        self.startBulle("1") # self.startBulle(self.server.checkRoom(startRoom, self.langue) if not startRoom == "" and not startRoom == "1" else self.server.recommendRoom(self.langue))
        self.server.loop.call_later(1, self.sendFlashPlayerWarning)
        self.server.loop.call_later(1, self.sendPunishmentPopup)
        print(self.playerName)

    def checkTimeAccount(self) -> bool:
        """
        Checks the time about playerName creates new account.
        """
        rrf = self.Cursor['account'].find_one({'Ip':self.ipAddress})
        return rrf == None or int(str(time.time()).split(".")[0]) >= int(rrf['Time'])
                    
    def fillLoginInformation(self, playerName, password) -> bool:
        """
        Login stage 2
        """
        if self.server.checkConnectedUser(playerName) or len(playerName) == 0:
            self.server.loop.call_later(2, lambda: self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(1).writeUTF("").writeUTF("").toByteArray()))
            return False
        
        if self.privLevel == -1:
            self.sendPacket(TFMCodes.old.send.Player_Ban_Login, ["This account is permanently banned."])
            return False
        
        banInfo = self.server.getBanInfo(playerName)
        if len(banInfo) > 0:
            timeCalc = Utils.getHoursDiff(banInfo[1])
            if timeCalc <= 0:
                self.server.removeBan(playerName)
                self.receivePunishmentPopup = True
            else:
                self.sendPacket(TFMCodes.old.send.Player_Ban_Login, [timeCalc, banInfo[0]])
                return False
    
        muteInfo = self.server.getMuteInfo(playerName)
        if len(muteInfo) > 0:
            timeCalc = Utils.getHoursDiff(muteInfo[1])
            if timeCalc <= 0:
                self.server.removeMute(self.playerName, "ServeurMute")
            else:
                self.isMuted = True
    
        rs = self.Cursor['users'].find_one({('Email' if "@" in playerName else 'Username'):playerName,'Password':password})
        if rs:
            if "@" in playerName:
                self.playerName = rs["Username"]
            else:
                self.playerName = playerName
            self.emailAddress = rs["Email"]
            self.privLevel = rs["PrivLevel"]
            self.playerID = rs["PlayerID"]
            self.titleID = rs["TitleID"]
            self.firstCount = rs["FirstCount"]
            self.cheeseCount = rs["CheeseCount"]
            self.bootcampCount = rs["BootcampCount"]
            self.shamanCheeses = rs["ShamanCheeses"]
            self.shopCheeses = rs["ShopCheeses"]
            self.shopFraises = rs["ShopFraises"]
            self.normalSaves = rs["NormalSaves"]
            self.normalSavesNoSkill = rs["NormalSavesNoSkill"]
            self.hardSaves = rs["HardSaves"]
            self.hardSavesNoSkill = rs["HardSavesNoSkill"]
            self.divineSaves = rs["DivineSaves"]
            self.divineSavesNoSkill = rs["DivineSavesNoSkill"]
            self.shamanType = rs["ShamanType"]
            self.shopItems = rs["ShopItems"]
            self.shopShamanItems = rs["ShopShamanItems"]
            self.shopCustomItems = rs["ShopCustomItems"]
            self.shopEmojies = rs["ShopEmojies"]
            self.shopClothes = rs["ShopClothes"]
            self.shopGifts = rs["ShopGifts"]
            self.shopMessages = rs["ShopMessages"]
            self.playerLook = rs["Look"]
            self.shamanLook = rs["ShamanLook"]
            self.mouseColor = rs["MouseColor"]
            self.shamanColor = rs["ShamanColor"]
            self.regDate = rs["RegDate"]
            self.cheeseTitleList = list(map(float, filter(None, rs['CheeseTitleList'].split(","))))
            self.firstTitleList = list(map(float, filter(None, rs['FirstTitleList'].split(","))))
            self.shamanTitleList = list(map(float, filter(None, rs['ShamanTitleList'].split(","))))
            self.shopTitleList = list(map(float, filter(None, rs['ShopTitleList'].split(","))))
            self.bootcampTitleList = list(map(float, filter(None, rs['BootcampTitleList'].split(","))))
            self.hardModeTitleList = list(map(float, filter(None, rs['HardModeTitleList'].split(","))))
            self.divineModeTitleList = list(map(float, filter(None, rs['DivineModeTitleList'].split(","))))
            self.eventTitleList = list(map(float, filter(None, rs['EventTitleList'].split(","))))
            self.staffTitleList = list(map(float, filter(None, rs['StaffTitleList'].split(","))))
            self.shamanLevel = rs['ShamanLevel']
            self.shamanExp = rs['ShamanExp']
            self.shamanExpNext = rs['ShamanExpNext']
            for skill in list(map(str, filter(None, rs['Skills'].split(";")))):
                values = skill.split(":")
                self.playerSkills[int(values[0])] = int(values[1])
            self.friendsList = rs['FriendsList'].split(",")
            self.ignoredsList = rs['IgnoredsList'].split(",")
            self.gender = rs['Gender']
            self.lastOn = rs['LastOn']
            self.lastDivorceTimer = rs['LastDivorceTimer']
            self.marriage = rs['Marriage']
            self.tribeCode = rs['TribeCode']
            self.tribeRank = rs['TribeRank']
            self.tribeJoined = rs['TribeJoined']
            self.survivorStats = list(map(int, rs['SurvivorStats'].split(",")))
            self.racingStats = list(map(int, rs['RacingStats'].split(",")))
            self.defilanteStats = list(map(int, rs['DefilanteStats'].split(",")))
            for consumable in list(map(str, filter(None, rs['Consumables'].split(";")))):
                values = consumable.split(":")
                self.playerConsumables[int(values[0])] = int(values[1])
                
            self.equipedConsumables = list(map(int, filter(None, rs['EquipedConsumables'].split(","))))
            self.pet = rs['Pet']
            self.petEnd = 0 if self.pet == 0 else Utils.getTime() + rs['PetEnd']
            self.fur = rs['Fur']
            self.furEnd = 0 if self.furEnd == 0 else Utils.getTime() + rs['FurEnd']
            self.shamanBadges = list(map(int, filter(None, rs['ShamanBadges'].split(","))))
            self.shopBadges = list(map(int, filter(None, rs['Badges'].split(","))))
            self.equipedShamanBadge = rs['EquipedShamanBadge']
            self.avatar = rs["Avatar"]
            self.totemInfo = rs["TotemInfo"]
            self.aventureInfo = json.loads(rs["AdventureInfo"])
            self.playerLetters = rs["Letters"]
            self.playerTime = rs["Time"]
            self.playerKarma = rs["Karma"]
            self.playerRoles = rs["Roles"].split(",")
            return True
        else:
            self.server.loop.call_later(2, lambda: self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(2).writeUTF("").writeUTF("").toByteArray()))
            return False
            
    def fillTribeInformation(self, tribeCode) -> None:
        rs = self.Cursor['tribe'].find_one({"Code":tribeCode})
        if rs:
            self.tribeName = rs["Name"]
            self.tribeMessage = rs["Message"]
            self.tribeHouse = rs["House"]
            self.tribeRanks = rs["Ranks"]
            self.tribeChat = rs["Chat"]
            
    def logConnection(self):
        country = self.server.geoIPData.country_name_by_addr(self.ipAddress)
        country_code = self.server.geoIPData.country_code_by_addr(self.ipAddress)
        self.countryName = country if country != "" else "localhost"
        self.countryCode = country_code if country_code != "" else "None"
        if self.countryName != "localhost":
            self.countryContinent = pycountry_convert.convert_continent_code_to_continent_name(pycountry_convert.country_alpha2_to_continent_code(pycountry_convert.country_name_to_country_alpha2(self.countryName)))
        else:
            self.countryContinent = "None"
        self.ipColor = Utils.ipColor(Utils.EncodeIP(self.ipAddress))
        if not self.isGuest:
            self.Cursor['loginlog'].insert_one({'Username':self.playerName, 'IP':Utils.EncodeIP(self.ipAddress), 'Country':self.countryName, 'IPColor': self.ipColor, 'Time': Utils.getDate(), 'Community': self.defaultLanguage, 'ConnectionID':self.server.serverInfo["game_name"]})
            
    def logMessage(self, message, whisper=''):
        if not self.playerName in self.server.chatMessages:
             messages = deque([], 60)
             messages.append([time.strftime("%Y/%m/%d %H:%M:%S"), message, self.roomName, whisper])
             self.server.chatMessages[self.playerName] = messages
        else:
            self.server.chatMessages[self.playerName].append([time.strftime("%Y/%m/%d %H:%M:%S"), message, self.roomName, whisper])
            
    def sendAccountTime(self) -> None:
        """
        Sends the account time before he can make alt.
        """
        date = datetime.datetime.now() + datetime.timedelta(hours=1)
        eventTime = int(str(time.mktime(date.timetuple())).split(".")[0])
        if not self.Cursor['account'].find_one({'Ip':self.ipAddress}):
           self.Cursor['account'].insert_one({'Ip':self.ipAddress,'Time':eventTime})
        else:
           self.Cursor['account'].update_one({'Ip':self.ipAddress},{'$set':{'Time':eventTime}})
            
    def sendAventurePoints(self):
        points = 0
        for info in self.aventureInfo:
            r1 = info["adv_points"]
            if r1 > 0:
                points += r1
        self.aventure_points = points
            
    def sendAnchors(self) -> None:
        """
        Sends all anchors in the room.
        """
        self.sendPacket(TFMCodes.old.send.Anchors, self.room.anchors)
            
    def sendBanMessage(self, hours, reason, silent) -> None:
        """
        Sends the ban pop up and message to everyone in the room.
        """
        self.transport.close()
        if self.room != None and not silent:
            for player in self.room.clients.copy().values():
                player.sendLangueMessage("", "<ROSE>• [Moderation] $Message_Ban", self.playerName, str(hours), reason)
            
    def sendCorrectVersion(self, lang='en') -> None:
        """
        Sends the login screen.
        """
        self.sendPacket(TFMCodes.game.send.Correct_Version, ByteArray().writeUnsignedInt(len(self.server.players)).writeUTF(lang).writeUTF('').writeInt(self.server.swfInfo["auth_key"]).writeBoolean(False).toByteArray())
        self.sendPacket(TFMCodes.game.send.Banner_Login, ByteArray().writeBoolean(True).writeByte(self.server.eventInfo["adventure_id"]).writeShort(256).toByteArray())
        self.sendPacket(TFMCodes.game.send.Image_Login, ByteArray().writeUTF(self.server.eventInfo["adventure_img"]).toByteArray())
        self.sendPacket(TFMCodes.game.send.Init_Authorization, ByteArray().writeInt(self.verifycoder).toByteArray())
                
    def sendDefaultChat(self) -> None:
        """
        Sends the default community custom chat.
        """
        if self.defaultLanguage in self.server.chats and not self.playerName in self.server.chats[self.defaultLanguage]:
            self.server.chats[self.defaultLanguage].append(self.playerName)
        elif not self.defaultLanguage in self.server.chats:
            self.server.lastChatID += 1
            self.server.chats[self.defaultLanguage] = [self.playerName]
        self.sendTribullePacket(TFMCodes.tribulle.send.ET_SignaleRejointCanal, ByteArray().writeUTF(self.defaultLanguage).toByteArray())
                
    def sendEnterRoom(self, roomName) -> None:
        found = False
        rooms = roomName[3:]
        count = "".join(i for i in rooms if i.isdigit())
        for room in ["vanilla", "survivor", "racing", "music", "bootcamp", "defilante", "village", "#fastracing"]:
            if rooms.startswith(room) and not count == "" or rooms.isdigit():
                found = not (int(count) < 1 or int(count) > 1000 or rooms == room)
        self.sendPacket(TFMCodes.game.send.Enter_Room, ByteArray().writeBoolean(found).writeUTF(roomName).writeUTF("xx" if roomName.startswith("*") else self.defaultLanguage.upper()).toByteArray())

    def sendFlashPlayerWarning(self):
        if self.sendFlashPlayerNotice:
            self.sendPacket(TFMCodes.game.send.Flash_Player_Attention_Popup, ByteArray().writeUTF("").toByteArray())
            self.sendFlashPlayerNotice = False

    def sendLangueMessage(self, community, message, *args, isAll=False) -> None:
        """
        Sends the message translated by transformice languages.
        """
        packet = ByteArray().writeUTF(community).writeUTF(message).writeByte(len(args))
        for arg in args:
            packet.writeUTF(arg)
        if isAll:
            self.room.sendAll(TFMCodes.game.send.Message_Langue, packet.toByteArray())
        else:
            self.sendPacket(TFMCodes.game.send.Message_Langue, packet.toByteArray())
            
    def sendLangueMessageOthers(self, community, message, *args) -> None:
        """
        Sends the message translated by transformice languages.
        """
        packet = ByteArray().writeUTF(community).writeUTF(message).writeByte(len(args))
        for arg in args:
            packet.writeUTF(arg)
        self.room.sendAllOthers(self, TFMCodes.game.send.Message_Langue, packet.toByteArray())
              
    def sendLogMessage(self, message):
        self.sendPacket(TFMCodes.game.send.Log_Message, ByteArray().writeByte(0).writeUTF("").writeUnsignedByte((len(message) >> 16) & 0xFF).writeUnsignedByte((len(message) >> 8) & 0xFF).writeUnsignedByte(len(message) & 0xFF).writeBytes(message).toByteArray())
              
    def sendLoginSourisInfo(self) -> None:
        """
        Sends the additional guest login information.
        """
        if self.isGuest:
            self.sendPacket(TFMCodes.game.send.Login_Souris, ByteArray().writeByte(1).writeByte(10).toByteArray())
            self.sendPacket(TFMCodes.game.send.Login_Souris, ByteArray().writeByte(2).writeByte(5).toByteArray())
            self.sendPacket(TFMCodes.game.send.Login_Souris, ByteArray().writeByte(3).writeByte(15).toByteArray())
            self.sendPacket(TFMCodes.game.send.Login_Souris, ByteArray().writeByte(4).writeByte(200).toByteArray())
              
    def sendMessage(self, message) -> None:
        """
        Sends a message in the chat.
        """
        self.sendPacket(TFMCodes.game.send.Message, ByteArray().writeUTF(message).toByteArray())
              
    def sendModInfo(self, isOnline) -> None:
        """
        Sends information when staff member connect or disconnect from the game.
        """
        if self.privLevel == 9:
            self.server.sendMessageAll(9, f"<font color='#fc0303'>• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
            
        elif self.privLevel in [8, 7]:
            cc = "<font color='#b993ca'>" if not self.privLevel == 8 else "<font color='#c565fe'>"
            self.server.sendMessageAll(7, f"{cc}• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
            
        elif self.privLevel == 6 or self.isMapCrew:
            self.server.sendMessageAll(6, f"<font color='#2F7FCC'>• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
            
        elif self.privLevel == 5 or self.isFunCorpTeam:
            self.server.sendMessageAll(5, f"<font color='#F89F4B'>• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
            
        elif self.privLevel == 4 or self.isLuaCrew:
            self.server.sendMessageAll(4, f"<font color='#79bbac'>• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
            
        elif self.privLevel == 3 or self.isFashionSquad:
            self.server.sendMessageAll(3, f"<font color='#ffb6c1'>• [{self.defaultLanguage.upper()}] {self.playerName} {'just connected' if bool(isOnline) else 'has disconnected'}.</font>")
              
        if (self.privLevel > 2 or self.isFashionSquad or self.isLuaCrew or self.isFunCorpTeam or self.isMapCrew) and isOnline == True:
            for player in self.server.players.values():
                if player != self:
                    if player.privLevel == 9 and self.privLevel == 9:
                        self.sendMessage(f"<font color='#fc0303'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif player.privLevel == 8 and self.privLevel == 8:
                        self.sendMessage(f"<font color='#b993ca'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif player.privLevel == 7 and self.privLevel == 7:
                        self.sendMessage(f"<font color='#c565fe'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif (player.privLevel == 6 or player.isMapCrew) and (self.privLevel == 6 or self.isMapCrew):
                        self.sendMessage(f"<font color='#2F7FCC'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif (player.privLevel == 5 or player.isFunCorpTeam) and (self.privLevel == 5 or self.isFunCorpTeam):
                        self.sendMessage(f"<font color='#F89F4B'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif (player.privLevel == 4 or player.isLuaCrew) and (self.privLevel == 4 or self.isLuaCrew):
                        self.sendMessage(f"<font color='#79bbac'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
                    elif (player.privLevel == 3 or player.isFashionSquad) and (self.privLevel == 3 or self.isFashionSquad):
                        self.sendMessage(f"<font color='#ffb6c1'>• [{player.defaultLanguage.upper()}] {player.playerName} : {player.roomName}</font>")
              
    def sendMuteMessage(self, playerName, hours, reason, only) -> None:
        """
        Sends the muted message.
        """
        if only == False:
            self.sendLangueMessageOthers("", "<ROSE>$MuteInfo2", playerName, hours, reason)
        else:
            player = self.server.players.get(playerName)
            if player:
                player.sendLangueMessage("", "<ROSE>$MuteInfo1", hours, reason, isAll=False)
                
    def sendPacketWholeChat(self, chatName, code, result, isAll=False) -> None:
        """
        Sends packet to everyone in the specific chat.
        """
        for player in self.server.players.copy().values():
            if player.playerCode != self.playerCode or isAll:
                if player.playerName in self.server.chats[chatName]:
                    player.sendTribullePacket(code, result)
                    
    def sendPacketWholeTribe(self, code, result, all=False) -> None:
        """
        Sends packet to everyone in the tribe.
        """
        for player in self.server.players.copy().values():
            if player.playerCode != self.playerCode or all:
                if player.tribeCode == self.tribeCode:
                    player.sendTribullePacket(code, result)
        
    def sendPing(self):
        self.ping += 1
        if self.ping > 255:
            self.ping = 0
        self.sendPacket(TFMCodes.game.send.Ping, ByteArray().writeByte(1).writeByte(self.ping).toByteArray())
        self.pingTime = time.time()
        
    def sendPlayerDisconnect(self):
        self.room.sendAll(TFMCodes.old.send.Player_Disconnect, [self.playerCode])
        
    def sendPlayerIdentification(self) -> None:
        """
        Sends the player identification (permissions).
        """
        permsCount = 0
        perms = ByteArray()
        """
        Fashion Squad - 3
        Lua Team - 4 
        Fun Corp - 5
        Map Crew - 6
        Private Mod - 7
        Moderator - 8
        Admin - 9
        """
        privAuthorization = {0:-1, 1:-1, 2:-1, 3:15, 4:12, 5:13, 6:11, 7:5, 8:5, 9:15}
        permsList = []
        
        for priv, auth in privAuthorization.items():
            if (self.privLevel >= priv):
                permsList.append(auth)
                
        if self.isMapCrew:
            permsList.append(11)
            
        if self.isFashionSquad:
            permsList.append(15)
            
        if self.isLuaCrew:
            permsList.append(12)
            
        if self.isFunCorpTeam:
            permsList.append(13)
                
        if self.privLevel >= 7:
            permsList.insert(1, 3) 
            
        if self.privLevel >= 9:
            permsList.append(10)

        for i in permsList:
            permsCount += 1
            perms.writeByte(i)

        data = ByteArray()
        data.writeInt(self.playerID)
        data.writeUTF(self.playerName)
        data.writeInt(self.playerTime)
        data.writeByte(self.defaultLanguageID)
        data.writeInt(self.playerCode)
        data.writeBoolean(not self.isGuest)
        data.writeByte(permsCount)
        data.writeBytes(perms.toByteArray())
        data.writeBoolean(self.privLevel >= 9)
        data.writeUnsignedShort(255)
        data.writeUnsignedShort(len(self.server.serverLanguagesInfo))
        for lang in self.server.serverLanguagesInfo:
            data.writeUTF(self.server.serverLanguagesInfo[lang][0]).writeUTF(self.server.serverLanguagesInfo[lang][2])
        self.sendPacket(TFMCodes.game.send.Player_Identification, data.toByteArray())
                
    def sendProfile(self, playerName) -> None:
        """
        Sends the player's profile.
        """
        player = self.server.players.get(playerName)
        if player != None and not player.isGuest:
            packet = ByteArray().writeUTF(player.playerName).writeInt(player.avatar).writeInt(str(player.regDate)[:10]).writeInt(int(self.server.getProfileColor(player), 16)).writeByte(player.gender).writeUTF(player.tribeName).writeUTF(player.marriage)
            
            for stat in [player.normalSaves, player.shamanCheeses, player.firstCount, player.cheeseCount, player.hardSaves, player.bootcampCount, player.divineSaves, player.normalSavesNoSkill, player.hardSavesNoSkill, player.divineSavesNoSkill]:
                packet.writeInt(stat)
                
            packet.writeShort(player.titleID).writeShort(len(player.titleList))
            for title in player.titleList:
                packet.writeShort(int(title - (title % 1)))
                packet.writeByte(int(round((title % 1) * 10)))
 
            packet.writeUTF(((str(player.fur) + ";" + player.playerLook.split(";")[1]) if player.fur != 0 else player.playerLook) + ";" + player.mouseColor)
            packet.writeShort(player.shamanLevel)
            
            badges = list(map(int, player.shopBadges))
            listBadges = []
            for badge in badges:
                if not badge in listBadges:
                    listBadges.append(badge)

            packet.writeShort(len(listBadges) * 2)
            for badge in listBadges:
                packet.writeShort(badge).writeShort(badges.count(badge))
 
            stats = [[30, player.racingStats[0], 1500, 124], [31, player.racingStats[1], 10000, 125], [33, player.racingStats[2], 10000, 127], [32, player.racingStats[3], 10000, 126], [26, player.survivorStats[0], 1000, 120], [27, player.survivorStats[1], 800, 121], [28, player.survivorStats[2], 20000, 122], [29, player.survivorStats[3], 10000, 123], [42, player.defilanteStats[0], 1500, 288], [43, player.defilanteStats[1], 10000, 287], [44, player.defilanteStats[2], 100000, 286]]
            packet.writeByte(len(stats))
            for stat in stats:
                packet.writeByte(stat[0]).writeInt(stat[1]).writeInt(stat[2]).writeShort(stat[3])

            shamanBadges = player.shamanBadges
            packet.writeByte(player.equipedShamanBadge).writeByte(len(shamanBadges))
            
            for shamanBadge in shamanBadges:
                packet.writeByte(shamanBadge)
                
            points = self.aventure_points
            packet.writeBoolean(points > 0)
            packet.writeInt(points)
            self.sendPacket(TFMCodes.game.send.Profile, packet.toByteArray())
                
    def sendPunishmentPopup(self):
        if self.receivePunishmentPopup:
            amount = random.randint(1000, 9999)
            self.sendPacket(TFMCodes.game.send.Take_Cheese_Popup, ByteArray().writeShort(amount).toByteArray())
            self.shopCheeses -= amount
            if self.shopCheeses < 0:
                self.shopCheeses = 0
            self.receivePunishmentPopup = False
                
    def sendServerMessage(self, message, tab=False) -> None:
        """
        Sends message in #Server
        """
        self.sendPacket(TFMCodes.game.send.Server_Message, ByteArray().writeBoolean(tab).writeUTF(message).writeByte(0).writeUTF("").toByteArray())
                        
    def sendRoomServer(self, gameType, serverType):
        self.sendPacket(TFMCodes.game.send.Room_Type, gameType)
        self.sendPacket(TFMCodes.game.send.Room_Server, serverType)
                
    def sendServerPartners(self):
        p = ByteArray()
        p.writeUnsignedShort(len(self.server.serverPartners))
        for partner in self.server.serverPartners:
            p.writeUTF(partner["name"]).writeUTF(partner["url"])
        self.sendPacket(TFMCodes.game.send.Community_Partner, p.toByteArray())
                
    def sendStaffChatMessage(self, type, message) -> None:
        """
        Sends a message in given staff channel.
        """
        for client in self.server.players.copy().values():
            if(type == 3):
                if(client.privLevel >= 7 and client.defaultLanguage == self.defaultLanguage):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 4):
                if(client.privLevel >= 7):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 2):
                if(client.privLevel >= 7 and client.defaultLanguage == self.defaultLanguage):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 5):
                if(client.privLevel >= 7):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 9):
                if(client.privLevel in [5, 9] or client.isFunCorpTeam == True):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 8):
                if(client.privLevel in [4, 9] or client.isLuaCrew == True):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())
                    
            elif(type == 10):
                if(client.privLevel in [3, 9] or client.isFashionSquad == True):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())

            elif(type == 7):
                if(client.privLevel in [6, 9] or client.isMapCrew == True):
                    client.sendPacket(TFMCodes.game.send.Send_Staff_Chat, ByteArray().writeByte(1 if type == -1 else type).writeUTF(self.playerName).writeUTF(message).writeShort(0).writeShort(0).toByteArray())

    def sendSwitchTribulle(self, isNew) -> None:
        """
        Switch to the new tribulle.
        """
        self.sendPacket(TFMCodes.game.send.Switch_Tribulle, ByteArray().writeBoolean(isNew).toByteArray())
        
    def sendTimeStamp(self) -> None:
        self.sendPacket(TFMCodes.game.send.Time_Stamp, ByteArray().writeInt(self.loginTime).toByteArray())
        
    def sendTribullePacket(self, code, result) -> None:
        """
        Sends packet to tribulle
        """
        self.sendPacket(TFMCodes.game.send.Tribulle_Packet, ByteArray().writeShort(code).writeBytes(result).toByteArray())
                       
    def startBulle(self, roomName) -> None:
        if not self.isEnterRoom:
            self.isEnterRoom = True
            self.server.loop.call_later(0.8, lambda: self.enterRoom(roomName))
            self.server.loop.call_later(6, setattr, self, "isEnterRoom", False)
                    
    def resetFuncorpEffects(self):
        self.playerFakeName = ""
        self.tempMouseColor = ""
        self.playerNameColor = "95d9d6"
                                        
    def enterRoom(self, roomName):
        roomName = roomName.replace("<", "&lt;")
        self.roomFuncorps = []
        
        if (roomName.startswith("*\x03") and not roomName == "*\x03" + self.tribeName and not roomName[2:] in self.invitedTribeHouses) or self.isPrisoned:
            roomName = self.lastRoom
            
        if not roomName.startswith("*") and not (len(roomName) > 3 and roomName[2] == "-" and self.privLevel > 6):
            roomName = "%s-%s" %(self.defaultLanguage.upper(), roomName)
            
        for rooms in ["\x03[Editeur]", "\x03[Totem]", "\x03[Tutorial]"]: #
            if roomName.startswith(rooms) and not self.playerName == roomName.split(" ")[1]: # 
                roomName = "%s-%s" %(self.langue, self.playerName) #
        
        if self.room != None:
            self.room.removeClient(self)
        
        self.roomName = roomName
        self.sendRoomServer(2, 0)
        self.sendEnterRoom(roomName)
        self.server.addClientToRoom(self, roomName)
        self.sendAnchors()
        
        for player in [*self.server.rooms[roomName].clients.values()]:
            if self.playerName in player.friendsList and player.playerName in self.friendsList:
                player.Tribulle.sendFriendChangedRoom(self.playerName)
                
        if self.tribeCode != 0:
            self.Tribulle.sendTribeMemberChangeRoom()
        
        
        
        if self.room.isFunCorp:
            for player in [*self.server.rooms[roomName].clients.values()]:
                if player.privLevel in [5, 9] or player.isFunCorpTeam:
                    self.roomFuncorps.append(player.playerName)
            self.sendLangueMessage("", "<FC>$FunCorpActiveAvecMembres</FC>", ', '.join(map(str, self.roomFuncorps)))
            
        self.lastRoom = self.roomName
        
        
    def getPlayerData(self):
        data = ByteArray()
        data.writeUTF(self.playerName if self.playerFakeName == "" else self.playerFakeName)
        data.writeInt(self.playerCode)
        data.writeBoolean(self.isShaman)
        data.writeBoolean(self.isDead)
        if not self.isHidden:
            data.writeShort(self.playerScore)
        data.writeBoolean(self.hasCheese)
        data.writeShort(self.titleID)
        data.writeByte(self.titleStars)
        data.writeByte(self.gender)
        data.writeUTF("")
        data.writeUTF("1;0,0,0,0,0,0,0,0,0,0") #if self.room.isBootcamp else (str(self.fur) + ";" + self.playerLook.split(";")[1] if self.fur != 0 else self.playerLook))
        data.writeBoolean(False)
        data.writeInt(int(self.tempMouseColor if not self.tempMouseColor == "" else self.mouseColor, 16))
        data.writeInt(int(self.shamanColor, 16))
        data.writeInt(0)
        data.writeInt(int(self.playerNameColor, 16))
        data.writeByte(0)
        return data.toByteArray()
          
    def updateDatabase(self) -> None: ########
        """
        Update the database
        """
        if self.isGuest:
            return

        #self.DailyQuests.updateMissions()
        self.Cursor['users'].update_one({'Username':self.playerName}, {'$set':{
            'TitleID':self.titleID,
            "FirstCount":self.firstCount,
            "CheeseCount":self.cheeseCount,
            "BootcampCount":self.bootcampCount,
            "ShamanCheeses":self.shamanCheeses,
            "ShopCheeses":self.shopCheeses,
            "ShopFraises":self.shopFraises,
            "NormalSaves":self.normalSaves,
            "NormalSavesNoSkill":self.normalSavesNoSkill,
            "HardSaves":self.hardSaves,
            "HardSavesNoSkill":self.hardSavesNoSkill,
            "DivineSaves":self.divineSaves,
            "DivineSavesNoSkill":self.divineSavesNoSkill,
            "ShamanType":self.shamanType,
            "ShopItems":self.shopItems,
            "ShopShamanItems":self.shopShamanItems,
            "ShopCustomItems":self.shopCustomItems,
            "shopEmojies":self.shopEmojies,
            "shopClothes": "|".join(map(str, self.shopClothes)),
            "shopGifts":self.shopGifts,
            "shopMessages":self.shopMessages,
            "Look":self.playerLook,
            "ShamanLook": self.shamanLook,
            "MouseColor": self.mouseColor,
            "ShamanColor": self.shamanColor,
            "RegDate": self.regDate,
            "CheeseTitleList": ",".join(map(str, self.cheeseTitleList)),
            "FirstTitleList": ",".join(map(str, self.firstTitleList)),
            "ShamanTitleList": ",".join(map(str, self.shamanTitleList)),
            "ShopTitleList": ",".join(map(str, self.shopTitleList)),
            "BootcampTitleList": ",".join(map(str, self.bootcampTitleList)),
            "HardModeTitleList": ",".join(map(str, self.hardModeTitleList)),
            "DivineModeTitleList": ",".join(map(str, self.divineModeTitleList)),
            "EventTitleList": ",".join(map(str, self.eventTitleList)),
            "StaffTitleList": ",".join(map(str, self.staffTitleList)),
            "ShamanLevel":self.shamanLevel,
            "ShamanExp":self.shamanExp,
            "ShamanExpNext":self.shamanExpNext,
            "Skills": ";".join(map(lambda skill: "%s:%s" %(skill[0], skill[1]), self.playerSkills.items())),
            "FriendsList": ",".join(map(str, filter(None, [friend for friend in self.friendsList]))),
            "IgnoredsList": ",".join(map(str, filter(None, [ignored for ignored in self.ignoredsList]))),
            "Gender": self.gender,
            "LastOn": self.Tribulle.getTime(),
            "LastDivorceTimer": self.lastDivorceTimer,
            "Marriage": self.marriage,
            "TribeCode": self.tribeCode,
            "TribeRank": self.tribeRank,
            "TribeJoined": self.tribeJoined,
            "SurvivorStats": ",".join(map(str, self.survivorStats)),
            "RacingStats": ",".join(map(str, self.racingStats)),
            "DefilanteStats": ",".join(map(str, self.defilanteStats)),
            "Consumables": "".join(map(lambda consumable: "%s:%s" %(consumable[0], consumable[1]), self.playerConsumables.items())),
            "EquipedConsumables": ",".join(map(str, self.equipedConsumables)),
            "Pet": self.pet,
            "PetEnd": abs(Utils.getSecondsDiff(self.petEnd)),
            "Fur": self.fur,
            "FurEnd": abs(Utils.getSecondsDiff(self.furEnd)),
            "Badges": ",".join(map(str, self.shopBadges)),
            "ShamanBadges": ",".join(map(str, self.shamanBadges)),
            "EquipedShamanBadge": self.equipedShamanBadge,
            "Letters": self.playerLetters,
            "Time": self.playerTime + abs(Utils.getSecondsDiff(self.loginTime)),
            "Karma": self.playerKarma,
            "AdventureInfo": json.dumps(self.aventureInfo),
            "TotemInfo": self.totemInfo,
            "Roles": ",".join(map(str, self.playerRoles))
        }})