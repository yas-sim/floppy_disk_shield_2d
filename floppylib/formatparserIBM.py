# folppy shield library

from enum import Enum

from floppylib.bitstream import bitstream
from floppylib.crc import CCITT_CRC
from floppylib.dataseparator import data_separator

class FormatParserIBM:
    def __init__(self, bit_stream, clk_spd = 4e6, spin_spd = 0.2, high_gain = 1, low_gain = 1, log_level = 0):
        self.bit_stream   = bit_stream
        self.clk_spd      = clk_spd
        self.spin_spd     = spin_spd
        self.high_gain    = high_gain
        self.low_gain     = low_gain
        self.set_log_level(log_level)
        #"""
        # MB8877
        # Fujitsu MB8877 FDC accepts several pattern of address mark bytes
        self.DELETED_DATA_ADDRESS_MARKS = [ 0xf8, 0xf9 ]
        self.DATA_ADDRESS_MARKS         = [ 0xfa, 0xfb ]
        self.ID_ADDRESS_MARKS           = [ 0xfc, 0xfd, 0xfe, 0xff ]
        self.INDEX_ADDRESS_MARKS        = [ 0xfc ]
        self.SECTOR_LENGTH_LIST         = [ 128, 256, 512, 1024 ]
        #"""
        """
        # uPD765A
        # Address marks for standard IBM format
        self.DELETED_DATA_ADDRESS_MARKS = [ 0xf8 ]
        self.DATA_ADDRESS_MARKS         = [ 0xfb ]
        self.ID_ADDRESS_MARKS           = [ 0xfe ]
        self.INDEX_ADDRESS_MARKS        = [ 0xfc ]
        self.SECTOR_LENGTH_LIST         = [ 128, 256, 512, 1024, 2048, 4096 ]
        """

    def set_log_level(self, log_level = 0):
        self.log_level = log_level

    def set_bit_stream(self, bit_stream):
        self.bit_stream = bit_stream

    def dump_list_hex(self, lst):
        print('[ ', end='')
        for i in lst:
            print('0x{}, '.format(format(i, '02X')) , end='')
        print(']')

    def dumpMFM(self, mfm_buf, mc_buf=None):
        count = 0
        for mfm in mfm_buf:
            if mc_buf is not None:
                mc = mc_buf.pop(0)
                if mc==True:
                    print(' *', end='')
                else:
                    print('  ', end='')
            else:
                print(' ', end='')
            print(format(mfm, '02X'), end='')
            count+=1
            if count==32:
                count=0
                print()
        print()

    def dumpMFM16(self, mfm_buf, mc_buf=None):
        def dumpAscii(asciiString):
            print('    '*(16-len(asciiString)), end='')
            print(' : ', end='')
            print(asciiString)
        count = 0
        asciiString=''
        for mfm in mfm_buf:
            if mc_buf is not None:
                mc = mc_buf.pop(0)
                if mc==True:
                    print(' *', end='')
                else:
                    print('  ', end='')
            else:
                print(' ', end='')
            print(format(mfm, '02X'), end='')
            asciiString += chr(mfm) if mfm>=0x20 and mfm<=0x7e else '.'
            count+=1
            if count==16:
                dumpAscii(asciiString)
                asciiString = ''
                count=0
        dumpAscii(asciiString)


    def read_track(self):
        """
        Decode track data from the preset 'interval_buffer'  
        """
        if self.log_level>0: print('**Read track')

        mfm_buf = []
        mc_buf  = []
        mfm_pos = []

        pos = 0

        ds = data_separator(self.bit_stream, clk_spd=self.clk_spd, spin_spd=self.spin_spd, high_gain=self.high_gain, low_gain=self.low_gain)    # Clock / Data separator
        ds.set_mode(0)      # AM seeking

        while True:
            data, mc = ds.get_byte()
            if data == -1:
                break
            mfm_buf.append(data)
            mc_buf.append(mc)
            mfm_pos.append(pos)
            pos = ds.cell_pos
        return mfm_buf, mc_buf, mfm_pos

    def set_bit_stream(self, bit_stream):
        self.bit_stream = bit_stream

    def search_all_idam(self, abort_by_idxmark=True, abort_by_sameid=True):
        """
        Decode bistream track data  
        Args:
            abort_by_idxmark (bool): Abort reading on detection of 2nd index mark 
            abort_by_sameid  (bool): Abort reading on detection of 2nd same ID detection (potential of 2nd lap)
        Returns:
            id_buf = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                            ID-CRC flag = True:No error False:error  
                            ds_pos  = ID position in the interval buffer
                            mfm_pos = ID position in the MFM buffer   
        """
        class State(Enum):
            IDLE       = 0
            CHECK_MARK = 1
            INDEX      = 2
            IDAM       = 3
            DAM        = 4
            DDAM       = 5
            DATA_READ  = 6
        
        ds = data_separator(self.bit_stream, clk_spd=self.clk_spd, spin_spd=self.spin_spd, high_gain=self.high_gain, low_gain=self.low_gain)    # Clock / Data separator
        ds.set_mode(0)      # AM seeking
        ds.set_pos(0)

        crc = CCITT_CRC()

        state = State.IDLE

        read_count = 0
        id_field = []
        id_lists = []    # for checking ID duplication (= potential of 2nd lap) 
        id_buf = []
        mc_byte = 0
        id_ds_pos  = 0
        id_mfm_pos = 0
        mfm_count  = 0
        idx_count  = 0   # index mark count

        if self.log_level>0: print('**Search all ID')

        while True:
            ## Format parsing

            # set data separator mode
            if state == State.IDLE or state == State.CHECK_MARK:
                ds.set_mode(0)      # AM seeking - respond to SYNC patterns and missing clock & use HIGH_GAIN for VFO
            else:
                ds.set_mode(1)      # data reading - Ignore SYNC and missing clock patterns & use LOW_GAIN for VFO

            data, mc = ds.get_byte()
            if data == -1:
                break
            mfm_count += 1

            # State machine for IBM format parsing
            if state == State.IDLE: 
                if  mc == True:                 # found a missing clock
                    state = State.CHECK_MARK

            elif state == State.CHECK_MARK:
                if mc == True:                  # Skip missing clock data
                    mc_byte = data
                    continue
                elif mc_byte == 0xa1 and data in self.ID_ADDRESS_MARKS: # ID AM
                    if self.log_level>0: print('IDAM ', end='')
                    id_field = [ data ]
                    read_count = 4+2   # ID+CRC
                    id_ds_pos  = ds.get_pos()   # ID position in the interval buffer
                    id_mfm_pos = mfm_count-1
                    state = State.IDAM
                elif mc_byte == 0xc2 and data in self.INDEX_ADDRESS_MARKS:
                    if self.log_level>0: print('IDX_MARK')
                    idx_count += 1
                    if ds.get_time_ms() > self.spin_spd*1000:    # index_abort will be enabled from the 2nd lap
                        if idx_count > 1 and abort_by_idxmark:
                            if self.log_level>0: print('2nd index mark is detected - read aborted')
                            break
                else:
                    state = State.IDLE

            elif state == State.IDAM:           # ID Address Mark
                id_field.append(data)
                read_count -= 1
                if read_count == 0:
                    crc.reset()
                    crc.data(id_field)
                    if ds.get_time_ms() > self.spin_spd*1000:    # same_id_abort will be enabled from the 2nd lap
                        if id_field[1:-2] in id_lists and abort_by_sameid:     # abort when the identical ID is detected
                            if self.log_level>0: print('Abort by 2nd identical ID detection')
                            break
                    id_lists.append(id_field[1:-2])   # remove DataAM and CRC
                    if crc.get()==0:
                        id_buf.append(id_field[1:] + [True, id_ds_pos, id_mfm_pos])  #id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                        if self.log_level>0: print("CRC - OK ({:02x},{:02x},{:02x},{:02x}) - {}, {}".format(id_field[1], id_field[2], id_field[3], id_field[4], id_ds_pos, id_mfm_pos))
                        if self.log_level>1: self.dump_list_hex(id_field)
                    else:
                        id_buf.append(id_field[1:] + [False, id_ds_pos, id_mfm_pos])
                        if self.log_level>0: print("CRC - ERROR {}-{}".format(id_ds_pos, id_mfm_pos))
                        if self.log_level>1: self.dump_list_hex(id_field)
                    state = State.IDLE
        return id_buf


    def read_sector(self, sect_num, ds_pos=0):
        """
        Decode bistream track data  
        Args:  
            sect_num (int): sector number to read
            ds_pos (int): start data position of data separator. ID search start from this position of the interval data buffer. (default=0)
        Return:  
            (Status, Data-CRC, Data, DAM/DDAM) : Status(False=Not found), Data-CRC(False=Error), Data=sector data(list), DAM/DDAM(True=DAM)
        """
        class State(Enum):
            IDLE       = 0
            CHECK_MARK = 1
            INDEX      = 2
            IDAM       = 3
            DAM        = 4
            DDAM       = 5
            DATA_READ  = 6

        state = State.IDLE
        read_count = 0
        mc_byte = 0
        id_field = []
        sector = []

        ds = data_separator(self.bit_stream, clk_spd=self.clk_spd, spin_spd=self.spin_spd, high_gain=self.high_gain, low_gain=self.low_gain)    # Clock / Data separator
        ds.set_mode(0)      # AM seeking

        #ds_pos = max(0, ds_pos - (16*16))   # Rewind the sector read start position a bit
        #ds.set_pos(ds_pos)                  # sector search start position

        crc = CCITT_CRC()

        if self.log_level>0: print('**Read sector {:02x}'.format(sect_num))

        while True:
            # set data separator mode
            if state == State.IDLE or state == State.CHECK_MARK:
                ds.set_mode(0)      # AM seeking - respond to SYNC patterns and missing clock & use HIGH_GAIN for VFO
            else:
                ds.set_mode(1)      # data reading - Ignore SYNC and missing clock patterns & use LOW_GAIN for VFO

            data, mc = ds.get_byte()
            if data == -1:
                break

            # State machine for IBM format parsing
            if state == State.IDLE:
                if  mc == True:                 # found a missing clock
                    state = State.CHECK_MARK

            elif state == State.CHECK_MARK:
                if mc == True:                  # Skip missing clock data
                    mc_byte = data
                    continue
                elif mc_byte == 0xa1 and (data in self.ID_ADDRESS_MARKS): # ID AM
                    if self.log_level>0: print('IDAM ', end='')
                    id_field = [ data ]
                    read_count = 4+2   # ID+CRC
                    state = State.IDAM
                elif mc_byte == 0xc2 and data in self.INDEX_ADDRESS_MARKS:  # Index AM
                    state = State.INDEX
                elif data in self.DATA_ADDRESS_MARKS or data in self.DELETED_DATA_ADDRESS_MARKS:      # DataAM or DeletedDataAM
                    if len(id_field) < 4:
                        state = State.IDLE
                    elif id_field[2] == sect_num:       # check sector # match
                        if self.log_level>0:
                            if data in self.DATA_ADDRESS_MARKS: print('DAM ', end='')
                            else:                               print('DDAM', end='')
                        sector = [ data ]
                        address_mark = True if data==0xfb else False  # DAM=True, DDAM=False
                        read_count = self.SECTOR_LENGTH_LIST[id_field[3] % len(self.SECTOR_LENGTH_LIST)]
                        read_count += 2   # for CRC
                        state = State.DATA_READ
                    else:
                        state = State.IDLE
                else:
                    state = State.IDLE

            elif state == State.INDEX:          # Index Address mark
                if self.log_level>0: print('INDEX')
                state = State.IDLE
    
            elif state == State.IDAM:           # ID Address Mark
                id_field.append(data)
                read_count -= 1
                if read_count == 0:
                    crc.reset()
                    crc.data(id_field)
                    id_ = id_field.copy()
                    id_field = id_field[1:-2]   # remove IDAM and CRC
                    if crc.get()==0:
                        if self.log_level>0: print("CRC - OK ({:02x},{:02x},{:02x},{:02x})".format(id_field[0], id_field[1], id_field[2], id_field[3]))
                    else:
                        if self.log_level>0: print("CRC - ERROR")
                        if self.log_level>1: self.dump_list_hex(id_)
                        #ds.reset()
                    state = State.IDLE

            # Read sector data for DAM and DDAM
            elif state == State.DATA_READ:
                sector.append(data)
                read_count -= 1
                if read_count == 0:
                    crc.reset()
                    crc.data(sector)
                    if crc.get()==0:
                        if self.log_level>0: print("CRC - OK")
                        if self.log_level>1: self.dump_list_hex(sector)
                        return (True, True, sector[1:-2], address_mark)  # Status, Data-CRC, Data (except AM and CRCs), DAM/DDAM
                    else:
                        if self.log_level>0: print("CRC - ERROR")
                        if self.log_level>1: self.dump_list_hex(sector)
                        return (True, False, sector[1:-2], address_mark)  # Status, Data-CRC, Data (except AM and CRCs), DAM/DDAM

        return (False, False, [], False)  # Status, CRC, Data, DAM/DDAM  (Sector not found)



    def read_all_sectors(self, abort_by_idxmark=True, abort_by_sameid=True):
        """
        Read all sector data in a track  
        Return:  
        track : track = [[id_field, data-CRC_status, sect_data, DAM],...]
                            id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
        num_read (int): number of sector read 
        num_error (int): number of sector read and caused error (CRC)
        """
        num_read  = 0
        num_error = 0
        track = []

        if self.log_level==2:
            print('Read all sectors')

        # Find all ID address marks
        id_list = self.search_all_idam(abort_by_idxmark=abort_by_idxmark, abort_by_sameid=abort_by_sameid)

        # Read all secrors based on the IDAM search result
        for id_field in id_list:
            sect    = id_field[2]
            idcrc   = id_field[6]
            pos     = id_field[7] # ds_pos
            if idcrc == False:  # ID-CRC error but add ID to the data (to let the ID exist in the image)
                num_error += 1
                track.append([id_field, False, [], True]) # ID, CRC=Err, Data, DAM=DAM
                continue
            status, datacrc, sector, dam = self.read_sector(sect_num = sect, ds_pos = pos)
            if status == False:   # record not found
                num_error += 1
                track.append([id_field, False, [], True])  # ID, CRC, Data, DAM
                continue
            if datacrc == False:      # CRC error
                num_error += 1
                track.append([id_field, False, sector, dam])  # ID, CRC, Data, DAM
            else:
                num_read += 1
                track.append([id_field, True, sector, dam])  # ID, CRC, Data, DAM
        return track, num_read, num_error

