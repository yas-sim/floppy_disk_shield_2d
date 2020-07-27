
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


def dump_list_hex(lst):
    print('[ ', end='')
    for i in lst:
        print('0x{}, '.format(format(i, '02X')) , end='')
    print(']')


class data_separator:
    def __init__(self, interval_buf, clk_spd =4e6, gain=0.01):
        self.interval_buf = interval_buf
        self.pos = 0
        self.reset(clk_spd=clk_spd, gain=gain)
        #print(self.cell_size, self.cell_size_min, self.cell_size_max)

    def set_gain(self, gain):
        self.gain = gain

    def reset(self, clk_spd=4e6, gain=0.01):
        self.clock_speed   = clk_spd
        self.bit_cell      = 500e3    # 1/2MHz
        self.cell_size     = self.clock_speed / self.bit_cell
        self.cell_size_ref = self.cell_size
        self.cell_size_max = self.cell_size * 1.2
        self.cell_size_min = self.cell_size * 0.8
        self.gain          = gain
        self.bit_stream    = []

    def get_interval(self):
        if self.pos >= len(self.interval_buf):
            return -1
        dt = self.interval_buf[self.pos]
        self.pos+=1
        return dt

    def get_pulse(self):
        while True:
            if len(self.bit_stream)>0:
                return self.bit_stream.pop(0)
            interval = self.get_interval()   # interval = pulse interval in 'cell_size' unit
            if interval == -1:
                return -1
            int_interval = int(interval / self.cell_size + 0.5)
            error = interval - int_interval * self.cell_size
            self.cell_size += error * self.gain               # Correct the cell_size
            # cell size range limitter
            self.cell_size = max(self.cell_size, self.cell_size_min)
            self.cell_size = min(self.cell_size, self.cell_size_max)
            if   int_interval <= 2:
                self.bit_stream = [0, 1]
            elif int_interval == 3:
                self.bit_stream = [0, 0, 1]
            elif int_interval == 4:
                self.bit_stream = [0, 0, 0, 1]



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



from enum import Enum

