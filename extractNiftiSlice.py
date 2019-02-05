# -*- coding: utf-8 -*-
import sys
import argparse
import numpy as np
import nibabel



if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='extractNiftiSlice')

    parser.add_argument('-i', '--input', help='3D input image (required)', type=str, required = True)
    parser.add_argument('-pl', '--plane', help='Plane to be extract (\'x\' (sagittal), \'y\' (coronal) or \'z\' (axial)) (required)', type=str, required = True)
    parser.add_argument('-sl', '--slice', help='Slice to be saved (required)', type=int, required = True)
    parser.add_argument('-p', '--padding', help='Padding to avoid in the image', type=int, default=0, required = False)
    parser.add_argument('-o', '--output', help='Prefix added to input name for output image (default \'_pl-\' + plane_name + \'-\' + slice_number)', type=str, default='', required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')


    try:
        print 'Input: \t'+args.input
        inputImage=nibabel.load(args.input)
        input = inputImage.get_data()
    except:
        print 'Input image file not found'
        sys.exit()

    if len(input.shape)!=3:
        print 'Input image must be in 3D'
        sys.exit()

    if args.plane not in ['x','y','z']:
        print 'Plane parameter must be assign one of these value: \'x\' (sagittal), \'y\' (coronal) or \'z\' (axial)'
        sys.exit()

    if (args.slice<0) | ((args.slice>=input.shape[0])&(args.plane=='x')) | ((args.slice>=input.shape[1])&(args.plane=='y')) | ((args.slice>=input.shape[2])&(args.plane=='z')):
        print 'Slice is out of bound'
        sys.exit()

    try:
        if args.plane=='x':
            slice = input[args.slice+1, args.padding:-args.padding, args.padding:-args.padding]
        elif args.plane=='y':
            slice = input[args.padding:-args.padding, args.slice+1, args.padding:-args.padding]
        elif args.plane=='z':
            slice = input[args.padding:-args.padding, args.padding:-args.padding, args.slice+1]
    except:
        print 'Padding too large'
        sys.exit()

    try:
        if args.output=='':
            splitInput=args.input.split('.')
            if splitInput[-1]=='nii':
                inputName='.'.join(splitInput[:-1])
            elif splitInput[-2]=='nii':
                inputName='.'.join(splitInput[:-2])
            else:
                print 'Input file must be a nifti image'
                sys.exit()
            nibabel.save(nibabel.Nifti1Image(slice,inputImage.affine),inputName+'_pl-'+args.plane+'-'+str(args.slice)+'.nii.gz')
        else:
            nibabel.save(nibabel.Nifti1Image(slice,inputImage.affine),args.output)
    except:
        print 'Output path is not correct'
        sys.exit()
