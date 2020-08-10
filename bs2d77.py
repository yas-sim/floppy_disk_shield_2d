import os
import sys
import argparse

from floppylib import *

def main(args):
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '.d77'
    else:
        out_name = args.input

    # read a bitstream file
    bs = bitstream()
    bs.open(args.input)
    spin_speed = bs.spin_spd
    print('Spin speed:', spin_speed*1000, 'ms')

    disk = []  # contains all track data
    mfm  = []  # decoded mfm data buffer
    mc   = []  # missing clock buffer

    ttl_read = 0   # Total count of successfully read sectors
    ttl_err  = 0   # Total count of error sectors
    ttl_trk  = 0   # Total count of tracks

    count = 0
    # Find all IDs and read sectors for all tracks
    for track_id in bs.disk:
        ttl_trk += 1
        track_data = bs.disk[track_id]     # pulse interval buffer

        # track = [[id_field, Data-CRC status, sect_data, DAM],...]
        #                            id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
        track, sec_read, sec_err = read_all_sectors(
                    track_data, 
                    clk_spd=args.clk_spd, 
                    spin_spd=spin_speed, 
                    high_gain=args.high_gain, 
                    low_gain=args.low_gain, 
                    log_level=args.log_level,
                    abort_by_idxmark=args.abort_index, 
                    abort_by_sameid=args.abort_id)
        ttl_read += sec_read
        ttl_err  += sec_err

        disk.append(track)
        
        mfm_buf, mc_buf = read_track(
                    track_data, 
                    clk_spd=args.clk_spd, 
                    spin_spd=spin_speed, 
                    high_gain=args.high_gain, 
                    low_gain=args.low_gain, 
                    log_level=args.log_level)
        mfm.append(mfm_buf)
        mc.append(mc_buf)

        trk, sid = track_id.split('-')
        print('{:03} {:02}/{:02}   '.format(int(trk)*2+int(sid), sec_read, sec_err), end='', flush=True)
        if count == 5 or args.log_level>0:
            count = 0
            print()
        else:
            count += 1
    if count!=0:
        print()

    # Identify disk type (2D / 2DD) 
    num_track = len(disk)
    if num_track > 84:
        disk_type = 0x10  # 2DD
    else:
        disk_type = 0     # 2D

    # D77 disk image generation
    d77 = d77_image()
    img = d77.generate(disk, mfm_data=mfm, mc_data=None, disk_type=disk_type)
    with open(out_name, 'wb') as f:
        f.write(img)

    print('{:5} sectors read (no error)'.format(ttl_read))
    print('{:5} error sectors'.format(ttl_err))
    print('{} sectors in a track (average)'.format((ttl_read + ttl_err) / ttl_trk))



if __name__ == "__main__":
    print('** Floppy shield bit-stream data to D77 image converter')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output D77 image path')
    parser.add_argument('--high_gain', type=float, required=False, default=0, help='high-speed data separator gain (default: 0, recommend: 0~0.4)')
    parser.add_argument('--low_gain', type=float, required=False, default=0, help='low-speed data separator gain (default: 0, recommend: 0~high_gain)')
    parser.add_argument('--log_level', type=int, required=False, default=0, help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    parser.add_argument('--abort_index', action='store_true', default=False, help='abort ID reading on 2nd index mark detection (Default=False)')
    parser.add_argument('--abort_id', action='store_true', default=False, help='abort ID reading on 2nd identical ID detection (Default=True)')    
    args = parser.parse_args()

    main(args)
