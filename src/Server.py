import asyncio
import psutil
from colorconsole import win
from src import Client
from src.modules import Config, Exceptions
from src.utils import Utils


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
                
        # Informations
        self.antiCheatInfo = self.config.readFile("./include/settings/anticheat.json")
        self.serverInfo = self.config.readFile("./include/settings/gameinfo.json")
        #self.serverLanguagesInfo = self.config.readFile("./include/settings/languages.json")
        self.serverLanguagesInfo = Utils.buildMap("za", [ "Afrikaans", "za" ], "az", [ "Azərbaycan dili", "az" ], "id", [ "Bahasa Indonesia", "id" ], "my", [ "Bahasa Melayu", "my" ], "vu", [ "Bislama", "vu" ], "ba", [ "Bosanski jezik", "ba" ], "ad", [ "Català", "ad" ], "mw", [ "ChiCheŵa", "mw" ], "dk", [ "Dansk", "dk" ], "de", [ "Deutsch", "de" ], "ee", [ "Eesti keel", "ee" ], "nr", [ "Ekakairũ Naoero", "nr" ], "gb", [ "English", "gb" ], "es", [ "Español", "es" ], "to", [ "Faka Tonga", "to" ], "mg", [ "Fiteny malagasy", "mg" ], "fr", [ "Français", "fr" ], "ws", [ "Gagana fa'a Samoa", "ws" ], "hr", [ "Hrvatski", "hr" ], "it", [ "Italiano", "it" ], "mh", [ "Kajin M̧ajeļ", "mh" ], "gl", [ "Kalaallisut", "gl" ], "bi", [ "KiRundi", "bi" ], "rw", [ "Kinyarwanda", "rw" ], "ke", [ "Kiswahili", "ke" ], "ht", [ "Kreyòl ayisyen", "ht" ], "lv", [ "Latviešu valoda", "lv" ], "lt", [ "Lietuvių kalba", "lt" ], "lu", [ "Lëtzebuergesch", "lu" ], "hu", [ "Magyar", "hu" ], "mt", [ "Malti", "mt" ], "nl", [ "Nederlands", "nl" ], "no", [ "Norsk", "no" ], "uz", [ "O'zbek", "uz" ], "pl", [ "Polski", "pl" ], "pt", [ "Português", "pt" ], "br", [ "Português brasileiro", "br" ], "ro", [ "Română", "ro" ], "bo", [ "Runa Simi", "bo" ], "st", [ "SeSotho", "st" ], "bw", [ "SeTswana", "bw" ], "al", [ "Shqip", "al" ], "sz", [ "SiSwati", "sz" ], "sk", [ "Slovenčina", "sk" ], "si", [ "Slovenščina", "si" ], "so", [ "Soomaaliga", "so" ], "fi", [ "Suomen kieli", "fi" ], "se", [ "Svenska", "se" ], "tl", [ "Tagalog", "tl" ], "vi", [ "Tiếng Việt", "vi" ], "tr", [ "Türkçe", "tr" ], "tm", [ "Türkmen", "tm" ], "fj", [ "Vosa Vakaviti", "fj" ], "sn", [ "Wollof", "sn" ], "ng", [ "Yorùbá", "ng" ], "is", [ "Íslenska", "is" ], "cz", [ "Česky", "cz" ], "gr", [ "Ελληνικά", "gr" ], "by", [ "Беларуская", "by" ], "kg", [ "Кыргыз тили", "kg" ], "md", [ "Лимба молдовеняскэ", "md" ], "mn", [ "Монгол", "mn" ], "ru", [ "Русский язык", "ru" ], "rs", [ "Српски језик", "rs" ], "tj", [ "Тоҷикӣ", "tj" ], "ua", [ "Українська мова", "ua" ], "bg", [ "български език", "bg" ], "kz", [ "Қазақ тілі", "kz" ], "am", [ "Հայերեն", "am" ], "il", [ "עברית", "il" ], "pk", [ "اردو", "pk" ], "eg", [ "العربية", "eg" ], "ir", [ "فارسی", "ir" ], "mv", [ "ދިވެހި", "mv" ], "np", [ "नेपाली", "np" ], "in", [ "हिन्दी", "in" ], "bd", [ "বাংলা", "bd" ], "lk", [ "தமிழ்", "lk" ], "th", [ "ไทย", "th" ], "la", [ "ພາສາລາວ", "la" ], "bt", [ "རྫོང་ཁ", "bt" ], "mm", [ "ဗမာစာ", "mm" ], "ge", [ "ქართული", "ge" ], "er", [ "ትግርኛ", "er" ], "et", [ "አማርኛ", "et" ], "kh", [ "ភាសាខ្មែរ", "kh" ], "cn", [ "中国语文", "cn" ], "jp", [ "日本語", "jp" ], "kr", [ "한국어", "kr" ])
        
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

    def startServer(self) -> None:##########
        """
        Obviously
        """
    
        for port in self.swfInfo["ports"]:
            server = self.loop.run_until_complete(self.loop.create_server(lambda: Client.Client(self), "127.0.0.1", port))
        
        self.sendConnectionInformation()
        self.loop.run_forever()