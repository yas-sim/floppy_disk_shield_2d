# bitstream inspector

import sys
import argparse
import cv2
import numpy as np

import matplotlib.pyplot as plt

from floppylib.bitstream import bitstream
from floppylib.dataseparator import data_separator
from floppylib.formatparserIBM import FormatParserIBM
from floppylib.d77image import d77_image


def pause():
    while True:
        key = cv2.waitKey(1)
        if key == ord(' '):
            return
        if key == 27:
            sys.exit(0)


# MFM decoder for bitstream visualizer
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

    def decode(self, bit, ds):
        while True:
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

# Visualize bitstream timing
def timing_history(bit_stream, spin_spd, args):
    val_max = 64
    ystep=1
    xstep = 4
    cell = 8
    height = 600
    writer = cv2.VideoWriter('history.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (val_max*xstep, height))

    ds = data_separator(bit_stream, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain)
    mfm_decoder = decode_MFM()

    count=0
    img = np.zeros((height, val_max * xstep, 3), dtype=np.uint8)
    while True:
        bit = ds.get_bit()
        mfm, mc = mfm_decoder.decode(bit, ds)
        if mfm != -1:
            color = (255,255,255) if mc==False else (0,255,255)
            cv2.putText(img, format(mfm, '02x'), (10, height), cv2.FONT_HERSHEY_PLAIN, 1, color, 1)
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
                img[-1, int(j * cell * xstep), :] = [ 0, 0, 255 ]       # current cell position line
                #img[-1, int(j *    8 * xstep), :] = [ 0, 255, 255 ]    # standard cell position line
            for j in range(1,4+1):
                img[-1, int((j+0.5) * cell * xstep), :] = [ 255, 0, 0 ] # cell limit line
        dataPos = min(interval * xstep, img.shape[1]-1)
        img[-1, dataPos, : ] = [ 255, 255, 255]                # data point


def histogram(bit_stream):
    interval_buf = []
    dist = 0
    for bit in bit_stream:
        if bit == 0:
            dist += 1
        else:
            interval_buf.append(dist)
            dist = 0

    fig = plt.figure(figsize=(8,4), dpi=200)
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)

    ax1.set_title('linear-scale')
    ax1.set_xlabel('count')
    ax1.set_ylabel('frequency')
    ax1.set_xlim(0,80)
    ax1.grid(True)
    ax1.hist(interval_buf, bins=80, range=(0,80), histtype='stepfilled', orientation='vertical', log=False)

    ax2.set_title('log-scale')
    ax2.set_xlabel('count')
    ax2.set_ylabel('frequency')
    ax2.set_xlim(0,80)
    ax2.grid(True)
    ax2.hist(interval_buf, bins=80, range=(0,80), histtype='stepfilled', orientation='vertical', log=True)

    plt.show()

