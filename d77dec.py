#d77dec.py
# Decode D77 Disk image file into JSON file

import os
import sys
import argparse
import json


from d77lib import *

def byteEncoder(object):
    if isinstance(object, bytes):
        res = ''
        for i, dt in enumerate(object):
            if i != 0:
                res += ','
            res += '0x{:02x}'.format(dt)
        return res

def main(args):
    with open(args.input, 'rb') as f:
        img = f.read()

    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '.json'
    else:
        out_name = args.input
    base, ext = os.path.splitext(out_name)

    # Divide multiple images from a file
    img_array = []
    while True:
        size = get_dword(img, 0x1c)      # D77 image size
        img_array.append(img[:size])
        if len(img) <= size:
            break
        img = img[size:]
    print(len(img_array), 'image data found')

    for idx, img in enumerate(img_array):
        d77dic = decode_d77(img)
        del d77dic['sector_offsets']
        if 'track_offsets' in d77dic.keys():
            del d77dic['track_offsets']
        out_name = '{}_{}{}'.format(base, idx, ext)
        print('generating', out_name)
        with open(out_name, 'w') as f:
            json.dump(d77dic, f, indent=2, default=byteEncoder)

if __name__ == "__main__":
    print('** D77 image to JSON decoder')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input D77 image file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output txt file path')
    parser.add_argument('--extension', action='store_true', default=False, help='Extract D77mod extension information')

    args = parser.parse_args()

    main(args)
