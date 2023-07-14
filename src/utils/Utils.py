from src.modules import ByteArray

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
        
def buildMap(*elems):
    m = {}
    i = 0
    while i < len(elems):
        m[elems[i]] = elems[i + 1]
        i += 2
    return m