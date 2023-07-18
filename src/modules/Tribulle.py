from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils
from src.modules import ByteArray

class Tribulle:
    def __init__(self, _client, _server):
        self.client = _client
        self.server = _server

    def parseTribulleCode(self, code, packet):
        print(code)
        if code == TFMCodes.tribulle.recv.ST_ListeAmis: # send the friend list
            self.sendFriendsList(packet)
        else:
            print(f"[ERREUR] Not implemented tribulle code -> Code: {code} packet: {repr(packet.toByteArray())}")
            
    def sendFriendsList(self, packet):
        pass