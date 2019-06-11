import argparse
import utils
import numpy as np
import pandas as pd
import random
import sklearn.datasets
import sys



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser(description="Create a synthetic classification dataset")
	parser.add_argument("--n-samples", help="number of samples", type=int, default=100)
	parser.add_argument("--n-genes", help="number of genes", type=int, default=20)
	parser.add_argument("--n-classes", help="number of classes", type=int, default=2)
	parser.add_argument("--n-sets", help="number of gene sets", type=int, default=10)
	parser.add_argument("--dataset", help="name of dataset file", default="example_data.txt")
	parser.add_argument("--labels", help="name of label file", default="example_labels.txt")
	parser.add_argument("--gene-sets", help="name of gene sets file", default="example_genesets.txt")

	args = parser.parse_args()

	# create synthetic dataset
	n_informative = args.n_genes // 10
	n_redundant = args.n_genes - n_informative

	X, y = sklearn.datasets.make_classification(args.n_samples, args.n_genes, n_informative=n_informative, n_redundant=n_redundant, n_classes=args.n_classes)

	# initialize gene names, sample names
	X_samples = ["sample-%08d" % i for i in range(args.n_samples)]
	X_genes = ["gene-%06d" % i for i in range(args.n_genes)]

	# initialize dataframes
	X = pd.DataFrame(X, index=X_samples, columns=X_genes)
	y = pd.DataFrame(y, index=X_samples)

	# create synthetic gene sets
	gene_sets = []

	for i in range(args.n_sets):
		n_genes = random.randint(5, min(max(10, args.n_genes // 10), args.n_genes))
		genes = random.sample(X_genes, n_genes)

		gene_sets.append(["gene-set-%03d" % i] + genes)

	# save dataset to file
	utils.save_dataframe(args.dataset, X)

	# save labels to file
	y.to_csv(args.labels, sep="\t", header=None)

	# save gene sets to file
	f = open(args.gene_sets, "w")
	f.write("\n".join(["\t".join(gene_set) for gene_set in gene_sets]))
