#!/bin/sh

FAIRSEQROOT=fairseq

GPU=0
MAINSRC=$1
PHONETICSRC=$2
TRG=$3
echo "Train "$MAINSRC$PHONETICSRC-$TRG

BASE_PATH=$DATA_ROOT
TEXT=$BASE_PATH/$MAINSRC$PHONETICSRC\_$TRG/

DATA_BIN=$BASE_PATH/data_bin/$MAINSRC$PHONETICSRC\_$TRG}/concat/
LOG_DIR=$BASE_PATH/log/$MAINSRC$PHONETICSRC\_$TRG/concat/
CPKT_DIR=$BASE_PATH/checkpoint/$MAINSRC$PHONETICSRC\_$TRG/concat/
RESULT_DIR=$BASE_PATH/result/$MAINSRC$PHONETICSRC\_$TRG/concat/
mkdir -p $CPKT_DIR $DATA_BIN $LOG_DIR $RESULT_DIR

echo "Preprocess "$MAINSRC$PHONETICSRC-$TRG
python $FAIRSEQROOT/preprocess.py \
--source-lang $MAINSRC$PHONETICSRC \
--target-lang $TRG \
--trainpref $TEXT/train.bpe \
--validpref $TEXT/valid.bpe \
--destdir $DATA_BIN \
--worker 10 | tee $LOG_DIR/prepro.out

# Train the Concatenation model
echo "Train "$MAINSRC$PHONETICSRC-$TRG
CUDA_VISIBLE_DEVICES=$GPU python $FAIRSEQROOT/train.py $DATA_BIN \
--lr 0.25 \
--clip-norm 0.1 \
--dropout 0.2 \
--max-tokens 6000 \
--arch fconv_iwslt_de_en \
--no-epoch-checkpoints \
--max-epoch 75 \
--patience 5 \
--save-dir $CPKT_DIR | tee $LOG_DIR/train.out

#Translate using Concatenated test data
echo "Translate  "$MAINSRC$PHONETICSRC-$TRG
CUDA_VISIBLE_DEVICES=$GPU python $FAIRSEQROOT/interactive.py $DATA_BIN \
--path $CPKT_DIR/checkpoint_best.pt \
--batch-size 32 \
--beam 12 \
--buffer-size 64 \
--remove-bpe \
--input $TEXT/test.bpe.$MAINSRC$PHONETICSRC | tee $RESULT_DIR/gen.sys

#Evaluate BLEU for translated data
grep ^H $RESULT_DIR/gen.sys | cut -f3- > $RESULT_DIR/hypo.tok.$TRG
cat $RESULT_DIR/hypo.tok.$TRG | $MOSESROOT/recaser/detruecase.perl | $MOSESROOT/tokenizer/detokenizer.perl -l $TRG > $RESULT_DIR/hypo.$TRG
cat $RESULT_DIR/hypo.$TRG | sacrebleu --tokenize=13a -t iwslt17 -l ${MAINSRC}-${TRG}