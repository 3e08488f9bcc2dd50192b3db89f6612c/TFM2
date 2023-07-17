import time, traceback

class ServeurException():
    def __init__(self):
        self.exception = ""
        
    def setException(self, exp):
        self.exception = exp
        
    def getTypeError(self, Type):
        if Type == "commanderreur":
            return "Command Erreur"
        elif Type == "tribulleerreur":
            return "Tribulle Erreur"
        elif Type == "packeterreur":
            return "Packet Erreur"
        return "Server Erreur"
        
    def SaveException(self, client, fileName, Type):
        c = open(f"./include/logs/Errors/{fileName}.log", "a")
        c.write("=" * 60)
        c.write(f"\n- Time: {time.strftime('%d/%m/%Y - %H:%M:%S')}\n- IP: {client.ipAddress}\n- {self.getTypeError(Type)} {self.exception}\n")
        traceback.print_exc(file=c)
        c.write("\n")
        c.close()