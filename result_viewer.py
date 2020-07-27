import sys
import argparse
import random

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def main(args):
    x = []
    y = []
    z = []
    best_sector = 0
    best_error = 99999999
    with open(args.input, 'r') as f:
        for line in f:
            if not 'High' in line:
                line = line[:31]
                hg, lg, sect, err = [ float(a) for a in line.split(' ') ]
                try:
                    err_rate = err / (sect+err)
                except DivisionByZero:
                    err_rate = 0

                x.append(hg)
                y.append(lg)
                if args.metric == 'read':
                    z.append(sect)
                elif args.metric == 'err':
                    z.append(err)
                elif args.metric == 'rate':
                    z.append(err_rate)

                report = False
                if sect > best_sector:
                    best_sector = sect
                    report = True
                if err < best_error:
                    best_error = err
                    report = True
                if report == True:
                    str = '{:10.8f} {:10.8f} {:04} {:04}'.format(hg, lg, sect, err)
                    print(str)

    # 3D scatter plot
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_xlabel('high gain')
    ax.set_ylabel('low_gain')
    ax.set_zlim(0,max(z))
    ax.plot(x, y, z, marker='o', linestyle='None')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=False, default='log.txt', help='optimizer log file path (default=log.txt)')
    parser.add_argument('--metric', type=str, default='err', required=False, help='plot metric: \'read\'=successfully read sectors, \'err\'=error sectors, \'rate\'=error rate', )
    args = parser.parse_args()

    metric_options = ['read', 'err', 'rate']
    if not args.metric in metric_options:
        print('--metric must be one of ', metric_options)
        sys.exit(-1)

    main(args)