# folppy shield library

from enum import Enum

import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


class bitstream:
    def __init__(self, file=None):
        self.disk = {}
        if file is not None:
            self.open(file)

    def open(self, file):
        self.disk = {}
        with open(file, 'r') as f:
            linebuf = ''
            for line in f:
                line = line.rstrip('\n')
                if len(line)==0:
                    continue
                if '**TRACK_READ' in line:
                    trk, side = [ int(v) for v in line.split(' ')[1:] ]
                    linebuf = ''
                elif '**TRACK_END' in line:
                    if len(linebuf)==0:
                        continue
                    interval_buf = [ ord(c)-ord(' ') for c in linebuf ]  # decode data of a track
                    key = '{}-{}'.format(trk, side)
                    self.disk[key] = interval_buf
                elif line[0]=='~':         # the data lines must start with '~'
                    linebuf += line[1:]

    def display_histogram(self, track, side):
        histo = [ 0 ] * (ord('z')-ord(' ')+1)
        key = '{}-{}'.format(track, side)
        data = self.disk[key]
        for l in data:
            if l<len(histo):
                histo[l]+=1
        
        fig = plt.figure()
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)
        ax1.grid(True)
        ax1.hist(data, bins=len(histo), range=(0,40), histtype='stepfilled', orientation='vertical', log=False)
        ax2.grid(True)
        ax2.hist(data, bins=len(histo), range=(0,40), histtype='stepfilled', orientation='vertical', log=True)
        plt.show()


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


# G(X) = 1+X~5+X~12+X~16
# 00*14*02*A1*A1 FE 01 01 03 01 DD EA
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


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


def dump_list_hex(lst):
    print('[ ', end='')
    for i in lst:
        print('0x{}, '.format(format(i, '02X')) , end='')
    print(']')

def dumpMFM(mfm_buf, mc_buf):
    count = 0
    for mfm, mc in zip(mfm_buf, mc_buf):
        if mc==True:
            print('*', end='')
        else:
            print(' ', end='')
        print(format(mfm, '02X'), end='')
        count+=1
        if count==32:
            count=0
            print('')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
    
            
class data_separator:
    def __init__(self, interval_buf, clk_spd =4e6, high_gain=0.3, low_gain=0.01):
        self.interval_buf = interval_buf
        self.pos = 0
        self.reset(clk_spd=clk_spd, high_gain=high_gain, low_gain=low_gain)
        missing_clock_c2 = (0x5224 & 0x7fff)  #  [0,1,0,1, 0,0,1,0, 0,0,1,0, 0,1,0,0]
        missing_clock_a1 = (0x4489 & 0x7fff)  #  [0,1,0,0, 0,1,0,0, 1,0,0,0, 1,0,0,1]
        pattern_ff       = (0x5555 & 0x7fff)
        pattern_00       = (0xaaaa & 0x7fff)
        self.missing_clock = [ missing_clock_c2, missing_clock_a1 ]
        self.sync_pattern  = [ pattern_ff, pattern_00 ]

    def set_gain(self, high_gain, low_gain):
        self.high_gain = high_gain
        self.low_gain = low_gain

    def switch_gain(self, gain_mode):
        if gain_mode == 1:
            self.gain = self.high_gain
        else:
            self.gain = self.low_gain

    def set_mode(self, mode):
        """
        Set data separator mode. Missing clock and 0x00 bit patterns will be cared when address-mark seeking mode.   
        Args:
          mode: 0=AM seeking, 1=Data reading (ignore missing clock and 0x00 patterns)
        """
        self.mode = mode

    def reset(self, clk_spd=4e6, high_gain=0.3, low_gain=0.01):
        self.clock_speed   = clk_spd
        self.bit_cell      = 500e3    # 1/2MHz
        self.cell_size     = self.clock_speed / self.bit_cell
        self.cell_size_ref = self.cell_size
        self.cell_size_max = self.cell_size * 1.2
        self.cell_size_min = self.cell_size * 0.8
        self.bit_stream    = []
        self.mc_check      = 0      # C+D data for missing clock checking
        self.set_gain(high_gain=high_gain, low_gain=low_gain)
        self.switch_gain(0)         # low speed gain
        self.set_mode(0)            # AM seeking
        self.cd_stream     = 0      # C+D bitstream
    
    def get_interval(self):
        if self.pos >= len(self.interval_buf):
            return -1
        dt = self.interval_buf[self.pos]
        self.pos+=1
        return dt

    def get_bit(self):
        while True:
            if len(self.bit_stream) > 0:
                bit = self.bit_stream.pop(0)
                return bit
            interval = self.get_interval()   # interval = pulse interval in 'cell_size' unit (cell_size=2us in case of 2D/2DD)
            if interval == -1:
                return -1
            int_interval = int(interval / self.cell_size + 0.5)
            error = interval - int_interval * self.cell_size
            self.cell_size += error * self.gain               # Correct the cell_size
            # cell size range limitter
            self.cell_size = max(self.cell_size, self.cell_size_min)
            self.cell_size = min(self.cell_size, self.cell_size_max)
            if   int_interval == 2:
                self.bit_stream += [0, 1]
            elif int_interval == 3:
                self.bit_stream += [0, 0, 1]
            elif int_interval == 4:
                self.bit_stream += [0, 0, 0, 1]

    def get_byte(self):
        data           = 0
        read_bit_count = 0   # read bit count
        while True:
            bit = self.get_bit()
            if bit == -1:
                return -1, False
            if read_bit_count % 2 == 1:
                data = (data<<1) | bit   # stores only data bits (skip clock bits)
            read_bit_count += 1
            self.cd_stream = ((self.cd_stream<<1) | bit) & 0x7fff
            if self.mode == 0 and (self.cd_stream in self.missing_clock):
                return data, True        # missing clock detected
            if self.mode == 0 and (self.cd_stream in self.sync_pattern):
                self.switch_gain(1)    # Fast tracking mode to get syncronized with SYNC pattern
            else:
                self.switch_gain(0)
            if read_bit_count >= 16:
                return data, False       # 8 bit data read completed

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------



