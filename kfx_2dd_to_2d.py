# KryoFlux stream files (*.raw images) culling tool (80 track -> 40 track / 2DD->2D)
# Remove odd tracks, rename even tracks (track number will be half)

import os, sys
import glob
import re

def split_track_side(file_name):
    m = re.match(r'.*track([0-9]+)\.([01])', file_name)
    track = int(m.groups()[0])
    side  = int(m.groups()[1])
    return track, side

dir_name = sys.argv[1]
dir_name = os.path.join(dir_name, '**', '*.raw')

track_files = glob.glob(dir_name, recursive=True)

num_files = len(track_files)
if num_files == 0:
    print('No image file detected.')
    sys.exit(0)

track_files.sort()
max_track, _ = split_track_side(track_files[-1])
if max_track < 80:
    print(f'Max track number is below 80 ({max_track}). Aborted.')
    sys.exit(0)

for track_file in track_files:
    path, file_name = os.path.split(track_file)
    track, side = split_track_side(track_file)
    if track % 2 == 0:
        new_track = track // 2
        new_file = f'track{new_track:02d}.{side}.raw'
        new_file = os.path.join(path, new_file)
        if track_file == new_file:
            continue
        if os.path.exists(new_file):
            print('remove ', new_file)
            os.remove(new_file)
        print(track_file, '->', new_file)
        os.rename(track_file, new_file)
    else:
        print('remove ', track_file)
        os.remove(track_file)
