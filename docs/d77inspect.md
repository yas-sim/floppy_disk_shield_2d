# d77inspect.py

```sh
python d77inspect.py -i gutchan_bank.d77 -t 0
```

```
** D77 disk image inspection tool
Header: {'name': 'DISK', 'write_protect': 'OFF', 'disk_type': '2D', 'disk_size': 956123, 'raw_track': 'Supported'}
0
#   C  H  R  N    S1 S2   AM   SIZE ICRC POS
000 00 00 01 01 - 00 00 - DAM   256 fa0c 009f
001 00 00 02 01 - 00 00 - DAM   256 af5f 0211
002 00 00 03 01 - 00 00 - DAM   256 9c6e 0383
003 00 00 04 01 - 00 00 - DAM   256 05f9 04f5
004 00 00 05 01 - 00 00 - DAM   256 36c8 0667
005 00 00 06 01 - 00 00 - DAM   256 639b 07d9
006 00 00 07 01 - 00 00 - DAM   256 50aa 094b
007 00 00 08 01 - 00 00 - DAM   256 4094 0abd
008 00 00 09 01 - 00 00 - DAM   256 73a5 0c2f
009 00 00 0a 01 - 00 00 - DAM   256 26f6 0da1
010 00 00 0b 01 - 00 00 - DAM   256 15c7 0f13
011 00 00 0c 01 - 00 00 - DAM   256 8c50 1085
012 00 00 0d 01 - 00 00 - DAM   256 bf61 11f7
013 00 00 0e 01 - 00 00 - DAM   256 ea32 136a
014 00 00 0f 01 - 00 00 - DAM   256 d903 14dc
015 00 00 10 01 - 00 00 - DAM   256 ca4e 164e
```

```sh
python d77inspect.py -i gutchan_bank.d77 -t (0,1)
```

```
** D77 disk image inspection tool
Header: {'name': 'DISK', 'write_protect': 'OFF', 'disk_type': '2D', 'disk_size': 956123, 'raw_track': 'Supported'}
0
#   C  H  R  N    S1 S2   AM   SIZE ICRC POS
000 00 00 01 01 - 00 00 - DAM   256 fa0c 009f
001 00 00 02 01 - 00 00 - DAM   256 af5f 0211
002 00 00 03 01 - 00 00 - DAM   256 9c6e 0383
003 00 00 04 01 - 00 00 - DAM   256 05f9 04f5
004 00 00 05 01 - 00 00 - DAM   256 36c8 0667
005 00 00 06 01 - 00 00 - DAM   256 639b 07d9
006 00 00 07 01 - 00 00 - DAM   256 50aa 094b
007 00 00 08 01 - 00 00 - DAM   256 4094 0abd
008 00 00 09 01 - 00 00 - DAM   256 73a5 0c2f
009 00 00 0a 01 - 00 00 - DAM   256 26f6 0da1
010 00 00 0b 01 - 00 00 - DAM   256 15c7 0f13
011 00 00 0c 01 - 00 00 - DAM   256 8c50 1085
012 00 00 0d 01 - 00 00 - DAM   256 bf61 11f7
013 00 00 0e 01 - 00 00 - DAM   256 ea32 136a
014 00 00 0f 01 - 00 00 - DAM   256 d903 14dc
015 00 00 10 01 - 00 00 - DAM   256 ca4e 164e
1
#   C  H  R  N    S1 S2   AM   SIZE ICRC POS
000 00 01 00 01 - 00 00 - DAM   256 fe0d 00a3
001 00 01 01 01 - 00 00 - DAM   256 cd3c 0217
002 00 01 02 01 - 00 00 - DAM   256 986f 038a
003 00 01 03 01 - 00 00 - DAM   256 ab5e 04fd
004 00 01 04 01 - 00 00 - DAM   256 32c9 066f
005 00 01 05 01 - 00 00 - DAM   256 01f8 07e1
006 00 01 06 01 - 00 00 - DAM   256 54ab 0953
007 00 01 07 01 - 00 00 - DAM   256 679a 0ac5
008 00 01 08 01 - 00 00 - DAM   256 77a4 0c37
009 00 01 09 01 - 00 00 - DAM   256 4495 0da9
010 00 01 0a 01 - 00 00 - DAM   256 11c6 0f1b
011 00 01 0b 01 - 00 00 - DAM   256 22f7 108f
012 00 01 0c 01 - 00 00 - DAM   256 bb60 1205
013 00 01 0d 01 - 00 00 - DAM   256 8851 1379
014 00 01 0e 01 - 00 00 - DAM   256 dd02 14ec
015 00 01 0f 01 - 00 00 - DAM   256 ee33 1661
```
