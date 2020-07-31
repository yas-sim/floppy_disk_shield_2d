# Kryoflux raw stream data to FD-Shield bit stream data converter
import sys
import os
import re
import glob
import argparse

import matplotlib.pyplot as plt

from floppylib import *


def histogram(data):
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    ax1.grid(True)
    ax1.set_title('linear')
    ax1.hist(data, bins=256, range=(0,256), histtype='stepfilled', orientation='vertical', log=False)
    ax2.grid(True)
    ax2.set_title('log')
    ax2.hist(data, bins=256, range=(0,256), histtype='stepfilled', orientation='vertical', log=True)
    plt.show()


class KFX_stream:
    def __init__(self):
        self.pos = 0
        pass

    def open(self, file):
        with open(file, 'rb') as f:
            self.streamdata = f.read()
    
    def get_byte(self, pos=-1):
        if pos == -1:
            if self.pos < len(self.streamdata):
                res = self.streamdata[self.pos]
                self.pos += 1
                return res
            return -1   # end of file
        else:
            if pos < len(self.streamdata):
                res = self.streamdata[pos]
                return res
            return -1
            
    def get_word(self, pos=-1):
        res = 0
        if pos == -1:
            dt1 = self.get_byte()
            if dt1 == -1:
                return -1            
            dt2 = self.get_byte()
            if dt2 == -1:
                return -1
            res = (dt2<<8) | dt1
            return res
        else:
            dt1 = self.get_byte(pos)
            if dt1 == -1:
                return -1            
            dt2 = self.get_byte(pos+1)
            if dt2 == -1:
                return -1
            res = (dt2<<8) | dt1
            return res

    def get_dword(self, pos=-1):
        res = 0
        if pos == -1:
            dt1 = self.get_byte()
            if dt1 == -1:
                return -1            
            dt2 = self.get_byte()
            if dt2 == -1:
                return -1
            dt3 = self.get_byte()
            if dt3 == -1:
                return -1
            dt4 = self.get_byte()
            if dt4 == -1:
                return -1
            res = (dt4<<24) | (dt3<<16) | (dt2<<8) | dt1
            return res
        else:
            dt1 = self.get_byte(pos)
            if dt1 == -1:
                return -1            
            dt2 = self.get_byte(pos+1)
            if dt2 == -1:
                return -1
            dt3 = self.get_byte(pos+3)
            if dt3 == -1:
                return -1
            dt4 = self.get_byte(pos+4)
            if dt4 == -1:
                return -1
            res = (dt4<<24) | (dt3<<16) | (dt2<<8) | dt1
            return res

    def get_variable_len(self, len, pos=-1):
        res = []
        if pos == -1:
            for i in range(len):
                dt = self.get_byte()
                if dt == -1:
                    return -1
                res.append(dt)
            return res
        else:
            for i in range(len):
                dt = self.get_byte(pos+i)
                if dt == -1:
                    return -1
                res.append(dt)
            return res


