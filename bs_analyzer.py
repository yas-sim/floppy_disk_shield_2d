# bitstream analyzer

import sys
import argparse
import cv2
import numpy as np

import matplotlib.pyplot as plt

from floppy_shield import *

def pause():
    while True:
        key = cv2.waitKey(1)
        if key == ord(' '):
            return
        if key == 27:
            sys.exit(0)


class decode_MFM:
    def __init__(self):
        self.data           = 0
        self.read_bit_count = 0   # read bit count
        self.cd_stream      = 0
        self.mode           = 0
        missing_clock_c2 = (0x5224)  #  [0,1,0,1, 0,0,1,0, 0,0,1,0, 0,1,0,0]
        missing_clock_a1 = (0x4489)  #  [0,1,0,0, 0,1,0,0, 1,0,0,0, 1,0,0,1]
        pattern_ff       = (0x5555555555555555)  # for 4 bytes of sync data (unused)
        pattern_00       = (0xaaaaaaaaaaaaaaaa)  # for 4 bytes of sync data
        self.missing_clock = [ missing_clock_c2, missing_clock_a1 ]
        #self.sync_pattern  = [ pattern_ff, pattern_00 ]
        self.sync_pattern  = [ pattern_00 ]
        self.bitstream     = []

    def decode(self, interval, ds):
        if interval == 2:
            self.bitstream += [0,1]
        if interval == 3:
            self.bitstream += [0,0,1]
        if interval == 4:
            self.bitstream += [0,0,0,1]
        while True:
            if len(self.bitstream)==0:
                return -1, False
            bit = self.bitstream.pop(0)
            if self.read_bit_count % 2 == 1:
                self.data = (self.data<<1) | bit   # stores only data bits (skip clock bits)
            self.read_bit_count += 1

            self.cd_stream = ((self.cd_stream<<1) | bit) & 0xffffffffffffffff
            if self.mode == 0 and ((self.cd_stream & 0x7fff) in self.missing_clock):
                data = self.data
                self.data = 0
                self.read_bit_count = 0
                return data, True        # missing clock detected

            if self.mode == 0 and (self.cd_stream in self.sync_pattern):
                ds.switch_gain(1)      # Fast tracking mode to get syncronized with SYNC pattern
                self.read_bit_count &= ~1     # C/D synchronize
            else:
                ds.switch_gain(0)

            if self.read_bit_count >= 16:
                data = self.data
                self.data = 0
                self.read_bit_count = 0
                return data, False       # 8 bit data read completed

