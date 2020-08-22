# folppy shield library

from enum import Enum

import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

"""
## Read encoded track data and decode it
- Disc read data will invert on every read pulse (0->1, 1->0)
- This data represents how long the same bit value continued (bit interval, 000 -> 3, 11111 -> 5)
- The bit interval is encoded with `ord(' ')+bit_interval`. 

FDD output    :  111101110111110111011101
Captured data :  000011110000001111000011
This data     :     4   4     6   4   4 2  => I call this as "interval data"
"""
class bitstream:
    def __init__(self, file=None):
        self.disk = {}
        if file is not None:
            self.open(file)

    def open(self, file):
        self.disk = {}
        self.spin_spd = 0.2             # default spin speed = 0.2ms = 300rpm
        with open(file, 'r') as f:
            linebuf = ''
            for line in f:
                line = line.rstrip('\n')
                if len(line)==0:
                    continue
                if '**SPIN_SPD'   in line:
                    self.spin_spd = float(line.split(' ')[1])
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
        ax1.hist(data, bins=80, range=(0,80), histtype='stepfilled', orientation='vertical', log=False)
        ax2.grid(True)
        ax2.hist(data, bins=80, range=(0,80), histtype='stepfilled', orientation='vertical', log=True)
        plt.show()


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

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


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


def dump_list_hex(lst):
    print('[ ', end='')
    for i in lst:
        print('0x{}, '.format(format(i, '02X')) , end='')
    print(']')

def dumpMFM(mfm_buf, mc_buf=None):
    count = 0
    for mfm in mfm_buf:
        if mc_buf is not None:
            mc = mc_buf.pop(0)
            if mc==True:
                print(' *', end='')
            else:
                print('  ', end='')
        else:
            print(' ', end='')
        print(format(mfm, '02X'), end='')
        count+=1
        if count==32:
            count=0
            print('')
    print('')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

"""
 MFM spec
 Clock bit is inserted when the previous and next data bit are both 0.

Normal data pattern
FF: ' D D D D D D D D'
00: '? C C C C C C C '
C2: ' D D  C C C  D  '
A1: ' D   D  C C C  D'

Missing clock data pattern (*=missing clock)
C2: ' D D  C * C  D  '
A1: ' D   D  C * C  D'
"""

