# -*- coding: utf-8 -*-
import sys
import argparse
import numpy as np
import nibabel
from skimage import filters



if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='thresholdNifti')

    parser.add_argument('-i', '--input', help='Input image (required, accepted multiple times)', type=str, nargs='*', required = True)
    parser.add_argument('-t', '--threshold', help='Threshold value (default Otsu method)', type=float, nargs='*', default=[-1], required = False)
    parser.add_argument('-o', '--output', help='Prefix added to input name for output image (default \'_th\' + threshold_value)', type=str, default='_th', required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')




if __name__ == '__main__':



    try:
        print('Input: \t'+args.input[0])
        if len(args.input)>1:
            for i in args.input[1:]:
                print('\t'+i)
        input=list()
        inputImage=nibabel.load(args.input[0])
        for i in args.input:
            input.append(nibabel.load(i).get_data())
    except:
        print('Input image file not found.')
        sys.exit()

    if len(args.threshold)>1:
        if len(args.threshold)!=len(input):
            print('Number of thresholds does not correspond to the number of inputs')
            sys.exit()
        else:
            thresholds=list()
            for i,th in enumerate(args.threshold):
                if th<0:
                    thresholds.append(filters.threshold_otsu(input[i]))
                else:
                    thresholds.append(th)
    else:
        if args.threshold[0]<0:
            thresholds = filters.threshold_otsu(input[0])*np.ones(len(input))
        else:
            thresholds = args.threshold[0]*np.ones(len(input))


    for i,im in enumerate(input):
        im[im<thresholds[i]]=0
        im[im>=thresholds[i]]=1
        splitInput=args.input[i].split('.')
        if splitInput[-1]=='nii':
            inputName='.'.join(splitInput[:-1])
        elif splitInput[-2]=='nii':
            inputName='.'.join(splitInput[:-2])
        else:
            print('Input file must be a nifti image')
            sys.exit()
        nibabel.save(nibabel.Nifti1Image(im,inputImage.affine),inputName+args.output+str(thresholds[i])+'.nii.gz')
