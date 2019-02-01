# -*- coding: utf-8 -*-
import sys
import argparse
import numpy as np
import nibabel



if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='ApplyMask2Nifti')

    parser.add_argument('-i', '--input', help='Input image (required, accepted multiple times)', type=str, nargs='*', required = True)
    parser.add_argument('-m', '--mask', help='Mask image to be applied into input image', type=str, required = True)
    parser.add_argument('-o', '--output', help='Prefix added to input name for output image (default \'_masked\')', type=str, default='_masked', required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')


    try:
        print 'Input: \t'+args.input[0]
        if len(args.input)>1:
            for i in args.input[1:]:
                print '\t'+i
        input=list()
        inputImage=nibabel.load(args.input[0])
        for i in args.input:
            input.append(nibabel.load(i).get_data())
    except:
        print 'Input image file not found.'
        sys.exit()
    try:
        print 'Mask: \t'+args.mask
        maskImage=nibabel.load(args.mask)
        mask=maskImage.get_data()
        for i in input:
            if mask.shape!=i.shape:
                print 'Mask must have same size as input'
                sys.exit()
    except:
        print 'Mask image file not found.'
        sys.exit()



    for i,im in enumerate(input):
        im[mask==0]=0
        splitInput=args.input[i].split('.')
        if splitInput[-1]=='nii':
            inputName='.'.join(splitInput[:-1])
        elif splitInput[-2]=='nii':
            inputName='.'.join(splitInput[:-2])
        else:
            print 'Input file must be a nifti image'
            sys.exit()
        nibabel.save(nibabel.Nifti1Image(im,inputImage.affine),inputName+args.output+'.nii.gz')
