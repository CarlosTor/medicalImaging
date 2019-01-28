# -*- coding: utf-8 -*-
import os,sys
from time import time
import argparse
import numpy as np
import nibabel
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from scipy import ndimage

def forceAspect(ax,aspect=1):
    im=ax.get_images()
    extent=im[0].get_extent()
    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)


if __name__ == '__main__':


    parser = argparse.ArgumentParser(prog='sliceScreenShot')

    parser.add_argument('-i', '--input', help='Input image (required)', type=str, required = True)
    parser.add_argument('-sl', '--slice', help='Slice to be saved (required)', type=int, required = True)
    parser.add_argument('-pl', '--plane', help='Plane to be saved (\'x\', \'y\' or \'z\') (required)', type=str, required = True)
    parser.add_argument('-o', '--output', help='Output screen shot (required)', type=str, default='', required = True)
    parser.add_argument('-f', '--format', help='Format image', type=str, default='png', required = False)
    parser.add_argument('-e', '--equal', help='Equal width and height', type=int, default=0, required = False)
    parser.add_argument('-n', '--normalise', help='Normalise the intensity levels', type=int, default=0, required = False)
    parser.add_argument('-c', '--contrast', help='Maximum intensity value for enhancing contrast', type=int, default=0, required = False)
    parser.add_argument('-fd', '--fourthDimension', help='Value of the 4th dimension, in case of 4D input image', type=int, default=0, required = False)
    parser.add_argument('-p', '--padding', help='Padding to avoid in the image', type=int, default=0, required = False)
    parser.add_argument('-cb', '--colorbar', help='Active the colorbar', type=int, default=0, required = False)
    parser.add_argument('-cm', '--cmap', help='Color map of the screenshot (\'grey\' or \'color\)', type=str, default='gray', required = False)



    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')



    inputImage=nibabel.load(args.input)


    tmp=inputImage.get_data()
    if (len(tmp.shape)==2):
        pixdim=inputImage.header['pixdim'][1:3]
        tmp=inputImage.get_data()[args.padding:tmp.shape[0]-args.padding, args.padding:tmp.shape[1]-args.padding]
    elif ((len(tmp.shape)>2) & (tmp.shape[2]==1)):
        tmp=inputImage.get_data()[args.padding:tmp.shape[0]-args.padding, args.padding:tmp.shape[1]-args.padding,0]
        pixdim=inputImage.header['pixdim'][1:3]
    else:
        if len(tmp.shape)==4:
            tmp=inputImage.get_data()[args.padding:tmp.shape[0]-args.padding, args.padding:tmp.shape[1]-args.padding, args.padding:tmp.shape[2]-args.padding, args.fourthDimension]
        else:
            tmp=inputImage.get_data()[args.padding:tmp.shape[0]-args.padding, args.padding:tmp.shape[1]-args.padding, args.padding:tmp.shape[2]-args.padding]

        if args.plane=='x':
            tmp=ndimage.rotate(np.transpose(tmp[args.slice,:,:]),90)
            pixdim=inputImage.header['pixdim'][2:4]
        elif args.plane=='y':
            tmp=tmp[:,args.slice,:]
            pixdim=[inputImage.header['pixdim'][1],inputImage.header['pixdim'][3]]
        elif args.plane=='z':
            tmp=tmp[:,:,args.slice]
            pixdim=inputImage.header['pixdim'][1:3]



    if args.normalise==1:
        tmp/=np.max(tmp)

    w,h=tmp.shape[0]*pixdim[0]/(pixdim[0]*6),tmp.shape[1]*pixdim[1]/(pixdim[0]*6)

    fig=plt.figure(frameon=False)
    fig.set_size_inches(w,h)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    if args.cmap=='gray':
        cmap='gray'
    else:
        cmap='plasma' #Set1

    if args.contrast>0:
        im=ax.imshow(ndimage.rotate(tmp, 90), cmap=cmap, aspect='auto', clim=(0.0, args.contrast))
    else:
        im=ax.imshow(ndimage.rotate(tmp, 90), cmap=cmap, aspect='auto')
    if args.equal==2:
        forceAspect(ax,aspect=1)

    if args.colorbar==1:
        cbar=fig.colorbar(im, extend='both')#, shrink=0.9)#, ax=ax)
        cbar.ax.tick_params(labelsize=50)
    plt.savefig(args.output+'_'+args.plane+str(args.slice)+'.'+args.format)
