# VFO class for data separator

class vfo_base:
    def __init__(self):
        self.set_cell_size_ref(8.0)
        self.set_gain(1.0, 2.0)
        self.set_gain_mode(False)
    
    def reset(self):
        self.set_cell_size(self.cell_size_ref)
        self.set_gain_mode(False)

    def set_cell_size_ref(self, cell_size_ref:float=8.0, window_ratio:float=1.0):
        self.cell_size_ref = cell_size_ref
        self.set_cell_size(cell_size_ref, window_ratio)

    def set_cell_size(self, cell_size:float=8.0, window_ratio:float=1.0):
        self.cell_size = cell_size
        self.window_ratio = window_ratio
        self.window_size = self.cell_size * self.window_ratio
        self.window_ofst = (self.cell_size - self.window_size) / 2.0
        self.cell_center = self.cell_size / 2.0

    def set_gain(self, gain_l:float=1.0, gain_h:float=2.0):
        self.gain_l = gain_l
        self.gain_h = gain_h

    def set_gain_mode(self, mode:bool):
        if(mode==True):
            self.current_gain = self.gain_h
        else:
            self.current_gain = self.gain_l

    def calc(self, pulse_pos:float):
        return pulse_pos

class vfo_simple2(vfo_base):
    def __init__(self):
        super().__init__()

    def calc(self, pulse_pos:float):
        phase_diff = self.cell_center - pulse_pos
        new_cell_size = self.cell_size - phase_diff * 0.025 * self.current_gain
        self.set_cell_size(new_cell_size)

        pulse_pos = self.cell_center
        return pulse_pos
