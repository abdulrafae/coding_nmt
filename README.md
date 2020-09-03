# Coding Neural Machine Translation (NMT)

## Install dependencies
Setup fairseq toolkit
```
git clone https://github.com/pytorch/fairseq
cd fairseq
pip install --editable ./

# on MacOS:
# CFLAGS="-stdlib=libc++" pip install --editable ./
```

Install evaluation packages
```
pip install sacrebleu
```
Install tokenization packages
```
git clone https://github.com/moses-smt/mosesdecoder.git
```

Install Byte-pair Encoding pacakges
```
git clone https://github.com/rsennrich/subword-nmt.git
```

## Download and Pre-process IWSLT'17 French-English data

Download and tokenize data
```
bash prepare_data.sh
```

Create Metaphone encoded data
```
python phonetic_encoding.py --source fr --target en --input data/ --output data/ --phonetic metaphone --siles train,valid,test
Use --phonetic metaphone,nysiis,soundex for multiple coding
```

Byte-pair encode the data
```
bash apply_bpe.sh fr mt en
```

## Train NMT System
Train French+Metaphone-English Concatenation Model
```
bash train_concatenation.sh
```
or

Train French+Metaphone-English Multisource Model
```
bash train_multisource.sh
```
