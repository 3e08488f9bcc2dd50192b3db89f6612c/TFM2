import random
import re
import time
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils
from src.modules import ByteArray

class Packets:
    def __init__(self, player, server):
        # Dict
        self.packets = {}
        
        # Objects
        self.client = player
        self.server = player.server
        self.Cursor = player.Cursor
        
        self.receivePackets()

    def packet(self, func=None, args=[]):
        if not func: 
            return lambda x: self.packet(x, args)
        else:
            if func.__name__ in dir(TFMCodes.game.recv):
                exec(f"self.ccc = TFMCodes.game.recv.{func.__name__}")
                self.packets[self.ccc[0] << 8 | self.ccc[1]] = [args,func]

    async def parsePacket(self, packetID, C, CC, packet):
        ccc = C << 8 | CC
        args = []
        self.packet = packet
        if ccc in self.packets:
            for i in self.packets[ccc][0]:
                exec(f"self.value = self.packet.{i}()")
                args.append(self.value)
            await self.packets[ccc][1](self, *args)
            if (self.packet.bytesAvailable()) and self.server.serverInfo["server_debug"]:
                print("[%s] Struct Error - C: %s - CC: %s - packet: %s" %(self.client.ipAddress, C, CC, repr(packet.toByteArray())))
        else:
            print("[%s] Packet not implemented - C: %s - CC: %s - packet: %s" %(self.client.ipAddress, C, CC, repr(packet.toByteArray())))
            
    def receivePackets(self):
        @self.packet(args=['readShort', 'readUTF', 'readUTF', 'readUTF', 'readByte', 'readUTF'])
        async def Correct_Version(self, version, lang, ckey, stand_type, _reserved, flashPlayerInfo):
            """
            Information:
                Checks if swf details are correct before connect to the game.
            
            Arguments:
                version - swf version
                lang - client language
                ckey - swf connection key
                stand_type - additional argument for checking if user is using standalone.
                _reserved - reserved
                flashPlayerInfo - User's flash information like hash, os name, os language, etc.
            """
            self.flashPlayerInformation = flashPlayerInfo
            if stand_type == "StandAlone":
                self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> connected with standalone.", 7)
                self.sendFlashPlayerNotice = True
            
            if ckey == self.server.swfInfo["ckey"] and version == int(self.server.swfInfo["version"]):
                self.client.validatingVersion = True
                self.client.sendCorrectVersion(lang)
            else:
                print("[ERREUR] Invalid version or CKey (%s, %s) --> %s" %(version, ckey, self.client.ipAddress))
                self.client.transport.close()

        @self.packet(args=["readUTF", "readUTF", "readUTF"])
        async def Computer_Information(self, osLanguage, osName, flashVersion):
            """
            Information:
                Receive most important computer information like os language, os name and flash version.
                
            Arguments:
                osLanguage - User's operation system language code (iso2) like en, tr, pt, etc.
                osName - User's operation system id like windows, linux and mac.
                flashVersion - User's adobe flash version.
            """
            self.osLanguage = osLanguage
            self.osVersion = osName
            self.flashPlayerVersion = flashVersion
        
        @self.packet(args=['readUTF', 'readUTF', 'readUTF', 'readUTF'])
        async def Create_Account(self, playerName, password, email, captcha):
            """
            Information:
                Invokes when somebody creates an account.
            
            Arguments:
                playerName - client's playername
                password - client's password (hashed)
                email - client's email address
                captcha - client's captcha id
            """
            try:
                if self.client.checkTimeAccount() and not self.server.serverInfo['server_debug']:
                    self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(5).writeUTF("").writeUTF("").toByteArray())
                if not re.match("^(?=^(?:(?!.*_$).)*$)(?=^(?:(?!_{2,}).)*$)[A-Za-z][A-Za-z0-9_]{2,11}$", playerName) or len(playerName) > 11:
                    self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(4).writeUTF("").writeUTF("").toByteArray())
                elif captcha != self.client.currentCaptcha:
                    self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(7).writeUTF("").writeUTF("").toByteArray())
                elif self.server.getEmailAddressCount(email) > 5:
                    self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(10).writeUTF("").writeUTF("").toByteArray())
                else:
                    tag = "".join([str(random.choice(range(9))) for x in range(4)])
                    playerName += "#" + tag
                    self.client.sendAccountTime()
                    if self.server.checkExistingUser(playerName):
                        self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(3).writeUTF("").writeUTF("").toByteArray())
                    else:
                        self.server.Cursor["config"].update_one({"lastPlayerID":self.server.lastPlayerID}, {'$inc': {'lastPlayerID': 1}})
                        self.server.lastPlayerID += 1
                        self.Cursor['users'].insert_one({
                            "Username":playerName,
                            "Password":password,
                            "Email":email,
                            "PlayerID": self.server.lastPlayerID,
                            "PrivLevel": 1,
                            "TitleID": 0,
                            "FirstCount": self.server.serverInfo["initial_firsts"],
                            "CheeseCount": self.server.serverInfo["initial_cheeses"],
                            "BootcampCount": self.server.serverInfo["initial_bootcamp"],
                            "ShamanCheeses": self.server.serverInfo["initial_shamanCheeses"],
                            "ShopCheeses": self.server.serverInfo["initial_shopcheese"],
                            "ShopFraises": self.server.serverInfo["initial_strawberries"],
                            "NormalSaves": self.server.serverInfo["initial_normal_saves"],
                            "NormalSavesNoSkill": self.server.serverInfo["initial_normal_saves_no_skill"],
                            "HardSaves": self.server.serverInfo["initial_hard_saves"],
                            "HardSavesNoSkill": self.server.serverInfo["initial_hard_saves_no_skill"],
                            "DivineSaves": self.server.serverInfo["initial_divine_saves"],
                            "DivineSavesNoSkill": self.server.serverInfo["initial_divine_saves_no_skill"],
                            "ShamanType": 0, # normal
                            "ShopItems": "",
                            "ShopShamanItems": "",
                            "ShopCustomItems": "",
                            "ShopEmojies": "",
                            "ShopClothes": "",
                            "ShopGifts": "",
                            "ShopMessages": "",
                            "Look": "1;0,0,0,0,0,0,0,0,0,0,0",
                            "ShamanLook": "0,0,0,0,0,0,0,0,0,0",
                            "MouseColor": "78583a",
                            "ShamanColor": "95d9d6",
                            "RegDate": Utils.getTime(),
                            "CheeseTitleList": "",
                            "FirstTitleList": "",
                            "ShamanTitleList": "",
                            "ShopTitleList": "",
                            "BootcampTitleList": "",
                            "HardModeTitleList": "",
                            "DivineModeTitleList": "",
                            "EventTitleList": "",
                            "StaffTitleList": "",
                            "BanHours": 0,
                            "ShamanLevel": 0,
                            "ShamanExp": 0,
                            "ShamanExpNext": 0,
                            "Skills": "",
                            "FriendsList": "",
                            "IgnoredsList": "",
                            "Gender": 0,
                            "LastOn": 0,
                            "LastDivorceTimer": 0,
                            "Marriage": "",
                            "TribeCode": 0,
                            "TribeRank": 0,
                            "TribeJoined": 0,
                            "SurvivorStats": "0,0,0,0",
                            "RacingStats": "0,0,0,0",
                            "DefilanteStats": "0,0,0",
                            "Consumables": "",
                            "EquipedConsumables": "",
                            "Pet": 0,
                            "PetEnd": 0,
                            "Fur": 0,
                            "FurEnd": 0,
                            "Badges": "",
                            "ShamanBadges": "",
                            "EquipedShamanBadge" : 0,
                            "Letters": "",
                            "Avatar": "",
                            "Time": 0,
                            "Karma": 0,
                            "AdventureInfo": "",
                            "TotemInfo": "",
                            "Roles":""
                        })
                        await self.client.loginPlayer(playerName, password, "\x03[Tutorial] %s" %(playerName))
                        self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> registered account with name <J>{playerName}</J> and email address <VP>{email}</VP>.", 9)
            
            except Exception as e:
                self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(6).writeUTF("").writeUTF("").toByteArray())
                self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> made error in the system. Check serveur.log for more information.", 9, True)
                self.server.exceptionManager.setException(e)
                self.server.exceptionManager.SaveException(self.client, "serveur", "packeterreur")
        
        @self.packet(args=['readInt', 'readUTF'])
        async def Create_New_Cafe_Post(self, topicID, message):
            await self.client.Cafe.createNewCafePost(topicID, message)

        @self.packet(args=['readUTF', 'readUTF'])
        async def Create_New_Cafe_Topic(self, message, title):
            await self.client.Cafe.createNewCafeTopic(message, title)
        
        @self.packet(args=['readInt', 'readBoolean'])
        async def Check_Cafe_Topic(self, topicID, delete):
            await self.client.Cafe.ModerateTopic(topicID, delete)
        
        @self.packet(args=['readInt', 'readUTF'])
        async def Delete_All_Cafe_Message(self, topicID, playerName):
            if self.client.privLevel >= 7:
                await self.client.Cafe.deleteAllCafePost(topicID, playerName)

        @self.packet(args=['readInt'])
        async def Delete_Cafe_Message(self, postID):
            if self.client.privLevel >= 7:
                await self.client.Cafe.deleteCafePost(postID)
        
        @self.packet
        async def Dummy(self):
            """
            Automatic kicks the player after 120 seconds.
            """
            if self.client.awakeTimer != None: 
                self.client.awakeTimer.cancel()
            self.client.awakeTimer = self.server.loop.call_later(120, self.client.transport.close)
        
        @self.packet(args=['readByte', 'readByte', 'readUnsignedByte', 'readUnsignedByte', 'readUTF'])
        async def Game_Log(self, errorC, errorCC, oldC, oldCC, error):
            if errorC == 1 and errorCC == 1:
                print(f"[{time.strftime('%H:%M:%S')}] [{self.client.playerName}][OLD] GameLog Error - C: {oldC} CC: {oldCC} error: {error}")
            elif errorC == 60:
                print(f"[{time.strftime('%H:%M:%S')}] [{self.client.playerName}][TRIBULLE] GameLog Error - Code: {oldC} error: {error}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] [{self.client.playerName}][PAQUET] GameLog Error - C: {errorC} CC: {errorCC} error: {error}")
        
        @self.packet
        async def Get_Cafe_Warnings(self):
            await self.client.Cafe.sendCafeWarnings()
        
        @self.packet
        async def Get_Captcha(self):
            """
            Information:
                Picks a random captcha from the list in case when somebody is creating a new account.
            
            Arguments:
                None
            """
            self.client.currentCaptcha = random.choice(list(self.server.captchaList))
            self.client.sendPacket(TFMCodes.game.send.Set_Captcha, self.server.captchaList[self.client.currentCaptcha][0])
        
        @self.packet(args=['readUTF'])
        async def Get_Language(self, langue):
            """
            Information:
                Receive the 2-iso language code and set it in the client.
            
            Arguments:
                lang - received language
            """
            self.client.defaultLanguage = langue.lower()
            self.client.defaultLanguageID = Utils.getLangueID(self.client.defaultLanguage)
            if "-" in self.client.defaultLanguage:
                self.client.defaultLanguage = self.client.defaultLanguage.split("-")[1]
            self.client.sendPacket(TFMCodes.game.send.Set_Language, ByteArray().writeUTF(langue).writeUTF(self.server.serverLanguagesInfo.get(self.client.defaultLanguage)[2]).writeBoolean(False).writeBoolean(True).writeUTF('').toByteArray())

        @self.packet
        async def Language_List(self):
            """
            Information:
                Send all languages on the server.
            
            Arguments:
                None
            """
            data = ByteArray().writeUnsignedShort(len(self.server.serverLanguagesInfo)).writeUTF(self.client.defaultLanguage)
            data.writeUTF(self.server.serverLanguagesInfo[self.client.defaultLanguage][1])
            data.writeUTF(self.server.serverLanguagesInfo[self.client.defaultLanguage][0])
                
            for info in self.server.serverLanguagesInfo:
                if info != self.client.defaultLanguage:
                    data.writeUTF(self.server.serverLanguagesInfo[info][0])
                    data.writeUTF(self.server.serverLanguagesInfo[info][1])
                    data.writeUTF(self.server.serverLanguagesInfo[info][0])
            self.client.sendPacket(TFMCodes.game.send.Language_List, data.toByteArray())

        @self.packet(args=['readUTF','readUTF','readUTF','readUTF','readInt'])
        async def Login_Account(self, playerName, password, url, startRoom, authKey):
            """
            Information:
                Invokes when somebody login in the game.
            
            Arguments:
                playerName - client's playername
                password - client's password (hashed)
                url - client's swf url
                authKey - special key to check if client is bot like aiotfm.
            """
            try:
                _local1 = self.server.swfInfo["loginKeys"]
                _local2 = self.server.swfInfo["auth_key"]
                _local3 = self.server.serverInfo["flash_url"]
                
                for i in _local1:
                    _local2 ^= i
                    
                if _local2 != authKey and len(_local1) > 0:
                    self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> tried login using bot like aiotfm.", 8)
                    self.client.transport.close()
                elif not _local3 in url and len(_local3) > 0:
                    self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> tried login with invalid swf url.", 9)
                    self.client.transport.close()
                else:
                    self.client.swfUrl = url
                    if playerName == "" and password != "":
                        self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(2).writeUTF(playerName).writeUTF("").toByteArray())
                    else:
                        await self.client.loginPlayer(playerName, password, startRoom)
            except Exception as e:
                self.client.sendPacket(TFMCodes.game.send.Login_Result, ByteArray().writeByte(6).writeUTF(playerName).writeUTF("").toByteArray())
                self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}</BV> made error in the system. Check serveur.log for more information.", 9, True)
                self.server.exceptionManager.setException(e)
                self.server.exceptionManager.SaveException(self.client, "serveur", "packeterreur")

        @self.packet(args=['readBoolean'])
        async def Open_Cafe(self, _isopen):
            self.client.isCafeOpen = _isopen

        @self.packet(args=['readInt'])
        async def Open_Cafe_Topic(self, topicID):
            await self.client.Cafe.openCafeTopic(topicID)

        @self.packet
        async def Reload_Cafe(self):
            if not self.client.isReloadCafe:
                await self.client.Cafe.loadCafeMode()
                self.client.isReloadCafe = True
                self.server.loop.call_later(2, setattr, self.client, "isReloadCafe", False)

        @self.packet(args=['readInt', 'readInt'])
        async def Report_Cafe_Post(self, PostID, TopicID):
            await self.client.Cafe.ReportCafePost(TopicID, PostID)

        @self.packet(args=['readShort'])
        async def Tribulle(self, code): 
            if self.client.isGuest:
                return
            self.client.tribulle.parseTribulleCode(code, self.packet)

        @self.packet(args=['readUTF'])
        async def View_Cafe_Posts(self, playerName):
            await self.client.Cafe.ViewCafePosts(playerName)

        @self.packet(args=['readInt', 'readInt', 'readBoolean'])
        async def Vote_Cafe_Post(self, topicID, postID, mode):
            await self.client.Cafe.voteCafePost(topicID, postID, mode)


    async def sendPacket(self, identifiers, data=b""):
        if self.client.isClosed:
            return
            
        packet = ByteArray()
        packet2 = ByteArray()
            
        if isinstance(data, list):
            data = ByteArray().writeUTF(chr(1).join(map(str, ["".join(map(chr, identifiers))] + data))).toByteArray()
            identifiers = [1, 1]
            
        elif isinstance(data, int):
            data = chr(data)
            
        elif isinstance(data, str):
            data = data.encode()
            
        self.client.lastPacketID = (self.client.lastPacketID + 1) % 255
        length = len(data) + 2
        calc1 = length >> 7
        while calc1 != 0:
            packet2.writeByte(((length & 127) | 128))
            length = calc1
            calc1 = calc1 >> 7
            
        packet2.writeByte((length & 127))
        packet.writeBytes(packet2.toByteArray()).writeByte(identifiers[0]).writeByte(identifiers[1]).writeBytes(data)
        self.client.transport.write(packet.toByteArray())