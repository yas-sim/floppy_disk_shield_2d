import sys
from pynput import keyboard

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

exit_flag = False

def on_press(key):
    global exit_flag
    exit_flag = True
    return True

def main():
    global exit_flag
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

    while True:
        line = uart.readline().rstrip(b'\n').rstrip(b'\r')
        if len(line)==0:
            continue
        line = line.decode(encoding='ascii', errors='ignore')
        if line[:5] == '++CMD':         # Command prompt
            break
    uart.write('+V\n'.encode('ascii'))

    print('\n*** Hit any key to exit ***\n')
    exit_flag = False
    with keyboard.Listener(on_press=on_press) as listener:
        while exit_flag == False:
            report = uart.readline().rstrip(b'\n').rstrip(b'\r')
            report = report.decode(encoding='ascii', errors='ignore')
            if(report[0]!='*'):
                t = float(report)
                print('rotation time = {:6.3f}ms, {:6.3f}rpm      \r'.format(t, 60000/t), end='')
    listener.join()
    uart.close()

if __name__ == '__main__':
    main()