def decodeFormat(interval_buf, clk_spd=4e6, high_gain=0.3, low_gain=0.01, log_level=0):
    """
    Decode bistream track data  
    Args:
      interval_buf : Bitstream buffer for a track (pulse interval buffer)
      clk_spd : clock speed of the floppy capture shield (default = 4MHz = 4e6)
      high_gain : data separator tracking gain for high speed (=address mark seeking) region
      low_gain : data separator tracking gain for low speed (=data reading) region
      log_level : 0=No message, 1=minimum message, 2=detailed message
    """
    class State(Enum):
        IDLE       = 0
        CHECK_MARK = 1
        INDEX      = 2
        IDAM       = 3
        DAM        = 4
        DDAM       = 5
        DATA_READ  = 6

    mfm_buf = []
    mc_buf  = []

    # Number of sectors successfully ( or error) read
    num_sect_read = 0
    num_sect_err  = 0

    state = State.IDLE
    read_count = 0
    id = []
    sector = []
    track = []
    ds = data_separator(interval_buf, clk_spd=clk_spd, high_gain=high_gain, low_gain=low_gain)    # Clock / Data separator
    crc = CCITT_CRC()

    ds.set_mode(0)      # AM seeking

    while True:
        ## Format parsing

        # set data separator mode
        if state == State.IDLE or state == State.CHECK_MARK:
            ds.set_mode(0)      # AM seeking
        else:
            ds.set_mode(1)      # data reading

        data, mc = ds.get_byte()
        if data == -1:
            break
        mfm_buf.append(data)
        mc_buf.append(mc)

        # State machine
        if state == State.IDLE:
            if  mc== True:                  # found a missing clock
                state = State.CHECK_MARK

        elif state == State.CHECK_MARK:
            if mc == True:                  # Skip missing clock data
                continue
            elif data == 0xfc:      # Index AM
                state = State.INDEX
            elif data == 0xfe:      # ID AM
                state = State.IDAM
            elif data == 0xfb:      # Data AM
                state = State.DAM
            elif data == 0xf8:      # Deleted Data AM
                state = State.DDAM
            else:
                state = State.IDLE

        elif state == State.INDEX:          # Index Address mark
            if log_level>0:
                print('INDEX')
            state = State.IDLE
 
        elif state == State.IDAM:           # ID Address Mark
            if read_count == 0:
                if log_level>0:
                    print('IDAM ', end='')
                id = [ 0xfe ]
                read_count = 4+2   # ID+CRC
            id.append(data)
            read_count -= 1
            if read_count == 0:
                crc.reset()
                crc.data(id)
                id_ = id.copy()
                id = id[1:-2]   # remove IDAM and CRC
                if crc.get()==0:
                    if log_level>0:
                        print("CRC - OK ({},{},{},{})".format(id[0], id[1], id[2], id[3]))
                else:
                    if log_level>0:
                        print("CRC - ERROR")
                    if log_level>1:
                        dump_list_hex(id_)
                state = State.IDLE

        elif state == State.DAM:             # Data Address Mark (Sector)
            if len(id)<4:
                state = State.IDLE
                continue
            if log_level>0:
                print('DAM ', end='')
            sector = [ 0xfb ]
            address_mark = True      # DM
            read_count = [128, 256, 512, 1024][id[3] & 0x03]
            read_count += 2   # for CRC
            state = State.DATA_READ

        elif state == State.DDAM:            # Deleted Data Address Mark (Sector)
            if len(id)<4:
                state = State.IDLE
                continue
            if read_count == 0:
                if log_level>0:
                    print('DDAM ', end='')
                sector = [ 0xf8 ]
                address_mark = False      # DDM
                read_count = [128, 256, 512, 1024][id[3] & 0x03]
                read_count += 2   # for CRC
            state = State.DATA_READ
 
        # Read sector data for DAM and DDAM
        if state == State.DATA_READ:
            sector.append(data)
            read_count -= 1
            if read_count == 0:
                crc.reset()
                crc.data(sector)
                _sector = sector.copy()
                sector = sector[1:-2]   # remove DAM or DDAM and CRC
                if crc.get()==0:
                    num_sect_read += 1
                    if log_level>0:
                        print("CRC - OK")
                    if log_level>1:
                        dump_list_hex(_sector)
                    track.append([id, True, sector, address_mark])  # ID, CRC, Data, AM
                else:
                    num_sect_err += 1
                    if log_level>0:
                        print("CRC - ERROR")
                    if log_level>1:
                        dump_list_hex(_sector)
                    track.append([id, False, sector, address_mark])
                id=[]
                ds.reset(high_gain=high_gain, low_gain=low_gain)
                state = State.IDLE

    return track, mfm_buf, mc_buf, num_sect_read, num_sect_err


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


