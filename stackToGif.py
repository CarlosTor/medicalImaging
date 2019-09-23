# -*- coding: utf-8 -*-

import sys
import imageio
import argparse
import numpy as np

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='stackToGif')

    parser.add_argument('-i', '--input', help = 'Input pattern name of stack frame, without format and with a \'XX\' where the number \
                            of frame is located (required)', type = str, nargs='*', required = True)
    parser.add_argument('-o', '--output', help = 'Output name of gif file, without format ', type = str, default = '', required = False)
    parser.add_argument('-f', '--format', help = 'Format of images (required)', type = str, default = 'png', required = False)
    parser.add_argument('-b', '--begin', help = 'First frame', type = int, default = 0, required = False)
    parser.add_argument('-e', '--end', help = 'Last frame (required)', type = int, required = True)
    parser.add_argument('-t', '--timeframe', help = 'Time per frame (in seconds)', type = float, default = 0.1, required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')

    ipathList = list()
    filename1List = list()
    filename2List = list()
    for fullInput in args.input:

        input = fullInput.split('/')
        ipath = '/'.join(input[:-1])

        if ipath != '':
            ipath = ipath+'/'
        filename = input[-1]
        f = filename.split('XX')

        if len(f) <= 2:
            filename1 = f[0]
            if len(f) == 2:
                filename2 = f[1]
            else:
                filename2 = ''
        else:
            print 'Error in the input name'
            sys.exit()

        if args.output == '':
            output = ipath+filename1+str(args.end)+filename2
        else:
            output = args.output

        ipathList.append(ipath)
        filename1List.append(filename1)
        filename2List.append(filename2)

    size = imageio.imread(ipathList[0]+filename1List[0]+str(args.begin)+filename2List[0]+'.'+args.format).shape
    sqrt = len(args.input)**0.5
    row = int(round(sqrt))
    col = int(sqrt)
    frame = np.zeros((size[0]*row, size[1]*col))

    frames = list()
    for i in range(args.begin,args.end+1):
        sel = 0
        frame = np.zeros((size[0]*row, size[1]*col, 4)).astype(np.uint8)
        for r in range(row):
            for c in range(col):
                im = imageio.imread(ipathList[sel]+filename1List[sel]+str(i)+filename2List[sel]+'.'+args.format)
                if len(im.shape) == 2:
                    newIm = np.zeros((im.shape[0],im.shape[1],4))
                    for k in range(4):
                        newIm[:,:,k] = im
                    im = newIm
                frame[size[0]*r:size[0]*(r+1),size[1]*c:size[1]*(c+1),:] = im
                sel += 1
        frames.append(frame)
    imageio.mimsave(output+'.gif', frames, 'GIF', duration=args.timeframe)
