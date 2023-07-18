import datetime
import pymongo
from src.modules import ByteArray
from src.utils.TFMCodes import TFMCodes
from src.utils.Utils import Utils

class Cafe:
    def __init__(self, _client, _server):
        self.client = _client
        self.server = _server
        
    def checkPerm(self):
        return self.client.isGuest or (self.client.cheeseCount < 1000 and self.client.playerTime < 108000)
   
    async def createNewCafePost(self, topicID, message):
        if self.checkPerm() == True:
            return
        commentsCount = 0
        if not self.server.checkMessage(message):
            self.server.Cursor['cafe_posts'].insert_one({
                "PostID": self.server.lastCafePostID,
                "TopicID": topicID,
                "Name": self.client.playerName,
                "Post": message,
                "Date": Utils.getTime(),
                "Points": 0,
                "Votes": "",
                "ModeratedBY": "",
                "Status": 0
            })
            self.server.Cursor["config"].update_one({"lastCafePostID":self.server.lastCafePostID}, {'$inc': {'lastCafePostID': 1}})
            self.server.lastCafePostID += 1
            self.server.Cursor['cafe_topics'].update_one({'TopicID':topicID}, {'$set':{'Date':Utils.getTime(), "LastPostName":self.client.playerName}, '$inc': {'Posts': 1}})
            commentsCount = self.server.Cursor["cafe_posts"].count_documents({"TopicID": topicID})
            await self.openCafeTopic(topicID)
            for player in self.server.players.copy().values():
                if player.isCafeOpen:
                    player.sendPacket(TFMCodes.game.send.Cafe_New_Post, ByteArray().writeInt(topicID).writeUTF(self.client.playerName).writeInt(commentsCount).toByteArray())
        else:
            self.client.sendServerMessage("You are not allowed to use blacklist words in your cafe post.", True)
        
    async def createNewCafeTopic(self, title, message):
        if self.checkPerm() == True:
            return
        if not self.server.checkMessage(title):
            self.server.Cursor['cafe_topics'].insert_one({
                "TopicID": self.server.lastCafeTopicID,
                "Title": title,
                "Author": self.client.playerName,
                "LastPostName": "",
                "Posts": 0,
                "Date": Utils.getTime(),
                "Langue": self.client.defaultLanguage
            })
            await self.createNewCafePost(self.server.lastCafeTopicID, message)
            self.server.Cursor["config"].update_one({"lastCafeTopicID":self.server.lastCafeTopicID}, {'$inc': {'lastCafeTopicID': 1}})
            self.server.lastCafeTopicID += 1
        else:
            self.client.sendServerMessage("You are not allowed to use blacklist words in your cafe topic.", True)
        await self.loadCafeMode()
        
    async def deleteAllCafePost(self, topicID, playerName):
        topic_posts = self.server.Cursor["cafe_posts"].count_documents({"TopicID": topicID})
        player_posts = self.server.Cursor["cafe_posts"].count_documents({"TopicID": topicID, "Name": playerName})
        self.server.Cursor["cafe_posts"].delete_many({"TopicID": topicID, "Name": playerName})
        self.server.Cursor["cafe_topics"].update_one({"TopicID": topicID}, {"$inc": {"Posts": -player_posts}})
        self.server.Cursor["config"].update_one({"lastCafePostID":self.server.lastCafePostID}, {'$inc': {'lastCafePostID': -player_posts}})
        self.server.lastCafePostID -= player_posts
        if topic_posts - player_posts == 0:
            self.server.Cursor["config"].update_one({"lastCafeTopicID":self.server.lastCafeTopicID}, {'$inc': {'lastCafeTopicID': -1}})
            self.server.lastCafeTopicID -= 1
            self.server.Cursor["cafe_topics"].delete_one({"TopicID": topicID})
            await self.loadCafeMode()
        else:
            await self.openCafeTopic(topicID)
        
    async def deleteCafePost(self, postID):
        res = self.server.Cursor["cafe_posts"].find_one({"PostID": postID})
        if res:
            topicID = res["TopicID"]
            self.server.Cursor["cafe_posts"].delete_one({"PostID": postID})
            self.server.Cursor["cafe_topics"].update_one({"TopicID": topicID}, {"$inc": {"Posts": -1}})
            self.server.Cursor["config"].update_one({"lastCafePostID":self.server.lastCafePostID}, {'$inc': {'lastCafePostID': -1}})
            self.server.lastCafePostID -= 1
            self.client.sendPacket(TFMCodes.game.send.Delete_Cafe_Message, ByteArray().writeInt(topicID).writeInt(postID).toByteArray())
            res = self.server.Cursor["cafe_topics"].find_one({"TopicID": topicID})
            if res and res["Posts"] == 0:
                self.server.Cursor["cafe_topics"].delete_one({"TopicID": topicID})
                self.server.Cursor["config"].update_one({"lastCafeTopicID":self.server.lastCafeTopicID}, {'$inc': {'lastCafeTopicID': -1}})
                self.server.lastCafeTopicID -= 1
                await self.loadCafeMode()
            else:
                await self.openCafeTopic(topicID)
        else:
            print(f"[ERREUR] Unable to find postid {postID} on the cafe.")
        
    async def loadCafeMode(self):
        if self.checkPerm() == True:
            self.client.sendLangueMessage("", "<ROSE>$PasAutoriseParlerSurServeur")
            return
        self.client.sendPacket(TFMCodes.game.send.Open_Cafe, ByteArray().writeBoolean(True).toByteArray())
        packet = ByteArray().writeBoolean(True).writeBoolean(not self.client.privLevel < 7)
        rss = self.server.Cursor['cafe_topics'].find().sort('Date', pymongo.DESCENDING).limit(20)
        for rs in rss:
            if rs["Langue"] == self.client.defaultLanguage:
                packet.writeInt(rs["TopicID"]).writeUTF(rs["Title"]).writeInt(self.server.getPlayerID(rs["Author"])).writeInt(rs["Posts"]).writeUTF(rs["LastPostName"]).writeInt(Utils.getSecondsDiff(rs["Date"]))
        self.client.sendPacket(TFMCodes.game.send.Cafe_Topics_List, packet.toByteArray())
        await self.client.Cafe.sendCafeWarnings()
        
    async def ModerateTopic(self, topicID, delete):
        self.server.Cursor["cafe_posts"].update_one({"PostID": self.server.moderatedCafeTopics[topicID][0]}, {'$set':{'Status': (2 if delete else 1), "ModeratedBY":self.client.playerName}})
        self.server.moderatedCafeTopics[topicID].pop(0)
        if len(self.server.moderatedCafeTopics[topicID]) == 0:
            del self.server.moderatedCafeTopics[topicID]
        await self.openCafeTopic(topicID)
        
    async def openCafeTopic(self, topicID):
        if self.checkPerm() == True:
            return
        packet = ByteArray().writeBoolean(True).writeInt(topicID).writeBoolean(1 if topicID in self.server.moderatedCafeTopics and self.client.privLevel >= 7 else 0).writeBoolean(True)
        results = self.server.Cursor["cafe_posts"].find({"TopicID": topicID}).sort("PostID", pymongo.ASCENDING)
        for rs in results:
            packet.writeInt(rs["PostID"]).writeInt(self.server.getPlayerID(rs["Name"])).writeInt(Utils.getSecondsDiff(rs["Date"])).writeUTF(rs["Name"]).writeUTF(rs["Post"]).writeBoolean(str(self.client.playerCode) not in rs["Votes"].split(",")).writeShort(rs["Points"]).writeUTF("" if self.client.privLevel < 7 else rs["ModeratedBY"]).writeByte(rs["Status"] if self.client.playerName == rs["Name"] and rs["Status"] in [0, 2] or self.client.privLevel > 7 else 0)
        self.client.sendPacket(TFMCodes.game.send.Open_Cafe_Topic, packet.toByteArray())
                
    async def ReportCafePost(self, postID, topicID):
        results = self.server.Cursor["cafe_posts"].find_one({"TopicID": topicID, "PostID": postID})
        results2 = self.server.Cursor["cafe_topics"].find_one({"TopicID": topicID})
        if not results or not results2:
            return
        post = results['Post'].replace("\n", "")
        self.server.sendStaffMessage(f"The post {post} made by <BV>{results['Name']}</BV> in topic {results2['Title']} was reported by {self.client.playerName}.", 7, True)
        if not topicID in self.server.moderatedCafeTopics:
            self.server.moderatedCafeTopics[topicID] = [postID]
        else:
            self.server.moderatedCafeTopics[topicID].append(postID)
                
    async def sendCafeWarnings(self):
        count = self.server.Cursor["cafe_posts"].count_documents({"Status": 2, "Name": self.client.playerName})
        self.client.sendPacket(TFMCodes.game.send.Send_Cafe_Warnings, ByteArray().writeUnsignedShort(count).toByteArray())
                
    async def ViewCafePosts(self, playerName):
        rss = self.server.Cursor["cafe_posts"].find({"Name": playerName})
        content = ""
        for rs in rss:
            msg = rs["Post"].replace("\n", " ")
            date = rs["Date"]
            content += str(datetime.datetime.fromtimestamp(date)) + " | " + msg + "\n"
        self.client.sendPacket(TFMCodes.game.send.Minibox_1, ByteArray().writeShort(300).writeUTF("Messages by "+playerName).writeUTF(content).toByteArray())
                
    async def voteCafePost(self, topicID, postID, mode):
        if self.checkPerm() == True:
            return
        results = self.server.Cursor["cafe_posts"].find_one({"TopicID": topicID, "PostID": postID})
        if not results:
            return
        score = results["Points"]
        votes = results["Votes"]
        
        if not str(self.client.playerID) in votes:
            votes += str(self.client.playerID) if votes == "" else "," + str(self.client.playerID)
            if mode:
                score += 1
            else:
                score -= 1
            self.server.Cursor["cafe_posts"].update_one({"TopicID":topicID, "PostID": postID}, {"$set": {"Points": score, "Votes": votes}})
            await self.openCafeTopic(topicID)