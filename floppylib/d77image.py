class d77_image:
    def __init__(self):
        pass

    def create_header(self, disk_name, wp_flag=0, disk_type=0):
        """
        Args:
          wp_flag = 0: no protect, 0x10: write protect
          disk_type = 0x00:2D, 0x10:2DD, 0x20:2HD
        """
        hdr = bytearray([0]*(0x20+ (4*164) + (4*164)))
        for p, c in enumerate(disk_name):
            hdr[p] = ord(c)
        hdr[0x1a] = wp_flag
        hdr[0x1b] = disk_type
        return hdr

    def create_sector(self, sect_data, c, h, r, n, num_sec, density=0, am=0, status=0, ext_status=0, id_crc1=0, id_crc2=0, pos=0):
        """
        Args:
          sect_data (list): sector data
          c, h, r, n: C/H/R/N (sector ID)
          num_sec: number sectors in this track
          density: 0x00: double, 0x40: single
          am: Address mark (0x00: Data Mark, 0x10: DDM)
          status: Disk BIOS status (0==no error)
          pos: Sector position in MFM byte count
        """
        sect_size = len(sect_data)
        sect = bytearray([c, h, r, n, 
                num_sec  % 0x100, 
                num_sec // 0x100, 
                density, 
                am, 
                status, 
                0, 0,         # sector position (WORD) placeholder
                ext_status, 
                id_crc1, id_crc2,
                sect_size  % 0x100, 
                sect_size // 0x100 ])
        self.set_word(sect, 0x09, pos)
        sect += bytearray(sect_data)
        return sect

    def set_dword(self, barray, pos, data):
        for i in range(4):
            barray[pos+i] = data & 0xff
            data >>= 8

    def set_word(self, barray, pos, data):
        for i in range(2):
            barray[pos+i] = data & 0xff
            data >>= 8

    def set_sect_table(self, hdr, track_num, data):
        """
        Set sect data offset to the offset table in the header of the d77 disk image
        """
        pos = 0x20 + track_num*4
        self.set_dword(hdr, pos, data)

    def set_track_table(self, hdr, track_num, data):
        """
        Set raw track data offset to the offset table in the header of the d77 disk image
        """
        pos = 0x2b0 + track_num*4
        self.set_dword(hdr, pos, data)

    def generate(self, disk_data, mfm_data=None, mc_data=None, disk_type=0, disk_name = 'DISK'):
        """
        Args:  
          disk_data : disk data
          track_img : track image data
          disk_type : 0=2D, 0x10=2DD, 0x20=2HD
          disk_name (string) : disk image name (not the file name)
        """
        img = self.create_header(disk_name, disk_type=disk_type)
        
        # Raw track data (D77 extension)
        if not mfm_data is None:
            if not mc_data is None:
                print('Adding raw track image data (MFM+MC)')
                img[0x11] = 0x10        # Raw track data extension flag
                track_num = 0
                # MFM+MC interleaved format  [MFM0, MC0, MFM1, MC1, ...]
                for i, (mfm, mc) in enumerate(zip(mfm_data, mc_data)):  # track_img[0]=mfm, track_img[1]=missing_clock
                    self.set_track_table(img, track_num, len(img))
                    buf = []
                    for _mfm, _mc in zip(mfm, mc):
                        buf += [_mfm, _mc]
                    track_len = len(buf)
                    _track = bytearray([0,0,0,0]+buf)
                    self.set_dword(_track, 0, track_len)        # set track data length
                    img += _track
                    track_num += 1
            else:
                print('Adding raw track image data (MFM only)')
                img[0x11] = 0x10        # Raw track data extension flag
                track_num = 0
                # MFM only format [ MFM0, MFM1, MFM2, ...]
                for mfm in mfm_data:
                    self.set_track_table(img, track_num, len(img))
                    buf = bytearray([ 0,0,0,0 ] + mfm)
                    self.set_dword(buf, 0, len(mfm))   # set track data length
                    img += buf
                    track_num += 1

        # Sector data
        for track_num, track in enumerate(disk_data):
            """
              track = [[id_field, Data-CRC_status, sect_data, DAM],...]
                        id_field = [ C, H, R, N, CRC1, CRC2, ID-CRC status, ds_pos, mfm_pos]
                        num_read (int): number of sector read 
                        num_error (int): number of sector read and caused error (CRC)
            """
            num_sects = len(track)
            if num_sects==0:
                continue
            self.set_sect_table(img, track_num, len(img))
            for sect in track:
                id_field   = sect[0]
                dt_crc_f   = sect[1]
                id_crc_f   = id_field[6]
                status     = 0x00 if dt_crc_f else 0xb0   # Data CRC error
                ext_status = 0x00 if id_crc_f else 0x01   # ID CRC error 
                am = 0 if sect[3] else 0x10
                sect_data = self.create_sector(
                    sect[2],                # Sector data
                    id_field[0], id_field[1], id_field[2], id_field[3], 
                    num_sects,
                    density=0, 
                    am=am,
                    status=status,
                    ext_status=ext_status,  # ID CRC error flag
                    id_crc1=id_field[4],    # ID CRC value
                    id_crc2=id_field[5],
                    pos = id_field[8])      # Sector pos in MFM byte count
                img += bytearray(sect_data)

        # set total disk image size
        self.set_dword(img, 0x001c, len(img))
        return img
