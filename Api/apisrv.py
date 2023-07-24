from aiohttp import web
from src import Server

class ServerApi:
    def __init__(self, loop, server):
        self.loop = loop
        self.server = server
        
    async def player_api(self, request):
        playerName = request.query.get("playerName")
        response = {}
        status = 200
        if playerName != None:
            try:
                playerInfo = self.server.players[playerName]
                _dict = {
                    "Name": playerInfo.playerName,
                    "ID": playerInfo.playerID,
                    "PrivilegeID": playerInfo.privLevel,
                    "Room": playerInfo.roomName,
                    "IP": playerInfo.ipAddress
                }
                response.update(_dict)
            except KeyError:
                response["error"] = "The player name is offline or does not exist."
                status = 403
        else:
            response["error"] = "The player name argument is missing."
            status = 400
            
        return web.json_response(response, status=status)
        
class startApi:
    def __init__(self, server):
        self.server = server
                
    async def startServer(self):
        app = web.Application()
        endpoint = ServerApi(self.server.loop, self.server)
        
        app.router.add_get("/player_api", endpoint.player_api)
        
        runner = web.AppRunner(app)
        await runner.setup()
        host = self.server.serverInfo["api"].split(":")
        site = web.TCPSite(runner, host[0], host[1])
        await site.start()