def get_asciiz(barray, pos):
    str=''
    while barray[pos] != 0:
        str += chr(barray[pos])
        pos += 1
    return str

def get_dword(barray, pos):
    val=0
    for i in range(3, -1, -1):
        val = val<<8 | barray[pos+i]
    return val

def get_word(barray, pos):
    val=0
    for i in range(1, -1, -1):
        val = val<<8 | barray[pos+i]
    return val

def set_dword(barray, pos, dt):
    for i in range(4):
        barray[pos + i] = (dt & 0xff)
        dt >>= 8

def set_word(barray, pos, dt):
    for i in range(2):
        barray[pos + i] = (dt & 0xff)
        dt >>= 8


def get_header(img):
    image_name = get_asciiz(img, 0)
    write_protect = img[0x1a]
    disk_type = img[0x1b]
    disk_size = get_dword(img, 0x1c)
    raw_track = img[0x11]
    hdr= { 'name'          : image_name, 
           'write_protect' : 'ON' if write_protect==0x10 else 'OFF',
           'disk_type'     : '2D' if disk_type==0 else '2DD' if disk_type==0x10 else '2HD',
           'disk_size'     : disk_size,
           'raw_track'     : 'Supported' if raw_track==0x10 else 'Not supported'
         }
    return hdr

def get_sect(img, ofst):
    CHRN         = img[ofst:ofst+4]
    num_sec      = get_word(img, ofst + 0x04)
    density      = img[ofst + 0x06]
    address_mark = img[ofst + 0x07]
    status       = img[ofst + 0x08]
    pos          = get_word(img, ofst + 0x09)
    ext_sta      = img[ofst + 0x0b]
    size         = get_word(img, ofst + 0x0e)
    id_crc_val   = img[ofst + 0x0c]<<8 | img[ofst + 0x0d]
    data         = img[ofst+0x10 : ofst+0x10+size]
    return { 'CHRN' : '{}:{}:{}:{}'.format(*CHRN),
              'num_sec' : num_sec,
              'density' : 'D' if density==0 else 'S',
              'status' : status,
              'am' : address_mark,
              'ext_sta': ext_sta,
              'id_crc_val': id_crc_val,
              'pos': pos,
              'size' : size,
              'data' : data }

def is_raw_track_supported(img):
    return True if img[0x11] == 0x10 else False

def get_track_offset(img, trk):
    return get_dword(img, 0x0020 + trk*4)

def get_raw_track_offset(img, trk):
    if is_raw_track_supported(img):
        return get_dword(img, 0x0020 + (4*164) + trk*4)
    return -1

def get_raw_track_data(img, trk):
    if is_raw_track_supported(img):
        ofst = get_raw_track_offset(img, trk)
        if ofst == 0:
            return bytearray([])
        size = get_dword(img, ofst)
        if size > 0x2800:
            print('Too large image {:x} {:x}'.format(ofst, size))
            return bytearray([])
        return img[ofst : ofst + size + 1]
    return bytearray([])



def decode_d77(img):
    d77 = {}

    # Extract Header information
    d77['header'] = get_header(img)

    # Extract track (sector data) offset
    trk_ofst = [0]*164
    for t in range(164):
        trk_ofst[t] = get_dword(img, 0x0020 + t*4)
    d77['trk_ofst'] = trk_ofst

    if is_raw_track_supported(img):       # Raw track image data is supported
        # Extract raw track image data offset
        raw_trk_ofst = [0]*164
        for t in range(164):
            raw_trk_ofst[t] = get_raw_track_offset(img, t)
        d77['raw_trk_ofst'] = raw_trk_ofst
    
        # Extract raw track image data
        d77['raw_trk_data'] = {}
        for t in range(164):
            d77['raw_trk_data'][t] = get_raw_track_data(img, t)

    # Extract sector data
    disk = {}
    for t in range(164):
        key = t
        disk[key] = []
        ofst = get_track_offset(img, t)
        if ofst == 0:
            continue
        sect = get_sect(img, ofst)
        num_sect = sect['num_sec']
        for i in range(num_sect):
            sect = get_sect(img, ofst)
            disk[key].append(sect)
            ofst += 0x10 + sect['size']
    d77['disk'] = disk
    return d77

def encode_d77(d77dic):
    d77hdr = d77dic['header']
    name  = bytearray('{:16}\0'.format(d77hdr['name']).encode('UTF-8'))         # Image name
    raw_track     = 0x10 if d77hdr['raw_track']=='Supported' else 0x00
    write_protect = 0x10 if d77hdr['write_protect']=='ON'    else 0x00
    disk_type     = 0x10 if d77hdr['disk_type']=='2DD'       else 0x20 if d77hdr['disk_type']=='2HD' else 0x00
    reserve       = 0
    hdr = name + bytearray([raw_track, 
                reserve, reserve, reserve, reserve, reserve, reserve, reserve, reserve, 
                write_protect, disk_type, 0, 0, 0, 0 ])  # The last 4 zeros are disk size place holder

    d77img = hdr + bytearray([0,0,0,0]*164)   # sector data table

    # raw track image data
    if raw_track == 0x10:
        d77img += bytearray([0,0,0,0]*164)   # raw track image data table
        tracks = d77dic['raw_trk_data']
        for trk_key, track_img in tracks.items():
            if track_img is None: continue
            trk_data = bytearray([0,0,0,0]) + track_img               # 1st 4 bytes are for track image size (DWORD)
            set_dword(trk_data, 0, len(track_img))                    # raw track image size
            set_dword(d77img, 0x0020 + (4*164) + int(trk_key)*4, len(d77img))    # raw track image data offset
            d77img += trk_data

    # sector data
    tracks = d77dic['disk']
    for trk_key, sects in tracks.items():
        if len(sects)==0: continue
        set_dword(d77img, 0x20 + int(trk_key)*4, len(d77img))    # set track data (sector data) offset table
        for sect in sects:
            c, h, r, n = sect['CHRN'].split(':')
            density = 0x00 if sect['density'] == 'D' else 0x40
            sect_data = bytearray([int(c), int(h), int(r), int(n),
                    0,0,                                # place holder for number of sectors (WORD)
                    density, sect['am'], sect['status'],
                    0,0,                                # place holder for sector position (D77mod extension)
                    0,                                  # place holder for extra status data (D77mod extension, ID_CRC error flag) 
                    0,0,                                # place holder for ID CRC value (D77mod extension)
                    0,0 ])                              # place holder for sector size
            set_word(sect_data, 0x04, sect['num_sec'])
            set_word(sect_data, 0x0e, sect['size'])
            if 'pos'        in sect.keys(): set_word(sect_data, 0x09, sect['pos'])
            if 'ext_sta'    in sect.keys(): sect_data[0x0b] = sect['ext_sta']
            if 'id_crc_val' in sect.keys():
                sect_data[0x0c] = (sect['id_crc_val']>>8) & 0xff 
                sect_data[0x0d] = (sect['id_crc_val']   ) & 0xff
            if sect['size']>0:
                d77img += sect_data + sect['data']
            else:
                d77img += sect_data                     # zero length sector (ID only)

    set_dword(d77img, 0x1c, len(d77img))   # D77 image size

    return d77img