class data_separator:
    def __init__(self, interval_buf, clk_spd =4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01):
        self.interval_buf = interval_buf
        self.rewind()
        self.reset(clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain)
        missing_clock_c2 = (0x5224)  #  [0,1,0,1, 0,0,1,0, *,0,1,0, 0,1,0,0]
        missing_clock_a1 = (0x4489)  #  [0,1,0,0, 0,1,0,0, 1,0,*,0, 1,0,0,1]
        pattern_ff       = (0x5555555555555555)  # for 4 bytes of sync data (unused)
        pattern_00       = (0xaaaaaaaaaaaaaaaa)  # for 4 bytes of sync data
        self.missing_clock = [ missing_clock_c2, missing_clock_a1 ]
        #self.sync_pattern  = [ pattern_ff, pattern_00 ]
        self.sync_pattern  = [ pattern_00 ]

    def rewind(self):
        '''
        Rewind the read pointer of the bit stream
        '''
        self.pos  = 0
        self.time = 0       # real time value at the current read pointer (ns)

    def set_gain(self, high_gain, low_gain):
        self.high_gain = high_gain
        self.low_gain  = low_gain

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

    def reset(self, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01):
        self.clock_speed    = clk_spd
        self.clock_cycle_ns = 1e9/clk_spd              # clock cycle in [ns] 4MHz == 250ns
        self.spin_speed     = spin_spd                 # ms/spin
        self.bit_cell       = 500e3                    # 1/2MHz
        self.cell_size      = (self.clock_speed*(spin_spd/0.2)) / self.bit_cell
        self.cell_size_ref  = self.cell_size
        self.cell_size_max  = self.cell_size * 1.1
        self.cell_size_min  = self.cell_size * 0.9
        self.bit_stream     = []
        self.set_gain(high_gain=high_gain, low_gain=low_gain)
        self.switch_gain(0)         # low speed gain
        self.set_mode(0)            # 0: AM seeking, 1: Data reading (ignore SYNC and missing clock patterns)
        self.cd_stream      = 0      # C+D bitstream for missing clock and SYNC pattern detection

    def get_interval(self):
        if self.pos >= len(self.interval_buf):
            return -1
        dt = self.interval_buf[self.pos]
        self.pos  += 1
        self.time += dt * self.clock_cycle_ns
        return dt

    def get_quantized_interval(self):
        """
        Get pulse interval value and do VFO tracking
        """
        interval = self.get_interval()   # interval = pulse interval in 'cell_size' unit (cell_size=2us in case of 2D/2DD)
        if interval == -1:
            return -1, -1

        quant_interval = int(interval / self.cell_size + 0.5)
        # Track rotatioin speed fluctuation
        try:
            error = interval / quant_interval - self.cell_size
        except ZeroDivisionError:
            pass
        else:
            self.cell_size += error * self.gain             # Adjust the cell_size

        # cell size range limitter
        self.cell_size = max(self.cell_size, self.cell_size_min)
        self.cell_size = min(self.cell_size, self.cell_size_max)
        return quant_interval, interval

    def calc_time_from_pos(self, pos):
        tm = 0
        if pos<len(self.interval_buf) and pos>0:
            for i in range(pos):
                tm += self.interval_buf[i] * self.clock_cycle_ns
        return tm

    def get_time_ns(self):
        return self.time

    def get_time_ms(self):
        return self.time / 1e6

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        if pos<len(self.interval_buf) and pos>0:
            self.pos  = pos
            self.time = self.calc_time_from_pos(pos) 

    def get_bit(self):  # Does VFO tracking
        while True:
            if len(self.bit_stream) > 0:
                bit = self.bit_stream.pop(0)
                return bit
            quant_interval, interval = self.get_quantized_interval()
            if quant_interval == -1:
                return -1
            if   quant_interval == 2:
                self.bit_stream +=       [0, 1]
            elif quant_interval == 3:
                self.bit_stream +=    [0, 0, 1]
            elif quant_interval == 4:
                self.bit_stream += [0, 0, 0, 1]

    def get_bit_2(self):  # No VFO tracking version
        while True:
            if len(self.bit_stream) > 0:
                bit = self.bit_stream.pop(0)
                return bit
            interval = self.get_interval()   # interval = pulse interval in 'cell_size' unit (cell_size=2us in case of 2D/2DD)
            if interval == -1:
                return -1

            int_interval = int(interval / self.cell_size_ref + 0.5)
            if   int_interval == 2:
                self.bit_stream +=       [0, 1]
            elif int_interval == 3:
                self.bit_stream +=    [0, 0, 1]
            elif int_interval == 4:
                self.bit_stream += [0, 0, 0, 1]

    # cd_data = CDCDCD... extract only D bits
    def extract_data_bits(self, cd_data):
        data = 0
        bit = 0x4000
        for i in range(8):
            data = (data<<1) | (0 if (cd_data & bit == 0) else 1)
            bit >>= 2
        return data

    # mode 0 = enable sync, mc detection (AM seek), 1 = disable sync, mc detection (data read)
    def get_byte(self):
        read_bit_count = 0   # read bit count
        while True:
            bit = self.get_bit()        # with VFO tracking
            #bit = self.get_bit_2()     # with fixed VFO
            if bit == -1:
                return -1, False
            read_bit_count += 1

            self.cd_stream = ((self.cd_stream<<1) | bit) & 0xffffffffffffffff

            if self.mode == 0 and ((self.cd_stream & 0xffff) in self.missing_clock):  # missing clock pattern check
                return self.extract_data_bits(self.cd_stream), True

            if self.mode == 0 and (self.cd_stream in self.sync_pattern):   # SYNC pattern check
                self.switch_gain(1)                                        # Fast tracking mode to get syncronized with SYNC pattern
                read_bit_count &= ~1                                       # C/D synchronize
            else:
                self.switch_gain(0)

            if read_bit_count >= 16:
                return self.extract_data_bits(self.cd_stream), False       # 8 bit data read completed

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

