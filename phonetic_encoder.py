import jellyfish
import argparse
import os
from shutil import copyfile as cp

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--source', '-s', metavar='source-lang', type=str, help='Source language')
parser.add_argument('--target', '-t', metavar='target-lang', type=str, help='Target language')
parser.add_argument('--phonetic', '-p', metavar='phonetic-algo', type=str, help='Phonetic algorithm comma separated (metaphone, nysiis or soundex)')
parser.add_argument('--input', '-i', metavar='input-path', type=str, default='', help='Input path')
parser.add_argument('--files', '-f', metavar='file-names', type=str, default='train,valid,test', help='Comma separated filenames')
parser.add_argument('--output', '-o', metavar='input-path', type=str, default='', help='Output path')
					
args = parser.parse_args()
src = args.source
tgt = args.target
input_path = args.input+"/"
output_path = args.output+"/"

filenames = args.files.split(',')
phonetic_encodings = args.phonetic.split(',')

config = {'metaphone':('mt',jellyfish.metaphone),'nysiis':('ny',jellyfish.nysiis),'soundex':('sx',jellyfish.soundex)}

for phonetic_encoding in phonetic_encodings:
	
	format,encode = config[phonetic_encoding]
	
	try: 
		path_output = output_path+src+format+'_'+tgt+'/'
		os.mkdir(path_output)
	except OSError:
		print ("Creation of the directory %s failed" % path_output)
	else:
		print ("Successfully created the directory %s " % path_output)

	for filename in filenames:
		print(src+" : "+format+" : "+filename)
		phonetic_file = open(path_output+filename+'.'+format,'w',)
		phonetic_concat_file = open(path_output+filename+'.'+src+format,'w')
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
					phonetic_file.write(str+'\n')
					phonetic_concat_file.write(line+' '+str+'\n')
				except:
					print("Line ",i)
					exit()
		phonetic_file.close()
		phonetic_concat_file.close()
		
		cp(input_path+filename+'.'+src,path_output+filename+'.'+src)
		if filename!='test':
			cp(input_path+filename+'.'+tgt,path_output+filename+'.'+tgt)
			
print("DONE!")