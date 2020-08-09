troubleshoot.md

### Read overlap too  much
The 1st sec
1% overlap
```sh
N:\work\fdcapture>python bs_inspect.py -i yd580\princess-quest.log --read_sectors -t 0
** Floppy data capture shield - bit stream data inspect tool
** TRACK  0
 # : (C ,H ,R ,N ) ID-CRC DT-CRC AM    MFM-POS
 1 : (00,00,01,01) OK     OK     DAM   0x002e
 2 : (00,00,02,01) OK     OK     DAM   0x01a5
 3 : (00,00,03,01) OK     OK     DAM   0x031a
 4 : (00,00,04,01) OK     OK     DAM   0x048f
 5 : (00,00,05,01) OK     OK     DAM   0x0604
 6 : (00,00,06,01) OK     OK     DAM   0x0779
 7 : (00,00,07,01) OK     OK     DAM   0x08ef
 8 : (00,00,08,01) OK     OK     DAM   0x0a65
 9 : (00,00,09,01) OK     OK     DAM   0x0bda
10 : (00,00,0a,01) OK     OK     DAM   0x0d4f
11 : (00,00,0b,01) OK     OK     DAM   0x0ec4
12 : (00,00,0c,01) OK     OK     DAM   0x1039
13 : (00,00,0d,01) OK     OK     DAM   0x11ae
14 : (00,00,0e,01) OK     OK     DAM   0x1324
15 : (00,00,0f,01) OK     OK     DAM   0x1499
16 : (00,00,10,01) OK     OK     DAM   0x160f
17 : (00,00,01,01) OK     ERR    DAM   0x18c6
OK=16, Error=1
```

2% overlap
```sh
N:\work\fdcapture>python bs_inspect.py -i yd580\princess-quest.log -t 0 --id_dump
** Floppy data capture shield - bit stream data inspect tool
** TRACK  0
 # : (C ,H ,R ,N ) ID-CRC AM    MFM-POS
 1 : (00,00,01,01) OK     DAM   0x002e
 2 : (00,00,02,01) OK     DAM   0x01a5
 3 : (00,00,03,01) OK     DAM   0x031a
 4 : (00,00,04,01) OK     DAM   0x048f
 5 : (00,00,05,01) OK     DAM   0x0604
 6 : (00,00,06,01) OK     DAM   0x0779
 7 : (00,00,07,01) OK     DAM   0x08ef
 8 : (00,00,08,01) OK     DAM   0x0a65
 9 : (00,00,09,01) OK     DAM   0x0bda
10 : (00,00,0a,01) OK     DAM   0x0d4f
11 : (00,00,0b,01) OK     DAM   0x0ec4
12 : (00,00,0c,01) OK     DAM   0x1039
13 : (00,00,0d,01) OK     DAM   0x11ae
14 : (00,00,0e,01) OK     DAM   0x1324
15 : (00,00,0f,01) OK     DAM   0x1499
16 : (00,00,10,01) OK     DAM   0x160f
```


```sh
N:\work\fdcapture>python bs_inspect.py -i fd55gfr\pascal-master.log --read_sectors -t 71 --high_gain=0.3
** Floppy data capture shield - bit stream data inspect tool
** TRACK  71
 # : (C ,H ,R ,N ) ID-CRC DT-CRC AM    MFM-POS
 1 : (23,01,01,01) OK     OK     DAM   0x00a0
 2 : (23,01,02,01) OK     OK     DAM   0x0218
 3 : (23,01,03,01) OK     OK     DAM   0x0390
 4 : (23,01,04,01) OK     OK     DAM   0x0509
 5 : (23,01,05,01) OK     OK     DAM   0x0683
 6 : (23,01,06,01) OK     OK     DAM   0x07fb
 7 : (23,01,07,01) OK     OK     DAM   0x0973
 8 : (23,01,08,01) OK     OK     DAM   0x0aeb
 9 : (23,01,09,01) OK     OK     DAM   0x0c63
10 : (23,01,0a,01) OK     OK     DAM   0x0dda
11 : (23,01,0b,01) OK     OK     DAM   0x0f52
12 : (23,01,0c,01) OK     OK     DAM   0x10cb
13 : (23,01,0d,01) OK     OK     DAM   0x1243
14 : (23,01,0e,01) OK     OK     DAM   0x13bb
15 : (23,01,0f,01) OK     OK     DAM   0x1533
16 : (23,01,10,01) OK     ERR    DAM   0x16ad
OK=15, Error=1
```