

from src.utils.TFMCodes import TFMCodes
from src.modules import ByteArray

class Shop:
    def __init__(self, _client, _server):
        self.client = _client
        self.server = _server
        
    def sendShopInfo(self):            
        self.client.sendPacket(TFMCodes.game.send.Shop_Info, ByteArray().writeInt(self.client.shopCheeses).writeInt(self.client.shopFraises).toByteArray())
    
    def sendShopList(self, sendItems=True):
        pass