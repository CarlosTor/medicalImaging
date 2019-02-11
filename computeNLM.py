# -*- coding: utf-8 -*-
import sys
import numpy as np
import nibabel
from scipy.ndimage import convolve
from numba import jit

import argparse



def computeSigmaNoise3D(img):
    hx=np.array([[[0.,0.,0.],[0.,-(1./6.),0.],[0.,0.,0.]],
                    [[0.,-(1./6.),0.],[-(1./6.),1.,-(1./6.)],[0.,-(1./6.),0.]],
                    [[0.,0.,0.],[0.,-(1./6.),0.],[0.,0.,0.]]])
    sigma2 = (6.0/7.0) * np.sum(np.square(convolve(img,hx))) / np.float(img.shape[0]*img.shape[1]*img.shape[2])
    return sigma2

def computeSigmaNoise2D(img):
    hx=np.array([[0.,-(1./4.),0.],[-(1./4.),1.,-(1./4.)],[0.,-(1./4.),0.]])
    sigma2 = (4.0/5.0) * np.sum(np.square(convolve(img,hx))) / np.float(img.shape[0]*img.shape[1])
    return sigma2



@jit
def computeNLM3DImageValue(data,hss,hps,h):
    padding3D=[(hps[0]+hss[0],hps[0]+hss[0]),(hps[1]+hss[1],hps[1]+hss[1]),(hps[2]+hss[2],hps[2]+hss[2])]
    data=np.pad(data,padding3D,mode='constant',constant_values=0)

    result=np.zeros(data.shape)
    for x in xrange(hps[0]+hss[0],data.shape[0]-(hps[0]+hss[0])):
        for y in xrange(hps[1]+hss[1],data.shape[1]-(hps[1]+hss[1])):
            for z in xrange(hps[2]+hss[2],data.shape[2]-(hps[2]+hss[2])):

                sumW = np.float(0.0)
                for ii in xrange(x-hss[0],x+hss[0]+1):
                    for jj in xrange(y-hss[1],y+hss[1]+1):
                        for kk in xrange(z-hss[2],z+hss[2]+1):

                            dist = np.float(0.0)
                            if (ii!=0) | (jj!=0) | (kk!=0):
                                for iii in xrange(-hps[0],hps[0]+1):
                                    for jjj in xrange(-hps[1],hps[1]+1):
                                        for kkk in xrange(-hps[2],hps[2]+1):

                                            dist += (data[x+iii,y+jjj,z+kkk]-data[ii+iii,jj+jjj,kk+kkk])**2

                            result[x,y,z] += data[ii,jj,kk] * np.exp(-dist/h)
                            sumW += np.exp(-dist/h)

                result[x,y,z] /= sumW

    return result[hps[0]+hss[0]:-(hps[0]+hss[0]),hps[1]+hss[1]:-(hps[1]+hss[1]),hps[2]+hss[2]:-(hps[2]+hss[2])]


@jit
def computeNLM2DImageValue(data,hss,hps,h):
    padding2D=[(hps[0]+hss[0],hps[0]+hss[0]),(hps[1]+hss[1],hps[1]+hss[1])]
    data=np.pad(data,padding2D,mode='constant',constant_values=0)

    eps = np.finfo(float).eps
    result=np.zeros(data.shape)
    for x in xrange(hps[0]+hss[0],data.shape[0]-(hps[0]+hss[0])):
        for y in xrange(hps[1]+hss[1],data.shape[1]-(hps[1]+hss[1])):

            sumW = np.float(0.0)
            for ii in xrange(x-hss[0],x+hss[0]+1):
                for jj in xrange(y-hss[1],y+hss[1]+1):

                    dist = np.float(0.0)
                    if (ii!=0) | (jj!=0):
                        for iii in xrange(-hps[0],hps[0]+1):
                            for jjj in xrange(-hps[1],hps[1]+1):

                                dist += (data[x+iii,y+jjj]-data[ii+iii,jj+jjj])**2

                    result[x,y] += data[ii,jj] * np.exp(-dist/h)
                    sumW += np.exp(-dist/h)

            result[x,y] /= sumW+eps

    return result[hps[0]+hss[0]:data.shape[0]-(hps[0]+hss[0]),hps[1]+hss[1]:data.shape[1]-(hps[1]+hss[1])]



if __name__ == '__main__':
  #'''
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', help='Input image (required)', type=str, required = True)
  parser.add_argument('-hss', '--hss', help='Half search-window size (default, 3 x 3 x 3)', type=int, nargs='*', default=3, required = False)
  parser.add_argument('-hps', '--hps', help='Half patch-window size (default, 3 x 3 x 3)', type=int, nargs='*', default=3, required = False)
  parser.add_argument('-hp', '--hparameter', help='Smooth parameter (default, the standard deviation of input)', type=float, default=-1.0, required = False)
  parser.add_argument('-o', '--output', help='Output image (default, input_name+\'_NLM\')', type=str, default='', required = False)

  args = parser.parse_args()
  np.seterr(divide='ignore', invalid='ignore')

  try:
      inputImage = nibabel.load(args.input)
      input = inputImage.get_data()
  except:
      print 'Input file not found'
      sys.exit()


  if isinstance(args.hss, int):
      hss = args.hss*np.ones(len(input.shape),dtype=int)
  elif len(args.hss) != len(input.shape):
      hss = args.hss[0]*np.ones(len(input.shape),dtype=int)
  else:
      hss = args.hss

  if isinstance(args.hps, int):
      hps = args.hps*np.ones(len(input.shape),dtype=int)
  elif len(args.hps) != len(input.shape):
      hps = args.hps[0]*np.ones(len(input.shape),dtype=int)
  else:
      hps = args.hps



  try:
      if len(input.shape)==2:
          if args.hparameter < 0:
              betah = 1.0
              h = np.float(2.0 * betah * (computeSigmaNoise2D(input)) * np.float((2*hps[0]+1)*(2*hps[1]+1)) )
          else:
              h = args.hparameter
          inputNLM = computeNLM2DImageValue(input,hss,hps,h)
      else:
          if args.hparameter < 0:
              betah = 1.0
              h = np.float(2.0 * betah * (computeSigmaNoise3D(input)) * np.float((2*hps[0]+1)*(2*hps[1]+1)*(2*hps[2]+1)) )
          else:
              h = args.hparameter
          inputNLM = computeNLM3DImageValue(input,hss,hps,h)
  except:
      print 'Error when computing NLM algortihm'
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
          nibabel.save(nibabel.Nifti1Image(inputNLM,inputImage.affine),inputName+'_NLM.nii.gz')
      else:
          nibabel.save(nibabel.Nifti1Image(inputNLM,inputImage.affine),args.output)
  except:
      print 'Output path is not correct'
