
import sys

with open(sys.argv[1], 'r') as f:
    file=[]
    for line in f:
        #line = line.rstrip('\n')
        if len(line)==0:
            continue
        if '**TRACK_READ' in line:
            file.append(line)
        elif '**TRACK_END' in line:
            file.append(line)
        else:
            file.append('~' + line)

with open(sys.argv[1], 'w') as f:
    f.writelines(file)

