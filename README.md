# Coding Textual Inputs Boosts the Accuracy of Neural Networks
Abdul Rafae Khan<sup>+</sup>, Jia Xu<sup>+</sup> & Weiwei Sun<sup>++</sup>

<sup>+</sup> Stevens Institute of Technology

<sup>++</sup> Cambridge University

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

Train English baseline
```
CUDA_VISIBLE_DEVICES=0 python train.py --exp_name xlm_en --dump_path ./dumped_xlm_en --data_path $OUTPATH --lgs 'en' --clm_steps '' --mlm_steps 'en' --emb_dim 256 --n_layers 6 --n_heads 8 --dropout 0.1 --attention_dropout 0.1 --gelu_activation true --batch_size 32 --bptt 256 --optimizer adam_inverse_sqrt,lr=0.00010,warmup_updates=30000,beta1=0.9,beta2=0.999,weight_decay=0.01,eps=0.000001 --epoch_size 300000 --max_epoch 100000 --validation_metrics _valid_en_mlm_ppl --stopping_criterion _valid_en_mlm_ppl,25 --fp16 true --word_mask_keep_rand '0.8,0.1,0.1' --word_pred '0.15' 
```

Train English+NYSIIS
```
CUDA_VISIBLE_DEVICES=0 python train.py --exp_name xlm_en_ny --dump_path ./dumped_xlm_en_ny --data_path $OUTPATH --lgs 'en' --clm_steps '' --mlm_steps 'en,ny' --emb_dim 256 --n_layers 6 --n_heads 8 --dropout 0.1 --attention_dropout 0.1 --gelu_activation true --batch_size 32 --bptt 256 --optimizer adam_inverse_sqrt,lr=0.00010,warmup_updates=30000,beta1=0.9,beta2=0.999,weight_decay=0.01,eps=0.000001 --epoch_size 300000 --max_epoch 100000 --validation_metrics _valid_en_mlm_ppl --stopping_criterion _valid_en_mlm_ppl,25 --fp16 true --word_mask_keep_rand '0.8,0.1,0.1' --word_pred '0.15' 
```

Train English+NYSIIS+Word Alignment
```
CUDA_VISIBLE_DEVICES=0 python train.py --exp_name mlm_en_ny --dump_path ./dumped_mlm_en_ny --data_path $OUTPATH --lgs 'en' --clm_steps '' --mlm_steps 'en,ny,en-ny' --emb_dim 256 --n_layers 6 --n_heads 8 --dropout 0.1 --attention_dropout 0.1 --gelu_activation true --batch_size 32 --bptt 256 --optimizer adam_inverse_sqrt,lr=0.00010,warmup_updates=30000,beta1=0.9,beta2=0.999,weight_decay=0.01,eps=0.000001 --epoch_size 300000 --max_epoch 100000 --validation_metrics _valid_en_mlm_ppl --stopping_criterion _valid_en_mlm_ppl,25 --fp16 true --word_mask_keep_rand '0.8,0.1,0.1' --word_pred '0.15' 
```
