#trim

import sys
import time
import argparse

# PySerial is required - pip install pyserial
import serial
from serial.tools import list_ports

last_line = ''

def detect_arduino():
    ports = list_ports.comports()
    aport = None
    for info in ports:
        if info.vid==0x2341:    # Found Arduino Uno (VID==0x2341)
            aport = info.device
    return aport

def get_response(uart):
    return uart.readline().decode(encoding='ascii', errors='ignore')

def wait_response(uart:serial.Serial, expected_response, verbose=False):
    global last_line
    count = 0
    # wait for prompt from Arduino 
    while count <=5:            # retry limit == 5
        line = get_response(uart)
        if verbose:
            print('res=', line)
        count += 1              # retry counter
        if len(line)==0:
            continue
        if line[0] != '+':      # Treat the line not starting with '+' as a message line
            print(line)
            count -= 1          # Don't count message lines
            continue
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


def rawstr_to_distbuf(rawstr:bytearray):
    dist_buf = []
    dist = 0
    encode_base = ord(' ')
    max_len     = ord('z') - encode_base
    extend_char = ord('{')
    for dt in rawstr:
        if dt == extend_char:
            dist += max_len
        else:
            dist += ord(dt) - encode_base
            dist_buf.append(dist)
            dist = 0
    return dist_buf



def distbuf_to_mfmbs(dist_buf:list):
    mfm_bs = []     # C/D MFM bit stream
    for dist in dist_buf:
        for i in range(dist - 1):
            mfm_bs.append(0)
        mfm_bs.append(1)
    return mfm_bs


def mfmbs_to_distbuf(mfmbs:list):
    dist = 0
    dist_buf = []
    for bit in mfmbs:
        dist += 1
        if bit == 1:
            dist_buf.append(dist)
            dist = 0
    if dist != 0:
        dist_buf.append(dist)
    return dist_buf        


def distbuf_to_rawstr(distbuf:list):
    encode_base = ord(' ');
    max_length  = ord('z') - encode_base;
    extend_char = ord('{');
    count = 0
    raw_buf = []
    tmp_buf = '~'
    for dist in distbuf:
        while dist > max_length:
            dist -= max_length
            tmp_buf += chr(extend_char)
            count += 1
            if count % 100 == 99:
                raw_buf.append(tmp_buf)
                tmp_buf = '~'
        tmp_buf += chr(dist + encode_base)
        count += 1
        if count % 100 == 99:
            raw_buf.append(tmp_buf)
            tmp_buf = '~'
    if len(tmp_buf) > 1:
        raw_buf.append(tmp_buf)
    return raw_buf     


def strip_data_bits(bitstream):
    dt = 0
    for i in range(14, -1, -2):  # 14 -> 0, step=-2
        dt = (dt << 1) | (1 if (bitstream & (1 << i)) != 0 else 0)
    return dt

# 16進ダンプ表示
def dump(data:list, mc:list==None):
    num_cols = 32
    if mc is not None:
        for count in range(len(data)):
            mark = '*' if mc[count] == 1 else ' '
            dt = data[count]
            print(f' {mark}{dt:02x}', end='')
            if (count % num_cols) == (num_cols - 1):
                print()
    else:
        for count in range(len(data)):
            dt = data[count]
            print(f' {dt:02x}', end='')
            if (count % num_cols) == (num_cols - 1):
                print()


def mfm_decode(mfm_bs:list, start_pos:int=0, size:int=0):
    missing_clock_c2 = (0x5224)  #  [0,1,0,1, 0,0,1,0, *,0,1,0, 0,1,0,0]
    missing_clock_a1 = (0x4489)  #  [0,1,0,0, 0,1,0,0, 1,0,*,0, 1,0,0,1]
    pattern_ff       = (0x5555555555555555)  # for 4 bytes of sync data (unused)
    pattern_00       = (0xaaaaaaaaaaaaaaaa)  # for 4 bytes of sync data

    bit_cell = 8

    shift_reg = 0       # Shift register for MFM decoding
    sreg_count = 0      # number of bit read
    sample_bit_count = 0
    sample_bit_reading = 0

    decoded_data = []
    mc = []
    pos_buf = []

    if size == 0:
        size = len(mfm_bs)

    bit_pos = start_pos
    mc_bit = 0
    for count in range(start_pos, size):
        pulse = mfm_bs[count]
        if pulse == 1:
            sample_bit_reading = 1
            sample_bit_count = bit_cell / 2               # Center the pulse
        sample_bit_count += 1
        if sample_bit_count >= bit_cell:
            shift_reg = (shift_reg << 1) | sample_bit_reading
            sample_bit_count = 0
            sample_bit_reading = 0
            sreg64 = shift_reg & 0xffffffffffffffff
            sreg16 = shift_reg & 0xffff
            if sreg64 == pattern_ff:      # SYNC pattern detection
                sreg_count &= ~1          # C/D synchronize
            sreg_count += 1
            if (sreg_count & 1==0) and (sreg16 == missing_clock_a1 or sreg16 == missing_clock_c2):  # Missing clock pattern detected
                sreg_count = 16                                  # Force alignment to the byte border
                mc_bit = 1

            if sreg_count >= 16:                                 # 1 byte data read completion by reading 16 bits (C+D)
                decoded_data.append(strip_data_bits(sreg16))
                mc.append(mc_bit)
                pos_buf.append(bit_pos)
                bit_pos = count + 1
                mc_bit = 0
                sreg_count = 0

    return (decoded_data, mc, pos_buf)


