# Coding Textual Inputs Boosts the Accuracy of Neural Networks

## (1) Coding Neural Machine Translation (NMT)

### Install dependencies
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

### Download and Pre-process IWSLT'17 French-English data

Download and tokenize data
```
bash prepare_data.sh
```

Create Metaphone coded data
```
python phonetic_encoding.py --source fr --target en --input data/ --output data/ --phonetic metaphone --files train,valid,test
Use --phonetic metaphone,nysiis,soundex for multiple coding
```

Byte-pair encode the data
```
bash apply_bpe.sh fr mt en
```

### Train NMT System
Train French+Metaphone-English Concatenation Model
```
bash train_concatenation.sh
```
or

Train French+Metaphone-English Multisource Model
```
bash train_multisource.sh
```

## (2) Coding Language Modeling

### Install dependencies
```
git clone https://github.com/facebookresearch/XLM.git
```

### Download and Pre-process IWSLT'17 French-English data

Download and tokenize data
```
bash prepare_data.sh
```

Create vocabulary 
```
OUTPATH=data/processed/XLM_en/30k
mkdir -p $OUTPATH

python utils/getvocab.py --input $OUTPATH/train.en --output $OUTPATH/vocab.en
python utils/getvocab.py --input $OUTPATH/train.ny --output $OUTPATH/vocab.ny
python utils/getvocab.py --input $OUTPATH/train.enny --output $OUTPATH/vocab.enny
```

Binarize data
```
python XLM/preprocess.py $OUTPATH/vocab.en $OUTPATH/train.en &
python XLM/preprocess.py $OUTPATH/vocab.en $OUTPATH/valid.en &
python XLM/preprocess.py $OUTPATH/vocab.en $OUTPATH/test.en &

python XLM/preprocess.py $OUTPATH/vocab.ny $OUTPATH/train.ny &
python XLM/preprocess.py $OUTPATH/vocab.ny $OUTPATH/valid.ny &
python XLM/preprocess.py $OUTPATH/vocab.ny $OUTPATH/test.ny &

python XLM/preprocess.py $OUTPATH/vocab.enny $OUTPATH/train.enny &
python XLM/preprocess.py $OUTPATH/vocab.enny $OUTPATH/valid.enny &
python XLM/preprocess.py $OUTPATH/vocab.enny $OUTPATH/test.enny &

mv $OUTPATH/train.enny.pth $OUTPATH/train.en-ny.pth
mv $OUTPATH/valid.enny.pth $OUTPATH/valid.en-ny.pth
mv $OUTPATH/test.enny.pth $OUTPATH/test.en-ny.pth
```