def timing_history(interval_buf, args):
    val_max = 64
    ystep=1
    xstep = 4
    cell = 8
    height = 400
    writer = cv2.VideoWriter('history.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (val_max*xstep, height))

    ds = data_separator(interval_buf, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain)
    mfm_decoder = decode_MFM()

    count=0
    img = np.zeros((height, val_max * xstep, 3), dtype=np.uint8)
    while True:
        quant_interval, interval = ds.get_quantized_interval()
        count+=1
        mfm, mc = mfm_decoder.decode(quant_interval, ds)
        if mfm != -1:
            cv2.putText(img, format(mfm, '02x'), (10, height), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)
        if count % 1==0:
            cell = ds.cell_size
            writer.write(img)
            cv2.imshow('history', img)
            key = cv2.waitKey(1)
            if key == 27:
                break
            if key == ord(' '):
                pause()
            img[:-2, :, :] = img[2:, :, :]  # scroll up
            img[-2:, :, :] = [0,0,0]
            for j in range(2,4+1):
                img[-1, int(j * cell * xstep), :] = [ 0, 0, 255 ]
            for j in range(1,4+1):
                img[-1, int((j+0.5) * cell * xstep), :] = [ 255, 0, 0 ]
        img[-1, interval * xstep, : ] = [ 255, 255, 255]


def histogram(interval_buf):
    #fig = plt.figure(figsize=(8,4), dpi=200)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)

    ax1.set_title('linear-scale')
    ax1.set_xlabel('count')
    ax1.set_ylabel('frequency')
    ax1.set_xlim(0,80)
    ax1.grid(True)
    ax1.hist(interval_buf, bins=100, range=(0,100), histtype='stepfilled', orientation='vertical', log=False)

    ax2.set_title('log-scale')
    ax2.set_xlabel('count')
    ax2.set_ylabel('frequency')
    ax2.set_xlim(0,80)
    ax2.grid(True)
    ax2.hist(interval_buf, bins=100, range=(0,100), histtype='stepfilled', orientation='vertical', log=True)

    plt.show()

def mfm_dump(interval, args):
    mfm_buf, mc_buf = read_track(interval, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    print('{} (0x{:x}) bytes read'.format(len(mfm_buf), len(mfm_buf)))
    dumpMFM(mfm_buf, mc_buf)

#      id_buf : [ [C,H,R,N, CRC flag, pos], ...]  
def id_dump(interval, args):
    """
    print(' # : (C ,H ,R ,N ) STA MFM-POS')
    id_buf = search_all_idam(interval, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    for i, idam in enumerate(id_buf):
        print('{:2} : ({:02x},{:02x},{:02x},{:02x}) {} 0x{:04x}'.format(i+1, idam[0], idam[1], idam[2], idam[3], 'OK ' if idam[4] else 'ERR', idam[6]))
    """
    track, sec_read, sec_err = read_all_sectors(interval, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    print(' # : (C ,H ,R ,N ) ID-CRC AM    MFM-POS')
    for i, sect in enumerate(track):
        idam = sect[0]
        print('{:2} : ({:02x},{:02x},{:02x},{:02x}) {:6} {} 0x{:04x}'.format(i+1, idam[0], idam[1], idam[2], idam[3], 'OK ' if idam[6] else 'ERR', 'DAM  ' if sect[3] else 'DDAM ', idam[8]))
        # track = [[id_field, CRC status, sect_data, DAM],...]
        #                            id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]


def generate_key(track):
    trk = track // 2
    sid = track %  2
    key = '{}-{}'.format(trk, sid)
    return key


def main(args):
    bs = bitstream()
    bs.open(args.input)

    t = eval(args.track)
    if type(t) is tuple:
        start = t[0]
        end   = t[1]
    else:
        start = t
        end   = t

    for track in range(start, end+1):
        print('** TRACK ', track)
        key = generate_key(track)
        interval_buf = bs.disk[key]

        if args.history:
            timing_history(interval_buf, args)
        if args.histogram:
            histogram(interval_buf)
        if args.mfm_dump:
            mfm_dump(interval_buf, args)
        if args.id_dump:
            id_dump(interval_buf, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-t', '--track', required=True, help='track number. single number or a tuple (start,end) (track # should be 0-83 for 2D, 0-163 for 2DD)')
    parser.add_argument('--high_gain', type=float, required=False, default=0.3, help='high-speed data separator gain (default: 0.3)')
    parser.add_argument('--low_gain', type=float, required=False, default=0.125, help='low-speed data separator gain (default: 0.125)')
    parser.add_argument('--log_level', type=int, required=False, default=0, choices=(0,1,2) ,help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    parser.add_argument('--histogram', action='store_true', default=False, help='display histogram of the pulse interval buffer')
    parser.add_argument('--history', action='store_true', default=False, help='display history graph of the pulse interval buffer')
    parser.add_argument('--mfm_dump', action='store_true', default=False, help='display MFM decoded data in HEX dump style')
    parser.add_argument('--id_dump', action='store_true', default=False, help='display decoded all ID address marks in the track')
    parser.add_argument('--montecarlo', action='store_true', default=False, help='run Monte Carlo optimization to find the best parameter for high_gain and low_gain')
    args = parser.parse_args()
    main(args)
