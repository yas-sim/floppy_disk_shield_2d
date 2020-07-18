import os
from floppy_shield import *

# Test code for floppy_shield.py


# CRC generation test
"""
# FE 01 01 03 01 DD EA
crc = CCITT_CRC()
crc.reset()
data=[0xfe, 0x01, 0x01, 0x03, 0x01, 0xdd, 0xea]
crc.data(data[:])
print(format(crc.get(), '04X'))
"""

image_name = 'putty/fb30.log'
base, ext = os.path.splitext(image_name)

# read a bitstream file
#"""
bs = bitstream()
bs.open(image_name)
#bs.display_histogram(1,0)
#"""

# decode all tracks in an image
"""
disk = []
for track_id in bs.disk:
    track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(bs.disk[track_id], clk_spd=4e6, high_gain=0., low_gain=0., log_level=0)
    print(sec_read, sec_err)
    disk.append(track)
"""

# track data dump
#"""
track_id = '0-0'
track, mfm_buf, mc_buf, sec_read, sec_err = decodeFormat(bs.disk[track_id], clk_spd=4e6, high_gain=0., low_gain=0., log_level=1)
dumpMFM(mfm_buf, mc_buf)
#"""

# display pritable characters in a track
"""
for track in disk:
    for sect in track:
        for c in sect[2]:
            if c>=ord(' ') and c<=ord('z'):
                print(chr(c), end='')
"""

# D77 disk image generation
"""
d77 = d77_image()
img = d77.generate(disk)
with open(base+'.d77', 'wb') as f:
    f.write(img)
"""
