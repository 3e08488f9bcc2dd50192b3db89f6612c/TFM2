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
    def EncodeIP(ip):
        ip = '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])
        return '#' + ip

    @staticmethod
    def DecodeIP(ip):
        ip = ip[1:]
        return '.'.join([hex(int(x)+256)[3:].upper() for x in ip.split('.')])