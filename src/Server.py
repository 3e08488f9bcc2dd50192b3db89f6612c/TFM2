import asyncio
import psutil
from api.Api import Api
from colorconsole import win
from src import Client
from src.modules import Config, Exceptions


class Server(asyncio.Transport):
    def __init__(self):
        # Integer
    
        # Float/Double
    
        # String
    
        # Dictionary
        self.rooms = {}
        self.players = {}
        self.connectedCounts = {}
        
        # List

        # Loops
        self.loop = asyncio.get_event_loop()
        
        # Other
        self.config = Config.ConfigParser()
        self.exceptionManager = Exceptions.ServeurException()
        self.api = None
                
        # Informations
        self.antiCheatInfo = self.config.readFile("./include/settings/anticheat.json")
        self.captchaList = self.config.readFile("./include/settings/captchas.json", False)
        self.eventInfo = self.config.readFile("./include/settings/event.json")
        self.serverInfo = self.config.readFile("./include/settings/gameinfo.json")
        self.serverLanguagesInfo = self.config.readFile("./include/settings/languages.json")
        self.swfInfo = self.config.readFile("./include/settings/swf_properties.json")

    def sendConnectionInformation(self) -> None:
        """
        Send additional information in the console when the server was started.
        """
        T = win.Terminal()
        T.set_title("Transformice is online!")
    
        T.cprint(15, 0, "[#] Server Debug: ")
        T.cprint(1,  0,  f"{self.serverInfo['server_debug']}\n")
        
        T.cprint(15, 0, "[#] Initialized ports: ")
        T.cprint(10, 0, f"{self.swfInfo['ports']}\n")
        
        T.cprint(15, 0, "[#] Server Name: ")
        T.cprint(12, 0, f"{self.serverInfo['game_name']}\n")
        if self.serverInfo["server_debug"]:
            T.cprint(15, 0, "[#] Server Version: ")
            T.cprint(14, 0, f"1.{self.swfInfo['version']}\n")
            
            T.cprint(15, 0, "[#] Server Connection Key: ")
            T.cprint(13, 0, f"{self.swfInfo['ckey']}\n")
            
            if len(self.swfInfo["packetKeys"]) > 0:
                T.cprint(15, 0, "[#] Server Packet_Keys: ")
                T.cprint(9,  0,  f"{self.swfInfo['packetKeys']}\n")
        
        T.cprint(15, 0, "[#] Minimum Players (Farm): ")
        T.cprint(2,  0,  f"{self.serverInfo['minimum_players']}\n")
        
        T.cprint(15, 0, "[#] Server Maximum Players: ")
        T.cprint(3,  0,  f"{self.serverInfo['maximum_players']}\n\n")
        
        T.cprint(15, 0, "[#] CPU Usage: ")
        T.cprint(5,  0,  f"{round(psutil.cpu_percent())}%\n")
        
        T.cprint(15, 0, "[#] Memory Usage: ")
        T.cprint(4,  0,  f"{round(psutil.virtual_memory().percent)}%\n")
        
        T.cprint(15, 0, "")
        return

    def sendStaffMessage(self, message, minLevel, tab=False) -> None:
        """
        Send a private message in #Server channel.
        
        Arguments:
        message - message context
        minLevel - minimum level to see the message
        """
        for client in self.players.copy().values():
            if client.privLevel >= minLevel:
                player.sendServerMessage(message, tab)

    def startServer(self) -> None:##########
        """
        Obviously
        """
        for port in self.swfInfo["ports"]:
            self.loop.run_until_complete(self.loop.create_server(lambda: Client.Client(self), "127.0.0.1", port))
        
        self.sendConnectionInformation()
        self.loop.run_forever()