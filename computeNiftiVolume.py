# -*- coding: utf-8 -*-
import sys
import argparse
import numpy as np
import nibabel
from skimage import filters



if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='computeDICEScore')

    parser.add_argument('-i', '--input', help='3D input image (required)', type=str, required=True)
    parser.add_argument('-s', '--segmentation', help='Segmentation map with one or more labels \
                            (default, Otsu\'s thresholding)', type=str, required=False)


    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')


    try:
        print('Input file: '+args.input)
        tmp = nibabel.load(args.input)
        input = tmp.get_data()
        affineMatrix = tmp.affine
        voxelSize = tmp.header['pixdim'][1:4]
        print('Voxel size: '+str(voxelSize))
    except:
        print('Input image file not found.')
        sys.exit()

    try:
        print('Segmentation file: '+args.segmentation)
        segmentation = nibabel.load(args.segmentation).get_data()
        if segmentation.shape!=input.shape:
            print('Error: Size of input image and segmentation map are not equal.')
            sys.exit()
    except:
        print('Segmentation file has not been provided or found. Applying Otsu\'s thresholding')
        otsuThreshold = filters.threshold_otsu(input)
        print('\tOtsu\'s threshold: '+str(otsuThreshold))
        segmentation = np.array(1 * (input>=otsuThreshold), dtype=np.float32)



    labels = list(np.unique(segmentation))
    try:
        labels.remove(0)
    except:
        print('Background of the segmentation map not detected (level 0).')
        sys.exit()
    numLabels = len(labels)

    print('\nResults:')
    for l in labels:
        numVoxels = len(input[segmentation==l])
        volume = numVoxels*voxelSize.prod()
        print('\tLabel '+str(int(l))+' has '+str(numVoxels)+' voxels, '+str(volume)+' mm^3')
