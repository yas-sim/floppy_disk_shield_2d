# RAW bitstream library

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

