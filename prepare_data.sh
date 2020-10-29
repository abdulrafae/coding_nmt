#!/usr/bin/env bash

MOSESROOT=/home/akhan4/packages/mosesdecoder/scripts/
TOKENIZER=$MOSESROOT/tokenizer/tokenizer.perl
TCROOT=$MOSESROOT/recaser/
CLEAN=$MOSESROOT/training/clean-corpus-n.perl

URL="https://wit3.fbk.eu/archive/2017-01-trnted/texts/fr/en/fr-en.tgz"
GZ=fr-en.tgz

if [ ! -d "$MOSESROOT" ]; then
    echo "Please set MOSESROOT variable correctly to point to Moses scripts."
    exit
fi

SRC=$1
TRG=$2
LANG=$SRC-$TRG
PREP=data
TMP=$PREP/tmp
ORIG=orig

mkdir -p $ORIG $TMP $PREP

# Download IWSLT'17 French-English Parallel Data 
echo "Downloading data from ${URL}..."
cd $ORIG
wget "$URL"

if [ -f $GZ ]; then
    echo "Data successfully downloaded."
else
    echo "Data not successfully downloaded."
    exit
fi

tar zxvf $GZ
cd ..

# Extract Raw Data and tokenize
echo "pre-processing train data..."
for L in $SRC $TRG
 do
    F=train.tags.$LANG.$L
    TOK=train.tags.$LANG.tok.$L

    cat $ORIG/$LANG/$F | \
    grep -v '<url>' | \
    grep -v '<talkid>' | \
    grep -v '<keywords>' | \
    sed -e 's/<title>//g' | \
    sed -e 's/<\/title>//g' | \
    sed -e 's/<description>//g' | \
    sed -e 's/<\/description>//g' | \
    $TOKENIZER -threads 8 -a -l $L > $TMP/$TOK
    echo ""
done

echo "Pre-processing valid data"
for L in $SRC $TRG
 do
    for O in `ls $ORIG/$LANG/IWSLT17.TED*.$L.xml`; do
    fname=${O##*/}
    F=$TMP/${fname%.*}
    echo $O $F
    grep '<seg id' $O | \
		grep -v '<url>' | \
		grep -v '<talkid>' | \
		grep -v '<keywords>' | \
		grep -v '<speaker>' | \
		grep -v '<reviewer' | \
		grep -v '<translator' | \
		grep -v '<doc' | \
		grep -v '</doc>' | \
		sed -e 's/<title>//g' | \
		sed -e 's/<\/title>//g' | \
		sed -e 's/<description>//g' | \
		sed -e 's/<\/description>//g' | \
		sed 's/^\s*//g' | \
		sed 's/\s*$//g' | \
    $TOKENIZER -threads 8 -a -l $L > $F
    echo ""
    done
done

echo "Creating valid file"
for L in $SRC $TRG
 do

	cat $TMP/IWSLT17.TED.dev2010.fr-en.$L \
		$TMP/IWSLT17.TED.tst2010.fr-en.$L \
		$TMP/IWSLT17.TED.tst2011.fr-en.$L \
		$TMP/IWSLT17.TED.tst2012.fr-en.$L \
		$TMP/IWSLT17.TED.tst2013.fr-en.$L \
		$TMP/IWSLT17.TED.tst2014.fr-en.$L \
		$TMP/IWSLT17.TED.tst2015.fr-en.$L \
		> $TMP/valid.tok.$L
	
done

# Clean Data
echo "cleaning train data..."
perl $CLEAN -ratio 1.5 $TMP/train.tags.$LANG.tok $SRC $TRG $TMP/train.tok.clean 1 175

# Truecase Data
$TCROOT/train-truecaser.perl -corpus $TMP/train.tok.clean.$SRC -model $PREP/truecase-model.$SRC
$TCROOT/train-truecaser.perl -corpus $TMP/train.tok.clean.$TRG -model $PREP/truecase-model.$TRG

echo "Truecasing train data"
for L in $SRC $TRG
 do
	$TCROOT/truecase.perl -model $PREP/truecase-model.$L < $TMP/train.tok.clean.$L > $TMP/train.tc.$L
done

echo "Truecasing valid data"
for L in $SRC $TRG 
 do
	$TCROOT/truecase.perl -model $PREP/truecase-model.$L < $TMP/valid.tok.$L > $TMP/valid.tc.$L
done

echo "Download test.$SRC"
sacrebleu --test-set iwslt17 --language-pair ${SRC}-${TRG} --echo src > $TMP/test.$SRC

echo "Tokenize test.$SRC"
cat $TMP/test.$SRC | $TOKENIZER -threads 8 -a -l ${SRC} > $TMP/test.tok.$SRC

echo "Truecase test.$SRC"
$TCROOT/truecase.perl -model $PREP/truecase-model.$SRC < $TMP/test.tok.$SRC > $TMP/test.tc.$SRC

for F in train valid
 do
	for L in $SRC $TRG 
	 do
		cp $TMP/$F.tc.$L $PREP/$F.$L
	done 
done

cp $TMP/test.tc.$SRC $PREP/test.$SRC

# Removing temporary directory
rm -rf $TMP $ORIG