def decode_track(file):
    """
    Decode a KryoFlux RAW file (1 track)  
    Args:  
      file       : KryoFlux RAW bitstream file name
    Returns:  
      stream     : Floppy pulse interval (count in sck)
      stream_pos : Bit stream position (byte position of corresponding stream data in the stream buffer)
      index_data : Index hole data [ (stream_position0, sample_counter0, index_counter0), (), ...]
      sck        : KryoFlux sampling clock rate (Hz)
    """
    bs = KFX_stream()
    bs.open(file)

    ovf = 0
    dur = 0
    stream = []
    pos = 0
    stream_pos = []

    sck = 0
    ick = 0

    stream_position = 0
    sample_counter  = 0
    index_counter   = 0
    index_data      = []
    prev_stream_position = 0
    prev_sample_counter  = 0
    prev_index_counter   = 0

    while True:
        dt = bs.get_byte()
        if dt == -1:
            break

        stream_len = 0
        if dt >= 0x0e and dt <= 0xff:
            dur = dt + ovf
            stream_len = 1
        elif dt <= 0x07:  # FLUX2
            val = bs.get_byte()
            dur = (dt<<8) + val + ovf
            stream_len = 2
        elif dt == 0x08: # NOP1
            stream_len = 1
        elif dt == 0x09: # NOP2
            bs.get_byte()
            stream_len = 2
        elif dt == 0x0a: # NOP3
            bs.get_byte()
            bs.get_byte()
            stream_len = 3
        elif dt == 0x0b: # OVL16
            ovf += 0x10000
            stream_len = 1
        elif dt == 0x0c: # FLUX3
            dur  = bs.get_byte() << 8
            dur += bs.get_byte() + ovf
            stream_len = 3
        elif dt == 0x0d: # OOB
            dt   = bs.get_byte()
            siz  = bs.get_word()
            if dt == 0x00: # Invalid
                data = bs.get_variable_len(siz) 
            if dt == 0x01: # StreamInfo
                data = bs.get_variable_len(siz) 
            if dt == 0x02: # Index
                stream_position = bs.get_dword()
                sample_counter  = bs.get_dword()
                index_counter   = bs.get_dword()
                index_data.append((stream_position, sample_counter, index_counter))
                """
                print(index_data[-1])
                if len(index_data)>1:
                    print(index_data[-1][0]-index_data[-2][0],
                          index_data[-1][1]-index_data[-2][1],
                          index_data[-1][2]-index_data[-2][2]) 
                """
                if len(index_data)==2:
                    try:
                        spin_time = (index_data[-1][2]-index_data[-2][2]) * (1/ick)
                        rpm = (1/spin_time) * 60
                    except ZeroDivisionError:
                        spin_time = 0
                        rpm = 0
                    print(', {:.2f} RPM'.format(rpm), end='')
                prev_stream_position = stream_position
                prev_sample_counter  = sample_counter
                prev_index_counter   = index_counter
            if dt == 0x03: # StreamEnd
                data = bs.get_variable_len(siz) 
            if dt == 0x04: #KFInfo
                data = bs.get_variable_len(siz) 
                string = bytearray(data).decode('UTF-8')
                string = string.translate(str.maketrans({' ':'', '\0':'', '\n':''}))
                params = string.split(',')
                for param in params:
                    if ('sck' in param):
                        sck = eval(param.split('=')[1])
                    if ('ick' in param):
                        ick = eval(param.split('=')[1])
                if sck!=0 and ick!=0:
                    print(', SCK={:.2f}MHz, ICK={:.2f}MHz'.format(sck/1e6, ick/1e6), end='')
            if dt == 0x0d: # EOF
                data = bs.get_variable_len(siz) 
                break

        if dur != 0:
            stream.append(dur)
            stream_pos.append(pos)
            pos += stream_len
            dur = 0
            ovf = 0

    print()
    return stream, stream_pos, index_data, sck


def get_track(stream, stream_pos, index):
    result = []
    if len(index)<2:
        return []
    index1 = index[-2][0] # stream_position
    index2 = index[-1][0]
    for s, pos in zip(stream, stream_pos):
        if pos>index1 and pos<index2:
            result.append(s)
    return result


def encode(stream, f):
    count = 0
    for s in stream:
        if s <= ord('z')-ord(' '):
            if count % 100==0:
                f.write('~')
            f.write(chr(s + ord(' ')))
            if count % 100==99:
                f.write('\n')
            count += 1


def main(args):
    # Get all 'raw' files and sort them
    dir_name = args.input
    files = glob.glob(dir_name+'/*.raw')
    files.sort()
    dirs = os.path.split(dir_name)
    base_dir = dirs[-1]

    fdshield_clk = args.clk_spd   # Clock speed of FD-Shield (default: 4MHz)

    out_file = base_dir + '.log'
    print(os.path.join(args.input, '*.raw'), '->', out_file)
    with open(out_file, 'w') as f:
        count = 0
        # Process all raw files in the directory
        for file in files:
            m = [ int(s) for s in re.findall(r'track(\d+)\.(\d)\.raw', file)[0] ]
            print('track {} {}  '.format(*m), end='', flush=True)
            f.write('**TRACK_READ {} {}\n'.format(*m))
            stream, stream_pos, index, sck = decode_track(file)     # parse KryoFlux raw stream data
            track = get_track(stream, stream_pos, index)            # Kryoflux stream buffer may contain track data for multiple spins. Extract the data of exact 1 track
            scale = sck / fdshield_clk
            track = [ int(s/scale) for s in track ]                 # Downsample
            encode(track, f)                                        # Output encoded stream data
            f.write('**TRACK_END\n')
            count += 1


if __name__ == '__main__':
    print('** FryoFlux RAW stream data to FD-Shield bitstream file converter (https://www.kryoflux.com/)')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='Directory name which contains input KryoFlux RAW bitstream files')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='clock speed for down-sampling (default=4MHz=4000000)')
    args = parser.parse_args()
    main(args)
