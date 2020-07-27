# Find the best high-gain and low-gain value for a FD bitstream data
# 
# This program uses Monte-Carlo optimization method to find the optimal value
# You can visualize the result in 3D scatter plot with 'result_viewer.py'

import argparse
import random

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from floppy_shield import *

def main(args):
    high_gain_range = eval(args.high_gain_range)
    low_gain_range =  eval(args.low_gain_range)

    print('High gain = {}, Low gain = {}'.format(high_gain_range, low_gain_range))

    bs = bitstream(args.input)

    x = []
    y = []
    z = []
    best_sector = 0
    best_error = 99999999
    with open(args.output, 'a') as f:
        str = 'High       Low        Read Error'
        print(str)
        f.write(str+'\n')
        f.flush()

        for i in range(args.iter):
            total_sector = 0
            total_error  = 0
            hg = random.uniform(0, 0.08)
            lg = random.uniform(0, hg) 
            for track_id in bs.disk:
                track_data = bs.disk[track_id]     # pulse interval buffer
                track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(track_data, high_gain=hg, low_gain=lg, log_level=0)

                trk, sid = track_id.split('-')
                total_sector += sec_read
                total_error  += sec_err

            x.append(hg)
            y.append(lg)
            z.append(total_error)

            updated = False
            if total_sector > best_sector:
                best_sector = total_sector
                updated = True
            if total_error < best_error:
                best_error = total_error
                updated = True
            str = '{:10.8f} {:10.8f} {:04} {:04} {}'.format(hg, lg, total_sector, total_error, '*' if updated else ' ')
            print(str)
            f.write(str+'\n')
            f.flush()

        """
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.set_xlabel('high gain')
        ax.set_ylabel('low_gain')
        ax.plot(x, y, z, marker='o', linestyle='None')
        plt.show()
        """

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-o', '--output', type=str, required=False, default='log.txt', help='optimizer output log file path. output will be appended if the log file is already existing (default=log.txt)')
    parser.add_argument('--high_gain_range', type=str, required=False, default='(0., 0.4)', help='high gain range (default = (0, 0.4))')
    parser.add_argument('--low_gain_range', type=str, required=False, default='(0., 0.4)', help='low gain range (default = (0, 0.4))')
    parser.add_argument('--iter', type=int, default=1000, required=False, help='number of iteration (default=1000)')
    args = parser.parse_args()
    main(args)
