# Floppy Disk Shield for Arduino UNO

## Caveat and Disclaimer - Read before you build a fd-shield  
- **The project is still WIP**
- I don't own any responsibility for the data loss or physical damage on your floppy disks or computer assets caused by the use of hardware and software included in this project.
- Hardware compatibility (especially, FDD and FD-Shield compatibility) is not guaranteed. Your FDD may now work with the FD-Shield.  
- The magnetic flux power on the old floppy disks are dropping and getting weak as time passes. Read-out data integrity with this system is not guaranteed.
- Recommended to use newer FDD. The old FDD may have problems on the magnetic head such as contamination, worn out or mechanical misalignment.

## Description
This is a project to develop a system for preserving old 2D/2DD floppy disk data.  
The system includes a bit-stream data to D77/D88 emulator disk image converter. You can generate the disk images from the phicical floppy disks.  

The system consists with hardware and software:  

**Hardware**  
|Item|Description|
|:----|:----|
|Arduino UNO|Arduino UNO. The firmware uses ATMega328 specific regiter. The other Arduino board may not work|
|Floppy disk shield for Arduino|Design data is included. Both schematics and PCB data are available (`./kicad/*`)|
|Floppy drive|2D/2DD/2HD FDD. 3.5" or 5.25" FDD (+ power supply and ribbon cable). 300rpm drive is recommended but 360rpm 2HD drive will work as a 2DD drive|  

**Software**  

|Name|Description|
|:--------|:-----------|
|`fdcapture.ino`|Arduino firmware (sketch) for the floppy shield (`./fdcapture/fdcapture.ino`)|
|`transfer.py`|Transfers raw bitstream data from Arduino to PC|
|`fdcapture.ino`|Arduino firmware for controlling floppy disk shield|
|`bs2d77.py`|Bit-stream data to emulator disk image (D77/D88) converter. The program generates modified D77 image data (D77mod). D77mod specification is [here](docs/D77mod_format.md). The D77mod is backward compatible with the standard D77 disk images. You can use the D77mod image with emulators which supports D77/D88 image data.|
|`bs_inspect.py`|Data inspection/analyze tool for bit-stream data|
|`d77_inspect.py`|Data inspection/analyze tool for D77/D88 disk image data|
|`floppylib.py`|A library which provides fundamental floppy disk functions. This library is including data-separator, digital VFO, MFM decoder and IBM format parser|
|`d77dec.py`|Convert D77/D88 disk image data to JSON (plane text) data|
|`d77enc.py`|Generate D77/D88 disk image data from JSON data|
|`d77lib.py`|A libray which provides basic D77/D88 floppy disk image manipulation functions|
|`kfx2bs.py`|[**KyroFlux**](https://www.kryoflux.com/) raw-bitstream data to fd-shield bit-stream data converter. You can capture FD image with KryoFlux and convert it|
### System Diagram
![system_diagram](resources/fd-shield.jpg)

## FD-Shield - How It Works
![FD_Shield How it works](resources/fd-shield1.jpg)

---------

## How to use (the most simple way)

1. Build Floppy shield for Arduino UNO  
- PCB design files can be found in the `./kicad` directory
2. Burn the floppy disk shield firmware (sketch) to Arduino UNO  
Use `fdcapture.ino`
3. Assemble the system
- Attach a floppy shield to an Arduino UNO
- Connect a floppy shield and a floppy disk drive with a 36pin ribon cable
- Connect Arduino UNO to PC via USB cable
4. Read raw bit-stream data from a floppy disk  
- Insert a 2D floppy disk to the floppy disk drive (FDD) -- 2DD floppy disk can be read but it requires a simple code modification to change head seek method on `fdcapture.ino`.
- Run following command on the Windows PC:
```sh
python transfer.py -o image_name.raw
```
- `transfer.py` will search COM port for Arduino UNO and use it.
5. Convert raw bit-stream data into emulator image data (D77mod)
```sh
python bs2d77.py -i image_name.raw
```
- `image_name.d77` will be generated.

## Test Environment

- Windows 10 1909
- Arduino UNO

|P/N|Mfg|FF|Description|
|---|----|----|----|
|FD55-GFR 19307673-93|TEAC|5.25"|2DD/2HD, 360rpm, for DOS/V|
|FD-235HG 19307773-04|TEAC|3.5"|2DD/2HD, 300/360rpm, Fixed to DS1|
|YD-580 1354|YE-Data|5.25"|2D, 300rpm, for Fujitsu FM-7 (1984-11)|
|YD625-1525|YE-Data|3.5"|2D, 300rpm, Fujitsu for FM-77|

---------------

## Addendum

![MFM Missing Clock Patterns](resources/missing_clock.jpg)

![system_diagram](resources/byte_sync.jpg)

