from src.modules import ByteArray
from src.utils.TFMCodes import TFMCodes

class Room:
    def __init__(self, server, roomName, creatorClient):
        # Instances
        self.name = roomName
        self.server = server
        self.creator = creatorClient
        
        # String
        self.langue = ""
        
        # List
        self.anchors = []
        
        # Dictionary
        self.clients = {}
        
        # NoneType
        self.luaRuntime = None
        
        # Boolean
        self.isBootcamp = False
        self.isFunCorp = False
        self.isTribeHouse = False
        
    def getPlayerCount(self):
        return len(list(filter(lambda player: not player.isHidden, self.clients.copy().values())))
        
    def removeClient(self, player):
        if player.playerName in self.clients:
            if self.isFunCorp:
                for player in self.clients.copy().values():
                    player.resetFuncorpEffects()
                    player.sendLangueMessage("", "<FC>$FunCorpDesactive</FC>")
                    self.isFuncorp = False
                    
            del self.clients[player.playerName]
            #player.resetPlay()
            player.isDead = True
            player.playerScore = 0
            player.sendPlayerDisconnect()
            
            
            if len(self.clients) == 0:
                del self.server.rooms[self.name]
            
            if self.luaRuntime != None:
                self.luaRuntime.invokeEvent("PlayerLeft", (player.playerName))
        
    def addClient(self, player, newRoom=False):
        self.clients[player.playerName] = player
        player.room = self
        if not newRoom:
            player.isDead = True
            self.sendAllOthers(player, TFMCodes.game.send.Player_Respawn, ByteArray().writeBytes(player.getPlayerData()).writeBoolean(False).writeBoolean(True).toByteArray())
            #player.startPlay()
        
        if self.luaRuntime != None:
            self.luaRuntime.invokeEvent("NewPlayer", (player.playerName))
            
    def sendAll(self, identifiers, packet=""):
        for player in self.clients.copy().values():
            player.sendPacket(identifiers, packet)
            
    def sendAllChat(self, playerName, message, state):
        p = ByteArray().writeUTF(playerName).writeUTF(message).writeBoolean(True)
        if state == 0:
            for client in self.clients.copy().values():
                client.sendPacket(TFMCodes.game.send.Chat_Message, p.toByteArray())
        else:
            player = self.clients.get(playerName)
            if player != None:
                player.sendPacket(TFMCodes.game.send.Chat_Message, p.toByteArray())
                if state == 1:
                    self.server.sendStaffMessage(f"The player <BV>{player.playerName}</BV> has sent a filtered text: [<J> {message} </J>].", 7)
            
    def sendAllOthers(self, senderClient, identifiers, packet=""):
        for player in self.clients.copy().values():
            if player != senderClient:
                player.sendPacket(identifiers, packet)