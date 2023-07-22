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

    def packet(self, func=None, args=[]) -> None:
        if not func: 
            return lambda x: self.packet(x, args)
        else:
            if func.__name__ in dir(TFMCodes.game.recv):
                exec(f"self.ccc = TFMCodes.game.recv.{func.__name__}")
                self.packets[self.ccc[0] << 8 | self.ccc[1]] = [args,func]

    async def parsePacket(self, packetID, C, CC, packet) -> None:
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
        @self.packet(args=['readUTF'])
        async def Chat_Message(self, message):
            message = message.replace("&amp;#", "&#").replace("<", "&lt;")
            if self.client.isGuest:
                self.client.sendLangueMessage("", "$Créer_Compte_Parler")
                return
                
            elif message.startswith("!") and self.client.room.luaRuntime != None:
                self.client.room.luaRuntime.invokeEvent("ChatCommand", (self.client.playerName, message[1:]))
                if message[1:] in self.client.room.luaRuntime.HiddenCommands:
                    return
                
            elif self.client.isHidden:
                self.client.sendServerMessage("You can't speak while you are watching somebody.", True)
                return
                
            elif not message == "" and len(message) < 256:
                if self.client.isMuted:
                    muteInfo = self.server.getMuteInfo(self.client.playerName)
                    timeCalc = Utils.getHoursDiff(muteInfo[1])
                    if timeCalc <= 0:
                        self.server.removeMute(self.client.playerName, "ServeurMute")
                        self.client.isMuted = False
                    else:
                        self.client.sendMuteMessage(self.client.playerName, timeCalc, muteInfo[0], True)
                        return
                if time.time() - self.client.msgTime > 3:
                    if message != self.client.lastMessage:
                        self.client.lastMessage = message
                        self.client.room.sendAllChat(self.client.playerName if self.client.playerFakeName == "" else self.client.playerFakeName, message, 2 if self.client.isMumuted else self.server.checkMessage(message))
                    else:
                        self.client.sendLangueMessage("", "$Message_Identique")
                    self.client.msgTime = time.time()
                else:
                    self.client.sendLangueMessage("", "$Doucement")
                
                self.client.logMessage(message)

        @self.packet(args=['readUTF'])
        async def Commands(self, command):
            if time.time() - self.client.CMDTime > 1:
                await self.client.Commands.parseCommand(command)
                self.client.CMDTime = time.time()

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
                self.client.sendFlashPlayerNotice = True
            
            if ckey == self.server.swfInfo["ckey"] and version == int(self.server.swfInfo["version"]):
                self.client.validatingVersion = True
                self.client.sendCorrectVersion(lang)
            else:
                print("[ERREUR] Invalid version or CKey (%s, %s) --> %s" %(version, ckey, self.client.ipAddress))
                self.client.transport.close()
        
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
                            "Avatar": 0,
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
        
        @self.packet(args=['readUTF', 'readByte'])
        async def Delete_Report(self, playerName, closeType):
            if self.client.privLevel >= 7:
                self.client.ModoPwet.deleteReport(playerName, closeType)
        
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
                print(f"[{time.strftime('%H:%M:%S')}] [{self.client.playerName}][TRIBULLE] GameLog Error - Code: {oldCC}-{oldC} error: {error}")
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
            self.client.sendPacket(TFMCodes.game.send.Set_Language, ByteArray().writeUTF(langue.upper()).writeUTF(self.server.serverLanguagesInfo.get(self.client.defaultLanguage)[2]).writeBoolean(False).writeBoolean(True).writeUTF('').toByteArray())

        @self.packet(args=['readByte', 'readUTF'])
        async def Get_Staff_Chat(self, _type, message):
            if self.client.privLevel < 2:
                return
            self.client.sendStaffChatMessage(_type, message)

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

        @self.packet(args=['readUTF', 'readBoolean'])
        async def Modopwet_Ban_Hack(self, playerName, silent):
            if self.client.privLevel >= 7:
                self.server.banPlayer(playerName, 360, self.server.translateMessage("$MessageTriche"), self.client.playerName, silent)

        @self.packet(args=['readUTF', 'readBoolean', 'readBoolean', 'readBoolean'])
        async def Modopwet_Change_Langue(self, langue, modopwetOnlyPlayerReports, sortBy, reOpen):
            if self.client.privLevel >= 7:
                self.client.modoPwetLangue = langue.upper()
                self.client.sendPacket(TFMCodes.game.send.Modopwet_Update_Language)
                if reOpen:
                    self.client.ModoPwet.openModoPwet(reOpen, modopwetOnlyPlayerReports, sortBy)

        @self.packet(args=['readUTF'])
        async def Modopwet_Chat_Log(self, playerName):
            if self.client.privLevel >= 7:
                self.client.ModoPwet.openChatLog(playerName)

        @self.packet(args=['readBoolean', 'readByte'])
        async def Modopwet_Notifications(self, isTrue, cmlen):
            if self.client.privLevel >= 7:
                self.client.isModoPwetNotifications = isTrue
                length = cmlen
                self.client.modopwetCommunityNotifications = []
                while length > 0:
                    self.client.modopwetCommunityNotifications.append(self.packet.readUTF())
                    length -= 1

        @self.packet(args=['readUTF'])
        async def New_Survey(self, description):
            if self.client.privLevel != 9:
                return
            description = '[' + description + ']'
            options = []
            while self.packet.bytesAvailable():
                options.append(self.packet.readUTF())
            if len(options) > 0:
                packet1 = ByteArray()
                packet2 = ByteArray()
                packet1.writeInt(self.client.playerID).writeUTF("").writeBoolean(False).writeUTF(description)
                packet2.writeInt(1).writeUTF("").writeBoolean(False).writeUTF(description)
                for option in options:
                    packet1.writeUTF(option)
                    packet2.writeUTF(option)
              
                for player in self.server.players.copy().values():
                    if player.defaultLanguage == self.client.defaultLanguage:
                        player.sendPacket(TFMCodes.game.send.Survey, packet1.toByteArray())
                    else:
                        player.sendPacket(TFMCodes.game.send.Survey, packet2.toByteArray())
            else:
                self.client.sendServerMessage("Your survey must require one valid option.", True)

        @self.packet
        async def Old_Protocol(self):
            data = self.packet.readUTFBytes(self.packet.readShort())
            if isinstance(data, (bytes, bytearray)):
                data = data.decode()
            await self.parsePacketUTF(data)

        @self.packet(args=['readBoolean'])
        async def Open_Cafe(self, _isopen):
            self.client.isCafeOpen = _isopen

        @self.packet(args=['readInt'])
        async def Open_Cafe_Topic(self, topicID):
            await self.client.Cafe.openCafeTopic(topicID)

        @self.packet(args=['readBoolean'])
        async def Open_Modopwet(self, isOpen):
            if self.client.privLevel >= 7:
                self.client.ModoPwet.openModoPwet(isOpen)
                self.client.ModoPwet.sendAllModopwetLangues()
                self.client.isModoPwet = isOpen
                
        @self.packet(args=['readUTF', 'readByte', 'readUTF'])
        async def Player_Report(self, playerName, _type, comment):
            self.client.ModoPwet.insertReport(playerName, _type, comment)

        @self.packet
        async def Reload_Cafe(self):
            if not self.client.isReloadCafe:
                await self.client.Cafe.loadCafeMode()
                self.client.isReloadCafe = True
                self.server.loop.call_later(1, setattr, self.client, "isReloadCafe", False)

        @self.packet(args=['readInt', 'readInt'])
        async def Report_Cafe_Post(self, PostID, TopicID):
            await self.client.Cafe.ReportCafePost(TopicID, PostID)
            
        @self.packet
        async def Request_Info(self):
            self.client.sendPacket(TFMCodes.game.send.Request_Info, ByteArray().writeUTF("http://localhost/info.php").toByteArray())
            
        @self.packet(args=['readInt', 'readByte'])
        async def Survey_Answer(self, playerID, optionID):
            for player in self.server.players.copy().values():
                if playerID == player.playerID:
                    player.sendPacket(TFMCodes.game.send.Survey_Answer, ByteArray().writeByte(optionID).toByteArray())

        @self.packet(args=['readUTF'])
        async def Survey_Result(self, description):
            if self.client.privLevel != 9:
                return
            options = []
            while self.packet.bytesAvailable():
                options.append(self.packet.readUTF())
            p = ByteArray()
            p.writeInt(0).writeUTF("").writeBoolean(False).writeUTF(description)
            for result in options:
                p.writeUTF(result)
            
            for player in self.server.players.copy().values():
                if player.defaultLanguage == self.client.defaultLanguage and player.playerName != self.client.playerName:
                    player.sendPacket(TFMCodes.game.send.Survey, p.toByteArray())
        
        @self.packet(args=['readShort'])
        async def Tribulle(self, code): 
            if self.client.isGuest:
                return
            self.client.Tribulle.parseTribulleCode(code, self.packet)

        @self.packet(args=['readUTF'])
        async def View_Cafe_Posts(self, playerName):
            await self.client.Cafe.ViewCafePosts(playerName)

        @self.packet(args=['readInt', 'readInt', 'readBoolean'])
        async def Vote_Cafe_Post(self, topicID, postID, mode):
            await self.client.Cafe.voteCafePost(topicID, postID, mode)


    async def sendPacket(self, identifiers, data=b"") -> None:
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
        
    async def parsePacketUTF(self, packet):
        values = packet.split('\x01')
        C, CC, values = ord(values[0][0]), ord(values[0][1]), values[1:]
        print(C, CC)