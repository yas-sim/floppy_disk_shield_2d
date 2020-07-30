#d77enc.py
# Encode JSON file to D77 Disk image file

import os
import sys
import argparse
import json

from d77lib import *

def decodeObject(dct):
    for key, val in dct.items():
        if isinstance(val, str):
            if val[:2] == '0x':
                trans = [ eval(dt) for dt in val.split(',') ]   # "0x00,0x01,0x02" => b'\00\01\02'
                dct[key] = bytearray(trans)
    return dct


def main(args):
    with open(args.input, 'r') as f:
        d77dic = json.load(f, object_hook=decodeObject)

    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '_.d77'
    else:
        out_name = args.input

    d77img = encode_d77(d77dic)

    with open(out_name, 'wb') as f:
        f.write(d77img)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input D77 image decoded JSON file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output D77 image file path')
    parser.add_argument('--extension', action='store_true', default=False, help='Extract D77mod extension information')

    args = parser.parse_args()

    main(args)
