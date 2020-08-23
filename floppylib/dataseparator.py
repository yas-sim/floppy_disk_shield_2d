# VFO + Data Separator

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
          mode: 0=AM seeking & use high_gain
                1=Data reading (ignore missing clock and 0x00 patterns) & use low_gain
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
