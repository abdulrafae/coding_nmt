import jellyfish
import argparse
import os
from shutil import copyfile as cp

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--source', '-s', metavar='source-lang', type=str, help='Source language')
parser.add_argument('--target', '-t', metavar='target-lang', type=str, help='Target language')
parser.add_argument('--coding', '-p', metavar='coding-algo', type=str, help='Coding algorithm comma separated (metaphone, nysiis, soundex, fixed-length or huffman)')
parser.add_argument('--base', '-b', metavar='coding-base', type=int, help='Coding base')
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

config = {'metaphone':('mt',jellyfish.metaphone),'nysiis':('ny',jellyfish.nysiis),'soundex':('sx',jellyfish.soundex), 'fixedlen':(fixed_len),'huffman':(huffman)}

def create_fixed_len_vocab(data,limit):

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

	print("Writing "+str(limit)+" chars of "+str(x)+" length!")
	new_mapping = dict()
	for i,word in enumerate(vocab):
		key = keywords[i]
		new_key = ''
		for ele in key:
			new_key += numbers[ele] + '__'
		new_mapping[word] = new_key[:-2]
		
	return new_mapping

def create_huffman_vocab(data,vocab,limit):
	freq_dict = get_huffman.list_freq(data) # Create frequency dictionary.
	freqs = list(freq_dict.items()) # HuffmanCode requires (symbol, freq) pairs.
	
	binary_huffman = get_huffman.HuffmanCode(freqs, base) # Usual base 2 Huffman coding.
	binary_encoding = binary_huffman.encode(data)
	
	new_mapping = dict()
	for word in vocab.keys():
		new_mapping[word] = binary_huffman.encode(word)
		
	return new_mapping
	
def fixed_len(word):
	if vocab_mappping == None:
		print("Vocab not created!")
	
	try:
		encoded_str = vocab_mappping[word]
		encoded_word = ""
		for x in encoded_str.split('__'):
			tmp = "{0}".format(x).zfill(2)
			encoded_word += str(tmp)
	except:
		print("ERROR coding word "+str(word)+" using fixed length")
		exit()
	
	return encoded_word
	
	
def huffman(word):
	if vocab_mappping == None:
		print("Vocab not created!")
		
	try:
		encoded_word = vocab_mappping[word]
		
	except:
		print("ERROR coding word "+str(word)+" using fixed length")
		exit()
	
	return encoded_word
	
vocab_mapping = None

data = ""
vocab = dict()
for filename in filenames:
	print(src+" : "+format+" : "+filename)
	coding_file = open(path_output+filename+'.'+format,'w',)
	coding_concat_file = open(path_output+filename+'.'+src+format,'w')
	with open(input_path+filename+'.'+src,'r') as input:
		for i,line in enumerate(input):
			line = line.strip()
			data += line.strip() + " "
			words = line.split()
			for word in words:
				vocab[word] += 1
			
for c in config:
	if format == 'fixedlen':
		base = args.base
		if base == '':
			print("Fixed Length coding needs base (use --base parameter)")
			exit()
		
for coding in codings:
	
	format,encode = config[phonetic_encoding]
	
	if format == 'fixedlen':
		vocab_mapping = create_fixed_len_vocab(vocab,base)
	elif format == 'huffman':
		vocab_mapping = create_huffman_vocab(filenames)
	
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
				str = ""
				for word in words:
					encoded_word = ""
					
					try:
						encoded_word = encode(word)
					except:
						encoded_word = word
					try:
						str += encoded_word + " "
					except:
						print("Error in line: ",i)
				str = str[:-1]
				try:
					coding_file.write(str+'\n')
					coding_concat_file.write(line+' '+str+'\n')
				except:
					print("Line ",i)
					exit()
		coding_file.close()
		phonetic_concat_file.close()
		
		cp(input_path+filename+'.'+src,path_output+filename+'.'+src)
		if filename!='test':
			cp(input_path+filename+'.'+tgt,path_output+filename+'.'+tgt)
			
print("DONE!")
