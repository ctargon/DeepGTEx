#/usr/bin/python

'''
	This file allows users to visualize sets of genes with tsne
'''

import numpy as np 
import os
import subprocess
import json
import shutil
import itertools
import sys, argparse
import time
from sklearn.manifold import TSNE
import seaborn as sns
import matplotlib.pyplot as plt
from halo import Halo
sys.path.append(os.path.dirname(os.getcwd()))

from GTEx import GTEx
from subset_gene_test import create_raw_combos, create_random_subset, load_data



if __name__ == '__main__':

	# parse arguments
	parser = argparse.ArgumentParser(description='Run tests on specified subsets of a hallmark or random set')
	parser.add_argument('--set', help='subset to be used', type=str, required=True, choices=['hedgehog', 'notch', 'random'])
	parser.add_argument('--num_genes', help='number of genes', type=int, required=True)
	parser.add_argument('--set_size', help='size of subsets to visualize', type=int, required=True, choices=[1,2,3])
	parser.add_argument('--save', help='save .npy TSNE matrix', type=int, required=False, choices=[0,1], default=0)
	parser.add_argument('--load', help='load .npy TSNE matrix', type=int, required=False, choices=[0,1], default=0)
	args = parser.parse_args()

	# start halo spinner
	spinner = Halo(text='Loading', spinner='dots')

	# load the GTEx float data and the list of total genes in GTEx
	print('loading genetic data...')
	spinner.start()
	gtex_gct_flt = np.load('../datasets/gtex_gct_data_float.npy')
	total_gene_list = np.load('../datasets/gtex_complete_gene_list_str.npy')
	spinner.stop()

	# load a data dictionary with keys as classes, values as partioned GEMs
	data = load_data("../data_scripts/numsamples.json", gtex_gct_flt)

	# load gene subset based on paramaters given
	if args.set == 'hedgehog':
		sub = np.load('../datasets/hallmark_numpys/HALLMARK_HEDGEHOG_SIGNALING.npy')
		genes = sub[:,1].tolist()
	elif args.set == 'notch':
		sub = np.load('../datasets/hallmark_numpys/HALLMARK_NOTCH_SIGNALING.npy')
		genes = sub[:,1].tolist()
	else:
		genes = create_random_subset(args.num_genes, total_gene_list)


	# create dictionary of combinations of genes
	gene_dict = create_raw_combos(genes, args.set_size)

	######## THIS IS HARDCODED FOR NOW... MUST CHANGE IN FUTURE ################
	# prev_accs = np.loadtxt('../logs/hedgehog/hh_3_gene_accuracy.txt', delimiter='\t', dtype=np.str)
	# accs = prev_accs[:,1]
	# accs = accs.astype(np.float32)

	# convert dictionary to list
	l = []
	for k in gene_dict:
		l.append(list(k))

	# create matrix to run through tsne
	# creating matrix for tsne calculations
	if args.load == 0:
		print('creating TSNE calculation matrix...')
		spinner.start()

		f = []
		for combo in l:
			d = GTEx(data, total_gene_list, combo)

			if args.set_size == 1:
				a = d.train.data[:,0]
			elif args.set_size == 2:
				a = np.append(d.train.data[:,0], d.train.data[:,1])
			elif args.set_size == 3:
				a = np.append(d.train.data[:,0], d.train.data[:,1])
				a = np.append(a, d.train.data[:,2])

			f.append(a)

		# convert to numpy format
		x_data = np.array(f)

		spinner.stop()

	
	spinner.start()
	
	if args.load == 1:
		print('Loading .npy TSNE file...')
		X_embedded = np.load('../datasets/TSNE/' + str(args.set) + '_' + str(args.set_size) + '.npy')
	else:
		# run TSNE
		print('running TSNE...')
		X_embedded = TSNE().fit_transform(x_data)
	
	spinner.stop()

	if args.save == 1:
		print('Saving .npy TSNE file...')
		np.save('../datasets/TSNE/' + str(args.set) + '_' + str(args.set_size) + '.npy', X_embedded)
	
	# viz with seaborne
	sns.regplot(x=X_embedded[:,0], y=X_embedded[:,1], fit_reg=False, scatter_kws={'s':1}, hue=accs)

	# UNCOMMENT FOR HUE VISUALIZATION OF CLASSIFICATIONS
	#plt.scatter(X_embedded[:,0], X_embedded[:,1], c=accs, s=1, cmap=plt.cm.coolwarm)
	#cbar = plt.colorbar()

	# show plot
	plt.show()