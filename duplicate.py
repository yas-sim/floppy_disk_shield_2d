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

last_line = ''

def wait_response(uart, expected_response, verbose=False):
    global last_line
    count = 0
    while True:         # wait for prompt from Arduino
        line = uart.readline() #.rstrip(b'\n').rstrip(b'\r')
        #if len(line)==0:
        #    continue
        if verbose:
            print(line)
        line = line.decode(encoding='ascii', errors='ignore')
        if line[:len(expected_response)] == expected_response:
            break
        count += 1
        if count >= 5:
            print(last_line)
            #print('_TO_', end='', flush=True)
            break


def main(args):
    global last_line
    # Search an Arduino and open UART
    print('Searching for Arduino')
    arduino_port = detect_arduino()
    if arduino_port is None:
        print('Arduino is not found')
        sys.exit(1)
    else:
        print('Arduino is found on "{}"'.format(arduino_port))
    try:
        uart = serial.Serial(arduino_port, baudrate=115200, timeout=3, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    except serial.serialutil.SerialException:
        print('ERROR : ' + arduino_port + ' is in use.')
        sys.exit(1)

    exit_flag = False

    wait_response(uart, '++CMD')   # wait for prompt from Arduino

    uart.write('+WR \n'.encode('ascii'));
    wait_response(uart, '++READY')

    mode = 0            # 0: cmd mode, 1: pulse data read mode
    with open(args.input, 'rt') as f:
        while exit_flag == False:
            line = f.readline()#.rstrip('\n').rstrip('\r')
            if len(line)==0:
                continue
            items = line.split()
            if line[:13] == '**TRACK_RANGE':
                track_start = int(items[1])
                track_end = int(items[2])
                print(f'Track range : {track_start} - {track_end}')
            elif line[:12] == '**MEDIA_TYPE':
                media_type = items[1]
                print(f'Media type : {media_type}')
            elif line[:10] == '**SPIN_SPD':
                spin_speed = float(items[1])
                print(f'Spin speed : {spin_speed}')
            elif line[:9] == '**OVERLAP':
                overlap = int(items[1])
                print(f'Overlap : {overlap}')
            elif line[:12] == '**TRACK_READ':
                curr_track = int(items[1])
                curr_side = int(items[2])
                print(f'** TRACK WRITE {curr_track} {curr_side}')
                uart.write((line).encode('ascii'))
                uart.flush()
                mode = 1                        # read pulse data mode
                wait_response(uart, '++ACK')
            elif line[:11] == '**TRACK_END':
                print('\nWRITING...')
                uart.write((line).encode('ascii'))
                uart.flush()
                mode = 0
                wait_response(uart, '++ACK')
            elif line[:11] == '**COMPLETED':
                uart.write((line).encode('ascii'))
                uart.flush()
                exit_flag = True
                wait_response(uart, '++ACK')
            elif mode == 1:
                if line[0] != '~':
                    continue
                print('.', end='', flush=True)
                line = line.replace('C', 'B')              # !?!? Mystery. When the line including 'C', Arduino gets hang up.
                last_line = line
                uart.write((line).encode('ascii'))
                uart.flush()
                wait_response(uart, '++ACK')

    uart.close()


if __name__ == '__main__':
    print('** Floppy shield - disk cloning tool')

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, default=None, help='input raw bit stream file name (Default = fdshield_(DATE-TIME).raw)')
    args = parser.parse_args()

    main(args)

# command format "+R strack etrack mode overlap"
