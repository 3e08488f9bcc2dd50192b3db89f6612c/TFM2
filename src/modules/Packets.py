from src.utils import TFMCodes
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
            if func.__name__ in dir(TFMCodes.TFMCodes.game.recv):
                exec(f"self.ccc = TFMCodes.TFMCodes.game.recv.{func.__name__}")
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
        Packet Info [28, 1]:
        
        Information:
            Checks if swf details are correct before connect to the game.
        
        Arguments:
            version - swf version
            lang - client language
            ckey - swf connection key
            stand - additional argument for checking if client is using standalone.
        """
        @self.packet(args=['readShort', 'readUTF', 'readUTF', 'readUTF']) ###############
        async def Correct_Version(self, version, lang, ckey, stand):
            #if "StandAlone":
                #self.sendServerMessage("[Anti-Cheat] The ip "+Utils.EncodeIP(self.ipAddress)+" is connected with standalone.")
                #self.sendFlashWarning = True
            
            if ckey == self.server.swfInfo["ckey"] and version == int(self.server.swfInfo["version"]):
                # if everything is okay
                self.client.validatingVersion = True
                self.client.sendCorrectVersion(lang)
            else:
                print("[ERREUR] Invalid version or CKey (%s, %s) --> %s" %(version, ckey, self.client.ipAddress))
                self.client.transport.close()
        #  b'\x00\x01-\x00)\xd0\xfa\x00\x00\x00@b4c6ead5d714b2cadd3d7fa492d49122d577caa9e9b199c15484aec570668e55\x00\xe3A=t&SA=t&SV=t&EV=t&MP3=t&AE=t&VE=t&ACC=f&PR=t&SP=f&SB=f&DEB=f&V=WIN 32,0,0,324&M=Adobe Windows&R=1920x1080&COL=color&AR=1.0&OS=Windows 8&ARCH=x86&L=pt&IME=t&PR32=t&PR64=t&CAS=32&PT=StandAlone&AVD=f&LFD=f&WD=f&TLS=t&ML=5.1&DP=72\x00\x00\x00\x00\x00\x00\nm\x00\x00'
        
        """
        Packet Info [176, 1]:
        
        Information:
            Set given language in the game.
        
        Arguments:
            lang - received language
        """
        @self.packet(args=['readUTF'])
        async def Set_Language(self, langue):
            langue = langue.upper()
            self.client.defaultLanguage = langue
            if "-" in self.client.defaultLanguage:
                self.client.defaultLanguage = self.client.defaultLanguage.split("-")[1]
            self.client.sendPacket(TFMCodes.TFMCodes.game.send.Set_Language, ByteArray().writeUTF(langue).writeUTF(self.server.serverLanguagesInfo.get(self.client.defaultLanguage.lower())[1]).writeShort(0).writeBoolean(False).writeBoolean(True).writeUTF('').toByteArray())

        """
        Packet Info [176, 2]:
        
        Information:
            Send given languages in the server.
        
        Arguments:
            None
        """
        @self.packet
        async def Language_List(self):
            data = ByteArray().writeShort(1).writeUTF(self.client.defaultLanguage.lower())
            for info in self.server.serverLanguagesInfo.get(self.client.defaultLanguage.lower()):
                data.writeUTF(info)

            data.writeUTF("za")
            data.writeUTF("Afrikaans")
            data.writeUTF("za")
            """for info in self.server.languages:
                if info[0] != self.client.langue.lower():
                    data.writeUTF(info[0])
                    data.writeUTF(info[1])
                    data.writeUTF(info[2])
            """
            self.client.sendPacket(Identifiers.send.Language_List, data.toByteArray())
        
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

        print(str(packet2.getBytes()) + "\n" + str(packet.getBytes()) + "\n" + str(data))
        packet.writeBytes(packet2.toByteArray()).writeByte(identifiers[0]).writeByte(identifiers[1]).writeBytes(data)
        self.client.transport.write(packet.toByteArray())