import os
import sys
import datetime
import argparse

# PySerial is required - pip install pyserial
import serial
from serial.tools import list_ports

def detect_arduino():
    ports = list_ports.comports()
    aport = None
    for info in ports:
        if info.vid==0x2341:    # Found Arduino Uno (VID==0x2341)
            aport = info.device
    return aport

def main(args):
    # Search an Arduino and open UART
    print('Searching for Arduino')
    arduino_port = detect_arduino()
    if arduino_port is None:
        print('Arduino is not found')
        sys.exit(1)
    else:
        print('Arduino is found on "{}"'.format(arduino_port))
    try:
        uart = serial.Serial(arduino_port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    except serial.serialutil.SerialException:
        print('ERROR : ' + arduino_port + ' is in use.')
        sys.exit(1)

    # generate output file name
    if args.output is None:
        log_file = 'fdshield_{}.raw'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    else:
        log_file = args.output
    print('Raw bit stream file :', log_file)

    exit_flag = False
    active_flag = False
    with open(log_file, 'w') as f:
        while exit_flag == False:
            line = uart.readline().rstrip(b'\n').rstrip(b'\r')
            if len(line)==0:
                continue
            line = line.decode(encoding='ascii', errors='ignore')
            if line[:5] == '++CMD':         # Command prompt
                start_track = 0
                if args.media_type == '2DD':
                    media_type = 1
                    bit_rate = 500e3
                    end_track = 163
                elif args.media_type == '2HD':
                    media_type = 1
                    bit_rate = 1e6
                    end_track = 163
                else:
                    media_type = 0
                    bit_rate = 500e3
                    end_track = 83
                if args.start_track != -1:
                    start_track = args.start_track
                if args.end_track != -1:
                    end_track = args.end_track
                uart.write('+R {} {} {} {}\n'.format(start_track, end_track, media_type, args.read_overlap).encode('ascii'))
                f.write('**BIT_RATE {}\n'.format(int(bit_rate)))
                f.write('**TRACK_RANGE {} {}\n'.format(start_track, end_track))
                f.write('**MEDIA_TYPE {}\n'.format(args.media_type))
            if line[:2] == '**' or line[:2] == '##':
                print('\n' + line)
            if line[:7] == '**START':
                active_flag = True
            if line[:12] == '**COMPLETED':
                exit_flag = True
            if active_flag:
                if line[:2] == '##':
                    continue
                f.write(line+'\n')
                if line[0] == '~':
                    print('.', flush=True, end='')

    uart.close()

if __name__ == '__main__':
    print('** Floppy shield - data transfer tool')

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, required=True, default=None, help='output raw bit stream file name (Default = fdshield_(DATE-TIME).raw)')
    parser.add_argument('--start_track', type=int, required=False, default=-1, help='start track number')
    parser.add_argument('--end_track', type=int, required=False, default=-1, help='end track number')
    parser.add_argument('--media_type', type=str, required=False, default="2D", help='media type (2D, 2DD or 2HD)')
    parser.add_argument('--read_overlap', type=int, required=False, default=0, help='track read 2nd lap overlap percentage (default = 0 percent)')
    args = parser.parse_args()

    main(args)

# command format "+R strack etrack mode overlap"
