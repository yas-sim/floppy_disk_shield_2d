# VFO classes for the MFM data separator

####################################################################################
# VFO_BASE

class vfo_base:
    def __init__(self):
        self.set_cell_size_ref(8.0)
        self.set_gain(1.0, 1.0)
        self.set_gain_mode(False)
    
    def reset(self):
        self.set_cell_size(self.cell_size_ref)
        self.set_gain_mode(False)

    def set_cell_size_ref(self, cell_size_ref:float=8.0, window_ratio:float=0.8):
        self.cell_size_ref = cell_size_ref
        self.set_cell_size(cell_size_ref, window_ratio)

    def set_cell_size(self, cell_size:float=8.0, window_ratio:float=0.8):
        self.cell_size = cell_size
        self.window_ratio = window_ratio
        self.window_size = self.cell_size * self.window_ratio
        self.window_ofst = (self.cell_size - self.window_size) / 2.0
        self.cell_center = self.cell_size / 2.0

    def set_gain(self, gain_l:float=1.0, gain_h:float=1.0):
        self.gain_l = gain_l
        self.gain_h = gain_h

    def set_gain_mode(self, mode:bool):
        if(mode==True):
            self.current_gain = self.gain_h
        else:
            self.current_gain = self.gain_l

    def calc(self, pulse_pos:float):
        return pulse_pos


####################################################################################
# VFO_SIMPLE2

class vfo_simple2(vfo_base):
    def __init__(self):
        super().__init__()

    def calc(self, pulse_pos:float):
        phase_diff = self.cell_center - pulse_pos
        new_cell_size = self.cell_size - phase_diff * 0.025 * self.current_gain
        self.set_cell_size(new_cell_size)

        pulse_pos = self.cell_center
        return pulse_pos


####################################################################################
# VFO_PID3

class vfo_pid3(vfo_base):
    def __init__(self):
        super().__init__()
        self.hist_ptr = 0
        self.history_len = 4
        self.coeff_sum = 0
        for i in range(1, self.history_len + 1):
            self.coeff_sum += i
        self.reset()

    def reset(self):
        super().reset()
        self.soft_reset()
    
    def soft_reset(self):
        self.prev_pulse_pos = 0
        self.prev_phase_err = 0
        self.phase_err_I = 0
        self.phase_err_PC = 1/4
        self.phase_err_IC = 1/128
        self.phase_err_DC = 1/512
        self.pulse_pos_history = [ self.cell_size / 2 for i in range(self.history_len) ]

    def calc(self, pulse_pos:float):
        self.hist_ptr += 1
        self.hist_ptr = self.hist_ptr & (self.history_len-1)
        self.pulse_pos_history[self.hist_ptr] = pulse_pos
        sum = 0
        # LPF - smooth bit cell size transition
        for i in range(1, self.history_len + 1):
            sum += self.pulse_pos_history[ (self.hist_ptr + i) & (self.history_len - 1)] * i
        avg = sum / self.coeff_sum

        # PID control
        phase_err_P          = self.cell_center - avg
        phase_err_D          = phase_err_P - self.prev_phase_err
        self.phase_err_I    += phase_err_P
        self.prev_phase_err  = phase_err_P
        new_cell_size = self.cell_size_ref - (phase_err_P * self.phase_err_PC - phase_err_D * self.phase_err_DC + self.phase_err_I * self.phase_err_IC) * self.current_gain

        # Limit cell size
        tolerance = 0.8
        new_cell_size = min(new_cell_size, self.cell_size_ref *     (1 + tolerance))
        new_cell_size = max(new_cell_size, self.cell_size_ref * 1 / (1 + tolerance))

        self.set_cell_size(new_cell_size)
        self.prev_pulse_pos = pulse_pos
    
        return pulse_pos
