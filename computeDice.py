# -*- coding: utf-8 -*-
import os,sys
from time import time
import argparse
import numpy as np
import nibabel
import nipype.algorithms.metrics as nipalg



def fuzzy_dice(rfile,ifile):

    overlap = nipalg.FuzzyOverlap()
    overlap.inputs.in_ref = [rfile] #e.g. [ 'ref_class0.nii', 'ref_class1.nii' ]
    overlap.inputs.in_tst = [ifile] #e.g. [ 'tst_class0.nii', 'tst_class1.nii' ]
    overlap.inputs.weighting = 'none'
    res = overlap.run()

    return res.outputs.dice


if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='computeDice')

    parser.add_argument('-i', '--input', help='Input image (required)', type=str, required = True)
    parser.add_argument('-r', '--reference', help='Reference image (required)', type=str, required = True)
    parser.add_argument('-t', '--threshold', help='Threshold level in order to binarized input image', type=float, default=0, required = False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')

    if args.threshold==0:
        print fuzzy_dice(args.reference,args.input)
    else:
        inputFull=nibabel.load(args.input)
        input=inputFull.get_data()
        input=1*(input>args.threshold)
        inputSplit=args.input.split('.')
        if inputSplit[-1]=='nii':
            inputJoin='.'.join(inputSplit[:-1])
        elif inputSplit[-2]=='nii':
            inputJoin='.'.join(inputSplit[:-2])
        inputPath=inputJoin+'_t'+str(args.threshold)+'.nii.gz'
        nibabel.save(nibabel.Nifti1Image(input,inputFull.affine),inputPath)
        print fuzzy_dice(args.reference,inputPath)
