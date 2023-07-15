import asyncio
import random
from src.modules import AntiCheat, ByteArray, Packets
from src.utils.Utils import Utils
from src.utils.TFMCodes import TFMCodes

class Client:
    def __init__(self, _server):
        # Istances
        self.server = _server
        self.clientPacket = ByteArray()

        # Boolean
        self.isClosed = False
        self.sendFlashPlayerNotice = False
        self.validatingVersion = False

        # Integer
        self.lastPacketID = 0
        self.verifycoder = random.choice(range(0, 10000))

        # Float/Double

        # String
        self.currentCaptcha = ""
        self.defaultLanguage = ""
        self.emailAddress = ""
        self.flashPlayerVersion = ""
        self.flashPlayerInformation = ""
        self.ipAddress = ""
        self.playerName = ""
        self.osLanguage = ""
        self.osVersion = ""

        # Dictionary

        # List

        # Loops
        self.loop = asyncio.get_event_loop()
        
        # Other
        self.transport = None
        
    def connection_made(self, transport: asyncio.Transport) -> None: ##########
        """
        Make connection between client and server.
        """
        self.transport = transport
        self.ipAddress = transport.get_extra_info("peername")[0]
        
        self.AntiCheat = AntiCheat(self, self.server)
        self.Packets = Packets(self, self.server)
        
        
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
            self.server.sendStaffMessage(f"The player <BV>{self.playerName}<BV> made error in the system. Check erreur.log for more information.", 10, True)
            self.server.exceptionManager.setException(e)
            self.server.exceptionManager.SaveException(self, "serveur", "servererreur")
            
    def sendCorrectVersion(self, lang='en') -> None:
        self.sendPacket(TFMCodes.game.send.Correct_Version, ByteArray().writeInt(len(self.server.players)).writeUTF(lang).writeUTF('').writeInt(self.server.swfInfo["auth_key"]).writeBoolean(False).toByteArray())
        self.sendPacket(TFMCodes.game.send.Banner_Login, ByteArray().writeBoolean(True).writeByte(self.server.eventInfo["adventure_id"]).writeShort(256).toByteArray())
        self.sendPacket(TFMCodes.game.send.Image_Login, ByteArray().writeUTF(self.server.eventInfo["adventure_img"]).toByteArray())
        self.sendPacket(TFMCodes.game.send.Verify_Code, ByteArray().writeInt(self.verifycoder).toByteArray())
        
    def sendServerMessage(self, message, tab=False) -> None:
        self.sendPacket(TFMCodes.game.send.Server_Message, ByteArray().writeBoolean(tab).writeUTF(message).writeByte(0).writeUTF("").toByteArray())
        
    def sendPacket(self, identifiers, data=b"") -> None:
        self.loop.create_task(self.Packets.sendPacket(identifiers, data))

