import asyncio
import datetime
import random
import time
from src.modules import AntiCheat, ByteArray, Cafe, Commands, DailyQuests, ModoPwet, Packets, Shop, Skills, Tribulle
from src.utils.Utils import Utils
from src.utils.TFMCodes import TFMCodes

class Client:
    def __init__(self, _server, _cursor):
        # Istances
        self.server = _server
        self.Cursor = _cursor
        self.clientPacket = ByteArray()

        # Boolean
        self.isCafeOpen = False
        self.isClosed = False
        self.isFashionSquad = False
        self.isFunCorpTeam = False
        self.isGuest = False
        self.isLuaCrew = False
        self.isMapCrew = False
        self.isReloadCafe = False
        self.sendFlashPlayerNotice = False
        self.openingFriendList = False
        self.validatingVersion = False

        # Integer
        self.banHours = 0
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
        self.playerCode = 0
        self.playerID = 0
        self.playerTime = 0
        self.playerKarma = 0
        self.privLevel = 0
        self.regDate = 0
        self.shamanCheeses = 0
        self.shamanExp = 0
        self.shamanExpNext = 32
        self.shamanLevel = 0
        self.shamanType = 0
        self.shopCheeses = 0
        self.shopFraises = 0
        self.titleID = 0
        self.tribeCode = 0
        self.tribeJoined = 0
        self.tribeRank = 0
        self.verifycoder = random.choice(range(0, 10000))

        # Float/Double

        # String
        self.aventureInfo = ""
        self.avatar = ""
        self.currentCaptcha = ""
        self.defaultLanguage = ""
        self.emailAddress = ""
        self.flashPlayerVersion = ""
        self.flashPlayerInformation = ""
        self.ipAddress = ""
        self.marriage = ""
        self.mouseColor = "78583a"
        self.osLanguage = ""
        self.osVersion = ""
        self.playerLetters = ""
        self.playerLook = "1;0,0,0,0,0,0,0,0,0,0,0"
        self.playerName = ""
        self.shamanColor = "95d9d6"
        self.shamanLook = "0,0,0,0,0,0,0,0,0,0"
        self.shopClothes = ""
        self.shopCustomItems = ""
        self.shopEmojies = ""
        self.shopGifts = ""
        self.shopItems = ""
        self.shopMessages = ""
        self.shopShamanItems = ""
        self.swfUrl = ""
        self.totemInfo = ""

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
        self.playerRoles = []
        self.racingStats = [0, 0, 0, 0]
        self.shamanTitleList = []
        self.shopTitleList = []
        self.staffTitleList = []
        self.survivorStats = [0, 0, 0, 0]

        # Loops
        self.loop = asyncio.get_event_loop()
        
        # Other
        self.awakeTimer = None
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
            del self.server.players[self.playerName]
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
                elif len(players) == 1:
                    if not self.fillLoginInformation(playerName, password):
                        return
                else:
                    self.server.loop.call_later(2, lambda: self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(2).writeUTF("").writeUTF("").toByteArray()))
                    return                    
                    
            elif self.server.checkConnectedUser(playerName):
                self.server.loop.call_later(2, lambda: self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(2).writeUTF("").writeUTF("").toByteArray()))
                return
            else:
                if not self.fillLoginInformation(playerName, password):
                    return
        
        self.playerCode += 1
        self.server.players[self.playerName] = self
        self.loginTime = Utils.getTime()
        #if len(self.server.players) > self.server.MaximumPlayers:
        #    self.sendPacket(Identifiers.send.Queue_popup, ByteArray().writeInt(len(self.server.players) - self.server.MaximumPlayers).toByteArray())
        #    await asyncio.sleep(10)
        #    self.transport.close()
        #    return
        #self.ipDetails = self.receiveIPDetails(self.ipAddress)
        self.sendPlayerIdentification()
        self.sendLoginSourisInfo()
        self.sendSwitchTribulle(True)
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
            self.sendTimeStamp()
         
        print(self.playerName)

    def checkTimeAccount(self):
        """
        Checks the time about playerName creates new account.
        """
        rrf = self.Cursor['account'].find_one({'Ip':self.ipAddress})
        return rrf == None or int(str(time.time()).split(".")[0]) >= int(rrf['Time'])
                    
    def fillLoginInformation(self, playerName, password):
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
            self.banHours = rs['BanHours']
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
            self.aventureInfo = rs["AdventureInfo"]
            self.playerLetters = rs["Letters"]
            self.playerTime = rs["Time"]
            self.playerKarma = rs["Karma"]
            self.playerRoles = rs["Roles"].split(",")
            return True
        else:
            self.server.loop.call_later(2, lambda: self.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(2).writeUTF("").writeUTF("").toByteArray()))
            return False
            
    def sendAccountTime(self):
        date = datetime.datetime.now() + datetime.timedelta(hours=1)
        eventTime = int(str(time.mktime(date.timetuple())).split(".")[0])
        if not self.Cursor['account'].find_one({'Ip':self.ipAddress}):
           self.Cursor['account'].insert_one({'Ip':self.ipAddress,'Time':eventTime})
        else:
           self.Cursor['account'].update_one({'Ip':self.ipAddress},{'$set':{'Time':eventTime}})
            
    def sendCorrectVersion(self, lang='en') -> None:
        self.sendPacket(TFMCodes.game.send.Correct_Version, ByteArray().writeUnsignedInt(len(self.server.players)).writeUTF(lang).writeUTF('').writeInt(self.server.swfInfo["auth_key"]).writeBoolean(False).toByteArray())
        self.sendPacket(TFMCodes.game.send.Banner_Login, ByteArray().writeBoolean(True).writeByte(self.server.eventInfo["adventure_id"]).writeShort(256).toByteArray())
        self.sendPacket(TFMCodes.game.send.Image_Login, ByteArray().writeUTF(self.server.eventInfo["adventure_img"]).toByteArray())
        self.sendPacket(TFMCodes.game.send.Verify_Code, ByteArray().writeInt(self.verifycoder).toByteArray())
                
    def sendLangueMessage(self, community, message, *args, isAll=False):
        packet = ByteArray().writeUTF(community).writeUTF(message).writeByte(len(args))
        for arg in args:
            packet.writeUTF(arg)
        if isAll:
            self.room.sendAll(TFMCodes.game.send.Message_Langue, packet.toByteArray())
        else:
            self.sendPacket(TFMCodes.game.send.Message_Langue, packet.toByteArray())
              
    def sendLoginSourisInfo(self):
        if self.isGuest:
            self.sendPacket(Identifiers.send.Login_Souris, ByteArray().writeByte(1).writeByte(10).toByteArray())
            self.sendPacket(Identifiers.send.Login_Souris, ByteArray().writeByte(2).writeByte(5).toByteArray())
            self.sendPacket(Identifiers.send.Login_Souris, ByteArray().writeByte(3).writeByte(15).toByteArray())
            self.sendPacket(Identifiers.send.Login_Souris, ByteArray().writeByte(4).writeByte(200).toByteArray())
              
    def sendServerMessage(self, message, tab=False) -> None:
        self.sendPacket(TFMCodes.game.send.Server_Message, ByteArray().writeBoolean(tab).writeUTF(message).writeByte(0).writeUTF("").toByteArray())
        
    def sendPlayerIdentification(self):
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
                
    def sendSwitchTribulle(self, isNew):
        self.sendPacket(TFMCodes.game.send.Switch_Tribulle, ByteArray().writeBoolean(isNew).toByteArray())
        
    def sendTimeStamp(self):
        self.sendPacket(TFMCodes.game.send.Time_Stamp, ByteArray().writeInt(self.loginTime).toByteArray())
        
    def sendTribullePacket(self, code, result):
        """
        Sends packet to tribulle
        """
        self.sendPacket(TFMCodes.game.send.Tribulle_Packet, ByteArray().writeShort(code).writeBytes(result).toByteArray())