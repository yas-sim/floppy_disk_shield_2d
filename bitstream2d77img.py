import os

import argparse

from floppy_shield import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output D77 image path')
    #parser.add_argument('--case_sensitive', action='store_true', default=False, help='case sensitive on layer search')
    args = parser.parse_args()

    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '.d77'
    else:
        out_name = args.input

    # read a bitstream file
    bs = bitstream()
    bs.open(args.input)
    #bs.display_histogram(1,0)

    disk = []
    for track_id in bs.disk:
        track_data = bs.disk[track_id]     # pulse interval buffer
        track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(track_data, clk_spd=4e6, high_gain=0., low_gain=0., log_level=0)
        print(track_id, sec_read, sec_err)
        disk.append(track)

    # D77 disk image generation
    d77 = d77_image()
    img = d77.generate(disk)
    with open(out_name, 'wb') as f:
        f.write(img)


if __name__ == "__main__":
    main()
