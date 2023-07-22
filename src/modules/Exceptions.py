import time, traceback

class ClientException():
    def __init__(self, client):
        self.client = client
        
    def Invoke(self, exType, playerName="", functionName="") -> None:
        if exType == "unknownuser":
            self.client.sendServerMessage("The supplied argument isn't a valid nickname.", True)
        elif exType == "moreargs":
            self.client.sendServerMessage("You need more arguments to use this command.", True)
        elif exType == "requireFC":
            self.client.sendServerMessage("FunCorp commands only work when the room is in FunCorp mode.", True)
        elif exType == "unknownuserorip":
            self.client.sendServerMessage("The supplied argument is neither a valid nickname nor an IP address.", True)
        elif exType == "notloggedin":
            self.client.sendServerMessage("The player "+playerName+" hasn't logged in since the last reboot.", True)
        elif exType == "notallowedlua":
            # Cooming Soon
            pass
        elif exType == "useralreadybanned":
            self.client.sendServerMessage("Player ["+playerName+"] is already banned, please wait.", True)
        elif exType == "usernotbanned":
            self.client.sendServerMessage("The player "+playerName+" is not banned.", True)
        elif exType == "useralreadymuted":
            self.client.sendServerMessage("Player ["+playerName+"] is already muted, please wait.", True)
        elif exType == "usernotmuted":
            self.client.sendServerMessage("The player "+playerName+" is not muted.", True)
        elif exType == "noonlinestaff":
            self.client.sendServerMessage("Don't have any online "+playerName+" at moment.", True)

class ServeurException():
    def __init__(self):
        self.exception = ""
        
    def setException(self, exp):
        self.exception = exp
        
    def getTypeError(self, Type) -> str:
        if Type == "commanderreur":
            return "Command Erreur"
        elif Type == "tribulleerreur":
            return "Tribulle Erreur"
        elif Type == "packeterreur":
            return "Packet Erreur"
        return "Server Erreur"
        
    def SaveException(self, client, fileName, Type) -> None:
        c = open(f"./include/logs/Errors/{fileName}.log", "a")
        c.write("=" * 60)
        c.write(f"\n- Time: {time.strftime('%d/%m/%Y - %H:%M:%S')}\n- IP: {client.ipAddress}\n- {self.getTypeError(Type)} {self.exception}\n")
        traceback.print_exc(file=c)
        c.write("\n")
        c.close()