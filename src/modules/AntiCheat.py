import json

class AntiCheat:
    def __init__(self, client, server):
        # Instances
        self.client = client
        self.server = client.server
        
        # Other
        self.info = self.server.antiCheatInfo
        
    def __get__(self):
        return self.info

    def __str__(self):
        return str(self.info)
                
    def checkPacket(self, packet) -> bool:
        r1 = self.getHackType(packet)
        if r1 != "Unknown":
            self.server.sendBanPunishment(self.client.playerName, self.info["ban_hours"], "Hack", "Anti-Cheat", True)
            return True
        return False
        
    def getHackType(self, packet_id) -> str:
        """
        Receive the hack type by packet id
        """
        if packet_id in [51, 55]: 
            return "Speed (Cheat Engine)"
            
        elif packet_id == 31: 
            return "Fly"
            
        return "Unknown"
        
    def readPacket(self, packet) -> None:        
        if packet in ["", " "]:
            return
            
        if packet in self.info["suspicious_packets"]:
            self.checkPacket(packet)
            
        elif packet in self.info["staff_packets"]:
            if self.client.privLevel < 3: # anti exploit stuff
                self.client.transport.close()
            
        elif packet not in self.info["allowed_packets"] and packet not in self.info["staff_packets"]:
            if self.server.serverInfo['server_debug']:
                # Learning the packet.
                #self.savePacket(packet)
                print(f"New packet found --> {packet}")
                
    def savePacket(self, packet) -> None:
        self.info["allowed_packets"].append(packet)