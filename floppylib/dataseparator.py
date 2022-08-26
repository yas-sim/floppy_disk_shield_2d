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


from floppylib.vfo import vfo_simple2


class data_separator:
    def __init__(self, bit_stream=None, clk_spd=4e6, spin_spd=0.2, high_gain=0.3, low_gain=0.01):
        self.vfo = vfo_simple2()
        self.rewind()
        self.reset(clk_spd=clk_spd, spin_spd=spin_spd, high_gain=high_gain, low_gain=low_gain)
        self.bit_stream = bit_stream
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
        self.cell_pos  = 0
        self.time = 0       # real time value at the current read pointer (ns)

    def set_gain(self, high_gain, low_gain):
        self.vfo.set_gain(low_gain, high_gain)

    def switch_gain(self, gain_mode):
        if gain_mode == 1:
            self.vfo.set_gain_mode(False)  # High
        else:
            self.vfo.set_gain_mode(False)  # Low

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
        self.bit_rate       = 500e3                    # 500HKz
        self.bit_stream     = []
        self.set_gain(high_gain=high_gain, low_gain=low_gain)
        self.switch_gain(0)         # low speed gain
        self.set_mode(0)            # 0: AM seeking, 1: Data reading (ignore SYNC and missing clock patterns)
        self.cd_stream      = 0      # C+D bitstream for missing clock and SYNC pattern detection
        self.distance_to_next_pulse = 0
        self.cell_pos = 0
        self.prev_cell_pos = 0
        self.vfo.reset()

    def calc_time_from_pos(self, pos):
        tm = 0
        if pos<len(self.bit_stream) and pos>0:
            for i in range(pos):
                tm += self.bit_stream[i] * self.clock_cycle_ns
        return tm

    def get_time_ns(self):
        return self.time

    def get_time_ms(self):
        return self.time / 1e6

    def get_pos(self):
        return self.cell_pos

    def set_pos(self, pos):
        pos = max(pos, 0)
        pos = min(pos, len(self.bit_stream)-1)
        self.cell_pos  = pos
        self.time = self.calc_time_from_pos(self.cell_pos) 

    def read_stream(self):
        val = self.bit_stream[self.cell_pos]
        self.cell_pos += 1
        if self.cell_pos >= len(self.bit_stream):
            self.cell_pos = 0
            return -1
        return val

    def get_distance_to_next_pulse(self):
        distance = 0
        while True:
            bit = self.read_stream()
            if bit == -1:
                return -1
            if bit != 0:
                return distance
            distance += 1
            if distance >= len(self.bit_stream):
                return distance

    def set_cell_size(self, cell_size):
        self.vfo.set_cell_size(cell_size)

    # Read next 1 bit (for actual reading)
    def get_bit(self):
        bit_reading = 0
        while True:
            if self.distance_to_next_pulse < self.vfo.cell_size:
                if self.distance_to_next_pulse >= self.vfo.window_ofst and \
                   self.distance_to_next_pulse <  self.vfo.window_ofst + self.vfo.window_size:
                    bit_reading = 1
                else:
                    pass    # irregular pulse

                self.distance_to_next_pulse = self.vfo.calc(self.distance_to_next_pulse)

                distance = self.get_distance_to_next_pulse()
                if distance == -1:
                    return -1

                self.distance_to_next_pulse += distance

            if self.distance_to_next_pulse >= self.vfo.cell_size:
                break

        if self.distance_to_next_pulse >= self.vfo.cell_size:
            self.distance_to_next_pulse -= self.vfo.cell_size
        return bit_reading


    # Read next 1 bit (for analysis)
    def get_bit_ex(self):
        bit_reading = 0
        advance_cell = False
        pulse_pos = 0

        while True:
            if self.distance_to_next_pulse < self.cell_size:
                pulse_pos = self.distance_to_next_pulse
                if self.distance_to_next_pulse >= self.window_ofst and \
                   self.distance_to_next_pulse <  self.window_ofst + self.window_size:
                    bit_reading = 1
                else:
                    pass    # irregular pulse
                distance = self.get_distance_to_next_pulse()
                if distance == -1:
                    return -1

                cell_center = self.window_ofst + self.window_size / 2;
                error = self.distance_to_next_pulse - cell_center

                # data pulse position adjustment == phase correction
                self.distance_to_next_pulse -= error * 0.5

                # cell size adjustment == frequency correction
                new_cell_size = self.cell_size + error * 0.1
                new_cell_size = max(new_cell_size, self.cell_size_ref * 0.8)
                new_cell_size = min(new_cell_size, self.cell_size_ref * 1.2)
                self.set_cell_size(new_cell_size)

                self.distance_to_next_pulse += distance
            if self.distance_to_next_pulse >= self.cell_size:
                advance_cell = True
                break
        if self.distance_to_next_pulse >= self.cell_size:
            self.distance_to_next_pulse -= self.cell_size
        return bit_reading, pulse_pos, advance_cell

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
