# bs2hfe.py

```sh
usage: bs2hfe.py [-h] -i INPUT [-o OUTPUT] [--log_level LOG_LEVEL] [--clk_spd CLK_SPD]
```

|option|description|
|-|-|
|-h, --help|show this help message and exit|
|-i INPUT, --input INPUT|input image file path|
|-o OUTPUT, --output OUTPUT|output D77 image path|
|--log_level LOG_LEVEL|log level: 0=off, 1=minimum, 2=verbose|
|--clk_spd CLK_SPD|FD-shield capture clock speed (default=4MHz=4000000)|

## Command line example
```
python bs2hfe.py -i diskimage.raw -o diskimage.hfe
** Floppy shield bit-stream data to HFE image converter
Spin speed: 199.13520000000003 ms
Conversion completed.
```
