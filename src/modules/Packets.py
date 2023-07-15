import random
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
        @self.packet(args=['readShort', 'readUTF', 'readUTF', 'readUTF', 'readByte', 'readUTF'])
        async def Correct_Version(self, version, lang, ckey, stand_type, _reserved, flashPlayerInfo):
            self.flashPlayerInformation = flashPlayerInfo
            if stand_type == "StandAlone":
                self.server.sendStaffMessage(f"The ip address <BV>{Utils.EncodeIP(self.client.ipAddress)}<BV> connected with standalone.", 6)
                self.sendFlashPlayerNotice = True
            
            if ckey == self.server.swfInfo["ckey"] and version == int(self.server.swfInfo["version"]):
                self.client.validatingVersion = True
                self.client.sendCorrectVersion(lang)
            else:
                print("[ERREUR] Invalid version or CKey (%s, %s) --> %s" %(version, ckey, self.client.ipAddress))
                self.client.transport.close()

        """
        Information:
            Receive most important computer information like os language, os name and flash version.
            
        Arguments:
            osLanguage - User's operation system language code (iso2) like en, tr, pt, etc.
            osName - User's operation system id like windows, linux and mac.
            flashVersion - User's adobe flash version.
        """
        @self.packet(args=["readUTF", "readUTF", "readUTF"])
        async def Computer_Information(self, osLanguage, osName, flashVersion):
            self.osLanguage = osLanguage
            self.osVersion = osName
            self.flashPlayerVersion = flashVersion
        
        """
        Information:
            Gets a random captcha from the list in case when somebody is creating a new account.
        
        Arguments:
            None
        """
        @self.packet
        async def Get_Captcha(self):
            self.client.currentCaptcha = random.choice(list(self.server.captchaList))
            self.client.sendPacket(TFMCodes.game.send.Set_Captcha, self.server.captchaList[self.client.currentCaptcha][0])
        
        """
        Information:
            Receive the 2-iso language code and set it in the client.
        
        Arguments:
            lang - received language
        """
        @self.packet(args=['readUTF'])
        async def Get_Language(self, langue):
            self.client.defaultLanguage = langue.lower()
            if "-" in self.client.defaultLanguage:
                self.client.defaultLanguage = self.client.defaultLanguage.split("-")[1]
            self.client.sendPacket(TFMCodes.game.send.Set_Language, ByteArray().writeUTF(langue).writeUTF(self.server.serverLanguagesInfo.get(self.client.defaultLanguage)[2]).writeBoolean(False).writeBoolean(True).writeUTF('').toByteArray())

        """
        Information:
            Send all languages on the server.
        
        Arguments:
            None
        """
        @self.packet
        async def Language_List(self):
            data = ByteArray().writeUnsignedShort(len(self.server.serverLanguagesInfo)).writeUTF(self.client.defaultLanguage)
            data.writeUTF(self.server.serverLanguagesInfo[self.client.defaultLanguage][1])
            data.writeUTF(self.server.serverLanguagesInfo[self.client.defaultLanguage][0])
                
            for info in self.server.serverLanguagesInfo:
                if info != self.client.defaultLanguage:
                    data.writeUTF(self.server.serverLanguagesInfo[info][0])
                    data.writeUTF(self.server.serverLanguagesInfo[info][1])
                    data.writeUTF(self.server.serverLanguagesInfo[info][0])
            self.client.sendPacket(TFMCodes.game.send.Language_List, data.toByteArray())


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