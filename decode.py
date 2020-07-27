# Find the best high-gain and low-gain value for a FD bitstream data
# 
# This program uses Monte-Carlo optimization method to find the optimal value
# You can visualize the result in 3D scatter plot with 'result_viewer.py'

import argparse

from floppy_shield import *

def dumpIDAM(id_buf):
    for idam in id_buf:
        print('{:02x} {:02x} {:02x} {:02x} {}'.format(idam[0], idam[1], idam[2], idam[3], 'OK' if idam[4] else 'ER'))

def main(args):
    bs = bitstream(args.input)

    #with open(args.output, 'a') as f:
    total_sector = 0
    total_error  = 0
    for track_id in bs.disk:
        trk, sid = track_id.split('-')
        print('**TRACK ', trk, sid)
        track_data = bs.disk[track_id]     # pulse interval buffer
        #mfm_buf, mc_buf = read_track(track_data, high_gain=args.high_gain, low_gain=args.low_gain, log_level=0)
        #dumpMFM(mfm_buf, mc_buf)
        id_buf = search_all_idam(track_data, high_gain=args.high_gain, low_gain=args.low_gain, log_level=0)
        for sect in id_buf:
            status, crc, data, dam = read_sector(track_data, sect[2], high_gain=args.high_gain, low_gain=args.low_gain, log_level=0)
            dump_list_hex(data)
        dumpIDAM(id_buf)
        print('')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-o', '--output', type=str, required=False, default='log.txt', help='optimizer output log file path. output will be appended if the log file is already existing (default=log.txt)')
    parser.add_argument('--high_gain', type=float, required=False, default=0.0, help='high gain range (default = 0.0)')
    parser.add_argument('--low_gain', type=float, required=False, default=0.0, help='low gain range (default = 0.0)')
    parser.add_argument('--montecarlo', action='store_true', default=False, help='run Monte Carlo optimization to find the best parameter for high_gain and low_gain')
    args = parser.parse_args()
    main(args)