# Find the pulse index number from the 
def find_data_index_from_bit_pos(bit_pos_list:list, bit_pos:int):
    for i, bp in enumerate(bit_pos_list):
        if bp >= bit_pos:
            return i
    return -1


def find_sync_field(data_list:list, mc_list:list, bit_pos_list:list, start_pos:int):
    def debug_dump(data_list, pos, size):
        for i in range(size):
            dt = data_list[pos+i]
            print(f'{dt:02x} ', end='')
        print()
    # Find the 1st SYNC+addres mark
    state = 0
    sync_pos = -1
    prev = -1
    start_index = find_data_index_from_bit_pos(bit_pos_list, start_pos)
    #print(f'Start index: {start_index}')
    for pos in range(start_index, len(data_list)):
        dt = data_list[pos]
        mc = mc_list[pos]
        bp = bit_pos_list[pos]
        if state == 0:
            if dt == 0 and prev != 0:
                sync_pos = bp                       # record the start position of the sync field
                sync_pos_idx = pos
        if state == 0:
            if mc == 1:
                state = 1
        elif state == 1:
            if mc == 0:
                if (dt & 0xf8) == 0xf8:       # Address mark
                    print(f'{sync_pos_idx:08d} ', end='')
                    debug_dump(data_list, pos - 8, 0x20)
                    return sync_pos
                else:
                    state = 0
        prev = dt
    return -1