def read_track(interval_buf, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01, log_level=0):
    """
    Decode bistream track data  
    Args:
      interval_buf : Bitstream buffer for a track (pulse interval buffer)
      clk_spd : clock speed of the floppy capture shield (default = 4MHz = 4e6)
      high_gain : data separator tracking gain for high speed (=address mark seeking) region
      low_gain : data separator tracking gain for low speed (=data reading) region
      log_level : 0=No message, 1=minimum message, 2=detailed message
    Returns:
      mfm_buf : MFM decoded data (list)
      mc_buf  : MC or not flags (list). each data corresponds to the MFM data in the same position
    """
    if log_level>0: print('**Read track')

    mfm_buf = []
    mc_buf  = []

    ds = data_separator(interval_buf, clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain)    # Clock / Data separator
    ds.set_mode(0)      # AM seeking

    while True:
        data, mc = ds.get_byte()
        if data == -1:
            break
        mfm_buf.append(data)
        mc_buf.append(mc)
    return mfm_buf, mc_buf



def search_all_idam(interval_buf, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01, log_level=0, abort_by_idxmark=True, abort_by_sameid=True):
    """
    Decode bistream track data  
    Args:
      interval_buf : Bitstream buffer for a track (pulse interval buffer)
      clk_spd : clock speed of the floppy capture shield (default = 4MHz = 4e6)
      high_gain : data separator tracking gain for high speed (=address mark seeking) region
      low_gain : data separator tracking gain for low speed (=data reading) region
      log_level : 0=No message, 1=minimum message, 2=detailed message
      abort_by_idxmark (bool): Abort reading on detection of 2nd index mark 
      abort_by_sameid  (bool): Abort reading on detection of 2nd same ID detection (potential of 2nd lap)
    Returns:
      id_buf = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                      ID-CRC flag = True:No error False:error  
                      ds_pos  = ID position in the interval buffer
                      mfm_pos = ID position in the MFM buffer   
    """
    class State(Enum):
        IDLE       = 0
        CHECK_MARK = 1
        INDEX      = 2
        IDAM       = 3
        DAM        = 4
        DDAM       = 5
        DATA_READ  = 6
    
    ds = data_separator(interval_buf, clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain)    # Clock / Data separator
    ds.set_mode(0)      # AM seeking
    ds.set_pos(0)

    crc = CCITT_CRC()

    state = State.IDLE

    read_count = 0
    id_field = []
    id_lists = []    # for checking ID duplication (= potential of 2nd lap) 
    id_buf = []
    mc_byte = 0
    id_ds_pos  = 0
    id_mfm_pos = 0
    mfm_count  = 0
    idx_count  = 0   # index mark count

    if log_level>0: print('**Search all ID')

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
        mfm_count += 1

        # State machine
        if state == State.IDLE:
            if  mc == True:                 # found a missing clock
                state = State.CHECK_MARK

        elif state == State.CHECK_MARK:
            if mc == True:                  # Skip missing clock data
                mc_byte = data
                continue
            # C2 C2 C2 FC is an Index mark but A1 A1 A1 FC can be used as ID mark (a bug in FDC?)
            elif data == 0xfe or (mc_byte == 0xa1 and data == 0xfc): # ID AM
                if log_level>0: print('IDAM ', end='')
                id_field = [ data ]
                read_count = 4+2   # ID+CRC
                id_ds_pos  = ds.get_pos()   # ID position in the interval buffer
                id_mfm_pos = mfm_count-1
                state = State.IDAM
            elif mc_byte == 0xc2 and data == 0xfc:
                if log_level>0: print('IDX_MARK')
                idx_count += 1
                if ds.get_time_ms() > spin_spd*1000:    # index_abort will be enabled from the 2nd lap
                    if idx_count > 1 and abort_by_idxmark:
                        if log_level>0: print('2nd index mark is detected - read aborted')
                        break
            else:
                state = State.IDLE

        elif state == State.IDAM:           # ID Address Mark
            id_field.append(data)
            read_count -= 1
            if read_count == 0:
                crc.reset()
                crc.data(id_field)
                if ds.get_time_ms() > spin_spd*1000:    # same_id_abort will be enabled from the 2nd lap
                    if id_field[1:-2] in id_lists and abort_by_sameid:     # abort when the identical ID is detected
                        if log_level>0: print('Abort by 2nd identical ID detection')
                        break
                id_lists.append(id_field[1:-2])   # remove DataAM and CRC
                if crc.get()==0:
                    id_buf.append(id_field[1:] + [True, id_ds_pos, id_mfm_pos])  #id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                    if log_level>0: print("CRC - OK ({:02x},{:02x},{:02x},{:02x}) - {}, {}".format(id_field[1], id_field[2], id_field[3], id_field[4], id_ds_pos, id_mfm_pos))
                    if log_level>1: dump_list_hex(id_field)
                else:
                    id_buf.append(id_field[1:] + [False, id_ds_pos, id_mfm_pos])
                    if log_level>0: print("CRC - ERROR {}-{}".format(id_ds_pos, id_mfm_pos))
                    if log_level>1: dump_list_hex(id_field)
                state = State.IDLE
    return id_buf