def decodeFormat(interval_buf, high_gain=0.15, low_gain=0.005, verbose=False, ignore_CRC_error=False):
    class State(Enum):
        IDLE       = 0
        CHECK_MARK = 1
        INDEX      = 2
        IDAM       = 3
        DAM        = 4
        DDAM       = 5

    mfm_buf = []
    mc_buf  = []

    missing_clock_c2 = 0x5224  #  [0,1,0,1, 0,0,1,0, 0,0,1,0, 0,1,0,0]
    missing_clock_a1 = 0x4489  #  [0,1,0,0, 0,1,0,0, 1,0,0,0, 1,0,0,1]
    pattern_ff       = 0x5555
    pattern_00       = 0x2aaa
    
    _success = 0
    _error   = 0
    
    state = State.IDLE
    count = 0
    id = []
    sector = []
    track = []
    bit_stream      = 0
    current_data    = 0
    read_bit_count  = 0
    data_valid_flag    = False
    missing_clock_flag = False
    ds = data_separator(interval_buf, clk_spd=4e6, gain=0)    # Clock / Data separator

    while True:
        pulse = ds.get_pulse()
        if pulse == -1:
            break

        ## MFM decoding
        bit_stream = ((bit_stream<<1) | pulse) & 0x7fff
        if read_bit_count % 2 == 1:
            current_data = ((current_data<<1) | pulse) & 0xff
        read_bit_count += 1
        if bit_stream == missing_clock_c2 or bit_stream == missing_clock_a1:
            data_valid_flag    = True
            missing_clock_flag = True
            read_bit_count = 0
        if state == State.IDLE and (bit_stream == pattern_ff or bit_stream == pattern_00):
            ds.set_gain(high_gain)  # High gain
        else:
            ds.set_gain(low_gain)   # Low gain
        if read_bit_count >= 16:
            data_valid_flag    = True

        if data_valid_flag == False:
            continue

        read_bit_count = 0
        mfm_buf.append(current_data)
        mc_buf.append(missing_clock_flag)
        mc = missing_clock_flag
        data_valid_flag    = False
        missing_clock_flag = False

        
        ## Format parsing
        
        if state == State.IDLE:
            if  mc== True:                  # found a missing clock
                state = State.CHECK_MARK

        elif state == State.CHECK_MARK:
            if mc == True:                  # Skip missing clock data
                continue
            elif current_data == 0xfc:      # Index AM
                state = State.INDEX
            elif current_data == 0xfe:      # ID AM
                state = State.IDAM
            elif current_data == 0xfb:      # Data AM
                state = State.DAM
            elif current_data == 0xf8:      # Deleted Data AM
                state = State.DDAM
            else:
                state = State.IDLE

        elif state == State.INDEX:      # Index Address mark
            if verbose:
                print('INDEX')
            state = State.IDLE
 
        elif state == State.IDAM:       # ID Address Mark
            if count == 0:
                if verbose:
                    print('IDAM ', end='')
                id = [ 0xfe ]
                count = 4+2   # ID+CRC
            id.append(current_data)
            count -= 1
            if count == 0:
                crc.reset()
                crc.data(id)
                id_ = id.copy()
                id = id[1:-2]   # remove IDAM and CRC
                if crc.get()==0 or ignore_CRC_error:
                    if verbose:
                        print("CRC - OK")
                        print("CHRN=", id)
                else:
                    if verbose:
                        print("CRC - ERROR")
                        dump_list_hex(id_)
                state = State.IDLE

        elif state == State.DAM:      # Data Address Mark (Sector)
            if len(id)<4:
                if verbose:
                    print("ERROR - ID=", id)
                state = State.IDLE
                continue
            if count == 0:
                if verbose:
                    print('DAM ', end='')
                sector = [ 0xfb ]
                count = [128, 256, 512, 1024][id[3] & 0x03]
                count += 2   # for CRC
            sector.append(current_data)
            count -= 1
            if count == 0:
                crc.reset()
                crc.data(sector)
                _sector = sector.copy()
                sector = sector[1:-2]   # remove DAM and CRC
                if crc.get()==0 or ignore_CRC_error:
                    _success += 1
                    if verbose:
                        print("CRC - OK")
                        dump_list_hex(_sector)
                    track.append([id, True, sector])
                else:
                    _error += 1
                    if verbose:
                        print("CRC - ERROR")
                        dump_list_hex(_sector)
                id=[]
                ds.reset()
                state = State.IDLE

        elif state == State.DDAM:      # Deleted Data Address Mark (Sector)
            if len(id)<4:
                if verbose:
                    print("ERROR - ID=", id)
                state = State.IDLE
                continue
            if count == 0:
                if verbose:
                    print('DDAM ', end='')
                sector = [ 0xf8 ]
                count = [128, 256, 512, 1024][id[3] & 0x03]
                count += 2   # for CRC
            sector.append(current_data)
            count -= 1
            if count == 0:
                crc.reset()
                crc.data(sector)
                sector = sector[1:-2]   # remove DDAM and CRC
                if crc.get()==0 or ignore_CRC_error:
                    _success += 1
                    if verbose:
                        print("CRC - OK")
                        dump_list_hex(_sector)
                    track.append([id, False, sector])
                else:
                    _error += 1
                    if verbose:
                        print("CRC - ERROR")
                id=[]
                ds.reset()
                state = State.IDLE    

        else:
            if verbose:
                print("**************WRONG STATE")
            state = State.IDLE

    if _error+_success == 0:
        error_rate = 1
    else:
        error_rate = _error / (_error + _success)
    return track, mfm_buf, mc_buf, error_rate



disk_data = 'trk-01-0.txt'
#disk_data = 'putty/4.log'

from mpl_toolkits.mplot3d import Axes3D

crc = CCITT_CRC()

disk = []
with open(disk_data, 'r') as f:
    linebuf = ''
    for line in f:
        line = line.rstrip('\n')
        if '**TRACK_READ' in line:
            trk, side = [ int(v) for v in line.split(' ')[1:] ]
            #print(trk, side, " ", end='')
            linebuf = ''
        elif '**TRACK_END' in line:
            if len(linebuf)==0:
                continue
            interval_buf = [ ord(c)-ord(' ') for c in linebuf ]
            x = []
            y = []
            z = []
            for lg in range(0, 4000, 5):
                min_er = 9999
                for hg in range(0, 600, 5):
                    _lg = lg/10000
                    _hg = hg/1000
                    track, mfm_buf, mc_buf, er = decodeFormat(interval_buf, high_gain=_hg, low_gain=_lg, verbose=False, ignore_CRC_error=False)
                    #if min_er>er or er==0:
                    #    min_er = er
                    x.append(_hg)
                    y.append(_lg)
                    z.append(er)
                    print(trk, side, _hg, _lg, er)

            #disk.append(track)
        else:
            linebuf += line

import matplotlib.pyplot as plt

fig = plt.figure()
ax = Axes3D(fig)
ax.set_xlabel('high gain')
ax.set_ylabel('low_gain')
ax.plot(x, y, z, marker='o', linestyle='None')
plt.show()