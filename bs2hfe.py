import os
import sys
import argparse

from floppylib.bitstream import bitstream

def set_word(barray:bytearray, pos:int, data:int):
    for i in range(2):
        barray[pos + i] = data & 0xff
        data >>= 8

def set_string(barray:bytearray, pos:int, string:str):
    for i, s in enumerate(string):
        barray[pos + i] = ord(s)

def align(val:int, border:int):
    return int(((val//border)+(1 if (val % border != 0) else 0))*border)

def main(args):
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        out_name = base + '.d77'
    else:
        out_name = args.output

    # read a bitstream file
    bs = bitstream()
    bs.read_dist_buf(args.input)
    spin_speed = bs.spin_spd
    print('Spin speed:', spin_speed*1000, 'ms')

    # Prepare MFM (HFE) quantized track buffer images. (C/D mixed)
    # Note: HFE format is LSB first.
    bit_cell_size = args.clk_spd / 500e3
    byte = 0
    bit_count = 0
    mfm_track_bufs = []
    for track_id, track_data in bs.disk.items():
        #if track_id == '3-0': break                  # FOR DEBUG PURPOSE
        mfm_track_buf = []
        for dist in track_data:
            quantized = int((dist + bit_cell_size / 2) / bit_cell_size)
            for q in range(quantized):
                bit = 1 if q == quantized -1 else 0
                byte |= (bit << bit_count)
                bit_count += 1
                if bit_count == 8:
                    mfm_track_buf.append(byte)
                    byte = 0
                    bit_count = 0
        if bit_count != 0:
            mfm_track_buf.append(byte)
        mfm_track_bufs.append(mfm_track_buf)
    if len(mfm_track_bufs) % 2 == 1:
        mfm_track_bufs.append([])    # add a dummy data to make the number of mfm tracks even

    track_data_offset = 2       # 0x200 unit. startng from 0x400 (==2)
    # Multiplex side 0 and side 1 data to generate HFE track data
    hfe_track_bufs = []
    hfe_track_table = bytearray([0] * 80 * 2)
    hfe_blk_size = 0x100
    offset_list = []
    for track_n in range(len(mfm_track_bufs) // 2):
        mfm_side0 = mfm_track_bufs[track_n * 2    ]
        mfm_side1 = mfm_track_bufs[track_n * 2 + 1]
        hfe_track_buf = bytearray([0] * align(len(mfm_side0) + len(mfm_side1), 0x400))
        blk_id = 0
        src_ptr = 0
        dst_ptr = 0
        while src_ptr < len(mfm_side0) or src_ptr < len(mfm_side1):
            if src_ptr < len(mfm_side0):
                size = hfe_blk_size if src_ptr + hfe_blk_size < len(mfm_side0) else len(mfm_side0) - src_ptr
                hfe_track_buf[dst_ptr:dst_ptr+size+1] = mfm_side0[src_ptr:src_ptr+size+1]
            dst_ptr += hfe_blk_size
            if src_ptr < len(mfm_side1):
                size = hfe_blk_size if src_ptr + hfe_blk_size < len(mfm_side1) else len(mfm_side1) - src_ptr
                hfe_track_buf[dst_ptr:dst_ptr+size+1] = mfm_side1[src_ptr:src_ptr+size+1]
            dst_ptr += hfe_blk_size
            src_ptr += hfe_blk_size
        hfe_track_bufs.append(hfe_track_buf)
        # set track_table
        track_len = len(mfm_side0) + len(mfm_side1)
        set_word(hfe_track_table, track_n * 4    , track_data_offset)
        set_word(hfe_track_table, track_n * 4 + 2, track_len)
        track_data_offset += align(track_len, 0x400) // 0x200     # increase track_data_offset

    # Create the header information
    hfe_header = bytearray([0] * 26)
    set_string(hfe_header, 0, "HXCPICFE")
    hfe_header[8] = 0                         # Revision 0
    hfe_header[9] = len(hfe_track_bufs)       # number of tracks
    hfe_header[10] = 2                        # number of valid side
    hfe_header[11] = 0                        # track_encoding 0==IBMPC_DD_FLOPPYMODE
    set_word(hfe_header, 12, 250)             # 250Kbit/sec (MFM, data only rate)
    set_word(hfe_header, 14, 0)               # rpm
    hfe_header[16] = 7                        # floppy interface mode 7==GENERIC_SHUGGART_DD_FLOPPYMODE
    hfe_header[17] = 1                        # dnu
    set_word(hfe_header, 18, 1)               # track list offset (x 0x200)
    hfe_header[20] = 0xff                     # write allowed
    hfe_header[21] = 0xff                     # ff:single step  00:double step mode
    hfe_header[22] = 0xff                     # use an alternate track encoding for track 0 side 0
    hfe_header[23] = 0xff                     # alternate track encoding for track 0 side 0
    hfe_header[24] = 0xff                     # use an alternate track encoding for track 0 side 1
    hfe_header[25] = 0xff                     # alternate track encoding for track 0 side 1

    with open(out_name, 'wb') as f:
        # write the file header
        f.write(hfe_header)

        # write track offset table
        f.seek(0x0200)
        f.write(hfe_track_table)

        # write track data
        for track_n, hfe_track in enumerate(hfe_track_bufs):
            offset = (hfe_track_table[track_n * 4] | (hfe_track_table[track_n * 4 + 1] << 8)) * 0x200
            f.seek(offset)
            f.write(hfe_track)

    print('Conversion completed.')

if __name__ == "__main__":
    print('** Floppy shield bit-stream data to HFE image converter')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image file path')
    parser.add_argument('-o', '--output', type=str, required=False, default=None, help='output D77 image path')
    parser.add_argument('--log_level', type=int, required=False, default=0, help='log level: 0=off, 1=minimum, 2=verbose')
    parser.add_argument('--clk_spd', type=int, required=False, default=4e6, help='FD-shield capture clock speed (default=4MHz=4000000)')
    args = parser.parse_args()

    main(args)
