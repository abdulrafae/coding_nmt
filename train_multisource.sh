#!/bin/sh

FAIRSEQROOT=fairseq

GPU=0
MAINSRC=$1
PHONETICSRC=$2
TRG=$3

BASE_PATH=$DATA_ROOT

DATA_BIN=$BASE_PATH/data-bin/$MAINSRC$PHONETICSRC\_$TRG/multisrc/
CPKT_DIR=$BASE_PATH/checkpoint/$MAINSRC$PHONETICSRC\_$TRG/multisrc/
LOG_DIR=$BASE_PATH/log/$MAINSRC$PHONETICSRC\_$TRG/multisrc/
RESULT_DIR=$BASE_PATH/results/$MAINSRC$PHONETICSRC\_$TRG/multisrc/

mkdir -p $LOG_DIR $RESULT_DIR

# Binarize the dataset
TEXT=$BASE_PATH/data/$MAINSRC$PHONETICSRC\_$TRG
python $FAIRSEQROOT/preprocess.py \
--source-lang $MAINSRC \
--target-lang $TRG \
--trainpref $TEXT/train.bpe \
--validpref $TEXT/valid.bpe \
--destdir $DATA_BIN \
--workers 10 | tee $LOG_DIR/prepro_$MAINSRC.out

# Binarize the Phonetic-French dataset
TEXT=$BASE_PATH/data/$MAINSRC$PHONETICSRC\_$TRG
python $FAIRSEQROOT/preprocess.py \
--source-lang $PHONETICSRC \
--target-lang $TRG \
--trainpref $TEXT/train.bpe \
--validpref $TEXT/valid.bpe \
--destdir $DATA_BIN \
--workers 10 --tgtdict $DATA_BIN/dict.$TRG.txt | tee $LOG_DIR/prepro_$PHONETICSRC.out


# Train a multilingual transformer model
CUDA_VISIBLE_DEVICES=$GPU python $FAIRSEQROOT/train.py $DATA_BIN \
--arch multilingual_transformer \
--task multilingual_translation \
--lang-pairs $MAINSRC-$TRG,$PHONETICSRC-$TRG \
--share-decoders \
--share-decoder-input-output-embed \
--ddp-backend=no_c10d \
--optimizer adam \
--adam-betas '(0.9, 0.98)' \
--lr 0.0005 \
--lr-scheduler inverse_sqrt \
--min-lr '1e-09' \
--warmup-updates 4000 \
--warmup-init-lr '1e-07' \
--label-smoothing 0.1 \
--criterion label_smoothed_cross_entropy \
--dropout 0.3 \
--weight-decay 0.0001 \
--max-tokens 4000 \
--update-freq 8 \
--max-epoch 75 \
--patience 5 \
--save-dir $CPKT_DIR | tee $LOG_DIR/train.out

# Translate using main source test data
CUDA_VISIBLE_DEVICES=$GPU python $FAIRSEQROOT/interactive.py $DATA_BIN \
--task multilingual_translation \
--lang-pairs $MAINSRC-$TRG,$PHONETICSRC-$TRG \
--source-lang $MAINSRC --target-lang $TRG \
--path $CPKT_DIR/checkpoint_best.pt \
--buffer-size 64 \
--batch-size 32 \
--beam 12 \
--remove-bpe \
--input $TEXT/test.bpe.$MAINSRC  | tee $RESULT_DIR/gen_$MAINSRC.sys

# Translate using phonetic source test data
CUDA_VISIBLE_DEVICES=$GPU python $FAIRSEQROOT/interactive.py $DATA_BIN \
--task multilingual_translation \
--lang-pairs $MAINSRC-$TRG,$PHONETICSRC-$TRG \
--source-lang $PHONETICSRC --target-lang $TRG \
--path $CPKT_DIR/checkpoint_best.pt \
--buffer-size 64 \
--batch-size 32 \
--beam 12 \
--remove-bpe \
--input $TEXT/test.bpe.$PHONETICSRC  | tee $RESULT_DIR/gen_$PHONETICSRC.sys


#Evaluate BLEU for translated English
grep ^H $RESULT_DIR/gen_$MAINSRC.sys | cut -f3- > $RESULT_DIR/hypo_$MAINSRC.tok.$TRG
cat $RESULT_DIR/hypo_$MAINSRC.tok.$TRG | $MOSESROOT/recaser/detruecase.perl | $MOSESROOT/tokenizer/detokenizer.perl -l $TRG > $RESULT_DIR/hypo_$MAINSRC.$TRG
cat $RESULT_DIR/hypo_$MAINSRC.$TRG | sacrebleu --tokenize=13a -t iwslt17 -l ${MAINSRC}-${TRG}

#Evaluate BLEU for translated Phonetic
grep ^H $RESULT_DIR/gen_$PHONETICSRC.sys | cut -f3- > $RESULT_DIR/hypo_$PHONETICSRC.tok.$TRG
cat $RESULT_DIR/hypo_$PHONETICSRC.tok.$TRG | $MOSESROOT/recaser/detruecase.perl | $MOSESROOT/tokenizer/detokenizer.perl -l $TRG > $RESULT_DIR/hypo_$PHONETICSRC.$TRG
cat $RESULT_DIR/hypo_$PHONETICSRC.$TRG | sacrebleu --tokenize=13a -t iwslt17 -l ${MAINSRC}-${TRG}
