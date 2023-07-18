import time
import datetime
from src.modules import ByteArray

class Utils:
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
    def getLangueID(langue) -> int:
        return 1
                
    @staticmethod
    def EncodeIP(ip) -> str:
        ip = '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])
        return '#' + ip

    @staticmethod
    def DecodeIP(ip) -> str:
        ip = ip[1:]
        return '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])
        
    @staticmethod
    def getSecondsDiff(endTimeMillis):
        return int(Utils.getTime() - endTimeMillis)
        
    @staticmethod
    def getHoursDiff(endTimeMillis):
        startTime = Utils.getTime()
        startTime = datetime.datetime.fromtimestamp(float(startTime))
        endTime = datetime.datetime.fromtimestamp(float(endTimeMillis))
        result = endTime - startTime
        seconds = (result.microseconds + (result.seconds + result.days * 24 * 3600) * 10 ** 6) / float(10 ** 6)
        hours = int(int(seconds) / 3600) + 1
        return hours
        
    @staticmethod
    def getTime() -> int:
        return int(int(str(time.time())[:10]))
        