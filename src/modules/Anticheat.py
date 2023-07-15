import json

class AntiCheat:
    def __init__(self, client, server):
        self.client = client
        self.server = client.server
        self.info = self.server.antiCheatInfo
        
    def getHackType(self, packet_id) -> str:
        """
        Receive the hack type by packet id
        """
    
        if packet_id in [51, 55]: 
            return "Speed / Cheat Engine"
            
        elif packet_id == 31: 
            return "Fly"
            
        return "Unknown"
        
    def readPacket(self, packet) -> None:
        if packet in ["", " "]:
            return
            
        if not packet in self.info["allowed_packets"]:
            if self.server.serverInfo['server_debug']:
                """
                Learning the packet
                """
                #self.info["allowed_packets"].append(packet)
                print(f"New packet found --> {packet}")
                
            else:
                """
                Checks if packet is invoked by a hack
                """
                if self.getHackType(packet) != "Unknown":
                    self.client.transport.close()