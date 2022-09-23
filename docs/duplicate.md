# duplicate.py

'*.raw' floppy disk image write back tool. This program transfers a raw bit stream FD data from a host PC to an Arduino.  

```sh
usage: duplicate.py [-h] -i INPUT.raw

optional arguments:
  -h, --help            show this help message and exit
  -o INPUT, --input INPUT
                        input raw bit stream file name
```

- Read a 2D disk  
```sh
python duplicate.py -i image.raw
```
