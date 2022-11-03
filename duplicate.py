import sys
import argparse
import time

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

def get_response(uart):
    return uart.readline().decode(encoding='ascii', errors='ignore')

def wait_response(uart:serial.Serial, expected_response, verbose=False):
    global last_line
    count = 0
    # wait for prompt from Arduino 
    while count <=5:            # retry limit == 5
        line = get_response(uart)
        count += 1              # retry counter
        if len(line)==0:
            continue
        if line[0] != '+':      # Treat the line not starting with '+' as a message line
            print(line)
            count -= 1          # Don't count message lines
            continue
        if verbose:
            print(line)
        if type(expected_response == list):
            for i, res in enumerate(expected_response):
                #print(i, res, len(res), line[:len(res)])
                if line[:len(res)] == res:
                    return i
        else:
            if line[:len(expected_response)] == expected_response:
                return 0

    # retry count exceeded the limit
    print(last_line)
    #print('_TO_', end='', flush=True)
    #sys.exit(-1)
    return -1


def submit_command(uart:serial.Serial, cmd, verbose=False):
    if verbose:
        print(cmd)
    uart.write(cmd.encode('ascii'))
    uart.flush()


def arduino_timer_calibration(uart):
    print('**Calibrating Arduino timer...')
    uart.write('+M\n'.encode('ascii'))
    while True:
        dt = uart.read(1).decode('utf8')
        if len(dt) == 0:
            continue
        if dt[0] == 'S':
            break
    stime = time.perf_counter()
    while True:
        dt = uart.read(1).decode('utf8')
        if len(dt) == 0:
            continue
        if dt[0] == 'E':
            break
    etime = time.perf_counter()

    actual = etime - stime
    arduino_timer_clock = 250e3
    expectation = (0x8000 * 40) / arduino_timer_clock   # == 5.24288 sec
    ratio = expectation / actual
    calibrated_timer_clock = arduino_timer_clock * ratio

    print(f'**Calibrated clock = {calibrated_timer_clock}Hz')
    return calibrated_timer_clock


def main(args):
    global last_line
    # Search an Arduino and open UART
    print('Searching for Arduino')
    #"""
    arduino_port = detect_arduino()
    if arduino_port is None:
        print('Arduino is not found')
        sys.exit(1)
    else:
        print('Arduino is found on "{}"'.format(arduino_port))
    """
    arduino_port = 'COM8'   # In case the Arduino is a kind of Arduino Uno compatible (equivalent) one. (meaning, not a genuine Arduino Uno)
    """
    try:
        uart = serial.Serial(arduino_port, baudrate=115200, timeout=3, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    except serial.serialutil.SerialException:
        print('ERROR : ' + arduino_port + ' is in use.')
        sys.exit(1)
    
    exit_flag = False

    wait_response(uart, '++CMD')   # wait for prompt from Arduino

    calibrated_clock = arduino_timer_calibration(uart)      # Calibrate Arduino timer 1
    wait_response(uart, '++CMD')   # wait for prompt from Arduino

    submit_command(uart, f'+S {int(calibrated_clock)}\n')
    wait_response(uart, '++CMD')   # wait for prompt from Arduino

    normalize_flag = 1 if args.normalize else 0             # data pulse timing normalization flag
    submit_command(uart, f'+WR {normalize_flag}\n')
    res = wait_response(uart, ['++READY', '++WRITE_PROTECTED'])
    if res == 1:
        print('[MSG] The floppy disk in the FDD is write protected. Aborted.')
        sys.exit(0)

    mode = 0            # 0: cmd mode, 1: pulse data read mode
    with open(args.input, 'rt') as f:
        while exit_flag == False:
            line = f.readline()
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
                submit_command(uart, line)
                wait_response(uart, '++ACK')
                mode = 1                        # read pulse data mode
            elif line[:11] == '**TRACK_END':
                submit_command(uart, line)
                wait_response(uart, '++ACK')
                print()
                mode = 0
            elif line[:11] == '**COMPLETED':
                submit_command(uart, line)
                wait_response(uart, '++ACK')
                exit_flag = True
            elif mode == 1:
                if line[0] != '~':
                    continue
                print('.', end='', flush=True)
                line = line.replace('C', 'B')              # !?!? Mystery. When the line including 'C', Arduino gets hang up.
                last_line = line
                submit_command(uart, line)
                wait_response(uart, '++ACK')

    uart.close()


if __name__ == '__main__':
    print('** Floppy shield - disk cloning tool')

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, default=None, help='input raw bit stream file name (*.raw)')
    parser.add_argument('-n', '--normalize', action='store_true', required=None, default=False, help='perform data pulse timing normalization (default=False)')
    args = parser.parse_args()

    main(args)
