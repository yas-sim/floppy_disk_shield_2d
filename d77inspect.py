# d77 inspectate utility

import argparse

from d77lib import *

def main(args):
    with open(args.input, 'rb') as f:
        img = f.read()
    d77 = decode_d77(img)

    # Display results
    print('Header:', d77['header'])

    t = eval(args.track)
    if type(t) is tuple:
        start = t[0]
        end   = t[1]
    else:
        start = t
        end   = t

    disk = d77['disk']
    for trkid in range(start, end+1):
        key = trkid
        track = disk[key]
        print(trkid)
        print('#   C  H  R  N    S1 S2   AM   SIZE ICRC POS')
        for i, sect in enumerate(track):
            c,h,r,n = sect['CHRN'].split(':')
            status = sect['status']
            size = sect['size']
            am = 'DDAM' if sect['am']==0x10 else 'DAM '
            pos = sect['pos']
            ext_sta = sect['ext_sta']
            id_crc = sect['id_crc_val']  # id crc value
            print('{:03} {:02x} {:02x} {:02x} {:02x} - {:02x} {:02x} - {:4} {:4} {:04x} {:04x}'.format(i,
                                                int(c),int(h),int(r),int(n),
                                                ext_sta, status, am, size, id_crc, pos))
            #print('density', sect['density'])
            #print('num_sec', sect['num_sec'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input bitstream file path')
    parser.add_argument('-t', '--track', required=True, help='track number. single number or a tuple (start,end) (track # should be 0-83 for 2D, 0-163 for 2DD)')
    args = parser.parse_args()
    main(args)
