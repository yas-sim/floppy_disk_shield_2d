# capture.py

This program transfers the raw bit stream FD data from the Arduino FD-cautpre shield to the host PC.  

```sh
usage: capture.py [-h] -o OUTPUT [--start_track START_TRACK]
                   [--end_track END_TRACK] [--media_type MEDIA_TYPE]
                   [--read_overlap READ_OVERLAP]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output raw bit stream file name (Default =
                        fdshield_(DATE-TIME).raw)
  --start_track START_TRACK
                        start track number
  --end_track END_TRACK
                        end track number
  --media_type MEDIA_TYPE
                        media type (2D, 2DD or 2HD)
  --read_overlap READ_OVERLAP
                        track read 2nd lap overlap percentage (default = 0
                        percent)
```

- Read a 2D disk  
```sh
python capture.py -o image.raw
```

- Read a 2DD disk with 5% read overlap (read 105% of track from the index hole)
```sh
python capture.py -o image.raw --medi_type 2DD --read_overlap 5
```
