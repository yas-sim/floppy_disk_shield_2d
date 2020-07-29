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

def get_header(img):
    image_name = get_asciiz(img, 0)
    write_protect = img[0x1a]
    disk_type = img[0x1b]
    disk_size = get_dword(img, 0x1c)
    raw_track = img[0x11]
    hdr= { 'name'          : image_name, 
           'write_protect' : 'ON' if write_protect==0x10 else 'OFF',
           'disk_type'     : '2D' if disk_type==0 else '2DD' if disk_type==0x10 else '2HD',
           'disk_size'     : '0x'+format(disk_size, '08X'),
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
    data         = img[ofst:ofst+size+1]
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

def decode_d77(file):
    with open(file, 'rb') as f:
        img = f.read()

    d77 = {}

    # Extract Header information
    d77['header'] = get_header(img)

    # Extract track offset
    trk_ofst = [0]*164
    for t in range(164):
        trk_ofst[t] = get_dword(img, 0x20 + t*4)
        #print('{} {:08X}'.format(t, trk_ofst[t]))
    d77['trk_ofst'] = trk_ofst

    # Extract sector data
    disk = []
    for t in range(164):
        disk.append([])
        ofst = trk_ofst[t]
        if ofst == 0:
            continue
        sect = get_sect(img, ofst)
        num_sect = sect['num_sec']
        for i in range(num_sect):
            sect = get_sect(img, ofst)
            disk[-1].append(sect)
            ofst += 0x10 + sect['size']
    d77['disk'] = disk
    return d77
