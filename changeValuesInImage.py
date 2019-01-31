# -*- coding: utf-8 -*-
import os,sys
from time import time
import argparse
import numpy as np
import nibabel




if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='changeValuesInImage')

    parser.add_argument('-i', '--input', help='Input image (required)', type=str, required = True)
    parser.add_argument('-a', '--area', help='Coordinates of the voxel area (point/rectangle/cube) to be replace (e.g. in 3D: x0, y0, z0, x1, y1, z1)', type=int, nargs='*', required = True)
    parser.add_argument('-o', '--output', help='Output image (default same as input)', type=str, default='', required = False)
    parser.add_argument('-v', '--value', help='New value to replace (default 0)', type=int, default=0, required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')


    try:
        print 'Input: '+args.input
        inputImage=nibabel.load(args.input)
        tmp=inputImage.get_data()
    except:
        print 'Input image file not found.'
        sys.exit()
    try:
        if 2*len(tmp.shape) != len(args.area):
            print 'The number of coordinates is not suitable to the input image dimensions.'
            sys.exit()
        if len(tmp.shape)==2:
            print 'Area: \tx -> '+str(args.area[0])+' to '+str(args.area[2])
            print '\t\ty -> '+str(args.area[1])+' to '+str(args.area[3])
            tmp[args.area[0]-1:args.area[2],args.area[1]-1:args.area[3]]=args.value
        elif len(tmp.shape)==3:
            print 'Area:\tx -> '+str(args.area[0])+' to '+str(args.area[3])
            print '\ty -> '+str(args.area[1])+' to '+str(args.area[4])
            print '\tz -> '+str(args.area[2])+' to '+str(args.area[5])
            tmp[args.area[0]-1:args.area[3],args.area[1]-1:args.area[4],args.area[2]-1:args.area[5]]=args.value
    except:
        print 'Area is out of index.'
        sys.exit()


    if args.output=='':
        nibabel.save(nibabel.Nifti1Image(tmp, inputImage.affine),args.input)
    else:
        try:
            nibabel.save(nibabel.Nifti1Image(tmp, inputImage.affine),args.output)
        except:
            print 'Output path does not exist.'
            sys.exit()
