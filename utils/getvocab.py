import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--input', '-i', metavar='N', type=int, nargs='+', help='input file')
parser.add_argument('--output', '-o', metavar='', type=str, help='output file')
args = parser.parse_args()

infile = args.input
vocab = defaultdict(int)
with open(infile,'r') as i:
	for line in i:
		words = line.strip().split()
		for word in words:
			vocab[word] += 1
			
outfile = args.output
o = open(outfile,'w')
for word in vocab.keys():
	o.write(word+"\n")
o.close()
