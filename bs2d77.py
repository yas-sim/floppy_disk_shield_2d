import os
import argparse

from floppy_shield import *

def main(args):
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '.d77'
    else:
        out_name = args.input

    # read a bitstream file
    bs = bitstream()
    bs.open(args.input)

    disk = []  # contains all track data
    mfm = []   # decoded mfm data buffer
    mc = []    # missing clock buffer

    count = 0
    # Find all IDs and read sectors for all tracks
    for track_id in bs.disk:
        track_data = bs.disk[track_id]     # pulse interval buffer

        # track = [[id_field, Data-CRC status, sect_data, DAM],...]
        #                            id_field = [ C, H, R, N, ID-CRC status, ds_pos, mfm_pos]
        track, sec_read, sec_err = read_all_sectors(track_data, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
        disk.append(track)
        mfm_buf, mc_buf = read_track(track_data, clk_spd=args.clk_spd, high_gain=args.high_gain, low_gain=args.low_gain, log_level=args.log_level)
        mfm.append(mfm_buf)
        mc.append(mc_buf)

        trk, sid = track_id.split('-')
        print('{:03}-{:02} {:02}/{:02}   '.format(int(trk), int(sid), sec_read, sec_err), end='', flush=True)
        if count == 4 or args.log_level>0:
            count = 0
            print('')
        else:
            count += 1

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output D77 image path')
    parser.add_argument('--high_gain', type=float, required=False, default=0.3, help='high-speed data separator gain (default: 0.3)')
    parser.add_argument('--low_gain', type=float, required=False, default=0.125, help='low-speed data separator gain (default: 0.125)')
    parser.add_argument('--log_level', type=int, required=False, default=0, help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    args = parser.parse_args()

    main(args)
