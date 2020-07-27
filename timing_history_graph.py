# timing history graph

import cv2
import numpy as np

disk_data = 'trk-01-0.txt'
#disk_data = 'putty/4.log'

with open(disk_data, 'r') as f:
    linebuf = ''
    for line in f:
        line = line.rstrip('\n')
        if '**TRACK_READ' in line:
            trk, side = [ int(v) for v in line.split(' ')[1:] ]
            #print(trk, side, " ", end='')
            linebuf = ''
        elif '**TRACK_END' in line:
            if len(linebuf)==0:
                continue
            interval_buf = [ ord(c)-ord(' ') for c in linebuf ]

            val_max = 64
            ystep=1
            xstep = 4
            cell = 8
            height = 400
            writer = cv2.VideoWriter('history.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (val_max*xstep, height))

            count=0
            img = np.zeros((height, val_max * xstep, 3), dtype=np.uint8)
            for y, i in enumerate(interval_buf):
                count+=1
                if count % 100==0:
                    writer.write(img)
                    cv2.imshow('history', img)
                    if cv2.waitKey(1)==27: break
                    img[:-1, :, :] = img[1:, :, :]  # scroll up
                    img[-1, :, :] = [0,0,0]
                    for j in range(2,4+1):
                        img[-1, j * cell * xstep, :] = [ 0, 0, 255 ]
                    for j in range(1,4+1):
                        img[-1, int((j+0.5) * cell * xstep), :] = [ 255, 0, 0 ]
                img[-1, i * xstep, : ] = [ 255, 255, 255]
                #cv2.imwrite('history.png', img)
            break
        else:
            linebuf += line