def read_sector(interval_buf, sect_num, ds_pos=0, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01, log_level=0):
    """
    Decode bistream track data  
    Args:  
      interval_buf : Bitstream buffer for a track (pulse interval buffer)
      sect_num (int): sector number to read
      ds_pos (int): start data position of data separator. ID search start from this position of the interval data buffer. (default=0)
      clk_spd : clock speed of the floppy capture shield (default = 4MHz = 4e6)
      high_gain : data separator tracking gain for high speed (=address mark seeking) region
      low_gain : data separator tracking gain for low speed (=data reading) region
      log_level : 0=No message, 1=minimum message, 2=detailed message
    Return:  
       (Status, Data-CRC, Data, DAM/DDAM) : Status(False=Not found), Data-CRC(False=Error), Data=sector data(list), DAM/DDAM(True=DAM)
    """
    class State(Enum):
        IDLE       = 0
        CHECK_MARK = 1
        INDEX      = 2
        IDAM       = 3
        DAM        = 4
        DDAM       = 5
        DATA_READ  = 6

    state = State.IDLE
    read_count = 0
    mc_byte = 0
    id_field = []
    sector = []

    ds = data_separator(interval_buf, clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain)    # Clock / Data separator
    ds.set_mode(0)      # AM seeking

    ds_pos = max(0, ds_pos - (16*16))  # Rewind the start position a bit
    ds.set_pos(ds_pos)  # sector search start position

    crc = CCITT_CRC()

    if log_level>0: print('**Read sector {:02x}'.format(sect_num))

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

        # State machine
        if state == State.IDLE:
            if  mc == True:                 # found a missing clock
                state = State.CHECK_MARK

        elif state == State.CHECK_MARK:
            if mc == True:                  # Skip missing clock data
                mc_byte = data
                continue
            # C2 C2 C2 FC is an Index mark but A1 A1 A1 FC can be used as ID mark (a bug in FDC?)
            elif data == 0xfe or (mc_byte == 0xa1 and data == 0xfc): # ID AM
                if log_level>0: print('IDAM ', end='')
                id_field = [ data ]
                read_count = 4+2   # ID+CRC
                state = State.IDAM
            elif mc_byte == 0xc2 and data == 0xfc:  # Index AM
                state = State.INDEX
            elif data == 0xfb or data == 0xf8:      # DataAM or DeletedDataAM
                if len(id_field) < 4:
                    state = State.IDLE
                elif id_field[2] == sect_num:       # check sector # match
                    if log_level>0:
                        if data == 0xfb: print('DAM ', end='')
                        else:            print('DDAM', end='')
                    sector = [ data ]
                    address_mark = True if data==0xfb else False  # DAM=True, DDAM=False
                    read_count = [128, 256, 512, 1024][id_field[3] & 0x03]
                    read_count += 2   # for CRC
                    state = State.DATA_READ
                else:
                    state = State.IDLE
            else:
                state = State.IDLE

        elif state == State.INDEX:          # Index Address mark
            if log_level>0: print('INDEX')
            state = State.IDLE
 
        elif state == State.IDAM:           # ID Address Mark
            id_field.append(data)
            read_count -= 1
            if read_count == 0:
                crc.reset()
                crc.data(id_field)
                id_ = id_field.copy()
                id_field = id_field[1:-2]   # remove IDAM and CRC
                if crc.get()==0:
                    if log_level>0: print("CRC - OK ({:02x},{:02x},{:02x},{:02x})".format(id_field[0], id_field[1], id_field[2], id_field[3]))
                else:
                    if log_level>0: print("CRC - ERROR")
                    if log_level>1: dump_list_hex(id_)
                state = State.IDLE

        # Read sector data for DAM and DDAM
        elif state == State.DATA_READ:
            sector.append(data)
            read_count -= 1
            if read_count == 0:
                crc.reset()
                crc.data(sector)
                if crc.get()==0:
                    if log_level>0: print("CRC - OK")
                    if log_level>1: dump_list_hex(sector)
                    return (True, True, sector[1:-2], address_mark)  # Status, Data-CRC, Data (except AM and CRCs), DAM/DDAM
                else:
                    if log_level>0: print("CRC - ERROR")
                    if log_level>1: dump_list_hex(sector)
                    return (True, False, sector[1:-2], address_mark)  # Status, Data-CRC, Data (except AM and CRCs), DAM/DDAM

    return (False, False, [], False)  # Status, CRC, Data, DAM/DDAM  (Sector not found)