def shrink_bs(bs:list, target_size:int):
    num_bits_per_track_img = len(bs)
    diff = num_bits_per_track_img - target_size
    step = int(num_bits_per_track_img // diff)
    print(f'shrink step={step}')
    for i in range(diff):
        pos = i * step - i
        while bs[pos] == 1:                      # Do not remove pulse
            pos += 1
        bs.pop(pos)
    return bs

def expand_bs(bs:list, target_size:int):
    num_bits_per_track_img = len(bs)
    diff = target_size - num_bits_per_track_img
    step = int(num_bits_per_track_img // diff)
    print(f'expand step={step}')
    for i in range(diff):
        pos = i * step + i
        bs.insert(pos, 0)
    return bs


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
        uart = serial.Serial(arduino_port, baudrate=115200, timeout=3, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    except serial.serialutil.SerialException:
        print('ERROR : ' + arduino_port + ' is in use.')
        sys.exit(1)

    exit_flag = False

    wait_response(uart, '++CMD')   # wait for prompt from Arduino

    calibrated_clock = arduino_timer_calibration(uart)      # Calibrate Arduino timer 1
    wait_response(uart, '++CMD')

    submit_command(uart, f'+S {int(calibrated_clock)}\n')
    wait_response(uart, '++CMD')

    print('**Measuring spindle speed...')
    submit_command(uart, '+C\n')     # Measure spindle speed
    while True:
        res = get_response(uart)
        if res[:11] == '++SPIN_TICK':
            fdd_spin_tick = int(res[12:])       # Arduino Uno TCNT1 count value (1/64 IOCLK == 250KHz)
            spindle_time = fdd_spin_tick / calibrated_clock
            print(f'**FDD_SPINDLE_TIME {spindle_time} ms (Tick={fdd_spin_tick})')
            break

    wait_response(uart, '++CMD')
    mode = 0            # 0: cmd mode, 1: pulse data read mode
    with open(args.input, 'rt') as fin, open(args.output, 'wt') as fout:
        while exit_flag == False:
            line = fin.readline()
            if len(line)==0:
                continue
            items = line.split()
            if line[:13] == '**TRACK_RANGE':
                track_start = int(items[1])
                track_end = int(items[2])
                print(line, file=fout)
                print(line)
            elif line[:12] == '**MEDIA_TYPE':
                media_type = items[1]
                print(line, file=fout)
                print(line)
                print('**START', file=fout)
                print('**START')
            elif line[:12] == '**DRIVE_TYPE':
                drive_type = items[1]
                print(line, file=fout)
                print(line)
            elif line[:10] == '**SPIN_SPD':
                spin_speed = float(items[1])
                print(line, file=fout)
                print(line)
            elif line[:9] == '**OVERLAP':
                overlap = int(items[1])
                print(line, file=fout)
                print(line)
            elif line[:12] == '**TRACK_READ':
                curr_track = int(items[1])
                curr_side = int(items[2])
                raw_data = ''
                mode = 1                        # read pulse data mode
            elif line[:11] == '**TRACK_END':
                print(f'**TRACK {curr_track} {curr_side}')
                dist_buf = rawstr_to_distbuf(raw_data)
                mfm_bs = distbuf_to_mfmbs(dist_buf)

                mfm_data, mc, bit_pos = mfm_decode(mfm_bs)
                #dump(mfm_data, mc)

                sync_field0 = find_sync_field(mfm_data, mc, bit_pos, 0)

                num_bits_per_track_img = int(4e6 * spin_speed)                 # Calculate the bit position of the top of the 2nd spin in the image from the spindle rotation time of image capturing
                offset = int((8 * 8) * ((4e6 / 500e3) * 2))                    # for 8 bytes in MFM bit stream (not to overwrite the 1st AM)
                sync_field1 = find_sync_field(mfm_data, mc, bit_pos, num_bits_per_track_img - offset)

                print(f'{sync_field0}, {sync_field1}')
                if sync_field0 != -1 and sync_field1 != -1:
                    #d1, m1, p1 = mfm_decode(mfm_bs, sync_field1)
                    #dump(d1, m1)
                    num_bits_per_track_img = sync_field1 - sync_field0          # 1st SYNC in 1st spin to 1st SYNC in 2nd spin -> number of bits per track in the image
                    num_bits_per_track_fdd = int(fdd_spin_tick * (4e6 / calibrated_clock)) # number of bits per track calculated from the actual FDD spindle speed
                    diff = num_bits_per_track_fdd - num_bits_per_track_img

                    # Matches the bitstream length to the actual FDD spindle speed
                    mfm_bs_head = mfm_bs[:sync_field0]
                    mfm_bs_body = mfm_bs[sync_field0:sync_field1]
                    print(f'BS length for 1 spin: capture_img={num_bits_per_track_img}, current_FDD={num_bits_per_track_fdd}, diff {diff}')
                    if diff > 0:
                        expand_bs(mfm_bs_body, num_bits_per_track_fdd)
                    elif diff < 0:
                        shrink_bs(mfm_bs_body, num_bits_per_track_fdd)
                    else:
                        pass    # NOP when bitstream size matches
                    adjust = int((4 * 8) * ((4e6 / 500e3) * 2))       # for 4 bytes in MFM bit stream (not to overwrite the 1st AM)
                    #mfm_bs = mfm_bs_head + mfm_bs_body
                    mfm_bs = mfm_bs_head + mfm_bs_body[:-adjust]
                else:
                    print('Couldn\'t find sync field. Simple trimming will be applied.')
                    mfm_bs = mfm_bs[:num_bits_per_track_img]
                    mfm_bs_body = mfm_bs

                #d1, m1, p1 = mfm_decode(mfm_bs)
                #dump(d1, m1)
                print(f'bs length after adjustment {len(mfm_bs_body)}')
                #print()
                write_time = len(mfm_bs) / 4e6
                arduino_timer_tick = int((calibrated_clock) * write_time)    # Arduino timer 1 (16bit) clock speed = 250KHz
                #print(f'Write time {write_time} sec, Arduino timer tick {arduino_timer_tick}')

                dist_buf = mfmbs_to_distbuf(mfm_bs)
                raw_encoded = distbuf_to_rawstr(dist_buf)
                print(f'**TRACK_READ {curr_track} {curr_side} {arduino_timer_tick}', file=fout)
                for line in raw_encoded:
                    print(line, file=fout)
                print('**TRACK_END', file=fout)
                print()
                mode = 0
            elif line[:11] == '**COMPLETED':
                print('**COMPLETED', file=fout)
                print('**COMPLETED')
                exit_flag = True
            elif mode == 1:
                if line[0] != '~':
                    continue
                raw_data += line[1:].rstrip('\r').rstrip('\n')


if __name__ == '__main__':
    print('** Floppy shield - disk cloning tool')

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, default=None, help='input raw bit stream file name (*.raw)')
    parser.add_argument('-o', '--output', type=str, required=False, default='trimmed.raw', help='output raw bit stream file name (*.raw) (default=\'trimmed.raw\')')
    parser.add_argument('-n', '--normalize', action='store_true', required=None, default=False, help='perform data pulse timing normalization (default=False)')
    args = parser.parse_args()

    main(args)


