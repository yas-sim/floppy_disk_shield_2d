# 
import os
import argparse
import random

from floppy_shield import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image file path')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    parser.add_argument('--iter', type=int, required=False, default=100, help='number of iterations for optimization try')
    args = parser.parse_args()

    # read a bitstream file
    bs = bitstream()
    bs.open(args.input)
    #bs.display_histogram(1,0)

    best_sector = 0
    best_error = 99999999
    for i in range(args.iter):
        total_sector = 0
        total_error  = 0
        for track_id in bs.disk:
            track_data = bs.disk[track_id]     # pulse interval buffer
            high_gain = random.uniform(0, 0.5)
            low_gain  = random.uniform(0, high_gain)
            track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(track_data, clk_spd=args.clk_spd, high_gain=high_gain, low_gain=low_gain, log_level=0)
            
            trk, sid = track_id.split('-')
            total_sector += sec_read
            total_error  += sec_err
        
        report = False
        if total_sector > best_sector:
            best_sector = total_sector
            report = True
        if total_error < best_error:
            best_error = total_error
            report = True
        if report == True:
            print('high={:10.8f} low={:10.8f} read={:04} error={:04}'.format(high_gain, low_gain, total_sector, total_error))

if __name__ == "__main__":
    main()
