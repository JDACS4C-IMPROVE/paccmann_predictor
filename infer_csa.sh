#!/bin/bash

# Launches model for inferencing from within the container


####################################################################
## Exceute inference script for your model with the CMD arguments ##
####################################################################
#infer=/usr/local/Paccmann_MCA/infer.py
IMPROVE_MODEL_DIR=${IMPROVE_MODEL_DIR:-$( dirname -- "$0" )}
CANDLE_MODEL=infer_csa.py
CANDLE_MODEL=${IMPROVE_MODEL_DIR}/${CANDLE_MODEL}

CUDA_VISIBLE_DEVICES=$1
CANDLE_DATA_DIR=$2

CMD="python3 ${CANDLE_MODEL}"


echo "using container "
echo "using CUDA_VISIBLE_DEVICES ${CUDA_VISIBLE_DEVICES}"
echo "using CANDLE_DATA_DIR ${CANDLE_DATA_DIR}"
echo "running command ${CMD}"

CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES} CANDLE_DATA_DIR=${CANDLE_DATA_DIR} $CMD