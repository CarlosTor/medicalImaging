# coding=utf-8
import sys
import os
import argparse
import numpy as np
import nibabel
from skimage import filters

if __name__ == '__main__':

	#Inputs#
	parser = argparse.ArgumentParser(prog='computeMeshBrainVISA')

	parser.add_argument('-i', '--input', help='Input NifTI image (required, accepted multiple times)', type=str, nargs='*', required = True)
	parser.add_argument('-t', '--threshold', help='Threshold value for binarization before meshing (default Otsu method)', type=float, nargs='*', default=[-1], required = False)
	parser.add_argument('-o', '--output', help='Prefix added to input name for output image (default \'_th\' + threshold_value + \'_S16\')', type=str, default='_th_S16', required = False)


	args = parser.parse_args()
	np.seterr(divide='ignore', invalid='ignore')


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
	print('Thresholds: '+str(thresholds))



	for i,im in enumerate(input):

		splitInput=args.input[i].split('.')
		if splitInput[-1]=='nii':
			inputName='.'.join(splitInput[:-1])
		elif splitInput[-2]=='nii':
			inputName='.'.join(splitInput[:-2])
		else:
			print('Input file must be a nifti image')
			sys.exit()
		splitInput = inputName.split('/')
		inputPath = '/'.join(splitInput[:-1])
		inputFilename = splitInput[-1]
		#output#
		if args.output=='_th_S16':
			output = '_th'+str(thresholds[i])+'_S16'
		else:
			output = args.output

		print('\nProcessing '+str(inputFilename))

		#Thresholding#
		print('Thresholding '+str(thresholds[i]))
		im[im<thresholds[i]]=0
		im[im>=thresholds[i]]=1
		inputImage = nibabel.load(args.input[i])
		nibabel.save(nibabel.Nifti1Image(im.astype(float),inputImage.affine),inputPath+'/'+inputFilename+'_th'+str(thresholds[i])+'.nii.gz')
		#Converting to S16 format#
		print('Converting to S16 format')
		os.system('AimsFileConvert -i '+inputPath+'/'+inputFilename+'_th'+str(thresholds[i])+'.nii.gz -o '+inputPath+'/'+inputFilename+'_th'+str(thresholds[i])+'_S16.nii.gz -t S16')
		#Generating BrainVISA mesh#
		print('Applying  to S16 format')
		os.system('AimsMeshBrain -i '+inputPath+'/'+inputFilename+'_th'+str(thresholds[i])+'_S16.nii.gz -o '+inputPath+'/'+inputFilename+output+'.gii')