class d77_image:
    def __init__(self):
        pass
    
    def create_header(self, disk_name, wp_flag=0, disk_type=0):
        """
        Args:
          wp_flag = 0: no protect, 0x10: write protect
          disk_type = 0x00:2D, 0x10:2DD, 0x20:2HD
        """
        hdr = bytearray([0]*0x02b0)
        for p, c in enumerate(disk_name):
            hdr[p] = ord(c)
        hdr[0x1a] = wp_flag
        hdr[0x1b] = disk_type
        return hdr

    def create_sector(self, sect_data, c, h, r, n, num_sec, density=0, am=0, status=0):
        """
        Args:
          sect_data (list): sector data
          c, h, r, n: C/H/R/N (sector ID)
          num_sec: number sectors in this track
          density: 0x00: double, 0x40: single
          am: Address mark (0x00: Data Mark, 0x10: DDM)
          status: Disk BIOS status (0==no error)
        """
        sect_size = len(sect_data)
        sect = bytearray([c, h, r, n, num_sec % 0x100, num_sec // 0x100, density, am, status, 0, 0, 0, 0, 0, sect_size % 0x100, sect_size // 0x100 ])
        sect += bytearray(sect_data)
        return sect

    def set_dword(self, barray, pos, data):
        for i in range(4):
            barray[pos+i] = data & 0xff
            data >>= 8

    def set_word(self, barray, pos, data):
        for i in range(2):
            barray[pos+i] = data & 0xff
            data >>= 8

    def set_track_table(self, hdr, track_num, data):
        """
        Set track offset to the offset table in the header of the d77 disk image
        """
        pos = 0x20 + track_num*4
        self.set_dword(hdr, pos, data)

    def generate(self, disk_data, disk_name = 'DISK'):
        img = self.create_header(disk_name)
        for track in disk:
            num_sects = len(track)
            if num_sects==0:
                continue
            track_num = track[0][0][0]*2 + track[0][0][1]  # C*2 + H
            self.set_track_table(img, track_num, len(img))
            for sect in track:
                idam = sect[0]
                sect_data = self.create_sector(sect[2], idam[0], idam[1], idam[2], idam[3], num_sects, density=0, am=0 if sect[3] else 0x10, status=0 if sect[1] else 0x80)
                img += bytearray(sect_data)
        # set total disk image size
        self.set_dword(img, 0x001c, len(img))
        return img



# CRC generation test
"""
# FE 01 01 03 01 DD EA
crc = CCITT_CRC()
crc.reset()
data=[0xfe, 0x01, 0x01, 0x03, 0x01, 0xdd, 0xea]
crc.data(data[:])
print(format(crc.get(), '04X'))
"""

# read a bitstream file
#"""
disk_data = 'putty/fb33l1.log'
bs = bitstream(disk_data)
#bs.open(disk_data)
#bs.display_histogram(1,0)
#"""

# decode all tracks in an image
#"""
disk = []
for track_id in bs.disk:
    track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(bs.disk[track_id], clk_spd=4e6, high_gain=0., low_gain=0., log_level=0)
    print(sec_read, sec_err)
    disk.append(track)
#"""

# track data dump
"""
track_id = '0-0'
track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(bs.disk[track_id], clk_spd=4e6, high_gain=0., low_gain=0., log_level=1)
#dumpMFM(mfm_buf, mc_buf)
"""

# display pritable characters in a track
"""
for track in disk:
    for sect in track:
        for c in sect[2]:
            if c>=ord(' ') and c<=ord('z'):
                print(chr(c), end='')
"""

# D77 disk image generation
#"""
d77 = d77_image()
img = d77.generate(disk)
with open('disk_img2.d77', 'wb') as f:
    f.write(img)
#"""
