# -*- coding: utf-8 -*-
import os,sys
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
    parser.add_argument('-pl', '--plane', help='Plane to be saved (\'x\' (sagittal), \'y\' (coronal) or \'z\' (axial)) (required)', type=str, required = True)
    parser.add_argument('-o', '--output', help='Output screen shot (required)', type=str, default='', required = True)
    parser.add_argument('-f', '--format', help='Format image', type=str, default='png', required = False)
    parser.add_argument('-e', '--equal', help='Equal width and height', type=int, default=0, required = False)
    parser.add_argument('-n', '--normalise', help='Normalise the intensity levels', type=int, default=0, required = False)
    parser.add_argument('-c', '--contrast', help='Maximum intensity value for enhancing contrast', type=float, default=0, required = False)
    parser.add_argument('-fd', '--fourthDimension', help='Value of the 4th dimension, in case of 4D input image', type=int, default=0, required = False)
    parser.add_argument('-p', '--padding', help='Padding to avoid in the image', type=int, nargs='*' ,default=0, required = False)
    parser.add_argument('-cb', '--colorbar', help='Active the colorbar with a positive integer different than 0', type=int, default=0, required = False)
    parser.add_argument('-cm', '--cmap', help='Color map of the screenshot (\'gray\' or \'color\)', type=str, default='gray', required = False)
    parser.add_argument('-seg', '--segmentation', help='Segmentation image', type=str, nargs='*', default='', required = False)
    parser.add_argument('-segcol', '--segmentationcolor', help='RGB color array of the segmentation image (given an array of length 3 and maximum 1: red, green and blue)', type=float, nargs='*', default=[1,0,0], required = False)
    parser.add_argument('-segtr', '--segmentationtransparent', help='Active the transparent overlap segmentation image (0: no, 1: yes)', type=int, default=0, required = False)
    parser.add_argument('-segfd', '--segFourthDimension', help='Value of the 4th dimension, in case of 4D segmentation image', type=int, default=0, required = False)
    parser.add_argument('-cr', '--crop', help='Coordinates of the image in order to crop (e.g. x0, y0, x1, y1, or x0 x1 z0 z1)', type=int, nargs='*', default=[0,0,0,0], required = False)



    args = parser.parse_args()
    np.seterr(divide='ignore', invalid='ignore')


    inputImage = nibabel.load(args.input)

    if np.sum(args.crop)==0:
        if (args.plane=='z') | (inputImage.shape==2):
            crop = [0,0,inputImage.shape[0],inputImage.shape[1]]
        if (args.plane=='x'):
            crop = [0,0,inputImage.shape[1],inputImage.shape[2]]
        if (args.plane=='y'):
            crop = [0,0,inputImage.shape[0],inputImage.shape[2]]
    elif len(args.crop)==4:
        crop = args.crop
    else:
        print('Crop coordinates must be sized 4 (2D) or 6 (3D)')
        sys.exit()

    tmp=inputImage.get_data()
    if isinstance(args.padding, int):
        padding = args.padding*np.ones(2*len(inputImage.get_data().shape),dtype='int')
    elif len(args.padding)==len(inputImage.get_data().shape):
        list = range(len(inputImage.get_data().shape))+range(len(inputImage.get_data().shape))
        list.sort()
        padding = np.array([args.padding[i] for i in list])
    else:
        padding = args.padding

    if len(padding)!=2*len(inputImage.get_data().shape):
        print('Length of padding array must be equal to the input dimension x2')
        sys.exit()

    if (len(tmp.shape)==2):
        pixdim=inputImage.header['pixdim'][1:3]
        tmp=inputImage.get_data()[crop[0]+padding[0]:crop[2]-padding[1], crop[1]+padding[2]:crop[3]-padding[3]]
    elif ((len(tmp.shape)>2) & (tmp.shape[2]==1)):
        tmp=inputImage.get_data()[crop[0]+padding[0]:crop[2]-padding[1], crop[1]+padding[2]:crop[3]-padding[3],0]
        pixdim=inputImage.header['pixdim'][1:3]
    else:
        if len(tmp.shape)==4:
            tmp=inputImage.get_data()[padding[0]:tmp.shape[0]-padding[1], padding[2]:tmp.shape[1]-padding[3], padding[4]:tmp.shape[2]-padding[5], args.fourthDimension]
        else:
            tmp=inputImage.get_data()[padding[0]:tmp.shape[0]-padding[1], padding[2]:tmp.shape[1]-padding[3], padding[4]:tmp.shape[2]-padding[5]]

        if args.plane=='x':
            tmp=ndimage.rotate(np.transpose(tmp[args.slice,crop[0]:crop[2],crop[1]:crop[3]]),90)
            pixdim=inputImage.header['pixdim'][2:4]
        elif args.plane=='y':
            tmp=tmp[crop[0]:crop[2],args.slice,crop[1]:crop[3]]
            pixdim=[inputImage.header['pixdim'][1],inputImage.header['pixdim'][3]]
        elif args.plane=='z':
            tmp=tmp[crop[0]:crop[2],crop[1]:crop[3],args.slice]
            pixdim=inputImage.header['pixdim'][1:3]


    if args.normalise==1:
        tmp/=np.max(tmp)


    if args.colorbar!=0:
        w,h=tmp.shape[0]*pixdim[0]/(pixdim[0]*6)+10,tmp.shape[1]*pixdim[1]/(pixdim[0]*6)
    else:
        w,h=tmp.shape[0]*pixdim[0]/(pixdim[0]*6),tmp.shape[1]*pixdim[1]/(pixdim[0]*6)



    if args.segmentation!='':
        if args.segmentationtransparent not in [0,1]:
            print('Transparency option for the segmentation overlap must be 0 or 1.')
            sys.exit()
        if len(args.segmentationcolor)!=3:
            print('Length of the RGB color array for segmentation overlap must be 3.')
            sys.exit()
        #Ensure that RGB color array contains only positive numbers#
        segmentationcolor=[abs(segcolor) for segcolor in args.segmentationcolor]

        if isinstance(args.segmentation, list):
            tmp = tmp/np.max(tmp)
            RGB = np.zeros((tmp.shape[0],tmp.shape[1],3))
            RGB[:,:,0]=tmp
            RGB[:,:,1]=tmp
            RGB[:,:,2]=tmp

            for i,seg in enumerate(args.segmentation):
                mask = nibabel.load(seg).get_data()
                if len(mask.shape)==4:
                    mask = nibabel.load(seg).get_data()[:,:,:,args.segFourthDimension]

                if args.plane=='x':
                    mask=ndimage.rotate(np.transpose(mask[args.slice,crop[0]+padding[2]:crop[2]-padding[3],crop[1]+padding[4]:crop[3]-padding[5]]),90)
                elif args.plane=='y':
                    mask=mask[crop[0]+padding[0]:crop[2]-padding[1],args.slice,crop[1]+padding[4]:crop[3]-padding[5]]
                elif args.plane=='z':
                    mask=mask[crop[0]+padding[0]:crop[2]-padding[1],crop[1]+padding[2]:crop[3]-padding[3],args.slice]

                #Fill color#
                maxsegcolor = np.max(segmentationcolor)
                RGB[mask>1e-6,0] *= segmentationcolor[0]
                RGB[mask>1e-6,1] *= segmentationcolor[1]
                RGB[mask>1e-6,2] *= segmentationcolor[2]
                #No transparency#
                if args.segmentationtransparent==0:
                    RGB[mask>1e-6,0] = segmentationcolor[0]
                    RGB[mask>1e-6,1] = segmentationcolor[1]
                    RGB[mask>1e-6,2] = segmentationcolor[2]

        else:
            mask = nibabel.load(args.segmentation).get_data()
            tmp = tmp/np.max(tmp)
            RGB = np.zeros((tmp.shape[0],tmp.shape[1],3))
            RGB[:,:,0]=tmp
            RGB[:,:,1]=tmp
            RGB[:,:,2]=tmp

            if len(mask.shape)==4:
                mask = mask[:,:,:,args.segFourthDimension]

            if args.plane=='x':
                mask=ndimage.rotate(np.transpose(mask[args.slice,crop[0]+padding[2]:crop[2]-padding[3],crop[1]+padding[4]:crop[3]-padding[5]]),90)
            elif args.plane=='y':
                mask=mask[crop[0]+padding[0]:crop[2]-padding[1],args.slice,crop[1]+padding[4]:crop[3]-padding[5]]
            elif args.plane=='z':
                mask=mask[crop[0]+padding[0]:crop[2]-padding[1],crop[1]+padding[2]:crop[3]-padding[3],args.slice]

            #Fill color#
            maxsegcolor = np.max(segmentationcolor)
            RGB[mask>1e-6,0] *= segmentationcolor[0]
            RGB[mask>1e-6,1] *= segmentationcolor[1]
            RGB[mask>1e-6,2] *= segmentationcolor[2]
            #No transparency#
            if args.segmentationtransparent==0:
                RGB[mask>1e-6,0] = segmentationcolor[0]
                RGB[mask>1e-6,1] = segmentationcolor[1]
                RGB[mask>1e-6,2] = segmentationcolor[2]


        tmp = RGB


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
        im=ax.imshow(ndimage.rotate(tmp, angle = 90), cmap=cmap, aspect='auto', clim=(0.0, args.contrast))
    else:
        im=ax.imshow(ndimage.rotate(tmp, angle = 90), cmap=cmap, aspect='auto')
    if args.equal==2:
        forceAspect(ax,aspect=1)

    if args.colorbar!=0:
        cbar=fig.colorbar(im, extend='both')#, shrink=0.9)#, ax=ax)
        cbar.ax.tick_params(labelsize=args.colorbar)
    plt.savefig(args.output+'_'+args.plane+str(args.slice)+'.'+args.format)
