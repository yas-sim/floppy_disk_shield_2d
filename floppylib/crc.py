"""
CRC calculation routine

CRC polynomial = CCITT-16  G(X) = 1+X^5+X^12+X^16 == 1 001 000 0010 001 == 0x11021  
FDC calculates CRC from the top of the address marks (0xA1) to CRC values.  
When FDC generates CRC, the CRC field (2 bytes) are set to 0x00,0x00 and the initial CRC value is 0x84Cf.  
However, the top of address marks can't be read precisely when reading the data from the disc. I decided to skip the top x3 0xA1 values and start CRC caluculation from (F8/FB/FC/FE) with CRC initial value of 0xe59a.

If the data are read correctly, the return value will be 0x0000.
    data=[0xfe, 0x01, 0x01, 0x03, 0x01, 0xdd, 0xea]
    crc_value = crc.data(data[:])  # crc_value must be 0
"""

class CCITT_CRC:
    def __init__(self):
        self.polynomial = 0x1102100    # 0001 0001 0000 0010 0001 [0000 0000]
        self.reset()

    def reset(self):
        self.crcval = 0xe59a00         # In case the 1st x3 A1s are omitted ( F8/FB/FC/FE )

    def reset2(self):
        self.crcval = 0x84cf00        # In case AM = A1 A1 A1 + F8/FB/FC/FE

    def get(self):
        return (self.crcval>>8) & 0xffff

    def data(self, buf):
        for byte in buf:
            self.crcval  |= byte
            for i in range(8):
                self.crcval <<= 1
                if self.crcval & 0x1000000 != 0:
                    self.crcval  ^= self.polynomial
