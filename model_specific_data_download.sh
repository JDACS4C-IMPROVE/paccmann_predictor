#!/bin/bash

DATA_URL=$1
OUTPUT_DIR=$2

if [ -f "$OUTPUT_DIR/Data" ]; then 
  echo "Model specific data directory present, skipping download"
elif [ ! -d $OUTPUT_DIR ]
then
    echo "Directory does not exist, Making an output directory"
    mkdir -p $OUTPUT_DIR
fi
wget -P $OUTPUT_DIR $DATA_URL
unzip -d $OUTPUT_DIR "$OUTPUT_DIR/Data_MCA.zip" #TODO: CHANGE THIS 