def read_all_sectors(interval_buf, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01, log_level=0, abort_by_idxmark=True, abort_by_sameid=True):
    """
    Read all sector data in a track  
    Return:  
      track : track = [[id_field, data-CRC_status, sect_data, DAM],...]
                        id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
      num_read (int): number of sector read 
      num_error (int): number of sector read and caused error (CRC)
    """
    num_read  = 0
    num_error = 0
    track = []

    if log_level==2:
        print('Read all sectors')

    id_list = search_all_idam(interval_buf, clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain, log_level=log_level,
                     abort_by_idxmark=abort_by_idxmark, abort_by_sameid=abort_by_sameid)
    for id_field in id_list:
        sect    = id_field[2]
        idcrc   = id_field[6]
        pos     = id_field[7] # ds_pos
        if idcrc == False:  # ID-CRC error but add ID to the data (to let the ID exist in the image)
            num_error += 1
            track.append([id_field, False, [], True]) # ID, CRC=Err, Data, DAM=DAM
            continue
        status, datacrc, sector, dam = read_sector(interval_buf, sect_num = sect, ds_pos = pos, clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain, log_level=log_level)
        if status == False:   # record not found
            num_error += 1
            track.append([id_field, False, [], True])  # ID, CRC, Data, DAM
            continue
        if datacrc == False:      # CRC error
            num_error += 1
            track.append([id_field, False, sector, dam])  # ID, CRC, Data, DAM
        else:
            num_read += 1
            track.append([id_field, True, sector, dam])  # ID, CRC, Data, DAM
    return track, num_read, num_error


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
        hdr = bytearray([0]*(0x20+ (4*164) + (4*164)))
        for p, c in enumerate(disk_name):
            hdr[p] = ord(c)
        hdr[0x1a] = wp_flag
        hdr[0x1b] = disk_type
        return hdr

    def create_sector(self, sect_data, c, h, r, n, num_sec, density=0, am=0, status=0, ext_status=0, id_crc1=0, id_crc2=0, pos=0):
        """
        Args:
          sect_data (list): sector data
          c, h, r, n: C/H/R/N (sector ID)
          num_sec: number sectors in this track
          density: 0x00: double, 0x40: single
          am: Address mark (0x00: Data Mark, 0x10: DDM)
          status: Disk BIOS status (0==no error)
          pos: Sector position in MFM byte count
        """
        sect_size = len(sect_data)
        sect = bytearray([c, h, r, n, 
                num_sec  % 0x100, 
                num_sec // 0x100, 
                density, 
                am, 
                status, 
                0, 0,         # sector position (WORD) placeholder
                ext_status, 
                id_crc1, id_crc2,
                sect_size  % 0x100, 
                sect_size // 0x100 ])
        self.set_word(sect, 0x09, pos)
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

    def set_sect_table(self, hdr, track_num, data):
        """
        Set sect data offset to the offset table in the header of the d77 disk image
        """
        pos = 0x20 + track_num*4
        self.set_dword(hdr, pos, data)

    def set_track_table(self, hdr, track_num, data):
        """
        Set raw track data offset to the offset table in the header of the d77 disk image
        """
        pos = 0x2b0 + track_num*4
        self.set_dword(hdr, pos, data)

    def generate(self, disk_data, mfm_data=None, mc_data=None, disk_type=0, disk_name = 'DISK'):
        """
        Args:  
          disk_data : disk data
          track_img : track image data
          disk_type : 0=2D, 0x10=2DD, 0x20=2HD
          disk_name (string) : disk image name (not the file name)
        """
        img = self.create_header(disk_name, disk_type=disk_type)
        
        # Raw track data (D77 extension)
        if not mfm_data is None:
            if not mc_data is None:
                print('Adding raw track image data (MFM+MC)')
                img[0x11] = 0x10        # Raw track data extension flag
                track_num = 0
                # MFM+MC interleaved format  [MFM0, MC0, MFM1, MC1, ...]
                for i, (mfm, mc) in enumerate(zip(mfm_data, mc_data)):  # track_img[0]=mfm, track_img[1]=missing_clock
                    self.set_track_table(img, track_num, len(img))
                    buf = []
                    for _mfm, _mc in zip(mfm, mc):
                        buf += [_mfm, _mc]
                    track_len = len(buf)
                    _track = bytearray([0,0,0,0]+buf)
                    self.set_dword(_track, 0, track_len)        # set track data length
                    img += _track
                    track_num += 1
            else:
                print('Adding raw track image data (MFM only)')
                img[0x11] = 0x10        # Raw track data extension flag
                track_num = 0
                # MFM only format [ MFM0, MFM1, MFM2, ...]
                for mfm in mfm_data:
                    self.set_track_table(img, track_num, len(img))
                    buf = bytearray([ 0,0,0,0 ] + mfm)
                    self.set_dword(buf, 0, len(mfm))   # set track data length
                    img += buf
                    track_num += 1

        # Sector data
        for track_num, track in enumerate(disk_data):
            """
              track = [[id_field, Data-CRC_status, sect_data, DAM],...]
                        id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                        num_read (int): number of sector read 
                        num_error (int): number of sector read and caused error (CRC)
            """
            num_sects = len(track)
            if num_sects==0:
                continue
            self.set_sect_table(img, track_num, len(img))
            for sect in track:
                id_field   = sect[0]
                dt_crc_f   = sect[1]
                id_crc_f   = id_field[6]
                status     = 0x00 if dt_crc_f else 0xb0   # Data CRC error
                ext_status = 0x00 if id_crc_f else 0x01   # ID CRC error 
                am = 0 if sect[3] else 0x10
                sect_data = self.create_sector(
                    sect[2],                # Sector data
                    id_field[0], id_field[1], id_field[2], id_field[3], 
                    num_sects,
                    density=0, 
                    am=am,
                    status=status,
                    ext_status=ext_status,  # ID CRC error flag
                    id_crc1=id_field[4],    # ID CRC value
                    id_crc2=id_field[5],
                    pos = id_field[8])      # Sector pos in MFM byte count
                img += bytearray(sect_data)

        # set total disk image size
        self.set_dword(img, 0x001c, len(img))
        return img
