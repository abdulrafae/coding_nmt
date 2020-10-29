import jellyfish
import argparse
import os
from shutil import copyfile as cp
from collections import defaultdict
import get_huffman
from string import ascii_lowercase
import math
import copy
from random import shuffle

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--source', '-s', metavar='source-lang', type=str, help='Source language')
parser.add_argument('--target', '-t', metavar='target-lang', type=str, help='Target language')
parser.add_argument('--coding', '-p', metavar='coding-algo', type=str, help='Coding algorithm comma separated (metaphone, nysiis, soundex, fixed-length or huffman)')
parser.add_argument('--fxln-base', '-fb', metavar='fixedlen-base', type=int, help='Fixed-Length Coding base', default=0)
parser.add_argument('--huff-base', '-hb', metavar='huffman-base', type=int, help='Huffman Coding base', default=0)
parser.add_argument('--input', '-i', metavar='input-path', type=str, default='', help='Input path')
parser.add_argument('--files', '-f', metavar='file-names', type=str, default='train,valid,test', help='Comma separated filenames')
parser.add_argument('--output', '-o', metavar='input-path', type=str, default='', help='Output path')

args = parser.parse_args()
src = args.source
tgt = args.target
input_path = args.input+"/"
output_path = args.output+"/"

filenames = args.files.split(',')
codings = args.coding.split(',')

def create_fixed_len_vocab(data,limit):

	def getcombinations(set,limit):
		k = limit
		prefix = []
		#set = ['a','b']
		for i in set:
			prefix.append(i)
		#print prefix
		k -= 1
		for j in range(k):
			#print j
			temp = copy.deepcopy(prefix)
			for i,newPrefix in enumerate(temp):
				for w in set:
					prefix.append(newPrefix + w)
		final = []
		for i,val in enumerate(prefix):
			if len(val) == limit:
				final.append(val)		
		return final

	numbers = {'a':'00','b':'01','c':'02','d':'03','e':'04','f':'05','g':'06','h':'07','i':'08','j':'09','k':'10','l':'11','m':'12','n':'13','o':'14','p':'15','q':'16','r':'17','s':'18','t':'19','u':'20','v':'21','w':'22','x':'23','y':'24','z':'25'}

	print("Words "+str(len(data.keys())))

	possible = []
	for j,c in enumerate(ascii_lowercase):#(numbers):
		if j==limit:
			break
		possible.append(c)
		
	x = int(math.ceil(math.log(len(data.keys()),limit)))
	
	keywords = getcombinations(possible,x)

	vocab = list(data.keys())
	shuffle(vocab)

	new_mapping = dict()
	for i,word in enumerate(vocab):
		key = keywords[i]
		new_key = ''
		for ele in key:
			new_key += numbers[ele] + '__'
		new_mapping[word] = new_key[:-2]
		
	print("Created Fixed Length mapping!")

	return new_mapping

def create_huffman_vocab(data,vocab,base):

	freq_dict = get_huffman.list_freq(data) # Create frequency dictionary.
	freqs = list(freq_dict.items()) # HuffmanCode requires (symbol, freq) pairs.
	
	binary_huffman = get_huffman.HuffmanCode(freqs, base) # Usual base 2 Huffman coding.
	#binary_encoding = binary_huffman.encode(data)
	
	new_mapping = dict()
	for word in vocab.keys():
		new_mapping[word] = binary_huffman.encode(word)

	print("Created Huffman mapping!")
	
	return new_mapping,binary_huffman
	
def fixed_len(word):
	if vocab_mapping == None:
		print("Vocab not created!")
	
	try:
		encoded_str = vocab_mapping[word]
		encoded_word = ""
		for x in encoded_str.split('__'):
			tmp = "{0}".format(x).zfill(2)
			encoded_word += str(tmp)
	except:
		print("ERROR coding word "+str(word)+" using fixed length")
		exit()
	
	return encoded_word
	
	
def huffman(word):
	if vocab_mapping == None:
		print("Vocab not created!")
		
	try:
		encoded_word = vocab_mapping[word]
		
	except:
		print("ERROR coding word "+str(word)+" using fixed length")
		exit()
	
	return encoded_word
	

config = {'metaphone':('mt',jellyfish.metaphone),'nysiis':('ny',jellyfish.nysiis),'soundex':('sx',jellyfish.soundex), 'fixedlen':('fx',fixed_len),'huffman':('hf',huffman)}

vocab_mapping = None

data = ""
vocab = defaultdict(int)
for filename in filenames:
	with open(input_path+filename+'.'+src,'r') as input:
		for i,line in enumerate(input):
			line = line.strip()
			data += line.strip() + " "
			words = line.split()
			for word in words:
				vocab[word] += 1
		
		
for coding in codings:
	
	format,encode = config[coding]

	if coding == 'fixedlen':
		fxln_base = args.fxln_base
		if fxln_base == 0:
			print("Fixed Length coding needs base (use --fxln-base parameter)")
			exit()
		format = 'fx'+str(fxln_base)
		print(encode)
		vocab_mapping = create_fixed_len_vocab(vocab,fxln_base)
	if coding == 'huffman':
		huff_base = args.huff_base
		if huff_base == 0:
			print("Huffman coding needs base (use --huff-base parameter)")
			exit()
		format = 'hf'+str(huff_base)
		print(encode)
		vocab_mapping,huff_tree = create_huffman_vocab(data,vocab,huff_base)
	
	try: 
		path_output = output_path+src+format+'_'+tgt+'/'
		os.mkdir(path_output)
	except OSError:
		print ("Creation of the directory %s failed" % path_output)
	else:
		print ("Successfully created the directory %s " % path_output)

	for filename in filenames:
		print(src+" : "+format+" : "+filename)
		coding_file = open(path_output+filename+'.'+format,'w',)
		coding_concat_file = open(path_output+filename+'.'+src+format,'w')
		with open(input_path+filename+'.'+src,'r') as input:
			for i,line in enumerate(input):
				line = line.strip()
				words = line.split()
				str_ = ""
				for word in words:
					encoded_word = ""
					
					try:
						encoded_word = encode(word)
					except:
						encoded_word = word
					try:
						str_ += encoded_word + " "
					except:
						print("Error in line: ",i)
				str_ = str_[:-1]
				try:
					coding_file.write(str_+'\n')
					coding_concat_file.write(line+' '+str_+'\n')
				except:
					print("Line ",i)
					exit()
		coding_file.close()
		coding_concat_file.close()
		
		cp(input_path+filename+'.'+src,path_output+filename+'.'+src)
		if filename!='test':
			cp(input_path+filename+'.'+tgt,path_output+filename+'.'+tgt)
			
print("DONE!")
