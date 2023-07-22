import time
import datetime
from src.modules import ByteArray

class Utils:
    @staticmethod
    def getDate() -> str:
        return str(datetime.datetime.now()).replace("-", "/").split(".")[0].replace(" ", " - ")

    @staticmethod
    def get_new_len(_byte : ByteArray):
        var_2068 = 0
        var_2053 = 0
        var_176 = _byte
        while var_2053 < 10:
            var_56 = var_176.readByte() & 0xFF
            var_2068 = var_2068 | (var_56 & 0x7F) << 7 * var_2053
            var_2053 += 1
            if not ((var_56 & 0x80) == 0x80 and var_2053 < 10): #5
                return var_2068+1, var_2053
                
    @staticmethod
    def getHoursDiff(endTimeMillis) -> int:
        startTime = Utils.getTime()
        startTime = datetime.datetime.fromtimestamp(float(startTime))
        endTime = datetime.datetime.fromtimestamp(float(endTimeMillis))
        result = endTime - startTime
        seconds = (result.microseconds + (result.seconds + result.days * 24 * 3600) * 10 ** 6) / float(10 ** 6)
        hours = int(int(seconds) / 3600) + 1
        return hours
                
    @staticmethod
    def getLangueID(langue) -> int:
        langues = {"en": 1, "fr":2, "ru":3, "br":4, "es":5, "tr":7, "vk":8, "pl":9, "hu":10, "nl":11, "ro":12, "id":13, "de":14, "gb":15, "sa":16, "ph":17, "lt":18, "jp":19, "cn":20, "fi":21, "cz":22, "hr":23, "sk":24, "bg":25, "lv":26, "il":27, "it":28, "ee":29, "az":30, "pt":31}
        if not langue in langues:
            return 1 # INTERNATIONALE
        return langues[langue]
                        
    @staticmethod
    def getSecondsDiff(endTimeMillis) -> int:
        return int(Utils.getTime() - endTimeMillis)
        
    @staticmethod
    def getTime() -> int:
        return int(int(str(time.time())[:10]))
                
    @staticmethod
    def EncodeIP(ip) -> str:
        ip = '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])
        return '#' + ip

    @staticmethod
    def DecodeIP(ip) -> str:
        ip = ip[1:]
        return '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])