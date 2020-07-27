# 00*14*02*A1*A1 FE 01 01 03 01 DD EA
class CCITT_CRC:
    def __init__(self):
        self.polynomial = 0x1102100    # 0001 0001 0000 0010 0001 0000 0000
        self.reset()

    # 最初のA1x3を入れるかで初期値を変えている
    # 読みだしたときはA1x3がきれいに読めることはないので省略した方を使う
    # CRC計算範囲はアドレスマーク(F8/FB/FC/FE)からCRCまで含める。結果が0になればOK
    def reset(self):
        #self.crcval = 0x84cf00        # In case AM = A1 A1 A1 + F8/FB/FC/FE
        self.crcval = 0xe59a00         # In case the 1st x3 A1s are omitted ( F8/FB/FC/FE )
    
    def get(self):
        return (self.crcval>>8) & 0xffff

    def data(self, buf):
        for byte in buf:
            #print(format(byte, '02X'))
            self.crcval  |= byte
            for i in range(8):
                self.crcval <<= 1
                if self.crcval & 0x1000000 != 0:
                    self.crcval  ^= self.polynomial

crc = CCITT_CRC()

# A1 A1 A1 FE 01 01 03 01 DD EA
crc.reset()
crc.data([0xfe, 0x01, 0x01, 0x03, 0x01, 0xdd, 0xea])
print(format(crc.get(), '04X'))

# A1 A1 A1 FE 01 01 10 01 8B CA
crc.reset()
crc.data([0xfe, 0x01, 0x01, 0x10, 0x01, 0x8b, 0xca])
print(format(crc.get(), '04X'))

# A1 A1 A1 FB + FF*256 + FB E5
crc.reset()
a  = [ 0xfb ]
a += [ 0xff ] * 256
a += [ 0xfb, 0xe5 ]
crc.data(a)
print(format(crc.get(), '04X'))