def mfm_dump(bit_stream, spin_spd, args):
    parser = FormatParserIBM(bit_stream, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    mfm_buf, mc_buf = parser.read_track()
    print('{} (0x{:x}) bytes read'.format(len(mfm_buf), len(mfm_buf)))
    parser.dumpMFM16(mfm_buf, mc_buf)

#   id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]  
def id_dump(interval, spin_spd, args):
    parser = FormatParserIBM(interval, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    id_buf = parser.search_all_idam(abort_by_idxmark=args.abort_index, abort_by_sameid=args.abort_id)
    print(' # : (C ,H ,R ,N ) ID-CRC CRC-val')
    for i, idam in enumerate(id_buf):
        print('{:2} : ({:02x},{:02x},{:02x},{:02x}) {}    0x{:04x}'.format(i+1, idam[0], idam[1], idam[2], idam[3], 'OK ' if idam[6] else 'ERR', (idam[4]<<8)+idam[5]))

def generate_key(track):
    trk = track // 2
    sid = track %  2
    key = '{}-{}'.format(trk, sid)
    return key

def read_sectors(interval, spin_spd, args):
    # track = [[id_field, Data-CRC status, sect_data, DAM],...]
    #                            id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
    parser = FormatParserIBM(interval, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    track, sec_read, sec_err = parser.read_all_sectors(abort_by_idxmark=args.abort_index, abort_by_sameid=args.abort_id)
    print(' # : (C ,H ,R ,N ) ID-CRC DT-CRC AM    MFM-POS')
    for i, sect in enumerate(track):
        idam = sect[0]
        print('{:2} : ({:02x},{:02x},{:02x},{:02x}) {:6} {:6} {} 0x{:04x}'.format(i+1, 
            idam[0], idam[1], idam[2], idam[3], 
            'OK '   if idam[6] else 'ERR',
            'OK '   if sect[1] else 'ERR',
            'DAM  ' if sect[3] else 'DDAM ',
            idam[8]))
    print('OK={}, Error={}'.format(sec_read, sec_err))

def ascii_dump(bit_stream, spin_spd, args):
    # track = [[id_field, Data-CRC status, sect_data, DAM],...]
    #                            id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
    parser = FormatParserIBM(bit_stream, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
    track, sec_read, sec_err = parser.read_all_sectors(abort_by_idxmark=args.abort_index, abort_by_sameid=args.abort_id)
    for i, sect in enumerate(track):
        idam = sect[0]
        print(' # : (C ,H ,R ,N ) ID-CRC DT-CRC AM    MFM-POS')
        print('{:2} : ({:02x},{:02x},{:02x},{:02x}) {:6} {:6} {} 0x{:04x}'.format(i+1, 
            idam[0], idam[1], idam[2], idam[3], 
            'OK '   if idam[6] else 'ERR',
            'OK '   if sect[1] else 'ERR',
            'DAM  ' if sect[3] else 'DDAM ',
            idam[8]))
        for dt in sect[2]:
            if dt>=0x20 and dt<=0x7e:
                print(chr(dt), end='', flush=True)
        print()

def main(args):
    bs = bitstream()
    bs.open(args.input)
    spin_speed = bs.spin_spd    # spin speed (ms)  300rpm == 200ms

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
        bit_stream = bs.disk[key]

        if args.history:
            timing_history(bit_stream, spin_speed, args)
        if args.histogram:
            histogram(bit_stream)
        if args.mfm_dump:
            mfm_dump(bit_stream, spin_speed, args)
        if args.id_dump:
            id_dump(bit_stream, spin_speed, args)
        if args.read_sectors:
            read_sectors(bit_stream, spin_speed, args)
        if args.ascii_dump:
            ascii_dump(bit_stream, spin_speed, args)


if __name__ == '__main__':
    print('** Floppy data capture shield - bit stream data inspect tool')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-t', '--track', required=True, help='track number. single number or a tuple (start,end) (track # should be 0-83 for 2D, 0-163 for 2DD)')
    parser.add_argument('--high_gain', type=float, required=False, default=0, help='data separator gain for high-speed tracking mode (default: 0, recommend: 0~0.4)')
    parser.add_argument('--low_gain', type=float, required=False, default=0, help='data separator gain for low-speed tracking mode (default: 0, recommend: 0~high_gain)')
    parser.add_argument('--log_level', type=int, required=False, default=0, choices=(0,1,2) ,help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    parser.add_argument('--histogram', action='store_true', default=False, help='display histogram of the pulse interval buffer')
    parser.add_argument('--history', action='store_true', default=False, help='display history graph of the pulse interval buffer')
    parser.add_argument('--mfm_dump', action='store_true', default=False, help='display MFM decoded data in HEX dump style')
    parser.add_argument('--ascii_dump', action='store_true', default=False, help='display printable data in the sectors')
    parser.add_argument('--id_dump', action='store_true', default=False, help='display decoded all ID address marks in the track')
    parser.add_argument('--read_sectors', action='store_true', default=False, help='read all sectors in the track and display result')
    parser.add_argument('--abort_index', action='store_true', default=False, help='abort ID reading on 2nd index mark detection')
    parser.add_argument('--abort_id', action='store_true', default=False, help='abort ID reading on 2nd identical ID detection')
    args = parser.parse_args()
    main(args)
