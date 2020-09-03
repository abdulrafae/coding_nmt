#!/usr/bin/env bash

BPEROOT=subword-nmt/subword_nmt
BPE_TOKENS=16000
DATA_DIR=data

MAINSRC=$1
PHONETICSRC=$2
TRG=$3

#(5) Byte Pair Encoding
BPE_DIR=$DATA_DIR/bpe/$MAINSRC$PHONETICSRC\_$TRG/
mkdir -p $BPE_DIR
BPE_CODE=$BPE_DIR/code

echo "learn_bpe.py on train"
cat $DATA_DIR/train.$MAINSRC $DATA_DIR/train.$PHONETICSRC $DATA_DIR/train.$TRG | $BPEROOT/learn_bpe.py -s $BPE_TOKENS > $BPE_CODE

for L in $MAINSRC $PHONETICSRC $MAINSRC$PHONETICSRC $TRG
 do
    for F in train valid
     do
        echo "apply_bpe.py on ${F}.${L}"
        python $BPEROOT/apply_bpe.py -c $BPE_CODE < $DATA_DIR/$F.$L > $DATA_DIR/$F.bpe.$L
    done
done

echo "Apply bpe on test.$MAINSRC"
python $BPEROOT/apply_bpe.py -c $BPE_CODE < $DATA_DIR/test.$MAINSRC > $DATA_DIR/test.bpe.$MAINSRC

echo "Apply bpe on test.$PHONETICSRC"
python $BPEROOT/apply_bpe.py -c $BPE_CODE < $DATA_DIR/test.$PHONETICSRC > $DATA_DIR/test.bpe.$PHONETICSRC

echo "Apply bpe on test.$MAINSRC$PHONETICSRC"
python $BPEROOT/apply_bpe.py -c $BPE_CODE < $DATA_DIR/test.$MAINSRC$PHONETICSRC > $DATA_DIR/test.bpe.$MAINSRC$PHONETICSRC
