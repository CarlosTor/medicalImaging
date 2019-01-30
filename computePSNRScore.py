# -*- coding: utf-8 -*-
import sys
import argparse
import numpy as np
import nibabel



if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='computePSNRScore')

    parser.add_argument('-i', '--input', help='Input image (required)', type=str, required = True)
    parser.add_argument('-r', '--reference', help='Reference image (required)', type=str, required = True)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')

    try:
        print 'input: '+args.input
        input=nibabel.load(args.input).get_data()
    except:
        print 'Input image file not found.'
        sys.exit()
    try:
        print 'reference: '+args.reference
        reference=nibabel.load(args.reference).get_data()
    except:
        print 'Ground truth image file not found.'
        sys.exit()


    ###--Compute PSNR--###
    MSE=np.mean((reference-input)**2)
    PSNR=10*np.log10(np.max(reference)**2/MSE)
    PSNR=10*np.log10(1.0/MSE)

print 'PSNR score: '+str(PSNR)+' dB'
