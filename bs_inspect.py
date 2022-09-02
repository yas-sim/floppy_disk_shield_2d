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
        if self.read_bit_count % 2 == 1:
            self.data = (self.data<<1) | bit   # stores only data bits (skip clock bits)
        self.read_bit_count += 1

        self.cd_stream = ((self.cd_stream<<1) | bit) & 0xffffffffffffffff
        if self.mode == 0 and (self.read_bit_count & 1) == 0 and ((self.cd_stream & 0x7fff) in self.missing_clock):  # Ignore MC compare on clock cycle
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
        return -1, False             # read data incomplete



# Visualize bitstream timing
def timing_history(bit_stream, spin_spd, args):
    val_max = 24
    ystep = 1
    xstep = 8
    cell = 8
    height = 400
    graph_x_ofst = 8
    writer = cv2.VideoWriter('history.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 240, ((graph_x_ofst+val_max)*xstep, height))

    ds = data_separator(bit_stream, clk_spd=args.clk_spd, spin_spd=spin_spd, high_gain=args.high_gain, low_gain=args.low_gain)
    mfm_decoder = decode_MFM()

    count=0
    img = np.zeros((height, (graph_x_ofst+val_max) * xstep, 3), dtype=np.uint8)
    bit_sts = 0
    draw = 0
    while True:
        bit, pos, advance = ds.get_bit_ex()
        bit_sts |= bit          # accumlate bit status in the same cell
        if advance:
            mfm, mc = mfm_decoder.decode(bit_sts, ds)
            if mfm != -1:
                color = (255,255,255) if mc==False else (0,255,255)
                cv2.putText(img, format(mfm, '02x'), (10, height), cv2.FONT_HERSHEY_PLAIN, 1, color, 1)
            if bit_sts == 1:
                draw = 1
            bit_sts = 0

        if count % 1==0:
            cell_size = ds.vfo.cell_size
            window_start = ds.vfo.window_ofst
            window_end   = ds.vfo.window_ofst + ds.vfo.window_size
            img[:-ystep, :, :] = img[ystep:, :, :]  # scroll up
            img[-ystep:, :, :] = [64,0,0]
            img[-1, int((graph_x_ofst               )*xstep):int((graph_x_ofst + cell_size) *xstep), :] = [0,0,128]
            img[-1, int((graph_x_ofst + window_start)*xstep):int((graph_x_ofst + window_end)*xstep), :] = [255,0,0]
        pos = int((graph_x_ofst + pos)*xstep)
        dataPos = min(pos, img.shape[1]-1)
        if draw == 1:
            img[-1, dataPos:dataPos+xstep, : ] = [ 255, 255, 255]                # data point
            draw = 0
        
        writer.write(img)
        cv2.imshow('history', img)
        key = cv2.waitKey(1)
        if key == 27:
            writer.release()
            break
        if key == ord(' '):
            pause()



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



def pulse_pitch_variation(bit_stream, sampling_rate, bit_rate):
    pulse_pitch = []
    bit_cell_ref = sampling_rate / bit_rate
    avg_bit_cell = bit_cell_ref
    ring_buf = [ bit_cell_ref for _ in range(32) ]
    ring_ptr = 0
    dist = 0
    for bit in bit_stream:
        dist += 1
        if bit == 0:
            pulse_pitch.append(avg_bit_cell)
        else:
            quantized = int((dist / bit_cell_ref) + 0.5)
            if quantized == 0:
                quantized = 0.1

            ring_buf[ring_ptr] = dist / quantized
            ring_ptr += 1
            if ring_ptr >= len(ring_buf):
                ring_ptr = 0
            avg_bit_cell = sum(ring_buf) / len(ring_buf)

            pulse_pitch.append(avg_bit_cell)
            dist = 0

    x_axis = [ i for i in range(len(pulse_pitch)) ]

    fig = plt.figure(figsize=(8,4), dpi=200)
    ax1 = fig.add_subplot(1,1,1)

    ax1.set_title('bit_cell pitch variation')
    ax1.set_xlabel('bit cell count')
    ax1.set_ylabel('bit cell pitch')
    ax1.set_ylim(0, 12)
    ax1.grid(True)
    ax1.plot(x_axis, pulse_pitch)
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
        if args.pulse_pitch:
            pulse_pitch_variation(bit_stream, 4e6, 500e3)


if __name__ == '__main__':
    print('** Floppy data capture shield - bit stream data inspect tool')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-t', '--track', required=True, help='track number. single number or a tuple (start,end) (track # should be 0-83 for 2D, 0-163 for 2DD)')
    parser.add_argument('--high_gain', type=float, required=False, default=1, help='data separator gain for high-speed tracking mode (default: 1)')
    parser.add_argument('--low_gain', type=float, required=False, default=1, help='data separator gain for low-speed tracking mode (default: 1)')
    parser.add_argument('--log_level', type=int, required=False, default=0, choices=(0,1,2) ,help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    parser.add_argument('--histogram', action='store_true', default=False, help='display histogram of the pulse interval buffer')
    parser.add_argument('--pulse_pitch', action='store_true', default=False, help='display pulse pitch variation in a track')
    parser.add_argument('--history', action='store_true', default=False, help='display history graph of the pulse interval buffer')
    parser.add_argument('--mfm_dump', action='store_true', default=False, help='display MFM decoded data in HEX dump style')
    parser.add_argument('--ascii_dump', action='store_true', default=False, help='display printable data in the sectors')
    parser.add_argument('--id_dump', action='store_true', default=False, help='display decoded all ID address marks in the track')
    parser.add_argument('--read_sectors', action='store_true', default=False, help='read all sectors in the track and display result')
    parser.add_argument('--abort_index', action='store_true', default=False, help='abort ID reading on 2nd index mark detection')
    parser.add_argument('--abort_id', action='store_true', default=False, help='abort ID reading on 2nd identical ID detection')
    args = parser.parse_args()
    main(args)
